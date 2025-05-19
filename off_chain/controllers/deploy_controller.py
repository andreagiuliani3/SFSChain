import os
from colorama import Fore, Style, init
from web3 import Web3
from solcx import compile_standard, get_installed_solc_versions, install_solc
import random

init(convert=True)

class DeployController:
    """
    Gestisce compilazione e deploy del contratto Solidity tramite Web3.
    """

    def __init__(self, http_provider='http://127.0.0.1:7545', solc_version='0.8.19'):
        print("[DeployController] Inizializzo connessione a nodo Ethereum...")
        self.http_provider = http_provider
        self.solc_version = solc_version
        self.w3 = Web3(Web3.HTTPProvider(self.http_provider))

        install_dir = os.getcwd()
        install_solc('0.8.19')
        print(f"[DeployController] Controllo installazione solc versione {self.solc_version}...")
        if self.solc_version not in get_installed_solc_versions():
            print(f"[DeployController] Versione solc non trovata, installo {self.solc_version}...")
        else: print("ok")

        if self.w3.is_connected():
            print(Fore.GREEN + "[DeployController] Connesso correttamente al nodo Ethereum." + Style.RESET_ALL)
        else:
            print(Fore.RED + "[DeployController] Errore: connessione al nodo Ethereum fallita." + Style.RESET_ALL)
            raise ConnectionError("Failed to connect to Ethereum node.")
        self.contract = None
        self.abi = None
        self.bytecode = None
        self.contract_id = None
        self.contract_interface = None

    def compile_and_deploy(self, contract_source_path, account=None):
        print(f"[DeployController] Avvio compile e deploy del contratto da: {contract_source_path}")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        shared_dir_path = os.path.dirname(os.path.dirname(dir_path))
        contract_full_path = os.path.normpath(os.path.join(shared_dir_path, contract_source_path))
        print(f"[DeployController] Percorso assoluto contratto: {contract_full_path}")

        with open(contract_full_path, 'r') as file:
            contract_source_code = file.read()
        print(f"[DeployController] Codice Solidity letto, lunghezza: {len(contract_source_code)} caratteri")

        self.compile_contract(contract_source_code)
        account = random.choice(self.w3.eth.accounts)
        balance = self.w3.eth.get_balance(account)
        print(f"[DeployController] Saldo account: {balance} wei")

        self.deploy_contract(account)

    def compile_contract(self, solidity_source):
        print(f"[DeployController] Controllo installazione solc versione {self.solc_version}...")
        if self.solc_version not in get_installed_solc_versions():
            print(f"[DeployController] Versione solc non trovata, installo {self.solc_version}...")
            install_solc('0.8.19')
        else:
            print(f"[DeployController] Versione solc già installata.")

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        node_modules_path = os.path.join(base_dir, 'node_modules')
        remappings = [f"@openzeppelin={node_modules_path}/@openzeppelin"]
        print(f"[DeployController] Uso remappings: {remappings}")

        print("[DeployController] Compilo il contratto Solidity...")
        compiled_sol = compile_standard({
            "language": "Solidity",
            "sources": {
                "CarbonCreditRecords.sol": {
                    "content": solidity_source
                }
            },
            "settings": {
                "remappings": remappings,
                "outputSelection": {
                    "*": {
                        "*": ["abi", "evm.bytecode"]
                    }
                }
            }
        }, solc_version=self.solc_version)

        self.contract_id, self.contract_interface = next(iter(compiled_sol['contracts']['CarbonCreditRecords.sol'].items()))
        self.abi = self.contract_interface['abi']
        self.bytecode = self.contract_interface['evm']['bytecode']['object']

        print(f"[DeployController] Compilazione completata per contratto: {self.contract_id}")
        print(f"[DeployController] ABI ottenuta con {len(self.abi)} elementi")
        print(f"[DeployController] Bytecode lunghezza: {len(self.bytecode)}")

    def deploy_contract(self, account):
        print(f"[DeployController] Inizio deploy contratto dall'account: {account}")

        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)

        try:
            print("[DeployController] Invio transazione di deploy...")
            tx_hash = contract.constructor().transact({'from': account})
            print(f"[DeployController] Transazione inviata, hash: {tx_hash.hex()}")

            print("[DeployController] Attendo il receipt della transazione...")
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"[DeployController] Transazione confermata nella block {tx_receipt.blockNumber}")

            self.contract = self.w3.eth.contract(address=tx_receipt.contractAddress, abi=self.abi)
            print(f'Contract deployed at {tx_receipt.contractAddress} from {account}')

        except Exception as e:
            print(Fore.RED + "[DeployController] Errore durante il deploy del contratto:" + Style.RESET_ALL)
            print(e)
            raise
