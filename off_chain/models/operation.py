from models.model_base import Model

class Operation(Model):
    def __init__(self, id_operation, creation_date, username, role, operations, co2):
        super().__init__()
        self.id_operation = id_operation
        self.creation_date = creation_date
        self.username = username
        self.role = role
        self.operations = operations
        self.co2 = co2

    def get_id_operation(self): return self.id_operation
    def get_creation_date(self): return self.creation_date
    def get_username(self): return self.username
    def get_role(self): return self.role
    def get_operations(self): return self.operations
    def get_co2(self): return self.co2

    def save(self, cur, conn):
        """
        Inserts or updates an Operation in the database.
        Requires an open cursor and connection.
        """
        if self.id_operation is None:
            # Insert new operation
            cur.execute('''
                INSERT INTO Operations (creation_date, username, role, operation, co2)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.creation_date, self.username, self.role, self.operations, self.co2))
            self.id_operation = cur.lastrowid
        else:
            # Update existing operation
            cur.execute('''
                UPDATE Operations 
                SET creation_date=?, username=?, role=?, operation=?, co2=?
                WHERE id=?
            ''', (self.creation_date, self.username, self.role, self.operations, self.co2, self.id_operation))
        conn.commit()

    def delete(self, cur, conn):
        """
        Deletes an Operation from the database.
        """
        if self.id_operation is not None:
            cur.execute('DELETE FROM Operations WHERE id=?', (self.id_operation,))
            conn.commit()
