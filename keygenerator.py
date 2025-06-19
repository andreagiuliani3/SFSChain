from web3 import Web3

# Crea un nuovo account Ethereum casuale
account = Web3().eth.account.create()

print("Indirizzo (public address):", account.address)
print("Chiave privata:", account.key.hex())  
