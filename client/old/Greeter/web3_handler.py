import json
#from web3 import Web3
#now interacting with contracts using Brownie instead
from client.LoadBrownieProject import *
gasPrice = 0
contract = Greeter.at("0xcA513bD46e73e748CCb8AfA31986a536686645C3")


#These functions are not used by default. They are automatically generated for your convenience
#They will allow the server to call the smart contract's functions
#Careful when using them, they WILL make you spend ETH for non view/pure transactions
#The front-end functions are defined in javascript in the ./templates/index.html file


def balance():
	return contract.balance()/10**18

def greet():
	return contract.greet()

def setGreeting(__greeting  ):
	return contract.setGreeting(__greeting  , {'from': accounts[0]})

