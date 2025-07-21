import re
from datetime import datetime
from colorama import init, Fore, Style
init(strip=False, convert=False)
from database.database_operation import DatabaseOperations
from session.session import Session
from models.credentials import Credentials
 
class Controller:
    """
    Controller class to manage user authentication, registration, and session handling.
    """
    
 
    def __init__(self, session: Session):
        """
        Initialize the Controller with a session object and set up the database operations.
       
        :param session: The session object to manage user sessions and login attempts.
        """
        self.db_ops = DatabaseOperations()
        self.session = session
        self.__n_attempts_limit = 5 # Maximum number of login attempts before lockout.
        self.__timeout_timer = 180 # Timeout duration in seconds.
 
       
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
        
   
    def registration(self, username: str, name: str, lastname: str, user_role: str, birthday: str, 
                     mail: str, phone: str, company_name: str, password: str, public_key: str, private_key: str):
        """
        Inserts user information into the database.
 
        :param username: The user's username.
        :param name: The user's first name. 
        :param lastname: The user's last name.
        :param user_role: The user's role (e.g., admin, user).
        :param birthday: The user's birthday in 'YYYY-MM-DD' format.
        :param mail: The user's email address.
        :param phone: The user's phone number.
        :param company_name: The user's company name.
        :param password: The user's password.
        :param public_key: The user's public key.
        :param private_key: The user's private key.
        :return: A registration code indicating the result of the operation.
        """
        
        registration_code = self.db_ops.register_user(username, name, lastname, user_role, birthday, mail, 
                                                    phone, company_name, password, public_key, private_key)
 
        if registration_code == 0:
            user = self.db_ops.get_user_by_username(username)
            self.session.set_user(user)
 
        return registration_code
    
    
    def insert_report_info(self, creation_date: str, start_date: str, end_date: str, username: str):
        """
        Inserts report information into the database and updates the session with the report details.
        """

        report_code = self.db_ops.insert_report(creation_date, username, start_date, end_date)
       
        if report_code == 1:
            report = self.db_ops.get_report_by_username(username)
            self.session.set_report(report)
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

    def check_username(self, username):
        """
        Checks if a username already exists in the database.
        """
        return self.db_ops.check_username(username)
   
    def check_keys(self, public_key, private_key):
        """
        Checks if the provided public and private keys exist in the database.
        """
        return self.db_ops.key_exists(public_key, private_key)
   
    def check_passwd(self, username, password):
        """
        Checks if the provided username and password match the credentials stored in the database.
        """
        return self.db_ops.check_passwd(username, password)
   
    def check_unique_phone_number(self, phone):
        """
        Checks if a phone number is unique in the database.
        """
        return self.db_ops.check_unique_phone_number(phone)
   
    def check_unique_email(self, mail):
        """
        Checks if an email address is unique in the database.
        """
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
        """
        Retrieves user information from the database based on the provided username.
        """
        return self.db_ops.get_user_by_username(username)
   
    def check_attempts(self):
        """
        Checks if the number of login attempts is below the limit set for the session.
        """
        if self.session.get_attempts() < self.__n_attempts_limit:
            return True
        else:
            return False
        
    def get_creds_by_username(self, username):
        """
        Retrieves credentials for a user based on their username.
        """
        return self.db_ops.get_creds_by_username(username)
    
    def get_public_key_by_username(self, username):
        """
        Retrieves the public key associated with a given username.
        """
        return self.db_ops.get_public_key_by_username(username)
    
    def get_role_by_username(self, username):
        """
        Retrieves the role of a user based on their username.
        """
        return self.db_ops.get_role_by_username(username)
   
    def get_report_by_username(self, username):
        """
        Retrieves the report associated with a given username.
        """
        return self.db_ops.get_report_by_username(username)
    
    def get_report_by_date(self, username, creation_date):
        """
        Retrieves a report for a user based on the creation date of the report.
        """
        return self.db_ops.get_report_by_date(username, creation_date)
    
    def get_information_for_credit(self):
        """
        Retrieves information necessary for calculating carbon credits.
        """
        return self.db_ops.get_information_for_credit()
    
    def update_user_profile(self, username, name, lastname, birthday, phone):
        """
        Updates the user's profile information in the database.
        """
        return self.db_ops.update_user_profile(username, name, lastname, birthday, phone)