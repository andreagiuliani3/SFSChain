class Actor:
    def __init__(self, username, name, last_name, company_name, phone, email, birth_date, carbon_credit, role):

        super().__init__()
        self.username = username
        self.name = name
        self.last_name = last_name
        self.company_name = company_name
        self.phone = phone
        self.email = email
        self.birth_date = birth_date
        self.carbon_credit = carbon_credit
        self.role = role

        def get_username(self): return self.username

        def get_name(self): return self.name

        def get_last_name(self): return self.last_name

        def get_company_name(self): return self.company_name

        def get_phone(self): return self.phone

        def get_email(self): return self.email

        def get_birth_date(self): return self.birth_date

        def get_role(self): return self.role


        def set_username(self, username): self.username = username

        def set_name(self, name): self.name = name

        def set_last_name(self, last_name): self.last_name = last_name

        def set_company_name(self, company_name): self.company_name = company_name

        def set_phone(self, phone): self.phone = phone

        def set_email(self, email): self.email = email

        def set_birth_date(self, birth_date): self.birth_date = birth_date

        def set_role(self, role): self.role = role


