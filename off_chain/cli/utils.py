import re
import click
import getpass
from colorama import Fore, Style, init
from datetime import date
from controllers.action_controller import *
from controllers.controller import Controller
from singleton.action_controller_instance import action_controller_instance as act_controller
from database.database_operation import DatabaseOperations
from session.session import Session


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
        self.today_date = str(date.today())
        

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
        act_controller.update_user(name, lastname, user_role, from_address=public_key)

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
        address = self.controller.get_public_key_by_username(username)
        balance = act_controller.check_balance(address)
        print(f"Your balance is {balance}")
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

        # Emissioni effettive inserite
        while True:
            try:
                co2 = int(input(f"Insert actual CO2 emission for '{operation_desc}' (in tons): "))
                break
            except ValueError:
                print(Fore.RED + "Please enter a valid integer." + Style.RESET_ALL)

        description = f"{operation_desc} ({units} hectares)"
        address = self.controller.get_public_key_by_username(username)
        
        delta = threshold - co2
        if balance - abs(delta) >= 0:
            receipt_so = act_controller.register_operation(address, operation_desc, description, delta, co2)
            if receipt_so.status == 1:
                if delta > 0:
                    action = "added to"
                    print(Fore.GREEN + f'The operation has been correctly recorded. {delta} credits has been {action} your wallet.' + Style.RESET_ALL)
                elif delta < 0: 
                    action = "removed from"
                    print(Fore.GREEN + f'The operation has been correctly recorded. {delta} credits has been {action} your wallet.' + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "The operation has been correctly recorded. No credit variation: emission equals threshold." + Style.RESET_ALL)
                    action = None
            else:
                print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
        else:
            print(Fore.RED + f"WARNING: YOUR BALANCE IS INSUFFICIENT! YOU NEED {balance - abs(delta)} MORE CREDITS" + Style.RESET_ALL)
            action = None

    
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

        # Emissioni effettive inserite
        while True:
            try:
                co2 = int(input(f"Insert actual CO2 emission for '{operation_desc}' (in tons): "))
                break
            except ValueError:
                print(Fore.RED + "Please enter a valid integer." + Style.RESET_ALL)
        
        description = f"{operation_desc} ({units} hectares)"
        
        

        address = self.controller.get_public_key_by_username(username)
        delta = threshold - co2
        if balance - abs(delta) >= 0:
            receipt_so = act_controller.register_operation(address, operation_desc, description, delta, co2)
            if receipt_so.status == 1:
                if delta > 0:
                    action = "added to"
                    print(Fore.GREEN + f'The operation has been correctly recorded. {delta} credits has been {action} your wallet.' + Style.RESET_ALL)
                elif delta < 0: 
                    action = "removed from"
                    print(Fore.GREEN + f'The operation has been correctly recorded. {delta} credits has been {action} your wallet.' + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "The operation has been correctly recorded. No credit variation: emission equals threshold." + Style.RESET_ALL)
                    action = None
            else:
                print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
        else:
            print(Fore.RED + f"WARNING: YOUR BALANCE IS INSUFFICIENT! YOU NEED {balance - abs(delta)} MORE CREDITS" + Style.RESET_ALL)
            action = None

    
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

        threshold = co2_per_unit * units
        while True:
            try:
                co2 = int(input(f"Insert actual CO2 emission for '{operation_desc}' (in tons): "))
                break
            except ValueError:
                print(Fore.RED + "Please enter a valid integer." + Style.RESET_ALL)

        description = f"{operation_desc} ({units} hectares)"
       
        

        address = self.controller.get_public_key_by_username(username)
        delta = threshold - co2
        if balance - abs(delta) >= 0:
            receipt_so = act_controller.register_operation(address, operation_desc, description, delta, co2)
            if receipt_so.status == 1:
                if delta > 0:
                    action = "added to"
                    print(Fore.GREEN + f'The operation has been correctly recorded. {delta} credits has been {action} your wallet.' + Style.RESET_ALL)
                elif delta < 0: 
                    action = "removed from"
                    print(Fore.GREEN + f'The operation has been correctly recorded. {delta} credits has been {action} your wallet.' + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "The operation has been correctly recorded. No credit variation: emission equals threshold." + Style.RESET_ALL)
                    action = None
            else:
                print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
        else:
            print(Fore.RED + f"WARNING: YOUR BALANCE IS INSUFFICIENT! YOU NEED {balance - abs(delta)} MORE CREDITS" + Style.RESET_ALL)
            action = None



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

        while True:
            try:
                units = int(input(f"Enter number of units for '{operation_desc}': "))
                if units > 0:
                    break
                else:
                    print(Fore.RED + "Units must be greater than 0." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)

        
        threshold = co2_per_unit * units
 
        while True:
            try:
                co2 = int(input(f"Insert actual CO2 emission for '{operation_desc}' (in tons): "))
                break
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)

        description = f"{operation_desc} ({units} hectares)"
        
        address = self.controller.get_public_key_by_username(username)
        delta = threshold - co2
        if balance - abs(delta) >= 0:
            receipt_so = act_controller.register_operation(address, operation_desc, description, delta, co2)
            if receipt_so.status == 1:
                if delta > 0:
                    action = "added to"
                    print(Fore.GREEN + f'The operation has been correctly recorded. {delta} credits has been {action} your wallet.' + Style.RESET_ALL)
                elif delta < 0: 
                    action = "removed from"
                    print(Fore.GREEN + f'The operation has been correctly recorded. {delta} credits has been {action} your wallet.' + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "The operation has been correctly recorded. No credit variation: emission equals threshold." + Style.RESET_ALL)
                    action = None
            else:
                print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
        else:
            print(Fore.RED + f"WARNING: YOUR BALANCE IS INSUFFICIENT! YOU NEED {balance - abs(delta)} MORE CREDITS" + Style.RESET_ALL)
            action = None


    def make_green_action(self, username, user_role):
        print(Fore.CYAN + "\nMake a Green Action" + Style.RESET_ALL)

       
        green_action = input("Enter the description of the green action you performed: ").strip()
        if not green_action:
            print(Fore.RED + "Green action description cannot be empty." + Style.RESET_ALL)
            return

      
        while True:
            try:
                co2_saved = int(input("Enter the amount of CO2 saved (in tons): "))
                if co2_saved > 0:
                    break
                else:
                    print(Fore.RED + "CO2 saved must be a positive number." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)
        
        description = f"Green Action: {green_action}"
        address = self.controller.get_public_key_by_username(username)
        receipt_ga = act_controller.register_green_action(address, description, co2_saved)

        if receipt_ga.status == 1:
            print(Fore.GREEN + f"Green action registered. {co2_saved} tons of CO2 saved credited to your wallet." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed to register the green action." + Style.RESET_ALL)



    def give_credit(self, username):
        print(Fore.YELLOW + "Type 'exit' at any prompt to cancel the operation.\n" + Style.RESET_ALL)
        
        credit_input = input("How many credits do you want to give? ")
        if credit_input.lower() == 'exit':
            print(Fore.RED + "Operation cancelled.\n" + Style.RESET_ALL)
            return

        if not credit_input.isdigit():
            print(Fore.RED + "Invalid input. Please enter a numeric value.\n" + Style.RESET_ALL)
            return

        credit = int(credit_input)
        if credit == 0:
            return 
        address = self.controller.get_public_key_by_username(username)
        balance = act_controller.check_balance(address)        
        if balance >= credit:
            while True:
                username_credit = input("Insert the username of the account you want to give credit (type 'exit' to go back):\n").strip()
                if username_credit.lower() == 'exit':
                    print(Fore.RED + "Operation cancelled.\n" + Style.RESET_ALL)
                    return 
                if username_credit != username:
                    if self.controller.check_username(username_credit) == -1:
                        break
                    else:
                        print(Fore.RED + 'The username is not correct or does not exist.\n' + Style.RESET_ALL)
                else:
                    print(Fore.RED + "You can't give credit to yourself!\n" + Style.RESET_ALL)

            proceed = input("Do you want to proceed with the operation? (Y/n): ").strip().upper()
            if proceed == "EXIT":
                print(Fore.RED + "Operation cancelled.\n" + Style.RESET_ALL)
                return
            elif proceed == "Y":
                addres_user = self.controller.get_public_key_by_username(username)
                addres_credit = self.controller.get_public_key_by_username(username_credit)
                print(f"{Fore.YELLOW}You will give credits to the address: {addres_credit}{Style.RESET_ALL}")
                receipt = act_controller.transfer_token(addres_user, addres_credit, credit) 
                if receipt.status == 1:
                    print(Fore.GREEN + f'Your credits have been successfully given to: {username_credit}' + Style.RESET_ALL)
                else:
                    print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
            elif proceed == "N":
                print(Fore.RED + "Operation Cancelled.\n" + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Wrong input, please insert Y or N!\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Action denied: insufficient balance.\n' + Style.RESET_ALL)
    
    def create_report(self, username):
        print(Fore.YELLOW + "Type 'exit' at any time to cancel the operation.\n" + Style.RESET_ALL)

        creation_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        # Inserimento data iniziale
        while True:
            start_date = input("Insert the first day of the operation you want to insert in the report (YYYY-MM-DD): ").strip()
            if start_date.lower() == "exit":
                print(Fore.RED + "Operation cancelled.\n" + Style.RESET_ALL)
                return
            if self.controller.check_birthdate_format(start_date):
                break
            else:
                print(Fore.RED + "\nInvalid date or incorrect format." + Style.RESET_ALL)

        # Inserimento data finale
        while True:
            end_date = input("Insert the date of the last operation you want to put into the report (YYYY-MM-DD): ").strip()
            if end_date.lower() == "exit":
                print(Fore.RED + "Operation cancelled.\n" + Style.RESET_ALL)
                return
            if self.controller.check_birthdate_format(end_date):
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if end_dt >= start_dt:
                    break
                else:
                    print(Fore.RED + "\nEnd date must be the same as or after the start date." + Style.RESET_ALL)
            else:
                print(Fore.RED + "\nInvalid date or incorrect format." + Style.RESET_ALL)

        # Creazione report
        report_code = self.controller.insert_report_info(creation_date, start_date, end_date, username)

        if report_code == 1:
            print(Fore.GREEN + 'Your report is ready' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Operation Failed!' + Style.RESET_ALL)
