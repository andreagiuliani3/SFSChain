from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from colorama import Fore, Style
import random

NODES = [
    "http://172.28.12.175:8545",
    "http://172.28.12.175:8546",
    "http://172.28.12.175:8547",
    "http://172.28.12.175:8548"
]

_w3_instance = None  

def get_web3():
    global _w3_instance
    if _w3_instance is not None:
        return _w3_instance  

    nodes_to_try = random.sample(NODES, len(NODES))  

    for node_url in nodes_to_try:
        w3 = Web3(Web3.HTTPProvider(node_url))
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        if w3.is_connected():
            print(Fore.GREEN + f"Connected to the Ethereum node: {node_url}" + Style.RESET_ALL)
            _w3_instance = w3  
            return _w3_instance
        else:
            print(Fore.YELLOW + f"Connection attempt failed: {node_url}" + Style.RESET_ALL)

    print(Fore.RED + "Error: no Ethereum node is available." + Style.RESET_ALL)
    raise ConnectionError("Failed to connect to any Ethereum node.")
