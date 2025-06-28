"""
This module handles all database operations for various user roles and their associated data within the system.
It manages the creation, update, and retrieval of user data through a series of defined methods.
"""

import datetime
import sqlite3
import os
import hashlib
import base64
from cryptography.fernet import Fernet
from colorama import Fore, Style, init
from config import config
from models.users import User
from models.credentials import Credentials
from models.report import Report
from collections import defaultdict
import datetime
from singleton.action_controller_instance import action_controller_instance as act_controller 
from types import SimpleNamespace


class DatabaseOperations:
    """
    Handles all interactions with the database for user data manipulation and retrieval.
    This class manages the connection to the database and executes SQL queries to manage the data.
    """
    init(convert=True)

    def __init__(self):
        """
        Initializes the database connection and cursor, and creates new tables if they do not exist.
        """
        self.conn = sqlite3.connect(config.config["db_path"])
        self.cur = self.conn.cursor()
        self._create_new_table()
        self.n_param = 2
        self.r_param = 8
        self.p_param = 1
        self.dklen_param = 64
        self.today_date = datetime.date.today().strftime('%Y-%m-%d')

    def _create_new_table(self):
        """
        Creates necessary tables in the database if they are not already present.
        This ensures that the database schema is prepared before any operations are performed.
        """
        self.cur.execute('''CREATE TABLE IF NOT EXISTS Credentials(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    hash_password TEXT NOT NULL,
                    role TEXT CHECK(role IN ('FARMER', 'CARRIER', 'PRODUCER', 'SELLER')) NOT NULL,
                    public_key TEXT NOT NULL,
                    private_key TEXT NOT NULL
                    );''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS Users(
                    username TEXT NOT NULL,
                    name TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    birthday DATE NOT NULL,
                    user_role TEXT CHECK(user_role IN ('FARMER', 'CARRIER', 'PRODUCER', 'SELLER')) NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    company_name TEXT,
                    FOREIGN KEY(username) REFERENCES Credentials(username)
                    );''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS Reports(
                    id_report INTEGER PRIMARY KEY AUTOINCREMENT,
                    creation_date TEXT NOT NULL,
                    operation_date DATE NOT NULL,
                    username TEXT NOT NULL,
                    role TEXT CHECK(role IN ('FARMER', 'CARRIER', 'PRODUCER', 'SELLER')) NOT NULL,
                    operations TEXT NOT NULL,
                    co2 INTEGER NOT NULL
                    );''')
        self.conn.commit()
    
    
    def register_user(self, username, name, lastname, user_role, birthday, email, phone, company_name, hash_password, public_key, private_key):
        """
        Registers a new user into the Users and Credentials table in the database.
        
        Args:
            username : The unique username for the user.
            name : The first name of the user.
            lastname : The last name of the user.
            user_role : The role of the user (e.g., 'FARMER', 'CARRIER', 'PRODUCER', 'SELLER').
            birthday : The birth date of the user in YYYY-MM-DD format.
            email : The email address of the user.
            hash_password : The password of the user, which will be hashed before storage.
            public_key : The public key of the user, used for encryption and identification.
            private_key : The private key of the user, which will be encrypted before storage.
            company_name : The name of the company associated with the user, if applicable.
            phone : The phone number of the user.

        Returns:
            int: 0 if the insertion was successful, -1 if an integrity error occurred (e.g., duplicate username).
        """
        try:
            if self.check_username(username) != 0:
                return -2  
            obfuscated_private_k = self.encrypt_private_k(private_key, hash_password)
            hashed_passwd = self.hash_function(hash_password)
            self.conn.execute("BEGIN")

            self.cur.execute("""
                            INSERT INTO Credentials
                            (username, hash_password, role, public_key, private_key) VALUES (?, ?, ?, ?, ?)""",
                            (
                                username,
                                hashed_passwd,
                                user_role,
                                public_key,
                                obfuscated_private_k
                            ))

            self.cur.execute("""
                            INSERT INTO Users
                            (username, name, lastname, user_role, birthday, email, phone, company_name)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?) """,
                            (
                                username, name, lastname, user_role, birthday, email, phone, company_name
                            ))
            
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError as e:
            print(f"Integrity error: {e}")
            self.conn.rollback()
            return -1
    
    def update_user_profile(self, username, name, lastname, birthday, phone):
        """
        Updates an existing user's profile information in the Users table.

        Args:
            username : Username of the user.
            name : First name of the user.
            lastname : Last name of the user.
            birthday : Birthday of the user.
            phone : Phone number of the user.

        Returns:
            int: 0 if the update was successful, -1 if an internal error occurred during the update process.
        """
        try:
            self.cur.execute("""
                UPDATE Users
                SET name = ?, lastname = ?, birthday = ?, phone = ?
                WHERE username = ?
            """, (name, lastname, birthday, phone, username))
            
            self.conn.commit()
            return 0
        except Exception as e:
            print(Fore.RED + f'Internal error while updating profile: {str(e)}' + Style.RESET_ALL)
            return -1

    def check_username(self, username):
        """
        Check if a username exists in the Credentials table.

        Args:
            username (str): Username to check in the database.
        Returns:
            int: 0 if username does not exist, -1 if it does.
        """
        self.cur.execute("SELECT COUNT(*) FROM Credentials WHERE username = ?", (username,))
        if self.cur.fetchone()[0] == 0: return 0
        else: return -1

    def check_unique_phone_number(self, phone):
        """
        Checks if a phone number is unique in the Users table.

        Args:
            phone (str): The phone number to check for uniqueness.

        Returns:
            int: 0 if the phone number is not found (unique), -1 if it is found (not unique).
        """
        query = "SELECT COUNT(*) FROM Users WHERE phone = ?"
        self.cur.execute(query, (phone,))
        count = self.cur.fetchone()[0]
        return 0 if count == 0 else -1
        
    def encrypt_private_k(self, private_key, passwd):
        """
        Encrypts a private key using a password.

        Args:
            private_key (str): The private key to encrypt.
            passwd (str): The password to use for encryption.

        Returns:
            bytes: The encrypted private key.
        """

        passwd_hash = hashlib.sha256(passwd.encode('utf-8')).digest()
        key = base64.urlsafe_b64encode(passwd_hash)
        cipher_suite = Fernet(key)
        ciphertext = cipher_suite.encrypt(private_key.encode('utf-8'))
        return ciphertext
        
    def decrypt_private_k(self, encrypted_private_k, passwd):
        """
        Decrypts an encrypted private key using a password.

        Args:
            encrypted_private_k (bytes): The encrypted private key.
            passwd (str): The password used for encryption.

        Returns:
            str: The decrypted private key.
        """

        passwd_hash = hashlib.sha256(passwd.encode('utf-8')).digest()
        key = base64.urlsafe_b64encode(passwd_hash)
        cipher_suite = Fernet(key)
        plaintext = cipher_suite.decrypt(encrypted_private_k.decode('utf-8'))
        return plaintext.decode('utf-8')
    
    def check_unique_email(self, email):
        """
        Checks if an email address is unique within the Users table in the database.

        Args:
            mail (str): The email address to check for uniqueness.

        Returns:
            int: 0 if the email address is not found in the Users records (unique), -1 if it is found (not unique).
        """
        query_users = "SELECT COUNT(*) FROM Users WHERE email = ?"
        self.cur.execute(query_users, (email,))
        count_users = self.cur.fetchone()[0]

        if count_users == 0:
            return 0 
        else:
            return -1

    def key_exists(self, public_key, private_key):
        """
        Checks if either a public key or a private key already exists in the Credentials table.

        Args:
            public_key (str): The public key to check against existing entries in the database.
            private_key (str): The private key to check against existing entries in the database.

        Returns:
            bool: True if either the public or private key is found in the database (indicating they are not unique),
                  False if neither key is found (indicating they are unique) or an exception occurs during the query.
        """
        try:
            query = "SELECT public_key, private_key FROM Credentials WHERE public_key=? OR private_key=?"
            existing_users = self.cur.execute(query, (public_key, private_key)).fetchall()
            return len(existing_users) > 0
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
            return False 
        
    def get_information_for_credit(self):
        
        information_data = self.cur.execute("""
            SELECT username, name, lastname, user_role, birthday, email, phone, company_name
            FROM Users
        """).fetchall()  

        if information_data:
            return [User(*row) for row in information_data]

        return None

    def get_creds_by_username(self, username):
        """
        Retrieves a user's credentials from the Credentials table based on their username.

        Args:
            username (str): The username of the user whose credentials are to be retrieved.

        Returns:
            Credentials: A Credentials object containing the user's credentials if found.
            None: If no credentials are found for the given username.
        """
        creds = self.cur.execute("""
                                SELECT *
                                FROM Credentials
                                WHERE username=?""", (username,)).fetchone()
        if creds is not None:
            return Credentials(*creds)
        return None

    def get_user_by_username(self, username):
        """
        Retrieves a user's detailed information from the Users table based on their username.

        Args:
            username (str): The username of the user whose detailed information is being requested.

        Returns:
            User|None: A User object containing the user's details if the user exists, otherwise None.
        """
        user_data = self.cur.execute("""
                                    SELECT username, name, lastname, user_role, birthday, email, phone, company_name
                                    FROM Users
                                    WHERE username = ?
                                    """, (username,)).fetchone()

        if user_data:
           return User(*user_data)  
        
        return None  
    
     
    def get_all_actions_grouped_by_date(self, username, start_date, end_date):
        """
        Retrieves all actions performed by a user within a specified date range, grouped by date.
        
        Args:
            username (str): The username of the user whose actions are to be retrieved.
            start_date (str): The start date of the range in YYYY-MM-DD format.
            end_date (str): The end date of the range in YYYY-MM-DD format.
        """ 
        
        user_address = self.get_public_key_by_username(username)
        raw_ops = act_controller.contract.functions.getOperations(user_address).call()
        raw_green = act_controller.contract.functions.getGreenActions(user_address).call()

        grouped = defaultdict(list)

        for op in raw_ops:
            action_type, description, timestamp, co2 = op
            ts = datetime.datetime.fromtimestamp(timestamp)
            date_str = ts.strftime("%Y-%m-%d")

            if start_date <= date_str <= end_date:
                grouped[date_str].append({
                    "description": f"[{action_type}] {description}",
                    "co2": co2  
                })

        for gop in raw_green:
            description, timestamp, co2 = gop
            ts = datetime.datetime.fromtimestamp(timestamp)
            date_str = ts.strftime("%Y-%m-%d")

            if start_date <= date_str <= end_date:
                grouped[date_str].append({
                    "description": f"[GREEN] {description}",
                    "co2": -co2  
                })

        results = []
        for date_str, ops in grouped.items():
            combined_desc = " | ".join(op["description"] for op in ops)
            total_co2 = sum(op["co2"] for op in ops)

            results.append(SimpleNamespace(
                creation_date=date_str,
                username=username,
                role=self.get_role_by_username(username),  
                operations=combined_desc,
                co2=total_co2
            ))

        return results
    
        
    def insert_report(self, creation_date, username, start_date, end_date):
        """
        Inserts a report into the Reports table based on the operations performed by a user within a specified date range.
        
        Args:
            creation_date (str): The date when the report is created, in YYYY-MM-DD format.
            username (str): The username of the user for whom the report is generated.
            start_date (str): The start date of the range in YYYY-MM-DD format.
            end_date (str): The end date of the range in YYYY-MM-DD format.
        
        Returns:
            int: 1 if the report was successfully inserted, -1 if an error occurred during the insertion.
        """

        try:
            operations = self.get_all_actions_grouped_by_date(username, start_date, end_date)

            if not operations:
                print(Fore.RED + f"No operations found for user {username} between {start_date} and {end_date}." + Style.RESET_ALL)
                return 0

            for op in operations:
                self.cur.execute("""
                    INSERT INTO Reports (creation_date, operation_date, username, role, operations, co2)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (creation_date, op.creation_date, op.username, op.role, op.operations, op.co2))
            
            self.conn.commit()
            return 1

        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            print("Integrity error while insert_report_info:", e)
            return -1

        except Exception as e:
            self.conn.rollback()
            print("Integrity error while insert_report_info:", e)
            return -1

        
    def get_report_by_username(self, username):
        """
        Retrieves all reports associated with a specific username from the Reports table.
        
        Args:
            username (str): The username of the user whose reports are to be retrieved.
        
        Returns:
            list|None: A list of Report objects if reports are found for the specified user, 
                       or None if no reports are found.
        """
        report_data = self.cur.execute("""
                                SELECT id_report, creation_date, operation_date, username, role, operations, co2
                                FROM Reports
                                WHERE username = ?
                                """, (username,)).fetchall()  

        if report_data:
           return [Report(*row) for row in report_data]

        return None
    
    def get_report_by_date(self, username, creation_date):
        """
        Retrieves reports for a specific user on a specific creation date from the Reports table.
        
        Args:
            username (str): The username of the user whose reports are to be retrieved.
            creation_date (str): The creation date of the report in YYYY-MM-DD format.
        
        Returns:
            list|None: A list of Report objects if reports are found for the specified user and date, 
                       or None if no reports are found.
        """
        report_data = self.cur.execute("""
                                SELECT id_report, creation_date, operation_date, username, role, operations, co2
                                FROM Reports
                                WHERE username = ? AND creation_date = ?
                                """, (username, creation_date)).fetchall()  

        if report_data:
           return [Report(*row) for row in report_data]

        return None


    def get_role_by_username(self, username):
        """
        Retrieves the role of a user from the database based on their username.
        
        Args:
            username (str): The username of the user whose role is to be determined.
        
        Returns:
            str|None: The role of the user as a string if found (e.g., 'FARMER', 'CARRIER', 'PRODUCER', 'SELLER'), 
                    or None if the username does not correspond to any known user in the system.
        """
        role = self.cur.execute("""
                                SELECT role
                                FROM Credentials
                                WHERE username = ?
                                """, (username,)).fetchone()
        if role:
            return role[0]  
        return None
            
    def get_public_key_by_username(self, username):
        """
        Retrieve the public key for a given username from the Credentials table.
        
        Args:
            username (str): The username of the user whose public key is to be retrieved.
        
        Returns:
            str: The public key of the user if found, None otherwise.
        """
        try:
            self.cur.execute("SELECT public_key FROM Credentials WHERE username = ?", (username,))
            result = self.cur.fetchone()
            if result:
                return result[0]  
            else:
                return None  
        except Exception as e:
            print(Fore.RED + f"An error occurred while retrieving public key: {e}" + Style.RESET_ALL)
            return None

    def hash_function(self, password: str):
        """
        Hashes the supplied password using the scrypt algorithm.
    
        Args:
            password: The password to hash.
            n: CPU/Memory cost factor.
            r: Block size.
            p: Parallelization factor.
            dklen: Length of the derived key.
    
        Returns:
            A string containing the hashed password and the parameters used for hashing.
        """

        salt = os.urandom(16)
        digest = hashlib.scrypt(
            password.encode(), 
            salt = salt,
            n = self.n_param,
            r = self.r_param,
            p = self.p_param,
            dklen = self.dklen_param
        )
        hashed_passwd = f"{digest.hex()}${salt.hex()}${self.n_param}${self.r_param}${self.p_param}${self.dklen_param}"
        return hashed_passwd
 
    def check_credentials(self, username, password, public_key, private_key):
        """
        Verifies a user's login credentials against the stored values in the database.

        Args:
            username (str): The username of the user whose credentials are being verified.
            password (str): The password provided by the user for verification.
            public_key (str): The public key provided by the user for verification.
            private_key (str): The private key provided by the user for verification.

        Returns:
            bool: True if all provided credentials match the stored values, False otherwise.
        """
        creds = self.get_creds_by_username(username)
        if(creds is not None and self.check_passwd(username, password) and creds.get_public_key() == public_key and private_key == self.decrypt_private_k(creds.get_private_key(), password)):
            return True
        else:
            return False
    
    def check_passwd(self, username, password):
        """
        Verifies a user's password by comparing it against the hashed password stored in the database.

        Args:
            username (str): The username of the user whose password is being verified.
            password (str): The plaintext password provided by the user for verification.

        Returns:
            bool: True if the provided password matches the stored hash, False otherwise.

        Note:
            This method assumes that the hashed password and the salt are stored in a specific format in the database,
            delimited by '$'. It extracts the salt and hash parameters from this format to perform the hashing operation.
        """
        result = self.cur.execute("""
                                SELECT hash_password
                                FROM Credentials
                                WHERE username =?""", (username,))
        hash = result.fetchone()
        if hash:
            saved_hash = hash[0]
            params = saved_hash.split('$')
            hashed_passwd = hashlib.scrypt(
                password.encode('utf-8'),
                salt=bytes.fromhex(params[1]),
                n = int(params[2]),
                r = int(params[3]),
                p = int(params[4]),
                dklen= int(params[5])
            )
        return hashed_passwd.hex() == params[0]
    
    def change_passwd(self, username, old_pass, new_pass):
        """
        Changes a user's password in the Credentials table after verifying the old password.

        Args:
            username (str): The username of the user whose password is being changed.
            old_pass (str): The current password of the user to verify its correctness before changing.
            new_pass (str): The new password to set for the user.

        Returns:
            int: 0 if the password change was successful, -1 if the user's credentials could not be found or the old
             password was incorrect.
        """
        creds = self.get_creds_by_username(username)
        if creds is not None:
            new_hash = self.hash_function(new_pass)
            private_key = self.decrypt_private_k(creds.get_private_key(), old_pass)
            new_encrypted_priv_k = self.encrypt_private_k(private_key, new_pass)
            try:
                self.cur.execute("""
                                UPDATE Credentials
                                SET hash_password = ?, private_key = ?
                                WHERE username = ?""", (new_hash, new_encrypted_priv_k, username))
                self.conn.commit()
                return 0
            except Exception as ex:
                raise ex
        else:
            return -1