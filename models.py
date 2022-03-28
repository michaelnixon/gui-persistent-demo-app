import shelve


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
        # no error handling, should return None if not found?
        return self.data_access[rid]

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

    def cleanup(self):
        ''' call this before the app closes to ensure data integrity 
        '''
        self.data_access.close()


class Contact():
    def __init__(self, name="", email=""):
        self.rid = 0  # 0 represents a new, unsaved record; will get updated
        self.name = name
        self.email = email

    def __str__(self):
        return f'Contact#: {self.rid}; Name: {self.name}, Email: {self.email}'
