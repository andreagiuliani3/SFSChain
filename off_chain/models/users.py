from colorama import Fore, Style, init
from models.model_base import Model

class User:
    def __init__(self, username, name, lastname, company_name, phone, mail, birthday, carbon_credit, role):

        super().__init__()
        self.username = username
        self.name = name
        self.lastname = lastname
        self.company_name = company_name
        self.phone = phone
        self.mail = mail
        self.birthday = birthday
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

    def save(self):
        """
        Saves a new or updates an existing Medic record in the database.
        Implements SQL queries to insert or update details based on the presence of a username.
        """
        try:
            if self.username is None:
                # Insert new medic record
                self.cur.execute('''INSERT INTO Users (username, name, lastname, birthday, company_name, carbon_credit, role, mail, phone)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (self.username, self.name, self.lastname, self.birthday, self.company_name, self.carbon_credit, self.role, self.mail, self.phone))
            else:
                # Update existing medic details
                self.cur.execute('''UPDATE Users SET name=?, lastname=?, birthday=?, company_name=?, carbon_credit=?, role=?, mail=?, phone=? WHERE username=?''',
                                (self.username, self.name, self.lastname, self.birthday, self.company_name, self.carbon_credit, self.role, self.mail, self.phone))
            self.conn.commit()
            self.username = self.cur.lastrowid
            print(Fore.GREEN + 'Information saved correctly!\n' + Style.RESET_ALL)
        except:
            print(Fore.RED + 'Internal error!' + Style.RESET_ALL)
    
    def delete(self):
        """
        Deletes a user record from the database based on its username.
        """
        if self.username is not None:
            self.cur.execute('DELETE FROM Users WHERE username=?', (self.username))
            self.conn.commit()
 
 


