import os
import time
import json
from colorama import Fore, Style, init
from controllers.deploy_controller import DeployController
from session.logging import log_msg, log_error
from web3 import Web3

init(convert=True)

class ActionController:
    """
    Interface per interagire con il contratto ERC20 CarbonCredit.
    Gestisce deploy, caricamento ABI e chiamate di lettura/scrittura.
    """

    def __init__(self, http_provider='http://127.0.0.1:7545'):
        print(f"[ActionController] Connessione a nodo Ethereum: {http_provider}")
        self.w3 = Web3(Web3.HTTPProvider(http_provider))
        if self.w3.is_connected():
            print(Fore.GREEN + "[ActionController] Connesso al nodo Ethereum." + Style.RESET_ALL)
        else:
            print(Fore.RED + "[ActionController] Errore connessione al nodo Ethereum." + Style.RESET_ALL)
            raise ConnectionError("Failed to connect to Ethereum node.")
        self.contract = None
        self.load_contract()

    def load_contract(self):
        try:
            print("[ActionController] Caricamento indirizzo contratto da file...")
            address = open('on_chain/contract_address.txt').read().strip()
            print(f"[ActionController] Indirizzo contratto: {address}")

            print("[ActionController] Caricamento ABI contratto da file...")
            abi = json.load(open('on_chain/contract_abi.json'))
            print(f"[ActionController] ABI caricata, {len(abi)} elementi")

            self.contract = self.w3.eth.contract(address=address, abi=abi)
            log_msg(f"Contract loaded at {address}")
        except Exception as e:
            log_error(f"Errore caricamento contratto: {e}")
            print(Fore.RED + f"[ActionController] Errore caricamento contratto: {e}" + Style.RESET_ALL)
            self.contract = None

    def deploy_and_initialize(self, source_path='../../on_chain/CarbonCreditRecords.sol', account=None):
        print("[ActionController] Inizio deploy e inizializzazione contratto...")
        controller = DeployController(self.w3.provider.endpoint_uri)

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), source_path))
        print(f"[ActionController] Percorso assoluto contratto: {path}")

        if account is None:
            account = self.w3.eth.accounts[0]
        print(f"[ActionController] Account non passato, uso primo disponibile: {account}")

        try:
            controller.compile_and_deploy(path, account=account)
            self.contract = controller.contract
            print(f"[ActionController] Contract deployed at {self.contract.address}")

            os.makedirs('on_chain', exist_ok=True)
            with open('on_chain/contract_address.txt', 'w') as f:
                f.write(self.contract.address)
            with open('on_chain/contract_abi.json', 'w') as f:
                import json
                json.dump(self.contract.abi, f)

            print("[ActionController] Indirizzo e ABI salvati su file.")
        except Exception as e:
            print(f"[ActionController] Deploy fallito: {e}")


    def read_data(self, fn_name, *args):
        print(f"[ActionController] Lettura dati: funzione {fn_name} con argomenti {args}")
        try:
            result = getattr(self.contract.functions, fn_name)(*args).call()
            log_msg(f"{fn_name} -> {result}")
            print(f"[ActionController] Risultato: {result}")
            return result
        except Exception as e:
            log_error(f"Errore read_data {fn_name}: {e}")
            print(Fore.RED + f"[ActionController] Errore in read_data {fn_name}: {e}" + Style.RESET_ALL)
            raise

    def write_data(self, fn_name, from_address, private_key, *args, gas=2000000):
        print(f"[ActionController] Scrittura dati: funzione {fn_name} da {from_address} con argomenti {args}")
        if not from_address or not private_key:
            raise ValueError(Fore.RED + "Specificare indirizzo e private key validi." + Style.RESET_ALL)
        try:
            nonce = self.w3.eth.get_transaction_count(from_address)
            print(f"[ActionController] Nonce corrente: {nonce}")

            tx = getattr(self.contract.functions, fn_name)(*args).build_transaction({
                'from': from_address,
                'nonce': nonce,
                'gas': gas,
                'gasPrice': self.w3.eth.gas_price
            })
            print(f"[ActionController] Transazione costruita: {tx}")

            signed = self.w3.eth.account.sign_transaction(tx, private_key)
            print(f"[ActionController] Transazione firmata.")

            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            print(f"[ActionController] Transazione inviata, hash: {tx_hash.hex()}")

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"[ActionController] Receipt ricevuto, status: {receipt.status}, block: {receipt.blockNumber}")

            if receipt.status == 0:
                log_error(f"Transaction {fn_name} failed: {tx_hash.hex()}")
                print(Fore.RED + f"[ActionController] Transazione fallita: {tx_hash.hex()}" + Style.RESET_ALL)
                raise Exception("Transaction failed")

            log_msg(f"Transaction {fn_name} success: {tx_hash.hex()}")
            print(Fore.GREEN + f"[ActionController] Transazione {fn_name} completata con successo." + Style.RESET_ALL)
            return receipt
        except Exception as e:
            log_error(f"Errore in write_data {fn_name}: {e}")
            print(Fore.RED + f"[ActionController] Eccezione in write_data {fn_name}: {e}" + Style.RESET_ALL)
            raise

    # Metodi equivalenti alle funzioni del contratto
    def register_entity(self, name, last_name, from_address, private_key):
        print(f"[ActionController] Chiamata register_entity con {name}, {last_name}")
        return self.write_data('addUser', from_address, private_key, name, last_name)

    def update_entity(self, name, last_name, from_address, private_key):
        print(f"[ActionController] Chiamata update_entity con {name}, {last_name}")
        return self.write_data('updateUser', from_address, private_key, name, last_name)

    def add_tokens(self, to_address, amount, from_address, private_key):
        print(f"[ActionController] Chiamata add_tokens a {to_address} quantità {amount}")
        return self.write_data('addTokens', from_address, private_key, to_address, amount)

    def remove_tokens(self, from_token_addr, amount, from_address, private_key):
        print(f"[ActionController] Chiamata remove_tokens da {from_token_addr} quantità {amount}")
        return self.write_data('removeTokens', from_address, private_key, from_token_addr, amount)

    def transfer_tokens(self, to_address, amount, from_address, private_key):
        print(f"[ActionController] Chiamata transfer_tokens a {to_address} quantità {amount}")
        return self.write_data('transferTokens', from_address, private_key, to_address, amount)

    def transfer_from(self, token_from, to_address, amount, from_address, private_key):
        print(f"[ActionController] Chiamata transfer_from da {token_from} a {to_address} quantità {amount}")
        return self.write_data('transferFrom', from_address, private_key, token_from, to_address, amount)

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
