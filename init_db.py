import sqlite3


def connect_database():
    global conn, cur

    # will connect to db if exists, or create a new one.
    conn = sqlite3.connect('sql_data.db')

    cur = conn.cursor()


def create_database():
    cur.execute('''DROP TABLE IF EXISTS contacts;''')
    cur.execute('''CREATE TABLE IF NOT EXISTS "contacts" (
            "contact_id"	INTEGER PRIMARY KEY,
            "name"	TEXT NOT NULL,
            "email"	TEXT NOT NULL
            );''')


def close_database():
    conn.commit()
    conn.close()


if __name__ == '__main__':
    connect_database()
    create_database()
    close_database()
