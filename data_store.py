import sqlite3
from config import file_db

class DataStore():
    def __init__(self, file_db):
        self.file = file_db

    def create_tb(self):
        self.con = sqlite3.connect(self.file)
        query = ('''CREATE TABLE IF NOT EXISTS data_store
                (show_id    INT    NOT NULL,
                find_id     INT    NOT NULL);''')
        self.con.execute(query)
        self.con.close()
        print('Created')

    def add_data(self, show_id, find_id):
        self.con = sqlite3.connect(self.file)
        query = (f'''INSERT INTO data_store (show_id, find_id)
                        VALUES ({show_id}, {find_id});''')
        self.con.execute(query)
        self.con.commit()
        self.con.close()
        print('Added')

    def show_data(self):
        self.con = sqlite3.connect(self.file)
        query = ('SELECT * FROM data_store;')
        rows = self.con.execute(query)
        i = 1
        print('  show_id  find_id')
        for row in rows:
            print(f'{i} {row[0]} {row[1]}')
            i += 1
        self.con.close()

    def drob_data(self):
        self.con = sqlite3.connect(self.file)
        query = ('DROP TABLE data_store;')
        self.con.execute(query)
        self.con.close()
        print('Deleted')

    def check_data(self, show_id, find_id):
        self.con = sqlite3.connect(self.file)
        query = (f'''SELECT * FROM data_store
                    WHERE show_id = {show_id} AND find_id = {find_id};''')
        rows = self.con.execute(query)
        for row in rows:
            return row
        self.con.close()

if __name__ == '__main__':
    db_test = DataStore(file_db)
    # db_test.create_tb()
    db_test.show_data()
    # db_test.drob_data()
    # db_test.check_data(14505394, 2623247)