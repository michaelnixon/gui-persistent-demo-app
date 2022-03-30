import shelve
import sqlite3


class SQLStorage():
    ''' Represents a persistence layer provided using sqlite
    '''
    FILENAME = "sql_data.db"

    def __init__(self):
        ''' initiate access to the data persistence layer
        '''
        self.conn = sqlite3.connect(self.FILENAME)
        self.data_access = self.conn.cursor()
        # data_access is now a cursor object

    def get_record(self, rid):
        ''' return a single record identified by the record id
        '''
        # note unintuitive creation of single item tuple
        self.data_access.execute(
            """SELECT * from contacts WHERE contact_id = ?;""", (rid,))
        row = self.data_access.fetchone()
        contact = Contact(row[1], row[2], row[0])
        return contact

    def get_all_records(self):
        ''' return all records stored in the database
        '''
        self.data_access.execute("""SELECT * from contacts;""")
        #rows = self.data_access.fetchall()
        contacts = []
        for row in self.data_access:
            contacts.append(
                Contact(row[1], row[2], row[0]))
        return contacts

    def save_record(self, record):
        ''' add a record represented by a dict with a new id
        '''
        # if it's still 0 then it's a new record, otherwise it's not
        if record.rid == 0:
            self.data_access.execute("""INSERT INTO contacts(name,email) VALUES (?,?)
            """, (record.name, record.email))
            record.rid = self.data_access.lastrowid
        else:
            self.data_access.execute("""UPDATE contacts SET name = ?, email = ?
            WHERE contact_id = ?""", (record.name, record.email, record.rid))
        self.conn.commit()

    def get_all_sorted_records(self):
        return sorted(self.get_all_records(), key=lambda x: x.rid)

    def delete_record(self, rid):
        # note unintuitive creation of single item tuple
        # convert to int since value comes from treeview (str)
        self.data_access.execute("""DELETE FROM contacts WHERE contact_id = ?""",
                                 (int(rid),))
        self.conn.commit()

    def cleanup(self):
        ''' call this before the app closes to ensure data integrity
        '''
        if (self.data_access):
            self.conn.commit()
            self.data_access.close()


class ShelveStorage():
    ''' Represents a simple persistence layer provided using the shelve module
    which pickles objects into a dbm
    '''
    FILENAME = "project_data.db"

    def __init__(self):
        ''' initiate access to the data persistence layer
        '''
        # using writeback is slower but avoids some weird caching issues
        self.data_access = shelve.open(self.FILENAME, writeback=True)

    def get_record(self, rid):
        ''' return a single record identified by the record id
        '''
        record_id = "record" + str(rid)
        return self.data_access[record_id]

    def get_all_records(self):
        ''' return all records stored in the database
        '''
        return list(self.data_access.values())

    def save_record(self, record):
        ''' add a record represented by a dict with a new id
        '''
        # if it's still 0 then it's a new record, otherwise it's not
        if record.rid == 0:
            record.rid = self.get_new_id()

        record_key = "record" + str(record.rid)

        # needs to be an string key for the dict
        self.data_access[record_key] = record

    def get_all_sorted_records(self):
        return sorted(self.get_all_records(), key=lambda x: x.rid)

    def delete_record(self, rid):
        del self.data_access["record" + str(rid)]

    def get_new_id(self):
        all_sorted_records = self.get_all_sorted_records()
        if len(all_sorted_records) == 0:
            return 1
        else:
            return int(self.get_all_sorted_records()[-1].rid) + 1
# edge case if all are deleted after creation, what is the safe number?

    def cleanup(self):
        ''' call this before the app closes to ensure data integrity
        '''
        self.data_access.close()


class Contact():
    def __init__(self, name="", email="", rid=0):
        self.rid = rid  # 0 represents a new, unsaved record; will get updated
        self.name = name
        self.email = email

    def __str__(self):
        return f'Contact#: {self.rid}; Name: {self.name}, Email: {self.email}'
