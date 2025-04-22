class Report:
    def __init__(self, id_report, creation_date, username, user_role, operations):
        super.__init__()
        self.id_report = id_report
        self.creation_date = creation_date
        self.username = username
        self.user_role = user_role
        self.operations = operations

        def get_id_report(self): return self.id_report

        def get_creation_date(self): return self.creation_date

        def get_username(self): return self.username

        def get_user_role(self): return self.user_role

        def get_operations(self): return self.operations

        """
        def save(self): 
        """