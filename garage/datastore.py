import sqlite3
import logging


DOOR_OPENED = 'door opened'
DOOR_CLOSED = 'door closed'


class DataStore:

    def __init__(self, setup=False):
        self.connection = sqlite3.connect('db/app.sqlite3.db')
        self.connection.row_factory = sqlite3.Row
        if setup:
            self.setup()

    def record_door_opened(self):
        self.add_event(DOOR_OPENED)

    def record_door_closed(self):
        self.add_event(DOOR_CLOSED)

    def add_event(self, event):
        params = [event]

        cursor = self.connection.cursor()
        cursor.execute("""insert into events (EVENT)
                values(?);""", params)
        self.connection.commit()
        cursor.close()

    def get_events(self):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM events order by DT desc""")
        rows = cursor.fetchall()
        events = []
        if rows is not None:
            for row in rows:
                event = {}
                for key in row.keys():
                    event[key.lower()] = row[key]
                events.append(event)
            cursor.close()
        return events

    def get_status(self):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM events order by DT desc""")
        rows = cursor.fetchall()
        events = []
        if rows is not None:
            for row in rows:
                event = {}
                for key in row.keys():
                    event[key.lower()] = row[key]
                events.append(event)
            cursor.close()
        return events

    def shutdown(self):
        self.connection.commit()
        self.connection.close()

    def setup(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute('select count(*) from events')
            # print cursor.fetchone()
        except Exception as e:
            logging.getLogger('garage').info('Required table not found... creating events table...')
            cursor.execute("""create table events(
                ID INTEGER PRIMARY KEY   AUTOINCREMENT,
                DT DATETIME DEFAULT CURRENT_TIMESTAMP,
                EVENT TEXT);""")
            logging.info('done!')
        finally:
            cursor.close()
