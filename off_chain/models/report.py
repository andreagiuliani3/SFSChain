import datetime
from colorama import Fore, Style, init
from models.model_base import Model

class Report:
    def __init__(self, id_report, creation_date, start_date, end_date, username, user_role, operations):
        super.__init__()
        self.id_report = id_report
        self.creation_date = creation_date
        self.start_date = start_date
        self.end_date = end_date
        self.username = username
        self.user_role = user_role
        self.operations = operations

    def get_id_report(self): return self.id_report

    def get_creation_date(self): return self.creation_date
    
    def get_start_date(self): return self.start_date

    def get_end_date(self): return self.end_date

    def get_username(self): return self.username

    def get_user_role(self): return self.user_role

    def get_operations(self): return self.operations

    def delete(self):
        """
        Deletes a report record from the database based on its id.
        """
        if self.id_report is not None:
            self.cur.execute('DELETE FROM Reports WHERE id_report=?', (self.id_report))
            self.conn.commit()

    def save(self):
        """
        Saves a new or updates an existing Report record in the database.
        Implements SQL queries to insert or update details based on the presence of an id_report.
        """
        today_date = datetime.date.today()
        # Insert new report record, using today's date by default
        self.cur.execute('''INSERT INTO Reports (creation_date, start_date, end_date, username, user_role, operations)
                                VALUES (?, ?, ?, ?, ?, ?)''',
                             (today_date, self.start_date, self.end_date, self.username, self.user_role, self.operations))
        self.conn.commit()