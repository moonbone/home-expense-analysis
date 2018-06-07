import sqlite3


if not "I AM SURE" == input("Are you sure? all data collected will be lost. (Type 'I AM SURE'): "):
    exit()

con = sqlite3.connect('expense.db')

con.executescript(open('database.sql','r').read())

con.commit()

con.close()