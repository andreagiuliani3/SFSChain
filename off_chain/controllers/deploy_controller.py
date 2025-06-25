import os
from colorama import Fore, Style, init
from solcx import compile_standard, get_installed_solc_versions, install_solc
from config.web3_provider import get_web3

init(convert=True)

class DeployController:
    """
    Gestisce compilazione e deploy del contratto Solidity tramite Web3.
    """

    def __init__(self, solc_version='0.8.19'):
        
        
        self.w3 = get_web3()
        
        self.solc_version = solc_version

        install_solc('0.8.19')
        print(f"[DeployController] Controllo installazione solc versione {self.solc_version}...")
        if self.solc_version not in get_installed_solc_versions():
            print(f"[DeployController] Versione solc non trovata, installo {self.solc_version}...")
        else: print("ok")

        self.contract = None
        self.abi = None
        self.bytecode = None
        self.contract_id = None
        self.contract_interface = None

    
    def compile_and_deploy(self, contract_source_path):
        print(f"[DeployController] Avvio compile e deploy del contratto da: {contract_source_path}")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        shared_dir_path = os.path.dirname(os.path.dirname(dir_path))
        contract_full_path = os.path.normpath(os.path.join(shared_dir_path, contract_source_path))
        print(f"[DeployController] Percorso assoluto contratto: {contract_full_path}")

        with open(contract_full_path, 'r') as file:
            contract_source_code = file.read()
        print(f"[DeployController] Codice Solidity letto, lunghezza: {len(contract_source_code)} caratteri")

        self.compile_contract(contract_source_code)

        balance = self.w3.eth.get_balance("0x2579257Ceb6F9B7041023a111E076606f72Db7Ce")
        print(f"[DeployController] Saldo account: {balance} wei")

        self.deploy_contract("0x2579257Ceb6F9B7041023a111E076606f72Db7Ce")

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

    def deploy_contract(self, account_address):
       
        print(f"[DeployController] Inizio deploy contratto dall'account: {account_address}")

        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        gas_estimate = contract.constructor().estimate_gas({'from': account_address})
        print(gas_estimate)
        try:
            print("[DeployController] Invio transazione di deploy...")
            nonce = self.w3.eth.get_transaction_count(account_address)
            transaction = contract.constructor().build_transaction({
                'from': account_address,
                'nonce': nonce,
                'gas': gas_estimate,               
                'gasPrice': self.w3.to_wei('5', 'gwei')
            })
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key="02f55087030340d96a19dd0c0c16e798cb028da49df8747883b1c2afeb1ea8a2")
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            print(f"[DeployController] Transazione inviata, hash: {tx_hash.hex()}")

            print("[DeployController] Attendo il receipt della transazione...")
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Status: {tx_receipt.status}")  # 1 = success, 0 = fail
            print(f"Contract Address: {tx_receipt.contractAddress}")
            print(f"Gas Used: {tx_receipt.gasUsed}")
            print(f"Block Number: {tx_receipt.blockNumber}")
            print(f"[DeployController] Transazione confermata nella block {tx_receipt.blockNumber}")
           

            self.contract = self.w3.eth.contract(address=tx_receipt.contractAddress, abi=self.abi)
            print(f"Contract address: {self.contract.address}")
            print(f"Contract code: {self.w3.eth.get_code(self.contract.address).hex()}")

            print(f'Contract deployed at {tx_receipt.contractAddress} from {account_address}')

            
        except Exception as e:
            print(Fore.RED + "[DeployController] Errore durante il deploy del contratto:" + Style.RESET_ALL)
            print(e)
            raise
