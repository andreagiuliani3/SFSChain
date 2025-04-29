from colorama import Fore, Style, init
from models.model_base import Model

class Operation:
    def __init__(self, id_operation, creation_date, username, role, operation):

        super.__init__()
        self.id_operation = id_operation
        self.creation_date = creation_date
        self.username = username
        self.role = role
        self.operation = operation

        def get_id_operation(self): return self.id_operation

        def get_creation_date(self): return self.creation_date

        def get_username(self): return self.username

        def get_role(self): return self.role

        def get_operation(self): return self.operation

    def save(self):
        """
        Saves a new or updates an existing Credentials record in the database.
        Implements SQL queries to insert or update credentials based on the presence of an ID.
        """
        if self.id is None:
            # Insert new credentials record
            self.cur.execute('''INSERT INTO Credentials (username, hash_password, role, public_key, private_key)
                                VALUES (?, ?, ?, ?)''', (self.creation_date, self.username, self.role, self.operation))
                                #I punti interrogativi come placeholder servono per la prevenzione di attacchi SQL Injection
        else:
            # Update existing credentials record
            self.cur.execute('''UPDATE Operation SET creation_date=?, username=?, role=?, operation=? WHERE id=?''',
                             (self.creation_date, self.username, self.role, self.operation))
        self.conn.commit()
        self.id = self.cur.lastrowid # Update the ID with the last row inserted ID if new record
 
    def delete(self):
        """
        Deletes a Credentials record from the database based on its ID.
        """
        if self.id is not None:
            self.cur.execute('DELETE FROM Credentials WHERE id=?', (self.id,))
            self.conn.commit()
