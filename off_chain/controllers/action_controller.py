import os
import time
import json
from colorama import Fore, Style, init
from controllers.deploy_controller import DeployController
from session.logging import log_msg, log_error
from web3 import Web3
import traceback

class ActionController:
    """
    ActionController interacts with the Ethereum blockchain through methods defined in the contract.
    Connection with provider is established thanks to DeployController and Web3.
    """

    init(convert=True)

    def __init__(self, http_provider='http://127.0.0.1:7545'):
        """
        Initialize the ActionController to interact with an Ethereum blockchain.

        Args:
            http_provider (str): The HTTP URL to connect to an Ethereum node.
        """
        #http://ganache:7545
        #http://127.0.0.1:7545
        self.http_provider = http_provider
        self.w3 = Web3(Web3.HTTPProvider(self.http_provider))
        assert self.w3.is_connected(), Fore.RED + "Failed to connect to Ethereum node." + Style.RESET_ALL
        self.load_contract()

    def load_contract(self):
        """
        Load the contract using the ABI and address from specified files.
        Logs error if files are missing or contents are invalid.
        """
        try:
            with open('on_chain/contract_address.txt', 'r') as file:
                contract_address = file.read().strip()
            with open('on_chain/contract_abi.json', 'r') as file:
                contract_abi = json.load(file)
            if contract_address and contract_abi:
                self.contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)
                log_msg(f"Contract loaded with address: {contract_address}")
            else:
                log_error("Contract address or ABI not found. Please deploy the contract.")
        except FileNotFoundError:
            log_error("Contract files not found. Deploy contract first.")
            print(Fore.RED + "Contract files not found. Deploy contract first." + Style.RESET_ALL)
            self.contract = None

    def deploy_and_initialize(self, contract_source_path='CarbonCreditRecords.sol'):
        """
        Deploys and initializes a smart contract.

        Args:
            contract_source_path (str): Relative path to the Solidity contract source file.
        """
        try:
            controller = DeployController(self.http_provider)
            contract_source_path = os.path.join(os.path.dirname(__file__), contract_source_path)
            controller.compile_and_deploy(contract_source_path)
            self.contract = controller.contract
            with open('on_chain/contract_address.txt', 'w') as file:
                file.write(self.contract.address)
            with open('on_chain/contract_abi.json', 'w') as file:
                json.dump(self.contract.abi, file)
            log_msg(f"Contract deployed at {self.contract.address} and initialized.")
        except Exception as e:
            log_error(str(e))
            traceback.print_exc()
            print(Fore.RED + "An error occurred during deployment." + Style.RESET_ALL)
        
    def read_data(self, function_name, *args):
        """
        Reads data from a contract's function.

        Args:
            function_name (str): The name of the function to call.
            *args: Arguments required by the contract function.

        Returns:
            The result returned by the contract function.
        """
        try:
            result = self.contract.functions[function_name](*args).call()
            log_msg(f"Data read from {function_name}: {result}")
            return result
        except Exception as e:
            log_error(f"Failed to read data from {function_name}: {str(e)}")
            raise e

    def write_data(self, function_name, from_address, *args, gas=2000000, gas_price=None, nonce=None):
        """
        Writes data to a contract's function.

        Args:
            function_name (str): The function name to call on the contract.
            from_address (str): The Ethereum address to send the transaction from.
            *args: Arguments required by the function.
            gas (int): The gas limit for the transaction.
            gas_price (int): The gas price for the transaction.
            nonce (int): The nonce for the transaction.

        Returns:
            The transaction receipt object.
        """
        if not from_address:
            raise ValueError("Invalid 'from_address' provided. It must be a non-empty string representing an Ethereum address.")
        
        # Print to debug the from_address
        print(f"[DEBUG] from_address: {from_address}")
        
        # Get the current balance of the address to check if there are enough funds
        balance = self.w3.eth.get_balance(from_address)
        print(f"[DEBUG] Balance of {from_address}: {self.w3.from_wei(balance, 'ether')} ETH")
        
        # Set default gas price if not provided
        gas_price = gas_price or self.w3.eth.gas_price

        # Ensure nonce is set properly
        nonce = nonce or self.w3.eth.get_transaction_count(from_address)

        tx_parameters = {
            'from': from_address,
            'gas': gas,
            'gasPrice': gas_price,
            'nonce': nonce
        }

        # Print transaction parameters for debugging
        print(f"[DEBUG] Transaction Parameters: {tx_parameters}")
        
        try:
            # Checking the contract method and args before the transaction
            print(f"[DEBUG] Calling function: {function_name} with arguments: {args}")
            function = getattr(self.contract.functions, function_name)(*args)
            
            # Print the estimated gas for the transaction
            estimated_gas = function.estimate_gas(tx_parameters)
            print(f"[DEBUG] Estimated Gas for the transaction: {estimated_gas}")
            
            # Execute the transaction
            tx_hash = function.transact(tx_parameters)
            
            # Wait for the transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Log the successful transaction
            print(f"[DEBUG] Transaction receipt: {receipt}")
            
            if receipt['status'] == 0:
                raise Exception(f"Transaction failed with status 0: {tx_hash.hex()}")
            
            print(f"[INFO] Transaction {function_name} executed successfully. From: {from_address}, Tx Hash: {tx_hash.hex()}, Gas: {gas}, Gas Price: {tx_parameters['gasPrice']}")
            
            return receipt
    
        except Exception as e:
            # Print the error and log it
            print(f"[ERROR] Error executing transaction: {str(e)}")
            # Assuming you have a logging function to log the error
            log_error(f"Error executing {function_name} from {from_address}. Error: {str(e)}")
            raise e

    def listen_to_event(self):
        """
        Listens to a specific event from the smart contract indefinitely.
        """
        event_filter = self.contract.events.ActionLogged.create_filter(fromBlock='latest')
        while True:
            entries = event_filter.get_new_entries()
            for event in entries:
                self.handle_action_logged(event)
            time.sleep(10)

    def handle_action_logged(self, event):
        """
        Handles events by logging a message when an event is caught.

        Args:
            event (dict): The event data returned by the blockchain.
        """
        log_msg(f"New Action Logged: {event['args']}")

    from colorama import Fore, Style

    # Già esistente - aggiornato con nuovi parametri
    def register_entity(self, name, last_name, role, email, from_address):
        """
        Registers a new user in the contract.

        Args:
            name (str): User's first name.
            last_name (str): User's last name.
            role (str): User role.
            email (str): Email address.
            from_address (str): The Ethereum address initiating the transaction.

        Returns:
            The transaction receipt object.
        """
        if not from_address:
            raise ValueError(Fore.RED + "A valid Ethereum address must be provided as 'from_address'." + Style.RESET_ALL)
        return self.write_data("registerUser", from_address, name, last_name, role, email)

    # 🔹 Lettura del saldo token
    def get_token_balance(self, address):
        """
        Returns the token balance of a given address.

        Args:
            address (str): The Ethereum address to check.

        Returns:
            int: The token balance.
        """
        return self.read_data("balanceOf", address)

    # 🔹 Trasferimento token
    def transfer_tokens(self, to_address, amount, from_address):
        """
        Transfers tokens from one address to another.

        Args:
            to_address (str): Recipient's Ethereum address.
            amount (int): Amount of tokens to transfer.
            from_address (str): Sender's Ethereum address.

        Returns:
            The transaction receipt object.
        """
        if not from_address or not to_address:
            raise ValueError(Fore.RED + "Both 'from_address' and 'to_address' must be provided." + Style.RESET_ALL)
        return self.write_data("transfer", from_address, to_address, amount)

    # 🔹 Burn token
    def burn_tokens(self, from_address, amount):
        """
        Burns tokens from the specified address.

        Args:
            from_address (str): Address from which tokens will be burned.
            amount (int): Amount to burn.

        Returns:
            The transaction receipt object.
        """
        if not from_address:
            raise ValueError(Fore.RED + "A valid Ethereum address must be provided as 'from_address'." + Style.RESET_ALL)
        return self.write_data("burn", from_address, from_address, amount)  # potrebbe richiedere `burn(from, amount)`

    def reward_tokens(self, user_address, amount):
        """
        Rewards tokens to the specified user address.

        Args:
            user_address (str): Address of the user to reward tokens.
            amount (int): Amount of tokens to reward.

        Returns:
            The transaction receipt object.
        """
        if not user_address:
            raise ValueError("A valid Ethereum address must be provided as 'user_address'.")
        return self.write_data("rewardUser", user_address, amount)
