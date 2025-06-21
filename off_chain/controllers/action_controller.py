import os
import time
import json
from pathlib import Path
from colorama import Fore, Style, init
from controllers.deploy_controller import DeployController
from session.logging import log_msg, log_error
from web3 import Web3
from config.web3_provider import get_web3
import getpass


init(convert=True)

class ActionController:
    """
    Interface per interagire con il contratto ERC20 CarbonCredit.
    Gestisce deploy, caricamento ABI e chiamate di lettura/scrittura.
    """

    def __init__(self):
        self.w3 = get_web3()
        self.contract = None


    def load_contract(self):
        if os.path.exists("on_chain/contract_address.txt"):
         try:
            print("[ActionController] Caricamento indirizzo contratto da file...")
            address = open('on_chain/contract_address.txt').read().strip()
            print(f"[ActionController] Indirizzo contratto: {address}")

            # Verifica che esista un contratto a quell'indirizzo
            code = self.w3.eth.get_code(address)
            if not code or code == b'\x00' or code.hex() == '0x':
                print(Fore.RED + "[ActionController] Nessun contratto trovato a questo indirizzo." + Style.RESET_ALL)
                return False  # Fa partire un nuovo deploy

            print("[ActionController] Caricamento ABI contratto da file...")
            abi = json.load(open('on_chain/contract_abi.json'))
            print(f"[ActionController] ABI caricata, {len(abi)} elementi")

            self.contract = self.w3.eth.contract(address=address, abi=abi)
            log_msg(f"Contract loaded at {address}")
            return True

         except Exception as e:
            log_error(f"Errore caricamento contratto: {e}")
            print(Fore.RED + f"[ActionController] Errore caricamento contratto: {e}" + Style.RESET_ALL)
            self.contract = None
            return False  # Fa partire un nuovo deploy
        else:
            print("[ActionController] Il contratto non è stato ancora deployato.")
        return False


    def deploy_and_initialize(self, source_path='../../on_chain/CarbonCreditRecords.sol'):
        print("[ActionController] Inizio deploy e inizializzazione contratto...")
        controller = DeployController()

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), source_path))
        print(f"[ActionController] Percorso assoluto contratto: {path}")

        try:
            controller.compile_and_deploy(path)
            self.contract = controller.contract
            print(f"[ActionController] Contract deployed at {self.contract.address}")

            os.makedirs('on_chain', exist_ok=True)
            with open('on_chain/contract_address.txt', 'w') as f:
                f.write(self.contract.address)
            with open('on_chain/contract_abi.json', 'w') as f:
                
                json.dump(self.contract.abi, f)

            print("[ActionController] Indirizzo e ABI salvati su file.")
        except Exception as e:
            print(f"[ActionController] Deploy fallito: {e}")

    def read_data(self, function_name, *args):
        """
        Reads data from a contract's function.

        Args:
            function_name (str): The function name to call.
            *args: Arguments required by the function.

        Returns:
            The return value of the function call.
        """
        try:
            function = getattr(self.contract.functions, function_name)(*args)
            
            return function.call()
        except Exception as e:
            log_error(f"Error calling {function_name} with args {args}: {str(e)}")
            raise

    def write_data_user(self, function_name, from_address, *args, gas_price=None, nonce=None):
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
        """if not from_address:
            raise ValueError("Invalid 'from_address' provided. It must be a non-empty string representing an Ethereum address.")"""
        
        try:
                private_key = "02f55087030340d96a19dd0c0c16e798cb028da49df8747883b1c2afeb1ea8a2"
                function = getattr(self.contract.functions, function_name)(*args)
                gas_estimate = function.estimate_gas({'from': "0x2579257Ceb6F9B7041023a111E076606f72Db7Ce"})
           
                transaction = function.build_transaction({
                'from': "0x2579257Ceb6F9B7041023a111E076606f72Db7Ce",
                'nonce': self.w3.eth.get_transaction_count("0x2579257Ceb6F9B7041023a111E076606f72Db7Ce"),
                'gas': int(gas_estimate),
                'gasPrice': self.w3.to_wei('5', 'gwei')
                })
                
                signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Transaction {function_name} executed. Tx Hash: {tx_hash.hex()}, Gas: {gas_estimate}, Gas Price: {gas_price or self.w3.eth.gas_price}")
                log_msg(f"Transaction {function_name} executed. Tx Hash: {tx_hash.hex()}, Gas: {gas_estimate}, Gas Price: {gas_price or self.w3.eth.gas_price}")
                
                user_data = self.contract.functions.users(from_address).call()
                print(f"Name: {user_data[0]}")
                print(f"Last Name: {user_data[1]}")
                print(f"Role: {user_data[2]}")
                print(f"Is Registered: {user_data[3]}")
                is_authorized = self.contract.functions.authorizedEditors(from_address).call()
                print(f"Is authorized editor? {is_authorized}")

                return receipt

        except Exception as e:
                log_error(f"Error executing {function_name} from {from_address}. Error: {str(e)}")
                raise e
        
    def write_data(self, function_name, from_address, *args, gas_price=None, nonce=None):
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
        """if not from_address:
            raise ValueError("Invalid 'from_address' provided. It must be a non-empty string representing an Ethereum address.")"""
        
        try:
            private_key = getpass.getpass('Inserisci la chiave privata per confermare la transazione: ')
            function = getattr(self.contract.functions, function_name)(*args)
            gas_estimate = function.estimate_gas({'from': from_address})
           
            transaction = function.build_transaction({
            'from': from_address,
            'nonce': self.w3.eth.get_transaction_count(from_address),
            'gas': int(gas_estimate),
            'gasPrice': self.w3.to_wei('0', 'gwei')
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Transaction {function_name} executed. Tx Hash: {tx_hash.hex()}, Gas: {gas_estimate}, Gas Price: {gas_price or self.w3.eth.gas_price}")
            log_msg(f"Transaction {function_name} executed. Tx Hash: {tx_hash.hex()}, Gas: {gas_estimate}, Gas Price: {gas_price or self.w3.eth.gas_price}")

            return receipt

        except Exception as e:
            log_error(f"Error executing {function_name} from {from_address}. Error: {str(e)}")
            raise e

    def listen_to_event(self, event_name, handler, poll_interval=10):
        print(f"[ActionController] Inizio ascolto evento {event_name} con polling ogni {poll_interval}s")
        filter_ = getattr(self.contract.events, event_name).create_filter(fromBlock='latest')
        while True:
            for evt in filter_.get_new_entries():
                print(f"[ActionController] Evento {event_name} ricevuto: {evt}")
                handler(evt)
            time.sleep(poll_interval)

    def handle_action_logged(self, event):
        print(f"[ActionController] Nuovo Action Logged evento: {event['args']}")
        log_msg(f"New Action Logged: {event['args']}")

    def add_user(self, name: str, last_name: str, user_role: str, from_address: str):
        """
        Calls addUser(name, lastName)
        """
        from_address = Web3.to_checksum_address(from_address)
        from_address1 = from_address
        return self.write_data_user('addUser', from_address1, from_address, name, last_name, user_role)

    def update_user(self, name: str, last_name: str, user_role: str, from_address: str):
        """
        Calls updateUser(name, lastName)
        """
        from_address = Web3.to_checksum_address(from_address)
        return self.write_data('updateUser', from_address, name, last_name, user_role)

    def add_token(self, amount: int, to_address: str):
        """
        Calls addToken(to, amount)
        """
        to_address = Web3.to_checksum_address(to_address)
        from_address = os.getenv('ADMIN_ADDRESS')
        from_address= Web3.to_checksum_address(from_address)
        return self.write_data('addToken', from_address, to_address, amount)
    
    def remove_token(self, amount: int, to_address: str):
        """
        Calls addToken(to, amount)
        """
        to_address = Web3.to_checksum_address(to_address)
        from_address = os.getenv('ADMIN_ADDRESS')
        from_address= Web3.to_checksum_address(from_address)
        return self.write_data('removeToken', from_address, to_address, amount)

    def transfer_token(self, from_address: str, to_address: str, amount: int):
        """
        Calls transferToken(to, amount)
        """
        from_address = Web3.to_checksum_address(from_address)
        to_address = Web3.to_checksum_address(to_address)
        return self.write_data('transferToken', from_address, to_address, amount)
    
    def check_balance(self, address: str):
        """
        Calls checkBalance(address)
        """
        address = Web3.to_checksum_address(address)
        function = getattr(self.contract.functions, 'checkBalance')()
        return function.call({'from': address})
    
    def is_registered(self, address: str):
        """
        Calls isRegistered(address)
        """
        address = Web3.to_checksum_address(address)
        return self.read_data('isRegistered', address)
