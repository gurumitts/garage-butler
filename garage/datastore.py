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
        cursor.execute("""select datetime(dt,'localtime') as dt, event from events order by dt desc limit 15""")
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
        cursor.execute("""select datetime(dt,'localtime') as dt, event,
                            (strftime('%s','now') - strftime('%s',dt))/60 as
                            elapsed_minutes from events order by dt desc limit 1""")
        row = cursor.fetchone()
        status = {}
        if row is not None:
            for key in row.keys():
                status[key.lower()] = row[key]
            cursor.close()
        return status

    def get_settings(self):
        cursor = self.connection.cursor()
        cursor.execute("""select * from settings limit 1""")
        row = cursor.fetchall()
        settings = {}
        if row is not None:
            for key in row.keys():
                settings[key.lower()] = row[key]
            cursor.close()
        return settings

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
            self.connection.commit()

        cursor = self.connection.cursor()
        try:
            cursor.execute('select count(*) from settings')
            # print cursor.fetchone()
        except Exception as e:
            logging.getLogger('garage').info('Required table not found... creating settings table...')
            cursor.execute("""CREATE TABLE "settings" (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                    "check_interval_mins" INTEGER DEFAULT (2),
                    "notify_interval_mins" INTEGER DEFAULT (30),
                    "warning_threshold_mins" INTEGER DEFAULT (15),
                    "sentry_mode" INTEGER DEFAULT (0))""")
            self.connection.commit()
            cursor.execute('insert into settings (id) values (1)')
            logging.info('done!')
        finally:
            cursor.close()
            self.connection.commit()
