import xlrd
from .base import Parser
import os
from threading import Thread
from multiprocessing import Lock
import datetime


class XLSXParser(Parser):
    def __init__(self, tab_names=[], keys=[]):
        self.tab_names = tab_names
        self.keys = keys


    def parse(self, path):
        result = []
        if not os.path.exists(path):
            raise Exception("file {} does not exist".format(path))

        workbook = xlrd.open_workbook(path, on_demand=True)
        if self.tab_names:
            for name in self.tab_names:
                sheet = workbook.sheet_by_name(name)
                result += self._parse_sheet(sheet)
        else:
            worksheet = workbook.sheet_by_index(0)
            result = self._parse_sheet(worksheet)

        return result


    def _parse_sheet(self, sheet: xlrd.sheet.Sheet):
        result = []
        index_key_map = {}
        for col in range(sheet.ncols):
            key = sheet.cell_value(0, col)
            if key in self.keys:
                index_key_map[key] = col

        if index_key_map:
            for row_no in range(1, sheet.nrows):
                row_dict = {}
                for key in index_key_map:
                    if index_key_map.get(key, None) != None:
                        row_dict[key] = sheet.cell_value(row_no, index_key_map[key])
                    else:
                        row_dict[key] = None
                if row_dict:
                    result.append(row_dict)

            return result
        else:
            return []






class ThreadedXLSXParser(Parser):
    def __init__(self, tab_names=[], keys=[], no_threads=1):
        self.tab_names = tab_names
        self.keys = keys
        self.no_threads = no_threads
        self.result_lock = Lock()
        self.result = []
        self.threads = {}
        self.thread_state = {}


    def parse(self, path, timeout=30):
        if not os.path.exists(path):
            raise Exception("file {} does not exist".format(path))

        workbook = xlrd.open_workbook(path, on_demand=True)
        if self.tab_names:
            for name in self.tab_names:
                sheet = workbook.sheet_by_name(name)
                self._parse_sheet(sheet)
        else:
            worksheet = workbook.sheet_by_index(0)
            self._parse_sheet(worksheet)
        end = False

        start_time = datetime.datetime.now()
        while not end:
            end = True
            for thread in self.threads.values():
                print("waiting for thread: {}".format(thread.__str__()))
                if thread.is_alive():
                    end = False
            if datetime.datetime.now() > start_time + datetime.timedelta(seconds=timeout):
                break
        return self.result


    def _parse_sheet(self, sheet: xlrd.sheet.Sheet):
        index_key_map = {}
        for col in range(sheet.ncols):
            key = sheet.cell_value(0, col)
            if key in self.keys:
                index_key_map[key] = col

        add_rows = (sheet.nrows - 1) % self.no_threads
        no_rows = sheet.nrows - 1 - add_rows
        step = int(no_rows / self.no_threads)
        for i in range(1, no_rows, step):
            end_row = i + step
            t = Thread(target=self._parse_target, kwargs={
                "sheet": sheet,
                "key_col": index_key_map,
                "start_row": i,
                "end_row": end_row,
                "name": str(i)
            }, daemon=True)
            t.start()
            self.threads[str(i)] = t

        if add_rows:
            print("---------------------add_rows-----------------")
            t_add = Thread(target=self._parse_target, kwargs={
                "sheet": sheet,
                "key_col": index_key_map,
                "start_row": no_rows + 1,
                "end_row": sheet.nrows,
                "name": "add_rows"
            }, daemon=True)
            t_add.start()
            self.threads[str(sheet.nrows + 1)] = t_add


    def _parse_target(self, sheet: xlrd.sheet.Sheet, key_col: dict, start_row: int, end_row: int, name: str):
        '''
        :param sheet: sheet to be parsed
        :param key_col: map key_name to column order ex: {"ip": 1, "username": 2}
        :param start_row: set to 1 for single thread
        :param end_row: set to sheet.nrows for single thread
        :return: Flag: Bool, columns_processes: int or error msg
        '''
        print("thread parse target started. start_row: {}, end_row: {}, name: {}".format(start_row, end_row, name))
        try:
            thread_result = []
            for row_no in range(start_row, end_row):
                row_dict = {}
                for key in key_col:
                    row_dict[key] = sheet.cell_value(row_no, key_col[key])
                thread_result.append(row_dict)

            self.result_lock.acquire()
            self.result += thread_result
            print("thread {} result:\n{}\n\n".format(name, thread_result))
            self.result_lock.release()
            self.thread_state[name] = True
            return True, end_row - start_row
        except Exception as e:
            self.result_lock.acquire()
            self.thread_state[name] = True
            self.result_lock.release()
            return False, e
