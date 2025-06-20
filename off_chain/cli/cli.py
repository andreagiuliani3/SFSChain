import getpass
from ipaddress import ip_address
import re
 
from eth_utils import *
from eth_keys import *
from controllers.controller import Controller
from controllers.action_controller import ActionController
from controllers.deploy_controller import DeployController
from session.session import Session
from database.database_operation import DatabaseOperations
from cli.utils import Utils
from colorama import Fore, Style, init
from datetime import date
import os
import json
from web3 import Web3


class CommandLineInterface:

    def __init__(self, session):

        self.session = session
        self.controller = Controller(session)
        self.act_controller = ActionController()
        self.deploy_controller = DeployController()
        self.ops = DatabaseOperations()
        self.util = Utils(session)
        # Esegui il deploy del contratto se non è stato effettuato precedentemente
        if not self.act_controller.load_contract():
            self.act_controller.deploy_and_initialize('../../on_chain/CarbonCreditRecords.sol')
        

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
        This method prompts users to decide whether to proceed with deployment and 
        initialization of the smart contract. It then collects wallet credentials, 
        personal information, and role selection from the user for registration. 
        The method validates user inputs and interacts with the Controller to perform 
        registration actions.
        """

        print('Please, enter your wallet credentials.')
        attempts = 0
        while True:
            public_key = input('Public Key: ')
            private_key = getpass.getpass('Private Key: ')
            confirm_private_key = getpass.getpass('Confirm Private Key: ')
            
            if private_key == confirm_private_key:
                if self.controller.check_keys(public_key, private_key):
                    print(Fore.RED + 'A wallet with these keys already exists. Please enter a unique set of keys.' + Style.RESET_ALL)
                    attempts += 1
                    if attempts >= 3:
                        print(Fore.RED + "Maximum retry attempts reached. Redeploying..." + Style.RESET_ALL)
                        self.act_controller.deploy_and_initialize('../../on_chain/CarbonCredit.sol')
                        attempts = 0  # Reset attempts after deployment
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
                        print(Fore.RED + 'Oops, there is no wallet with the matching public and private key provided.\n' + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Private key and confirmation do not match. Try again.\n' + Style.RESET_ALL)

        if is_address(public_key) and (public_key == pk):

            print('Enter your personal information.')

            while True:
                username = input('Username: ')
                if self.controller.check_username(username) == 0: break
                else: print(Fore.RED + 'Your username has been taken.\n' + Style.RESET_ALL)

            while True: 
                role = input("Insert your role: \n (F) Farmer \n (P) Producer \n (C) Carrier \n (S) Seller \n Your choice: ").strip().upper()
    
                if role == 'F':
                    user_role = 'FARMER'
                    confirm = input("Do you confirm you're a Farmer? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)

                elif role == 'P':
                    user_role = 'PRODUCER'
                    confirm = input("Do you confirm you're a Producer? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)

                elif role == 'C':
                    user_role = 'CARRIER'
                    confirm = input("Do you confirm you're a Carrier? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)

                elif role == 'S':
                    user_role = 'SELLER'
                    confirm = input("Do you confirm you're a Seller? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)

                else:
                    print(Fore.RED + "You have to select a role between Farmer (F), Producer (P), Carrier (C), or Seller (S). Retry\n" + Style.RESET_ALL)

            while True:
                while True:
                    password = getpass.getpass('Password: ')
                    passwd_regex = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?!.*\s).{8,100}$'
                    if not re.fullmatch(passwd_regex, password):
                        print(Fore.RED + 'Password must contain at least 8 characters, at least one digit, at least one uppercase letter, one lowercase letter, and at least one special character.\n' + Style.RESET_ALL)
                    else: break

                confirm_password = getpass.getpass('Confirm Password: ')
                
                if password != confirm_password:
                    print(Fore.RED + 'Password and confirmation do not match. Try again\n' + Style.RESET_ALL)
                else:
                    break

            reg_code = self.controller.registration(username, password, user_role, public_key, private_key)
            if reg_code == 0:
                self.insert_user_info(username, user_role, private_key)
            elif reg_code == -1:
                print(Fore.RED + 'Your username has been taken.\n' + Style.RESET_ALL)
        
        else:
            print(Fore.RED + 'Sorry, but the provided public and private key do not match to any account\n' + Style.RESET_ALL)
            return
        
    
    def insert_user_info(self, username, user_role, private_key):
        """
        This method guides users through the process of providing personal information.
        It validates user inputs and ensures data integrity before inserting the
        information into the system. Additionally, it registers the user entity
        on the blockchain.
 
        Args:
            username (str): The username of the users.
            role (str): The role of the user.
        """
 
        print("\nProceed with the insertion of a few personal information.")
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
        carbon_credit = 5
        from_address_users = self.controller.get_public_key_by_username(username)
        self.act_controller.add_user(name, lastname, user_role, from_address_users)
        insert_code = self.controller.insert_user_info(username, name, lastname, user_role, birthday, email, phone, company_name, carbon_credit)
        if insert_code == 0:
            print(Fore.GREEN + 'Information saved correctly!' + Style.RESET_ALL)
            self.user_menu(username,user_role)
        elif insert_code == -1:
            print(Fore.RED + 'Internal error!' + Style.RESET_ALL)

    def login_menu(self):
        """
        This method prompts users to provide their credentials (public and private keys,
        username, and password) for authentication. It verifies the credentials with
        the Controller and grants access if authentication is successful. The method
        handles authentication failures, including too many login attempts.
 
        Returns:
            int: An indicator of the login outcome (-1 for authentication failure, -2 for too many login attempts, 0 for successful login).
        """
 
        while True:
            if not self.controller.check_attempts() and self.session.get_timeout_left() < 0:
                self.session.reset_attempts()
 
            if self.session.get_timeout_left() <= 0 and self.controller.check_attempts():
                public_key = input('Insert public key: ')
                private_key = getpass.getpass('Private Key: ')
                username = input('Insert username: ')
                passwd = getpass.getpass('Insert password: ')
 
                login_code, user_role = self.controller.login(username, passwd, public_key, private_key)
 
                if login_code == 0:
                    print(Fore.GREEN + '\nYou have succesfully logged in!\n' + Style.RESET_ALL)
                    self.user_menu(username, user_role)
                elif login_code == -1:
                    print(Fore.RED + '\nThe credentials you entered are wrong\n' + Style.RESET_ALL)
                elif login_code == -2:
                    print(Fore.RED + '\nToo many login attempts\n' + Style.RESET_ALL)
                    return -1
               
            else:
                print(Fore.RED + '\nMax number of attemps reached\n' + Style.RESET_ALL)
                print(Fore.RED + f'You will be in timeout for: {int(self.session.get_timeout_left())} seconds\n' + Style.RESET_ALL)
                return -2
    
    def user_menu(self, username, user_role):
        """
        This method presents users with a menu of options tailored to their role.

        Args:
            username (str): The username of the logged-in user.
        """
        user_options = {
            1: "Profile",
            2: "Operation",
            3: "Report",
            4: "Ask for credit",  # Triggers the sub-menu
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
                break  # Uscita dal submenu

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
            3: "Make Operation"
        }

        while True:
            print(Fore.CYAN + "\nCREDIT MENU (press Enter to go back)" + Style.RESET_ALL)
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
                        self.util.give_credit(username, user_role)
                    elif choice == 3:
                        self.util.make_operation(username, user_role)
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
            1: "View Reports",
            2: "Generate New Report"
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
                        self.view_user_report(username)
                    elif choice == 2:
                        self.util.create_report(username)
                else:
                    print(Fore.RED + "Invalid choice! Please try again." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a valid number." + Style.RESET_ALL)

    def view_userview(self, username):
        """
        This method retrieves and displays the profile information of the user 
        identified by the given username. It presents details such as username, 
        name, lastname, birthday, birth place, residence, autonomous status, 
        and phone number.
        """
        userview = self.controller.get_user_by_username(username)
        print(Fore.CYAN + "\nUser INFO\n" + Style.RESET_ALL)
        print("Username: ", userview.get_username())
        print("Name: ", userview.get_name())
        print("Last Name: ", userview.get_lastname())
        print("Birth Date: ", userview.get_birthday())
        print("Company Name: ", userview.get_company_name())
        print("Role: ", userview.get_user_role())  # Corrected field here
        print("Phone: ", userview.get_phone())
        input("\nPress Enter to exit\n")

    def view_balance(self, username):
        balance = self.controller.get_credit_by_username(username)
        address = self.controller.get_public_key_by_username(username)
        balance2 = self.act_controller.check_balance(address)
        print(Fore.CYAN + "\nBalance:\n" + Style.RESET_ALL)
        print("Your balance is: ", balance)
        print("Your balance is: ", balance2)
        
    def view_user_report(self, username):
        """
        Visualize the user report and allow the user to select a specific report based on the date.

        Args:
            username (str): The username of the logged-in user.
        """
        reportview = self.controller.get_report_by_username(username)
        if not reportview:
            print("No reports found for this user.")
            return  # Uscita immediata se non ci sono report

        available_dates = list({report.get_creation_date() for report in reportview})  # set per eliminare i duplicati, list per ordinabilità
        available_dates.sort()  # opzionale: ordina le date

        print("\nAvailable report:")
        for date in available_dates:
            print("- " + date)

        while True:
            user_input_date = input("Insert the date of the report you want to see (YYYY-MM-DD): ").strip()
            if user_input_date == "":
                print("Returning to previous menu.")
                return

            if not self.controller.check_birthdate_format(user_input_date):
                print(Fore.RED + "\nInvalid date or incorrect format." + Style.RESET_ALL)
                continue

            if user_input_date not in available_dates:
                print(Fore.RED + "\nNo report found for the date entered." + Style.RESET_ALL)
                continue

            print(f"Displaying the report for {user_input_date}...")
            break

        reportdateview = self.controller.get_report_by_date(username, user_input_date)
        if reportdateview:
            for report in reportdateview:
                print("Date: ", report.get_operation_date())
                print("Operation: ", report.get_operations())
        else:
            print("Report not found.")

        input("\nPress Enter to return to the menu...\n")

    def ask_for_credit(self):
        informationview = self.controller.get_information_for_credit()
        print("You can see a list of user with the amount of credit and their email. Try to contact them and ask for credit")
        if informationview:
            for users in informationview:
                print("\nCredit: ", users.get_carbon_credit())
                print("Username: ", users.get_username())
                print("Email: ", users.get_email())