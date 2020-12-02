import json
#from web3 import Web3
#now interacting with contracts using Brownie instead
from client.LoadBrownieProject import *

contract = SimpleTextStorage.at("0xb98ab00790daB7A2076ad0Ae5a5a57537A49A932")


#These functions are not used by default. They are automatically generated for your convenience
#They will allow the server to call the smart contract's functions
#Careful when using them, they WILL make you spend ETH for non view/pure transactions
#The front-end functions are defined in javascript in the ./templates/index.html file

def get():
	return contract.get()

def set(_x):
	return contract.set(_x, {'from': accounts[0]})

