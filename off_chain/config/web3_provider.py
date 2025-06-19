from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from colorama import Fore, Style, init

HTTP_PROVIDER = "http://172.28.12.175:8545"  
w3 = Web3(Web3.HTTPProvider(HTTP_PROVIDER))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

if w3.is_connected():
    print(Fore.GREEN + "Connesso al nodo Ethereum." + Style.RESET_ALL)
else:
    print(Fore.RED + "Errore connessione al nodo Ethereum." + Style.RESET_ALL)
    raise ConnectionError("Failed to connect to Ethereum node.")

def get_web3():
    return w3