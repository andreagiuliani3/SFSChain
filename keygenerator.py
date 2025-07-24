from web3 import Web3

# Create a random Ethereum account
account = Web3().eth.account.create()

print("Public address:", account.address)
print("Private key:", account.key.hex())  
