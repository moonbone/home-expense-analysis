# coding= utf-8
__author__ = 'maord'
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class consts:
    db_path = os.path.join(BASE_DIR, r'expense.db')
    card_sheets_folder_path = os.path.join(BASE_DIR, r'CC sheets')

