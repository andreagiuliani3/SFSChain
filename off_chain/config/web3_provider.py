from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from colorama import init, Fore, Style
init(strip=False, convert=False)
import random
import sys
import os
import time
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../', '.env'))

NODES = os.getenv('ETHEREUM_NODES').split(",")
NODES = [node.strip() for node in NODES if node.strip()]

_w3_instance = None

def try_connect():
    """
    Tries to connect to a random Ethereum node from the list.
    If the connection is successful, it returns the Web3 instance.
    If all nodes fail, it returns None.
    Prints connection status messages to the console.
    """
    nodes_to_try = random.sample(NODES, len(NODES))  

    for node_url in nodes_to_try:
        w3 = Web3(Web3.HTTPProvider(node_url))
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        if w3.is_connected():
            print(Fore.GREEN + f"Connected to ethereum node: {node_url}" + Style.RESET_ALL)
            return w3
        

    return None


def get_web3():
    """
    Returns a Web3 instance connected to an Ethereum node.
    If no instance exists, it attempts to connect to a node every 5 seconds.
    The user can exit at any time with Ctrl+C.
    """
    global _w3_instance
    if _w3_instance is not None:
        return _w3_instance

    print(Fore.YELLOW + "Attempting to connect to an Ethereum node..." + Style.RESET_ALL)

    try:
        while True:
            w3 = try_connect()
            if w3:
                _w3_instance = w3
                return _w3_instance
            else:
                print(Fore.RED + "No available Ethereum nodes. Retrying in 10 seconds... (Press Ctrl+C to exit)" + Style.RESET_ALL)
                time.sleep(10)
    except KeyboardInterrupt:
        print(Fore.CYAN + "\nConnection attempt aborted by user. Exiting..." + Style.RESET_ALL)
        sys.exit(1)
