import datetime
import math
import re
import click
import getpass
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table
from datetime import date

from controllers.controller import Controller
from controllers.action_controller import ActionController
from database.database_operation import DatabaseOperations
from session.session import Session
from session.logging import log_error



class Utils:
    """
    This class provides various utility methods for handling user input, updating profiles, changing passwords, 
    displaying data, and navigating through pages of the user.

    Attributes:
        PAGE_SIZE (int): The number of items to display per page.
        current_page (int): The index of the current page being displayed.

    """

    init(convert=True)

    PAGE_SIZE = 3
    current_page = 0
    
    def __init__(self, session: Session):

        """
        Initializes the Utils class with a session object.

        Parameters:
            session (Session): The session object containing user information.

        Attributes:
            session (Session): The session object containing user information.
            controller (Controller): An instance of the Controller class for database interaction.
            act_controller (ActionController): An instance of the ActionController class for managing actions.
            today_date (str): The current date in string format.
        """

        self.session = session
        self.controller = Controller(session)
        self.database_operation = DatabaseOperations()
        self.act_controller = ActionController()
        self.today_date = str(datetime.date.today())

    def change_passwd(self, username):
        """
        Allows the user to change their password.

        Args:
            username (str): The username of the user whose password is being changed.

        Returns:
            None
        """

        while True:
            confirmation = input("Do you want to change your password (Y/n): ").strip().upper()
            if confirmation == 'Y':
                while True:
                    old_pass = input('Old Password: ')
                    if not self.controller.check_passwd(username, old_pass):
                        print(Fore.RED + '\nYou entered the wrong old password.\n' + Style.RESET_ALL)
                        break
                    else:
                        while True:
                            new_passwd = getpass.getpass('New password: ')
                            new_confirm_password = getpass.getpass('Confirm new password: ')

                            passwd_regex = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?!.*\s).{8,100}$'
                            if not re.fullmatch(passwd_regex, new_passwd):
                                print(Fore.RED + 'Password must contain at least 8 characters, at least one digit, at least one uppercase letter, one lowercase letter, and at least one special character.\n' + Style.RESET_ALL)    
                            elif new_passwd != new_confirm_password:
                                print(Fore.RED + 'Password and confirmation do not match. Try again\n' + Style.RESET_ALL)
                            else:
                                response = self.controller.change_passwd(username, old_pass, new_passwd)
                                if response == 0:
                                    print(Fore.GREEN + '\nPassword changed correctly!\n' + Style.RESET_ALL)
                                elif response == -1 or response == -2:
                                    print(Fore.RED + '\nSorry, something went wrong!\n' + Style.RESET_ALL)
                                break
                        break
            else:
                print("Okay\n")
            break
            
    def update_profile(self, username, user_role):
        """
        Updates the profile information of a user.

        Parameters:
            username (str): The username of the user whose profile is being updated.
            role (str): The role of the user (e.g., "Patient", "Caregiver", "Medic").

        Returns:
            None
        """
     
        print(Fore.CYAN + "\nUpdate profile function"  + Style.RESET_ALL)
        us = self.controller.get_user_by_username(username)
        us.set_name(click.prompt('Name ', default=us.get_name()))
        us.set_lastname(click.prompt('Lastname ', default=us.get_lastname()))
        while True:
                birthday = click.prompt('Date of birth (YYYY-MM-DD) ', default=us.get_birthday())
                if self.controller.check_birthdate_format(birthday): 
                    us.set_birthday(birthday)
                    break
                else: print(Fore.RED + "Invalid birthdate or incorrect format." + Style.RESET_ALL)
        while True:
                phone = click.prompt('Phone ', default=us.get_phone())
                if self.controller.check_phone_number_format(phone): 
                    us.set_phone(phone)
                    break
                else: print(Fore.RED + "Invalid phone number format."  + Style.RESET_ALL)
        name = us.get_name()
        lastname = us.get_lastname()
        public_key = self.controller.get_public_key_by_username(username)
        self.act_controller.update_entity(user_role, name, lastname, from_address=public_key)

        us.save()

    def make_operation(self, username, user_role):
        operation_code = self.controller.check_balance(username)
        if operation_code:
            print(Fore.CYAN + "\nMake an Operation"  + Style.RESET_ALL)
            while True:
                from datetime import date
                creation_date = date.today().strftime("%Y-%m-%d")
                if self.controller.check_birthdate_format(creation_date): break
                else: print(Fore.RED + "\nInvalid birthdate or incorrect format." + Style.RESET_ALL)
            operation = str(input("Insert the descripion of the Operation: "))
            credit_core = self.controller.delete_credit(username)
            insert_code = self.controller.insert_operation_info(creation_date, username, user_role, operation)
            try:
                from_address_user = self.controller.get_public_key_by_username(username)
                self.act_controller.manage_operation('add', creation_date, operation, from_address=from_address_user)
            except Exception as e:
                log_error(e)  
            if insert_code == 0 and credit_core == 0:
                print(Fore.GREEN + 'Information saved correctly!' + Style.RESET_ALL)
            elif insert_code == -1 or credit_core == -1:
                print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
        else:
            print("\nYou haven't enough carbon credit!")

    def give_credit(self, username, user_role):
        operation_code = self.controller.check_balance(username)
        if operation_code:
            while True:
                username_credit = str(input("Insert the username of the account you want to give 1 credit:\n"))
                if username != username_credit:
                    if self.controller.check_username(username_credit) == -1: break
                    else: print(Fore.RED + 'The username is not correct/not exist.\n' + Style.RESET_ALL)
                else: print("You can't give a credit to yourself!")
            proceed = input("Do you want to proceed with the operation? (Y/n): ")
            if proceed.strip().upper() == "Y":
                creation_date = date.today()
                operation = "Credit give to: "+username_credit
                credit_code = self.controller.give_credit(username)
                credit_user_code = self.controller.delete_credit(username)
                operation_code = self.controller.insert_operation_info(creation_date, username, user_role, operation) 
                try:
                    from_address_user = self.controller.get_public_key_by_username(username)
                    self.act_controller.manage_operation('add', creation_date, operation, from_address=from_address_user)
                except Exception as e:
                    log_error(e)           
                if operation_code == 0 and credit_code == 0 and credit_user_code == 0:
                    print(Fore.GREEN + 'Your credit is succesfully give to: ', username_credit + Style.RESET_ALL)
                elif operation_code == -1 or credit_code == -1 or credit_user_code == -1:
                    print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
            elif proceed.strip().upper() == "N":
                    print(Fore.RED + "Operation Cancelled." + Style.RESET_ALL)
            else:
                    print(Fore.RED + 'Wrong input, please insert Y or N!' + Style.RESET_ALL)
        else:
            print("\nYou can't give a carbon credit, your balance is 0!")
    
    def create_report(self, username):
        creation_date = date.today()
        while True:
            start_date = input("Insert the first day of the operation you want to insert in the report (YYYY-MM-DD): ")
            if self.controller.check_birthdate_format(start_date): break
            else: print(Fore.RED + "\nInvalid date or incorrect format." + Style.RESET_ALL)
        while True:
            end_date = input("Insert the date of the last operation you want to put into the report (YYYY-MM-DD): ")
            if self.controller.check_birthdate_format(end_date): break
            else: print(Fore.RED + "\nInvalid date or incorrect format." + Style.RESET_ALL)
        report_code = self.controller.insert_report_info(creation_date, start_date, end_date, username)

        if report_code == 0:
            print(Fore.GREEN + 'Your report is ready' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)