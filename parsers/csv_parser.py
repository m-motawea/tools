from .base import Parser
import csv
import os
from threading import Thread
from multiprocessing import Lock
import datetime


class CSVParser(Parser):
    def __init__(self, *keys):
        self.keys = keys

    def parse(self, path):
        result = []
        index_key_map = {}
        if not os.path.exists(path):
            raise Exception("file {} does not exist.".format(path))

        with open(path, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            for col_no in range(0, len(header)):
                key = header[col_no]
                if key in self.keys:
                    index_key_map[key] = col_no

            if not index_key_map:
                print("failed to acquire any keys")
                return []

            for row in reader:
                row_dict = {}
                for key in index_key_map:
                    row_dict[key] = row[index_key_map[key]]
                result.append(row_dict)

        return result


class ThreadedCSVParser(Parser):
    def __init__(self, no_threads=1, *keys):
        self.no_threads = no_threads
        self.keys = keys
        self.index_key_map = {}
        self.result = []
        self.threads = {}
        self.result_lock = Lock()
        self.thread_state = {}


    def parse(self, path, timeout=60):
        csv_list = []

        if not os.path.exists(path):
            raise Exception("file {} does not exist.".format(path))

        with open(path, "r") as f:
            reader = csv.reader(f)
            print("creating list")
            csv_list = list(reader)

        header = csv_list[0]
        for col_no in range(0, len(header)):
            key = header[col_no]
            if key in self.keys:
                self.index_key_map[key] = col_no

        if not self.index_key_map:
            print("failed to acquire any keys")
            return []

        if self.no_threads == 1:
            self._parse_batch(*csv_list[1:])
        else:
            add_rows = (len(csv_list) - 1) % self.no_threads
            no_rows = len(csv_list) - 1 - add_rows
            step = int(no_rows / self.no_threads)
            for i in range(1, no_rows + 1, step):
                end_row = i + step
                t = Thread(target=self._parse_batch, args=csv_list[i:end_row], daemon=True)
                t.start()
                self.threads[str(i)] = t

            if add_rows:
                print("---------------------add_rows---------------------")
                t_add = Thread(target=self._parse_batch, args=csv_list[no_rows+1:len(csv_list)], daemon=True)
                t_add.start()
                self.threads['add'] = t_add

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


    def _parse_batch(self, *rows):
        try:
            thread_result = []
            for row in rows:
                row_dict = {}
                for key in self.index_key_map:
                    row_dict[key] = row[self.index_key_map[key]]
                thread_result.append(row_dict)

            self.result_lock.acquire()
            self.result += thread_result
            self.result_lock.release()
            return True, len(rows)
        except Exception as e:
            return False, e

