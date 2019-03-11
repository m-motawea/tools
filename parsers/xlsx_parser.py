import xlrd
from .base import Parser
import os

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
            else:
                index_key_map[key] = None

        if index_key_map:
            for row_no in range(1, sheet.nrows):
                row_dict = {}
                for key in index_key_map:
                    if index_key_map[key]:
                        row_dict[key] = sheet.cell_value(row_no, index_key_map[key])
                    else:
                        row_dict[key] = None
                if row_dict:
                    result.append(row_dict)

            return result
        else:
            return []