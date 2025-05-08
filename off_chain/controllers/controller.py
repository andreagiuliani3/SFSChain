import re
from datetime import datetime
from colorama import Fore, Style, init
from database.database_operation import DatabaseOperations
from session.session import Session
from models.credentials import Credentials
 
class Controller:
    """
    Controller handles user and medical data interactions with the database.
    """
    init(convert=True)
 
    def __init__(self, session: Session):
        """
        Initialize the Controller with a session object and set up the database operations.
       
        :param session: The session object to manage user sessions and login attempts.
        """
        self.db_ops = DatabaseOperations()
        self.session = session
        self.__n_attempts_limit = 5 # Maximum number of login attempts before lockout.
        self.__timeout_timer = 180 # Timeout duration in seconds.
 
    def registration(self, username: str, password: str, role: str, public_key: str, private_key: str):
        """
        Registers a new user in the database with the given credentials.
       
        :param username: The user's username.
        :param password: The user's password.
        :param role: The user's role in the system.
        :param public_key: The user's public key.
        :param private_key: The user's private key.
        :return: A registration code indicating success or failure.
        """
        registration_code = self.db_ops.register_creds(username, password, role, public_key, private_key)
 
        return registration_code
   
    def login(self, username: str, password: str, public_key: str, private_key: str):
        """
        Attempts to log a user in by validating credentials and handling session attempts.
       
        :param username: The user's username.
        :param password: The user's password.
        :param public_key: The user's public key.
        :param private_key: The user's private key.
        :return: Tuple containing a status code and the user's role, if successful.
        """
        if(self.check_attempts() and self.db_ops.check_credentials(username, password, public_key, private_key)):
            creds: Credentials = self.db_ops.get_creds_by_username(username)
            user_role = creds.get_role()
            user = self.db_ops.get_user_by_username(username)
            self.session.set_user(user)
            return 0, user_role
        elif self.check_attempts():
            self.session.increment_attempts()
            if self.session.get_attempts() == self.__n_attempts_limit:
                self.session.set_error_attempts_timeout(self.__timeout_timer)
            return -1, None
        else:
            return -2, None
   
    def insert_user_info(self, username: str, name: str, lastname: str, user_role: str, birthday: str, mail: str, phone: str, company_name: str, carbon_credit: int):
        """
        Inserts user information into the database.
 
        :param user_role: The role of the user.
        :param username: The username of the user.
        :param name: The first name of the user.
        :param lastname: The last name of the user.
        :param birthday: The birthday of the user (format YYYY-MM-DD).
        :param mail: Email of the user.
        :param phone: Phone number of the user.
        :param company_name: The company of the user (if it exists).
        :return: An insertion code indicating success (0) or failure.
        """
        insertion_code = self.db_ops.insert_user(username, name, lastname, user_role, birthday, mail, phone, company_name, carbon_credit)
 
        if insertion_code == 0:
            user = self.db_ops.get_user_by_username(username)
            self.session.set_user(user)
            print(Fore.GREEN + 'DONE' + Style.RESET_ALL)
 
        return insertion_code
    
    def insert_operation_info(self, creation_date: str, username: str, user_role: str, operation: str):
        insertion_code = self.db_ops.insert_operation(creation_date, username, user_role, operation)
 
        if insertion_code == 0:
            operation = self.db_ops.get_operation_by_username(operation, creation_date)
            self.session.set_operation(operation)
            print(Fore.GREEN + 'Your operation has been registered' + Style.RESET_ALL)
 
        return insertion_code
    
    def insert_report_info(self, creation_date: str, start_date: str, end_date: str, username: str):
        report_code = self.db_ops.insert_report(creation_date, username, start_date, end_date)

        if report_code == 0:
            report = self.db_ops.get_report_by_username(username)
            self.session.set_report(report)
            print(Fore.GREEN + 'Your report has been created' + Style.RESET_ALL)
        return report_code
    
    def check_null_info(self, info):
        """
        Checks if the provided information is non-null (or truthy).
 
        :param info: The information to be checked. This can be any type, including strings, numbers, or other objects.
        :return: Returns True if the information is non-null/non-empty (truthy), False otherwise (falsy).
        """
        if info:
            return True
        else:
            return False
       
    def check_birthdate_format(self, date_string):
        """
        Validates that a provided date string is in the correct format ('YYYY-MM-DD') and is a date in the past.
 
        :param date_string: The date string to validate, expected to be in the format 'YYYY-MM-DD'.
        :return: Returns True if the date string is correctly formatted and represents a past date;
        returns False if the date is not in the correct format or is in the future.
        """
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
            current_date = datetime.now()
            if date < current_date:
                return True
            else:
                return False
        except ValueError:
            return False
 
    def check_tpdate_format(self, date_string, check_today = 0):
        """
        Validates that a provided date string is in the correct format ('YYYY-MM-DD') and optionally checks if the date is today or in the future.
 
        :param date_string: The date string to validate, which can be a string or a datetime object. If it is a datetime object, it is formatted to a string.
        :param check_today: A flag indicating the type of validation. If set to 0 (default), the function checks if the date is today or in the future.
                            If set to any other value, the function simply checks the format without considering the date's relation to today.
        :return: Returns True if the date string is correctly formatted and, if check_today is 0, represents today's or a future date.
                 Returns False if the date is not in the correct format, is in the past (when check_today is 0), or on any parsing failure.
        """
        try:
            if not isinstance(date_string, str):
                date_string = date_string.strftime('%Y-%m-%d')
            date = datetime.strptime(date_string, '%Y-%m-%d')
            current_date = datetime.now()
            if check_today == 0:
                if date >= current_date:
                    return True
                else:
                    return False
            else: return True
        except ValueError:
            return False
       
    def check_date_order(self, first_date_string, second_date_string):
        """
        Checks if the second date is chronologically after the first date.
 
        :param first_date_string: The first date as a string or a datetime object. If it is a datetime object, it will be formatted to a string.
        :param second_date_string: The second date as a string or a datetime object. If it is a datetime object, it will be formatted to a string.
        :return: Returns True if the second date is later than the first date.
                 Returns False if either date is not in the correct 'YYYY-MM-DD' format or if the second date is not after the first date.
        """
        try:
            if not isinstance(first_date_string, str):
                first_date_string = first_date_string.strftime('%Y-%m-%d')
            if not isinstance(second_date_string, str):
                second_date_string = second_date_string.strftime('%Y-%m-%d')
           
            first_date = datetime.strptime(first_date_string, '%Y-%m-%d')
            second_date = datetime.strptime(second_date_string, '%Y-%m-%d')
           
            return second_date > first_date
        except ValueError:
            return False
       
    def check_phone_number_format(self, phone_number):
        """
        Validates that a given phone number is in a correct numerical format and within the expected length range.
 
        :param phone_number: The phone number string to validate. The number may contain spaces or hyphens.
        :return: Returns True if the phone number contains only digits (after removing spaces and hyphens)
                 and if its length is between 7 and 15 characters. Returns False otherwise.
        """
        if phone_number.replace('-', '').replace(' ', '').isdigit():
            if 7 <= len(phone_number) <= 15:
                return True
        return False
   
    def check_email_format(self, email):
        """
        Validates that a given email address conforms to a standard email format.
 
        :param email: The email string to validate.
        :return: Returns True if the email matches the standard email format pattern.
                 Returns False if the email does not match this pattern.
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return True
        else:
            return False
       
    def possessive_suffix(self, name):
        """
        Determines the appropriate possessive suffix for a given name based on its final character.
 
        :param name: The name string to which the possessive suffix will be applied.
        :return: Returns "'s" if the last character of the name is not 's', otherwise returns "'" to form the possessive correctly.
        """
        if name[-1].lower() != 's':
            return"'s"
        else:
            return "'"
       
    def check_username(self, username):
        return self.db_ops.check_username(username)
   
    def check_keys(self, public_key, private_key):
        return self.db_ops.key_exists(public_key, private_key)
   
    def check_passwd(self, username, password):
        return self.db_ops.check_passwd(username, password)
   
    def check_unique_phone_number(self, phone):
        return self.db_ops.check_unique_phone_number(phone)
   
    def check_unique_email(self, mail):
        return self.db_ops.check_unique_email(mail)
   
    def change_passwd(self, username, old_pass, new_pass):
        """
        Changes a user's password in the database after verifying the old password.
 
        :param username: The username for which to change the password.
        :param old_pass: The current password to verify.
        :param new_pass: The new password to set.
        :return: A response code indicating the result of the operation; -2 if an error occurred.
        """
        if self.db_ops.check_passwd(username, old_pass):
            try:
                response = self.db_ops.change_passwd(username, old_pass, new_pass)
                return response
            except:
                return -2
   
    def get_user_by_username(self, username):
        return self.db_ops.get_user_by_username(username)
   
    def check_attempts(self):
        if self.session.get_attempts() < self.__n_attempts_limit:
            return True
        else:
            return False
    
    def check_balance(self,username):
        if self.db_ops.get_credit_by_username(username) > 0:
            return True
        else:
            return False
        
    def get_creds_by_username(self, username):
        return self.db_ops.get_creds_by_username(username)
    
    def get_public_key_by_username(self, username):
        return self.db_ops.get_public_key_by_username(username)
    
    def get_role_by_username(self, username):
        return self.db_ops.get_role_by_username(username)
    
    def get_credit_by_username(self, username):
        return self.db_ops.get_credit_by_username(username)
   
    def give_credit(self, username):
        return self.db_ops.give_credit(username)
    
    def delete_credit(self,username):
        return self.db_ops.delete_credit(username)
    
    def get_report_by_username(self, username):
        return self.db_ops.get_report_by_username(username)
    
    def get_report_by_date(self, username, creation_date):
        return self.db_ops.get_report_by_date(username, creation_date)