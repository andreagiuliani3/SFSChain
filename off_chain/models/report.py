import datetime
from models.model_base import Model

class Report(Model):
    def __init__(self, id_report, creation_date, operation_date, username, user_role, operations):
        super().__init__()
        self.id_report = id_report
        self.creation_date = creation_date
        self.operation_date = operation_date
        self.username = username
        self.user_role = user_role
        self.operations = operations

    def get_id_report(self): return self.id_report
    def get_creation_date(self): return self.creation_date
    def get_operation_date(self): return self.operation_date
    def get_username(self): return self.username
    def get_user_role(self): return self.user_role
    def get_operations(self): return self.operations

    def delete(self):
        """
        Deletes a report record from the database based on its id.
        """
        if self.id_report is not None:
            self.cur.execute('DELETE FROM Reports WHERE id_report=?', (self.id_report,))
            self.conn.commit()

    def save(self):
        """
        Saves a new or updates an existing Report record in the database.
        If id_report is None, inserts a new record. Otherwise, updates the existing one.
        """
        if self.id_report is None:
            today_date = datetime.date.today()
            self.cur.execute('''INSERT INTO Reports (creation_date, operation_date, username, user_role, operations)
                                VALUES (?, ?, ?, ?, ?)''',
                             (today_date, self.operation_date, self.username, self.user_role, self.operations))
            self.conn.commit()
            self.id_report = self.cur.lastrowid
        else:
            self.cur.execute('''UPDATE Reports 
                                SET creation_date=?, operation_date=?, username=?, user_role=?, operations=?
                                WHERE id_report=?''',
                             (self.creation_date, self.operation_date,
                              self.username, self.user_role, self.operations, self.id_report))
            self.conn.commit()
