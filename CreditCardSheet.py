# coding= utf-8
__author__ = 'maord'

from xml.dom import minidom as xml
import bs4
import datetime
import sqlite3
import xlrd
import sys
import os
from Consts import *
import re

class CreditEntry:
    def __init__(self, date, name, total, charge, notes=''):
        self._date = date
        self._name = name.replace(u"'", u"''")
        self._total_sum = total.replace(u',', u'')
        self._charge_sum = charge.replace(u',', u'')
        self._notes = notes
        charge_number = 1
        total_charges = 1
        mo = re.match(r"תשלום (\d+)\s+מתוך (\d+)", self._notes)
        if mo:
            charge_number = int(mo.group(1))
            total_charges = int(mo.group(2))

        self._charge_number = charge_number
        self._total_charges = total_charges



    @staticmethod
    def factory(date, name, total, charge, notes=''):
        try:
            t = datetime.datetime.strptime(*date)
            return CreditEntry(t, name, total, charge, notes)
        except ValueError:
            print (date[0], name, total, charge, notes, file=sys.stderr)

    def get_sqlite_entry_str(self):
        return r"'%s','%s',%s,%s,'%s',%d,%d" % (datetime.datetime.strftime(self._date, '%Y-%m-%d'),
                                          self._name,
                                          self._total_sum,
                                          self._charge_sum,
                                          self._notes,
                                          self._charge_number, self._total_charges)



class CreditCardSheet:

    def __init__(self, file_path):
        self._fp = file_path
        self._transactions = []
        self._sql = sqlite3.connect(consts.db_path)
        c = self._sql.execute(r"INSERT INTO files (file_name) VALUES ('%s');" % os.path.basename(self._fp))
        self._file_id = c.lastrowid


    def finalize(self):
        self._sql.commit()
        self._sql.close()

    def read_transactions(self):
        for trans in filter(bool, self._read_file_data()):
            try:
                self._sql.execute(r'INSERT INTO expense (date, name, total, charge, notes,charge_number, total_charges, file_id) values (%s,%d);' %
                                  (trans.get_sqlite_entry_str(), self._file_id))
            except:
                print (trans.get_sqlite_entry_str(),file=sys.stderr)

    def _read_file_data(self):

        s = ''
        x = None
        if self._fp.endswith('xlsx'):
            b = xlrd.open_workbook(self._fp)
            s = b.sheet_by_index(0)
            header = list(s.get_rows())[0]
            rows = []
            for row in list(s.get_rows())[1:]:
                row_l = []
                for cell in row:
                    row_l.append(cell.value)
                if r'סכום מקור' in map(lambda h: h.value, header):
                    rows.append(CreditEntry.factory((row_l[0], '%d/%m/%Y'), row_l[2], str(row_l[4]), str(row_l[6]), row_l[7]))
                else:
                    rows.append(CreditEntry.factory((row_l[0], '%d/%m/%Y'), row_l[2], str(row_l[5]), str(row_l[6]), row_l[7]))
            return rows
        else:
            try:
                s = open(self._fp,encoding='cp1255').read()
                soup = bs4.BeautifulSoup(s, 'html.parser')
                x = xml.parseString(soup.prettify())
                e = x.getElementsByTagName('table')[1]
                rows = []
                for row in e.getElementsByTagName('tr')[4:-1]:
                    row_l = []
                    cells = row.getElementsByTagName('td')
                    if len(cells) == 6:
                        for cell in cells:
                            row_l.append(cell.childNodes[0].data.strip())
                        rows.append(CreditEntry.factory((row_l[0], '%d/%m/%Y'), *(row_l[1:4]+[row_l[5]])))
                return rows

            except UnicodeDecodeError:
                s = open(self._fp).read()
                x = xml.parseString(s)
                e = x.getElementsByTagName('Table')[0]
                rows = []
                for row in e.getElementsByTagName('Row')[1:]:
                    row_l = []
                    for cell in row.getElementsByTagName('Data'):
                        if cell.childNodes:
                            row_l.append(cell.childNodes[0].data.strip())
                        else:
                            row_l.append('')
                    #print row_l
                    rows.append(CreditEntry.factory((row_l[0][:11], '%Y-%m-%dT'), row_l[2], row_l[5], *row_l[6:]))
                return rows
                
