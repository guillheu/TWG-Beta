from brownie import accounts
from brownie import Greeter
import pytest




@pytest.fixture
def contract():
	global _greet
	_greet = "Hello world!"
	return Greeter.deploy(_greet, {'from':accounts[0]})

def testGreet(contract):	
	assert _greet == contract.greet()

def testSetGreet(contract):
	newGreet = "Hallo Welt!"
	contract.setGreeting(newGreet, {"from": accounts[0]})
	assert newGreet == contract.greet()