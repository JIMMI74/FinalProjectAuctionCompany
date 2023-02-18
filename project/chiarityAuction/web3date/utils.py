from web3 import Web3

def sendTransaction(message):
    w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/fdc1544f98cf4cad88593ef6c26d108a'))
    address = '0xBa4f66ec7cfF5733A0775d31D6e74eF1155a0fb1'
    privateKey = '0xe4d2fe1c45ab8afa67bea86d3f8d84f642f7589005a2a3a81c9f04eb0cd9db25'
    nonce = w3.eth.getTransactionCount(address)
    gasPrice = w3.eth.gasPrice
    value = w3.toWei(0, 'ether')
    signedTx = w3.eth.account.signTransaction(dict(
        nonce=nonce,
        gasPrice=gasPrice,
        gas=100000,
        to='0xF9968D1Ded25731Ef085bbBb09C92955d23F105a',
        value=value,
        data=message.encode('utf-8')
    ), privateKey)

    tx = w3.eth.sendRawTransaction(signedTx.rawTransaction)
    txId = w3.toHex(tx)
    return txId