__author__ = 'maord'

import sqlite3
import sys

from Consts import *
import CreditCardSheet


def main(argv):
    os.chdir(consts.card_sheets_folder_path)
    sql = sqlite3.connect(consts.db_path)
    for fn in filter(os.path.isfile, os.listdir(consts.card_sheets_folder_path)):
        c = sql.execute("SELECT * FROM files where file_name = ?;", (fn,))
        if not len(c.fetchall()):
            print (fn)
            cc = CreditCardSheet.CreditCardSheet(fn)
            cc.read_transactions()
            cc.finalize()


if __name__ == '__main__':
    main(sys.argv)
