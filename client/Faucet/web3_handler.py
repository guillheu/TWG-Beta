import json
#from web3 import Web3
#now interacting with contracts using Brownie instead
from client.LoadBrownieProject import *

gasPrice = 0
contract = Faucet.at("0x731469b4E7E4A25B606d0de8aa6945Dd84a10A73")
web3URL = "http://127.0.0.1:8545"

#These functions are not used by default. They are automatically generated for your convenience
#They will allow the server to call the smart contract's functions
#Careful when using them, they WILL make you spend ETH for non view/pure transactions
#The front-end functions are defined in javascript in the ./templates/index.html file

def request(_addr):
	if(contract.balance() >= 1.1*10**19):
		try:
			return contract.request(_addr, {'from': accounts[0]})
		except:
			return "An error occurred. Are you on timeout ?"

def timeouts(_):
	return contract.timeouts(_)

def balance():
	return contract.balance()/10**18