import os
from colorama import Fore, Style, init
from solcx import compile_standard, get_installed_solc_versions, install_solc, set_solc_version
from config.web3_provider import get_web3
from packaging.version import Version

init(convert=True)

class DeployController:
    """
    This class is responsible for compiling and deploying smart contracts on the Ethereum blockchain.
    It uses the `solcx` library to compile Solidity contracts and the `web3` library to interact with the Ethereum network.
    It handles the compilation of the contract source code, deployment to the blockchain, and provides methods
    to compile and deploy contracts based on a given Solidity source file.
    It also ensures that the specified version of the Solidity compiler is installed and set for use.
    """

    def __init__(self, solc_version='0.8.19'):
        
        
        self.w3 = get_web3()
        self.solc_version = solc_version

        
        if Version(self.solc_version) not in get_installed_solc_versions():
            install_solc(solc_version)
            set_solc_version(solc_version)
       

        self.contract = None
        self.abi = None
        self.bytecode = None
        self.contract_id = None
        self.contract_interface = None

    
    def compile_and_deploy(self, contract_source_path):
        """
        Compiles and deploys a smart contract from the specified Solidity source file.
        :param contract_source_path: Path to the Solidity source file relative to the shared directory.
        """
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        shared_dir_path = os.path.dirname(os.path.dirname(dir_path))
        contract_full_path = os.path.normpath(os.path.join(shared_dir_path, contract_source_path))

        with open(contract_full_path, 'r') as file:
            contract_source_code = file.read()

        self.compile_contract(contract_source_code)
        address = os.getenv('ADMIN_ADDRESS')
        self.deploy_contract(address)

    def compile_contract(self, solidity_source):
        """
        Compiles the provided Solidity source code using the specified version of the Solidity compiler.
        :param solidity_source: Solidity source code as a string.
        """

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        node_modules_path = os.path.join(base_dir, 'node_modules')
        remappings = [f"@openzeppelin={node_modules_path}/@openzeppelin"]
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
        

    def deploy_contract(self, account_address):
        """
        Deploys the compiled smart contract to the Ethereum blockchain using the provided account address.
        :param account_address: The Ethereum address from which the contract will be deployed.
        """

        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        gas_estimate = contract.constructor().estimate_gas({'from': account_address})
        try:
            nonce = self.w3.eth.get_transaction_count(account_address)
            transaction = contract.constructor().build_transaction({
                'from': account_address,
                'nonce': nonce,
                'gas': gas_estimate,               
                'gasPrice': self.w3.eth.gas_price,
            })
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=os.getenv('ADMIN_PRIVATE_KEY'))
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Status: {Fore.GREEN + 'SUCCESS' + Style.RESET_ALL if tx_receipt.status == 1 else Fore.RED + 'FAIL' + Style.RESET_ALL}")
            self.contract = self.w3.eth.contract(address=tx_receipt.contractAddress, abi=self.abi)
            print(f"Contract address: {self.contract.address}")
            

            
        except Exception as e:
            print(Fore.RED + "Error while deploying contract:" + Style.RESET_ALL)
            print(e)
            raise
