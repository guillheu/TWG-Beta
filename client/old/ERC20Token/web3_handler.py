import json
#from web3 import Web3
#now interacting with contracts using Brownie instead
from client.LoadBrownieProject import *

contract = ERC20Token.at("0xdd22F143234D7d6a19Ed03E29d518852Cc434F25")


#These functions are not used by default. They are automatically generated for your convenience
#They will allow the server to call the smart contract's functions
#Careful when using them, they WILL make you spend ETH for non view/pure transactions
#The front-end functions are defined in javascript in the ./templates/index.html file

def allowance(_owner, _spender):
	return contract.allowance(_owner, _spender)

def approve(_spender, _amount):
	return contract.approve(_spender, _amount, {'from': accounts[0]})

def balanceOf(_account):
	return contract.balanceOf(_account)

def decimals():
	return contract.decimals()

def decreaseAllowance(_spender, _subtractedValue):
	return contract.decreaseAllowance(_spender, _subtractedValue, {'from': accounts[0]})

def increaseAllowance(_spender, _addedValue):
	return contract.increaseAllowance(_spender, _addedValue, {'from': accounts[0]})

def name():
	return contract.name()

def symbol():
	return contract.symbol()

def totalSupply():
	return contract.totalSupply()

def transfer(_recipient, _amount):
	return contract.transfer(_recipient, _amount, {'from': accounts[0]})

def transferFrom(_sender, _recipient, _amount):
	return contract.transferFrom(_sender, _recipient, _amount, {'from': accounts[0]})

