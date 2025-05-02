"""This module provides various utility functions for handling user input, updating profiles, changing passwords, 
displaying data, managing reports and treatment plans, and navigating through pages of patient records, reports, 
and treatment plans. It also includes functions for adding new reports and treatment plans.
"""

import datetime
import math
import re
import click
import getpass
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table

from controllers.controller import Controller
from controllers.action_controller import ActionController
from database.database_operation import DatabaseOperations
from session.session import Session
from session.logging import log_error



class Utils:
    """
    This class provides various utility methods for handling user input, updating profiles, changing passwords, 
    displaying data, managing reports and treatment plans, and navigating through pages of patient records, reports, 
    and treatment plans. It also includes methods for adding new reports and treatment plans.

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
        print(Fore.CYAN + "\nMake an Operation"  + Style.RESET_ALL)
        while True:
            creation_date = input('Insert today date (YYYY-MM-DD): ')
            if self.controller.check_birthdate_format(creation_date): break
            else: print(Fore.RED + "\nInvalid birthdate or incorrect format." + Style.RESET_ALL)
        operation = str(input("Insert the descripion of the Operation: "))
        insert_code = self.controller.insert_operation_info(creation_date, username, user_role, operation)
        if insert_code == 0:
            print(Fore.GREEN + 'Information saved correctly!' + Style.RESET_ALL)
            self.user_menu(username,user_role)
        elif insert_code == -1:
            print(Fore.RED + 'Internal error!' + Style.RESET_ALL)