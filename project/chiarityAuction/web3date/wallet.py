from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/fdc1544f98cf4cad88593ef6c26d108a'))

account = w3.eth.account.create()
privateKey = account.privateKey.hex()
address = account.address
print(f"Your address: (address) (nYour key: (privateKey)")

