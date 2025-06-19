from colorama import Fore, Style, init
from models.model_base import Model

class User:
    def __init__(self, username, name, lastname, user_role, birthday, email, phone, company_name, carbon_credit):

        super().__init__()
        self.username = username
        self.name = name
        self.lastname = lastname
        self.company_name = company_name
        self.phone = phone
        self.email = email
        self.birthday = birthday
        self.carbon_credit = carbon_credit
        self.user_role = user_role

    def get_username(self): return self.username
    
    def get_name(self): return self.name

    def get_lastname(self): return self.lastname

    def get_company_name(self): return self.company_name

    def get_phone(self): return self.phone

    def get_email(self): return self.email

    def get_birthday(self): return self.birthday

    def get_user_role(self): return self.user_role

    def get_carbon_credit(self): return self.carbon_credit


    def set_username(self, username): self.username = username
    
    def set_name(self, name): self.name = name

    def set_lastname(self, lastname): self.last_name = lastname

    def set_company_name(self, company_name): self.company_name = company_name

    def set_phone(self, phone): self.phone = phone

    def set_email(self, email): self.email = email

    def set_birthday(self, birthday): self.birthday = birthday

    def set_user_role(self, user_role): self.user_role = user_role

    def set_carbon_credit(self, carbon_credit): self.carbon_credit = carbon_credit

    def save(self):
        """
        Saves a new or updates an existing Medic record in the database.
        Implements SQL queries to insert or update details based on the presence of a username.
        """
        try:
            if self.username is None:
                # Insert new Users record
                self.cur.execute("""
                            INSERT INTO Users
                            (username, name, lastname, user_role, birthday, email, phone, company_name, carbon_credit)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) """,
                            (
                                self.username, self.name, self.lastname, self.user_role, self.birthday, self.email, self.phone, self.company_name, self.carbon_credit
                            ))
            else:
                # Update existing Users details
                self.cur.execute("""UPDATE Users SET name=?, lastname=?, birthday=?, phone=? WHERE username=?""",
                                (self.name, self.lastname, self.birthday, self.phone, self.username))
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
 
 


