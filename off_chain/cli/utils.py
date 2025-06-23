import datetime
import math
import re
import click
import getpass
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table
from datetime import date
from controllers.action_controller import *

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
        self.contract = self.act_controller.load_contract()

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
            
    """def update_profile(self, username, user_role):
        
        Updates the profile information of a user.

        Parameters:
            username (str): The username of the user whose profile is being updated.
            role (str): The role of the user (e.g., "Patient", "Caregiver", "Medic").

        Returns:
            None
        
     
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
        self.act_controller.update_user(name, lastname, user_role, from_address=public_key)

        us.save()"""
    
    def update_profile(self, username, user_role):
    
        print(Fore.CYAN + "\nUpdate profile function" + Style.RESET_ALL)

        current = self.controller.get_user_by_username(username)

        name = click.prompt('Name ', default=current.get_name())
        lastname = click.prompt('Lastname ', default=current.get_lastname())

        while True:
            birthday = click.prompt('Date of birth (YYYY-MM-DD) ', default=current.get_birthday())
            if self.controller.check_birthdate_format(birthday): 
                break
            print(Fore.RED + "Invalid birthdate or incorrect format." + Style.RESET_ALL)

        while True:
            phone = click.prompt('Phone ', default=current.get_phone())
            if self.controller.check_phone_number_format(phone): 
                break
            print(Fore.RED + "Invalid phone number format." + Style.RESET_ALL)

        # Blockchain update (se necessario)
        public_key = self.controller.get_public_key_by_username(username)
        self.act_controller.update_user(name, lastname, user_role, from_address=public_key)

        # DB update
        result = self.controller.update_user_profile(username, name, lastname, birthday, phone)

        if result == 0:
            print(Fore.GREEN + "Profile updated successfully!" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed to update profile!" + Style.RESET_ALL)

    def make_operation_farmer(self, username, user_role):
        if user_role != "FARMER":
            print(Fore.RED + "Operation not available for your role." + Style.RESET_ALL)
            return

        balance = self.controller.get_credit_by_username(username)
        if balance <= 0:
            print(Fore.RED + 'WARNING: YOUR BALANCE IS ZERO OR BELOW!' + Style.RESET_ALL)

        print(Fore.CYAN + "\nAvailable FARMER Operations:" + Style.RESET_ALL)

        operation_factors = {
            1: ("Soil Preparation", 12),
            2: ("Sowing", 3),
            3: ("Fertilization", 7),
            4: ("Irrigation", 5),
            5: ("Harvesting", 8)
        }

        for key, (desc, factor) in operation_factors.items():
            print(f"{key}. {desc} (reference: {factor} tons CO2 per hectare)")

        # Scelta dell’operazione
        while True:
            try:
                op_choice = int(input("\nSelect the operation (1-5): "))
                if op_choice in operation_factors:
                    break
                else:
                    print(Fore.RED + "Invalid option. Try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a number." + Style.RESET_ALL)

        operation_desc, co2_per_unit = operation_factors[op_choice]

        # Richiesta numero di unità
        while True:
            try:
                units = int(input(f"Enter number of hectares (or units) for '{operation_desc}': "))
                if units > 0:
                    break
                else:
                    print(Fore.RED + "Units must be greater than 0." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)

        # Calcolo soglia dinamica
        threshold = co2_per_unit * units

        # Data operazione
        creation_date = date.today().strftime("%Y-%m-%d")

        # Emissioni effettive inserite
        while True:
            try:
                co2 = int(input(f"Insert actual CO2 emission for '{operation_desc}' (in tons): "))
                break
            except ValueError:
                print(Fore.RED + "Please enter a valid integer." + Style.RESET_ALL)

        description = f"{operation_desc} ({units} hectares)"
        # Inserimento nel sistema
        insert_code = self.controller.insert_operation_info(
            creation_date, username, user_role, description, co2
        )

        

        address = self.controller.get_public_key_by_username(username)
        self.act_controller.register_operation(address, operation_desc, description, co2)
        credit_core = 0
        controller = 0

        if co2 < threshold:
            delta = threshold - co2
            credit_core = self.controller.give_credit(username, delta)
            self.act_controller.add_token(delta, address)
            action = "added to"
        elif co2 > threshold:
            delta = co2 - threshold
            credit_core = self.controller.delete_credit(username, delta)
            self.act_controller.remove_token(delta, address)
            if delta > balance:
                controller = 1
            action = "removed from"
        else:
            print(Fore.YELLOW + "No credit variation: emission equals threshold." + Style.RESET_ALL)
            action = None

        # Output finale
        if insert_code == 0 and (credit_core == 0 or action is None):
            if action:
                print(Fore.GREEN + f'Credit has been {action} your wallet.' + Style.RESET_ALL)
            if controller == 1:
                print(Fore.RED + 'WARNING: YOUR BALANCE IS BELOW ZERO!' + Style.RESET_ALL)
        elif insert_code == -1 or credit_core == -1:
            print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
    
    def make_operation_producer(self, username, user_role):
        if user_role != "PRODUCER":
            print(Fore.RED + "Operation not available for your role." + Style.RESET_ALL)
            return

        balance = self.controller.get_credit_by_username(username)
        if balance <= 0:
            print(Fore.RED + 'WARNING: YOUR BALANCE IS ZERO OR BELOW!' + Style.RESET_ALL)

        print(Fore.CYAN + "\nAvailable PRODUCER Operations:" + Style.RESET_ALL)

        operation_factors = {
            1: ("Raw Material Processing", 15),
            2: ("Product Packaging", 6),
            3: ("Warehouse Storage", 4),
            4: ("Quality Control", 2)
        }

        for key, (desc, factor) in operation_factors.items():
            print(f"{key}. {desc} (reference: {factor} tons CO2 per unit)")

        # Scelta dell’operazione
        while True:
            try:
                op_choice = int(input("\nSelect the operation (1-4): "))
                if op_choice in operation_factors:
                    break
                else:
                    print(Fore.RED + "Invalid option. Try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a number." + Style.RESET_ALL)

        operation_desc, co2_per_unit = operation_factors[op_choice]

        # Richiesta numero di unità
        while True:
            try:
                units = int(input(f"Enter number of units (e.g., lots or batches) for '{operation_desc}': "))
                if units > 0:
                    break
                else:
                    print(Fore.RED + "Units must be greater than 0." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)

        # Calcolo soglia dinamica
        threshold = co2_per_unit * units

        # Data operazione
        creation_date = date.today().strftime("%Y-%m-%d")

        # Emissioni effettive inserite
        while True:
            try:
                co2 = int(input(f"Insert actual CO2 emission for '{operation_desc}' (in tons): "))
                break
            except ValueError:
                print(Fore.RED + "Please enter a valid integer." + Style.RESET_ALL)
        
        description = f"{operation_desc} ({units} hectares)"
        # Inserimento nel sistema
        insert_code = self.controller.insert_operation_info(
            creation_date, username, user_role, description, co2
        )
        

        address = self.controller.get_public_key_by_username(username)
        self.act_controller.register_operation(address, operation_desc, description, co2)
        credit_core = 0
        controller = 0

        if co2 < threshold:
            delta = threshold - co2
            credit_core = self.controller.give_credit(username, delta)
            self.act_controller.add_token(delta, address)
            action = "added to"
        elif co2 > threshold:
            delta = co2 - threshold
            credit_core = self.controller.delete_credit(username, delta)
            self.act_controller.remove_token(delta, address)
            if delta > balance:
                controller = 1
            action = "removed from"
        else:
            print(Fore.YELLOW + "No credit variation: emission equals threshold." + Style.RESET_ALL)
            action = None

        # Output finale
        if insert_code == 0 and (credit_core == 0 or action is None):
            if action:
                print(Fore.GREEN + f'Credit has been {action} your wallet.' + Style.RESET_ALL)
            if controller == 1:
                print(Fore.RED + 'WARNING: YOUR BALANCE IS BELOW ZERO!' + Style.RESET_ALL)
        elif insert_code == -1 or credit_core == -1:
            print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
    
    def make_operation_carrier(self, username, user_role):
        if user_role != "CARRIER":
            print(Fore.RED + "Operation not available for your role." + Style.RESET_ALL)
            return

        balance = self.controller.get_credit_by_username(username)
        if balance <= 0:
            print(Fore.RED + 'WARNING: YOUR BALANCE IS ZERO OR BELOW!' + Style.RESET_ALL)

        print(Fore.CYAN + "\nAvailable CARRIER Operations:" + Style.RESET_ALL)

        operation_factors = {
            1: ("Product Loading", 2),
            2: ("Transport", 10),
            3: ("Product Unloading", 2)
        }

        for key, (desc, factor) in operation_factors.items():
            print(f"{key}. {desc} (reference: {factor} tons CO2 per shipment unit)")

        # Scelta dell’operazione
        while True:
            try:
                op_choice = int(input("\nSelect the operation (1-3): "))
                if op_choice in operation_factors:
                    break
                else:
                    print(Fore.RED + "Invalid option. Try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a number." + Style.RESET_ALL)

        operation_desc, co2_per_unit = operation_factors[op_choice]

        # Richiesta numero di unità
        while True:
            try:
                units = int(input(f"Enter number of units (e.g., shipments or pallets) for '{operation_desc}': "))
                if units > 0:
                    break
                else:
                    print(Fore.RED + "Units must be greater than 0." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)

        # Calcolo soglia dinamica
        threshold = co2_per_unit * units

        # Data operazione
        creation_date = date.today().strftime("%Y-%m-%d")

        # Emissioni effettive inserite
        while True:
            try:
                co2 = int(input(f"Insert actual CO2 emission for '{operation_desc}' (in tons): "))
                break
            except ValueError:
                print(Fore.RED + "Please enter a valid integer." + Style.RESET_ALL)

        description = f"{operation_desc} ({units} hectares)"
        # Inserimento nel sistema
        insert_code = self.controller.insert_operation_info(
            creation_date, username, user_role, description, co2
        )
        

        address = self.controller.get_public_key_by_username(username)
        self.act_controller.register_operation(address, operation_desc, description, co2)
        credit_core = 0
        controller = 0

        if co2 < threshold:
            delta = threshold - co2
            credit_core = self.controller.give_credit(username, delta)
            self.act_controller.add_token(delta, address)
            action = "added to"
        elif co2 > threshold:
            delta = co2 - threshold
            credit_core = self.controller.delete_credit(username, delta)
            self.act_controller.remove_token(delta, address)
            if delta > balance:
                controller = 1
            action = "removed from"
        else:
            print(Fore.YELLOW + "No credit variation: emission equals threshold." + Style.RESET_ALL)
            action = None

        # Output finale
        if insert_code == 0 and (credit_core == 0 or action is None):
            if action:
                print(Fore.GREEN + f'Credit has been {action} your wallet.' + Style.RESET_ALL)
            if controller == 1:
                print(Fore.RED + 'WARNING: YOUR BALANCE IS BELOW ZERO!' + Style.RESET_ALL)
        elif insert_code == -1 or credit_core == -1:
            print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)


    def make_operation_seller(self, username, user_role):
        if user_role != "SELLER":
            print(Fore.RED + "Operation not available for your role." + Style.RESET_ALL)
            return

        balance = self.controller.get_credit_by_username(username)
        if balance <= 0:
            print(Fore.RED + 'WARNING: YOUR BALANCE IS ZERO OR BELOW!' + Style.RESET_ALL)

        print(Fore.CYAN + "\nAvailable SELLER Operations:" + Style.RESET_ALL)

        operation_factors = {
            1: ("Storage (e.g. fridge/freezer)", 5),
            2: ("Sales (energy, POS, etc.)", 0.5),
            3: ("Packaging Disposal", 2)
        }

        for key, (desc, factor) in operation_factors.items():
            print(f"{key}. {desc} (reference: {factor} tons CO2 per unit)")

        # Scelta dell’operazione
        while True:
            try:
                op_choice = int(input("\nSelect the operation (1-3): "))
                if op_choice in operation_factors:
                    break
                else:
                    print(Fore.RED + "Invalid option. Try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a number." + Style.RESET_ALL)

        operation_desc, co2_per_unit = operation_factors[op_choice]

        # Richiesta numero di unità
        while True:
            try:
                units = int(input(f"Enter number of units for '{operation_desc}': "))
                if units > 0:
                    break
                else:
                    print(Fore.RED + "Units must be greater than 0." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)

        # Calcolo soglia dinamica
        threshold = co2_per_unit * units

        # Data operazione
        creation_date = date.today().strftime("%Y-%m-%d")

        # Emissioni effettive inserite
        while True:
            try:
                co2 = int(input(f"Insert actual CO2 emission for '{operation_desc}' (in tons): "))
                break
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)

        description = f"{operation_desc} ({units} hectares)"
        # Inserimento nel sistema
        insert_code = self.controller.insert_operation_info(
            creation_date, username, user_role, description, co2
        )
        

        address = self.controller.get_public_key_by_username(username)
        self.act_controller.register_operation(address, operation_desc, description, co2)
        credit_core = 0
        controller = 0

        if co2 < threshold:
            delta = threshold - co2
            credit_core = self.controller.give_credit(username, delta)
            self.act_controller.add_token(delta, address)
            action = "added to"
        elif co2 > threshold:
            delta = co2 - threshold
            credit_core = self.controller.delete_credit(username, delta)
            self.act_controller.remove_token(delta, address)
            balance = self.controller.get_credit_by_username(username)
            if delta > balance:
                controller = 1
            action = "removed from"
        else:
            print(Fore.YELLOW + "No credit variation: emission equals threshold." + Style.RESET_ALL)
            action = None

        # Output finale
        if insert_code == 0 and (credit_core == 0 or action is None):
            if action:
                print(Fore.GREEN + f'Credit has been {action} your wallet.' + Style.RESET_ALL)
            if controller == 1:
                print(Fore.RED + 'WARNING: YOUR BALANCE IS BELOW ZERO!' + Style.RESET_ALL)
        elif insert_code == -1 or credit_core == -1:
            print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)

    def make_green_action(self, username, user_role):
        print(Fore.CYAN + "\nMake a Green Action" + Style.RESET_ALL)

        # Descrizione azione green
        green_action = input("Enter the description of the green action you performed: ").strip()
        if not green_action:
            print(Fore.RED + "Green action description cannot be empty." + Style.RESET_ALL)
            return

        # CO2 risparmiata (tonnellate)
        while True:
            try:
                co2_saved = int(input("Enter the amount of CO2 saved (in tons): "))
                if co2_saved > 0:
                    break
                else:
                    print(Fore.RED + "CO2 saved must be a positive number." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)

        # Data azione
        creation_date = date.today().strftime("%Y-%m-%d")
        
        description = f"Green Action: {green_action}"

        # Inserimento azione green come operazione con emissioni negative (risparmio)
        insert_code = self.controller.insert_operation_info(
            creation_date, username, user_role, description, -co2_saved
        )
        

        address = self.controller.get_public_key_by_username(username)
        self.act_controller.register_green_action(address, description, co2_saved)

        # Aggiunta crediti corrispondenti al risparmio
        credit_core = self.controller.give_credit(username, co2_saved)
        self.act_controller.add_token(co2_saved, address)

        if insert_code == 0 and credit_core == 0:
            print(Fore.GREEN + f"Green action registered. {co2_saved} tons of CO2 saved credited to your wallet." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed to register the green action." + Style.RESET_ALL)



    def give_credit(self, username, user_role):
        credit = int(input("How many credit you want to give? "))
        balance = self.controller.get_credit_by_username(username)
        if balance>credit:
            while True:
                username_credit = str(input("Insert the username of the account you want to give credit:\n"))
                if username != username_credit:
                    if self.controller.check_username(username_credit) == -1: break
                    else: print(Fore.RED + 'The username is not correct/not exist.\n' + Style.RESET_ALL)
                else: print("You can't give a credit to yourself!")
            proceed = input("Do you want to proceed with the operation? (Y/n): ")
            if proceed.strip().upper() == "Y":
                creation_date = date.today()
                operation = " Credit give to: "+username_credit
                credit_code = self.controller.give_credit(username_credit, credit)
                credit_user_code = self.controller.delete_credit(username, credit)
                operation_code = self.controller.insert_operation_info(creation_date, username, user_role, operation, co2 = 0)
                addres_user = self.controller.get_public_key_by_username(username)
                addres_credit = self.controller.get_public_key_by_username(username_credit)
                print("1: "+addres_user)
                print("2: "+addres_credit)
                self.act_controller.transfer_token(addres_user, addres_credit, credit) 
                if operation_code == 0 and credit_code == 0 and credit_user_code == 0:
                    print(Fore.GREEN + 'Your credit is succesfully give to: ', username_credit + Style.RESET_ALL)
                elif operation_code == 0 or credit_code == -1 or credit_user_code == -1:
                    print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
            elif proceed.strip().upper() == "N":
                    print(Fore.RED + "Operation Cancelled." + Style.RESET_ALL)
            else:
                    print(Fore.RED + 'Wrong input, please insert Y or N!' + Style.RESET_ALL)
        else:
            print("\nYou can't give you don't have enough balance!")
    
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