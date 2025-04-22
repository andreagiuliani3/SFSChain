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

        """
        def save(self):
        """
