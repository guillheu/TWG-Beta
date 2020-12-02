import json
#from web3 import Web3
#now interacting with contracts using Brownie instead
from client.LoadBrownieProject import *

contract = SimpleStorage.at("0x1a31197FAF8aF733a34bA250d70657B6f7aeC20F")


#These functions are not used by default. They are automatically generated for your convenience
#They will allow the server to call the smart contract's functions
#Careful when using them, they WILL make you spend ETH for non view/pure transactions
#The front-end functions are defined in javascript in the ./templates/index.html file

def get():
	return contract.get()

def set(_x):
	return contract.set(_x, {'from': accounts[0]})

