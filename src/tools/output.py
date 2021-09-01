import csv
import io
from typing import List


class Output:
    TEXT = 'text'
    CSV = 'csv'
    TABLE = 'table'
    CHOICES = ['text', 'csv', 'table']

    def __init__(self, *headers: List[str]):
        if not isinstance(headers, tuple) or not headers:
            raise ValueError('expected list of strings for headers')
        self._headers = headers
        self._data = []
        self._col_width = [len(header) for header in headers]

    def add(self, *row: List[str]):
        if not isinstance(row, tuple) or len(row) != len(self._headers):
            raise ValueError(
                f'expected list of ({len(self._headers)} strings for row. Got {row}')
        self._data.append(row)
        for index, cell in enumerate(row):
            self._col_width[index] = max(
                self._col_width[index], len(str(cell)))

    def export(self, type: int) -> str:
        if type == self.TEXT:
            return self._export_text()
        elif type == self.CSV:
            return self._export_csv()
        elif type == self.TABLE:
            return self._export_table()

    def _get_padded_lines(self) -> list:
        lines = []
        for row in self._data:
            line = [pad(cell, self._col_width[index])
                    for index, cell in enumerate(row)]

            lines.append(line)
        return lines

    def _export_text(self) -> str:
        lines = self._get_padded_lines()
        return '\n'.join(['|'.join(line) for line in lines])

    def _export_csv(self) -> str:
        with io.StringIO(newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self._headers)
            writer.writerows(self._data)
            f.seek(0)
            return f.read()

    def _export_table(self) -> str:
        with io.StringIO(newline='') as f:
            f.writelines([
                '+'+'+'.join(['-'*n for n in self._col_width])+'+\n',
                '|'+'|'.join([pad(h, self._col_width[n])
                             for n, h in enumerate(self._headers)])+'|\n',
                '+'+'+'.join(['-'*n for n in self._col_width])+'+\n',
            ])
            for row in self._data:
                f.write(
                    '|'+'|'.join(pad(cell, self._col_width[n]) for n, cell in enumerate(row))+'|\n')

            f.writelines([
                '+'+'+'.join(['-'*n for n in self._col_width])+'+\n'])
            f.seek(0)
            return f.read()


def pad(x, n) -> str:
    if isinstance(x, str):
        return x.ljust(n)
    return str(x).rjust(n)
