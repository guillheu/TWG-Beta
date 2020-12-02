import json
#from web3 import Web3
#now interacting with contracts using Brownie instead
from client.LoadBrownieProject import *

contract = Whitelist.at("0xB1C739780939100909C6bDD8703c28c96B6C4421")


#These functions are not used by default. They are automatically generated for your convenience
#They will allow the server to call the smart contract's functions
#Careful when using them, they WILL make you spend ETH for non view/pure transactions
#The front-end functions are defined in javascript in the ./templates/index.html file

def _whitelist(_):
	return contract._whitelist(_)

def addresses(_):
	return contract.addresses(_)

def getAddresses():
	return contract.getAddresses()

def whitelist(__address):
	return contract.whitelist(__address, {'from': accounts[0]})

