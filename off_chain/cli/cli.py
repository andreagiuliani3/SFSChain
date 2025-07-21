import getpass
import re
from session.session import Session
from eth_utils import *
from eth_keys import *
from controllers.controller import Controller
from singleton.action_controller_instance import action_controller_instance as act_controller
from controllers.deploy_controller import DeployController
from database.database_operation import DatabaseOperations
from cli.utils import Utils
from colorama import init, Fore, Style
init(strip=False, convert=False)
from tabulate import tabulate


class CommandLineInterface:
    """
    This class implements the command line interface for the Carbon Credit Management System.
    It provides methods for user registration, login, and various functionalities based on user roles.
    It allows users to register a new account, log in, view and update their profile, check their balance,
    perform operations, generate reports, and ask for carbon credits from other users.
    It also handles user input validation and provides a menu-driven interface for easy navigation.
    """

    def __init__(self, session: Session):

        self.session = session
        self.controller = Controller(session)
        self.deploy_controller = DeployController()
        self.ops = DatabaseOperations()
        self.util = Utils(session)

        
        self.menu = {
            1: 'Register New Account',
            2: 'Log In',
            3: 'Exit',
        }

    PAGE_SIZE = 3 
    current_page = 0

    def print_menu(self):
        """
        This method prints the main menu options available to the user and prompts for 
        their choice. It then directs the user to the corresponding functionality based 
        on their selection. The method handles user input validation to ensure a valid 
        choice is made.
        """

        print(Fore.CYAN + r""" 
    ____  _____ ____   ____ _   _    _    ___ _   _ 
   / ___||  ___/ ___| / ___| | | |  / \  |_ _| \ | |
   \___ \| |_  \___ \| |   | |_| | / _ \  | ||  \| |
    ___) |  _|  ___) | |___|  _  |/ ___ \ | || |\  |
   |____/|_|   |____/ \____|_| |_/_/   \_\___|_| \_|
              
        
            """ + Style.RESET_ALL)
        
        for key in self.menu.keys():
            print(key, '--' ,self.menu[key])

        try:
            choice = int(input('Enter your choice: '))

            if choice == 1:
                    print('Proceed with the registration...')
                    self.registration_menu()
            elif choice == 2:
                    print('Proceed with the log in...')
                    res_code = self.login_menu()
                    if res_code == 0:
                        self.print_menu()
                    elif res_code == -3:
                        print(Fore.CYAN + "Login cancelled. Returning to previous menu..." + Style.RESET_ALL)
            elif choice == 3:
                    print('Bye Bye!')
                    exit()
            else:
                    print(Fore.RED + 'Wrong option. Please enter one of the options listed in the menu!' + Style.RESET_ALL)

        except ValueError:
            print(Fore.RED + 'Wrong input. Please enter a number!\n'+ Style.RESET_ALL)
            return
    
    
    def registration_menu(self):
        """
        Prompts user for wallet credentials, personal info, and role selection for registration.
        Allows exiting at any input step by typing 'exit'.
        """

        print(Fore.YELLOW + "Type 'exit' at any prompt to cancel and go back.\n" + Style.RESET_ALL)
        print('Please, enter your wallet credentials.')
        attempts = 0

        while True:
            public_key = input('Public Key: ')
            if public_key.lower() == 'exit': return -1

            private_key = getpass.getpass('Private Key: ')
            if private_key.lower() == 'exit': return -1

            confirm_private_key = getpass.getpass('Confirm Private Key: ')
            if confirm_private_key.lower() == 'exit': return -1

            if private_key == confirm_private_key:
                if self.controller.check_keys(public_key, private_key):
                    print(Fore.RED + 'A wallet with these keys already exists. Please enter a unique set of keys.' + Style.RESET_ALL)
                else:
                    try:
                        pk_bytes = decode_hex(private_key)
                        priv_key = keys.PrivateKey(pk_bytes)
                        pk = priv_key.public_key.to_checksum_address()
                        if pk.lower() != public_key.lower():
                            print(Fore.RED + 'The provided keys do not match. Please check your entries.' + Style.RESET_ALL)
                        else:
                            break
                    except Exception:
                        print(Fore.RED + 'Invalid private key format.\n' + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Private key and confirmation do not match. Try again.\n' + Style.RESET_ALL)

        if is_address(public_key) and (public_key == pk):
            print('Enter your personal information.')

            while True:
                username = input('Username: ')
                if username.lower() == 'exit': return -1

                if self.controller.check_username(username) == 0:
                    break
                else:
                    print(Fore.RED + 'Your username has been taken.\n' + Style.RESET_ALL)

            while True:
                role = input("Insert your role: \n (F) Farmer \n (P) Producer \n (C) Carrier \n (S) Seller \n Your choice: ").strip().upper()
                if role.lower() == 'exit': return -1

                roles = {'F': 'FARMER', 'P': 'PRODUCER', 'C': 'CARRIER', 'S': 'SELLER'}
                if role in roles:
                    user_role = roles[role]
                    confirm = input(f"Do you confirm you're a {user_role.title()}? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    elif confirm.lower() == 'exit':
                        return -1
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "You must select a valid role. Retry\n" + Style.RESET_ALL)

            while True:
                while True:
                    password = getpass.getpass('Password: ')
                    if password.lower() == 'exit': return -1

                    passwd_regex = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?!.*\s).{8,100}$'
                    if not re.fullmatch(passwd_regex, password):
                        print(Fore.RED + 'Password must be at least 8 characters long and include digits, upper and lower case letters, and a special character.\n' + Style.RESET_ALL)
                    else:
                        break

                confirm_password = getpass.getpass('Confirm Password: ')
                if confirm_password.lower() == 'exit': return -1

                if password != confirm_password:
                    print(Fore.RED + 'Password and confirmation do not match. Try again\n' + Style.RESET_ALL)
                else:
                    break

            while True:
                name = input('Name: ')
                if self.controller.check_null_info(name): break
                else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
            while True:
                lastname = input('Lastname: ')
                if self.controller.check_null_info(lastname): break
                else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
            while True:
                birthday = input('Date of birth (YYYY-MM-DD): ')
                if self.controller.check_birthdate_format(birthday): break
                else: print(Fore.RED + "\nInvalid birthdate or incorrect format." + Style.RESET_ALL)
            while True:
                email = input('E-mail: ')
                if self.controller.check_null_info(email):
                    if self.controller.check_unique_email(email) == 0: break
                    else: print(Fore.RED + "This e-mail has already been inserted. \n" + Style.RESET_ALL)
                else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
            company_name = input('Company name: ')
            while True:
                phone = input('Phone number: ')
                if self.controller.check_phone_number_format(phone):
                    if self.controller.check_unique_phone_number(phone) == 0: break
                    else: print(Fore.RED + "This phone number has already been inserted. \n" + Style.RESET_ALL)
                else: print(Fore.RED + "Invalid phone number format.\n" + Style.RESET_ALL)
            act_controller.add_user(name, lastname, user_role, public_key)
            registration_code = self.controller.registration(username, name, lastname, user_role, birthday, email, phone, company_name, password, public_key, private_key)
            if registration_code == 0:
                print(Fore.GREEN + 'Information saved correctly!' + Style.RESET_ALL)
                self.user_menu(username,user_role)
            elif registration_code == -1:
                print(Fore.RED + 'Internal error!' + Style.RESET_ALL)
            elif registration_code == -2:
                    print(Fore.RED + 'Your username has been taken.\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Sorry, but the provided public and private key do not match.\n' + Style.RESET_ALL)
            return -1

        
    def login_menu(self):
        """
        Prompts user credentials for authentication.
        Allows exiting at any input step by typing 'exit'.

        Returns:
            int: -1 = auth failure, -2 = timeout, -3 = user exited, 0 = success
        """
        print(Fore.YELLOW + "Type 'exit' at any prompt to cancel and go back.\n" + Style.RESET_ALL)

        while True:
           
            if not self.controller.check_attempts() and self.session.get_timeout_left() <= 0:
                self.session.reset_attempts()
                

            if self.session.get_timeout_left() <= 0 and self.controller.check_attempts():

                public_key = input('Insert public key: ')
                if public_key.lower() == 'exit': return -3

                private_key = getpass.getpass('Private Key: ')
                if private_key.lower() == 'exit': return -3

                username = input('Insert username: ')
                if username.lower() == 'exit': return -3

                passwd = getpass.getpass('Insert password: ')
                if passwd.lower() == 'exit': return -3

                login_code, user_role = self.controller.login(username, passwd, public_key, private_key)

                if login_code == 0:
                    print(Fore.GREEN + '\nYou have successfully logged in!\n' + Style.RESET_ALL)
                    self.user_menu(username, user_role)
                elif login_code == -1:
                    print(Fore.RED + '\nThe credentials you entered are wrong\n' + Style.RESET_ALL)
                elif login_code == -2:
                    print(Fore.RED + '\nToo many login attempts\n' + Style.RESET_ALL)
                    return -1
            else:
                print(Fore.RED + '\nMax number of attempts reached\n' + Style.RESET_ALL)
                print(Fore.RED + f'You will be in timeout for: {int(self.session.get_timeout_left())} seconds\n' + Style.RESET_ALL)
                return -2

    
    def user_menu(self, username, user_role):
        """
        This method presents users with a menu of options tailored to their role.

        """
        user_options = {
            1: "Profile",
            2: "Operation",
            3: "Report",
            4: "Ask for credit", 
            5: "Log out"
        }

        while True:
            print(Fore.CYAN + "\nMENU" + Style.RESET_ALL)
            for key, value in user_options.items():
                print(f"{key} -- {value}")

            try:
                choice = int(input("Choose an option: "))
                if choice in user_options:
                    if choice == 1:
                        self.profile_submenu(username, user_role)
                    elif choice == 2:
                        self.credit_submenu(username, user_role)
                    elif choice == 3:
                        self.report_submenu(username)
                    elif choice == 4:
                        self.ask_for_credit()
                    elif choice == 5:
                        confirm = input("\nDo you really want to leave? (Y/n): ").strip().upper()
                        if confirm == 'Y':
                            print(Fore.CYAN + "\nThank you for using the service!\n" + Style.RESET_ALL)
                            self.session.reset_session()
                            self.print_menu()
                            return
                        else:
                            print(Fore.RED + "Invalid choice! Please try again." + Style.RESET_ALL)

            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a valid number." + Style.RESET_ALL)


    def profile_submenu(self, username, user_role):
        """
        This method presents a sub-menu for profile-related actions.
        Press Enter without typing anything to go back.
        """
        report_options = {
            1: "View Profile",
            2: "Update Profile",
            3: "Change Password"
        }

        while True:
            print(Fore.CYAN + "\nPROFILE MENU (press Enter to go back)" + Style.RESET_ALL)
            for key, value in report_options.items():
                print(f"{key} -- {value}")

            choice = input("Choose an option: ").strip()
            if choice == "":
                break  

            try:
                choice = int(choice)
                if choice in report_options:
                    if choice == 1:
                        self.view_userview(username)
                    elif choice == 2:
                        self.util.update_profile(username, user_role)
                    elif choice == 3:
                        self.util.change_passwd(username)
                else:
                    print(Fore.RED + "Invalid choice! Please try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a valid number." + Style.RESET_ALL)


    def credit_submenu(self, username, user_role):
        """
        This method presents a sub-menu for credit-related actions.
        Press Enter without typing anything to go back.
        """
        report_options = {
            1: "Check Balance",
            2: "Give Credit",
            3: "Make Operation",
            4: "Make Green Action"
        }

        while True:
            print(Fore.CYAN + "\nOPERATION MENU (press Enter to go back)" + Style.RESET_ALL)
            for key, value in report_options.items():
                print(f"{key} -- {value}")

            choice = input("Choose an option: ").strip()
            if choice == "":
                break

            try:
                choice = int(choice)
                if choice in report_options:
                    if choice == 1:
                        self.view_balance(username)
                    elif choice == 2:
                        self.util.give_credit(username)
                    elif choice == 3:
                        if user_role == 'FARMER':
                            self.util.make_operation_farmer(username, user_role)   
                        elif user_role == 'PRODUCER':
                            self.util.make_operation_producer(username, user_role)
                        elif user_role == 'CARRIER':
                            self.util.make_operation_carrier(username, user_role)
                        elif user_role == 'SELLER':
                            self.util.make_operation_seller(username, user_role)
                    elif choice == 4:
                        self.util.make_green_action(username)
                else:
                    print(Fore.RED + "Invalid choice! Please try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a valid number." + Style.RESET_ALL)


    def report_submenu(self, username):
        """
        This method presents a sub-menu for report-related actions.
        Press Enter without typing anything to go back.
        """
        report_options = {
            1: "Generate New Report",
            2: "View Report"
        }

        while True:
            print(Fore.CYAN + "\nREPORT MENU (press Enter to go back)" + Style.RESET_ALL)
            for key, value in report_options.items():
                print(f"{key} -- {value}")

            choice = input("Choose an option: ").strip()
            if choice == "":
                break

            try:
                choice = int(choice)
                if choice in report_options:
                    if choice == 1:                        
                        self.util.create_report(username)
                    elif choice == 2:
                        self.view_user_report(username)
                else:
                    print(Fore.RED + "Invalid choice! Please try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a valid number." + Style.RESET_ALL)


    def view_userview(self, username):
        """
        This method retrieves and displays the profile information of the user 
        identified by the given username. It presents details such as username, 
        name, lastname, birthday, company name, role and phone number.
        """
        userview = self.controller.get_user_by_username(username)
        print(Fore.CYAN + "\nUser INFO\n" + Style.RESET_ALL)
        print("Username: ", userview.get_username())
        print("Name: ", userview.get_name())
        print("Last Name: ", userview.get_lastname())
        print("Birth Date: ", userview.get_birthday())
        print("Company Name: ", userview.get_company_name())
        print("Role: ", userview.get_user_role())  
        print("Phone: ", userview.get_phone())
        input("\nPress Enter to exit\n")


    def view_balance(self, username):
        """
        This method retrieves and displays the balance of the user identified by the given username.
        It fetches the user's public key and checks the balance using the action controller.
        """
        address = self.controller.get_public_key_by_username(username)
        balance = act_controller.check_balance(address)
        print(Fore.CYAN + "\nBalance:\n" + Style.RESET_ALL)
        if balance == 1:
            print(f"Your balance is: {balance} credit")
        else:
            print(f"Your balance is: {balance} credits")

        
    def view_user_report(self, username):
        """
        Visualize the user report and allow the user to select a specific report by number.
        """
        reportview = self.controller.get_report_by_username(username)
        if not reportview:
            print("No reports found for this user.")
            return

        available_dates = sorted({report.get_creation_date() for report in reportview})

        print("\nAvailable reports (sorted by creation date and time):")
        for idx, date in enumerate(available_dates, start=1):
            print(f"{idx}. {date}")

        while True:
            user_input = input("Enter the number of the report you want to see (or press Enter to go back): ").strip()
            if user_input == "":
                print("Returning to previous menu.")
                return

            if not user_input.isdigit():
                print(Fore.RED + "\nPlease enter a valid number." + Style.RESET_ALL)
                continue

            selection = int(user_input)
            if 1 <= selection <= len(available_dates):
                selected_date = available_dates[selection - 1]
                print(f"\nDisplaying the report for {selected_date}...\n")
                break
            else:
                print(Fore.RED + "\nInvalid selection. Please choose a number from the list." + Style.RESET_ALL)

        reportdateview = self.controller.get_report_by_date(username, selected_date)
        if reportdateview:
            if len(reportdateview) > 1:
                print("There is more than one report for this date:\n")

            table_data = []
            for report in reportdateview:
                operations_raw = report.get_operations()
                operations = operations_raw.split(" | ") if isinstance(operations_raw, str) else [str(operations_raw)]

                for i, op in enumerate(operations):
                    row = [
                        report.get_operation_date() if i == 0 else "",
                        op.strip(),
                        report.get_co2() if i == 0 else ""
                    ]
                    table_data.append(row)

            headers = ["Date", "Operation", "Total CO₂ Emissions"]
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

        else:
            print("Report not found.")

        input("\nPress Enter to return to the menu...\n")

    def ask_for_credit(self):
        """
        This method retrieves and displays a list of users who have carbon credits available.
        """
        informationview = self.controller.get_information_for_credit()
        print("You can see a list of user and their email. Try to contact them and ask for credit")
        if informationview:
            for users in informationview:
                print("Username: ", users.get_username())
                print("Email: ", users.get_email())