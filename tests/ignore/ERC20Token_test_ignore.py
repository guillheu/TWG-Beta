from brownie import accounts, ERC20Token
import brownie
import pytest


@pytest.fixture
def contract():
	global _name
	_name = 'ALYRA'
	global _symbol
	_symbol= 'ALY'
	global _initialSupply
	_initialSupply = 1000
	global _decimals
	_decimals = 18
	global owner
	owner = accounts[0]
	global recipient
	recipient = accounts[1]
	global thirdParty
	thirdParty = accounts[2]

	contract = ERC20Token.deploy(_initialSupply, {'from':owner})
	return contract

def testName(contract):
	assert contract.name() == _name

def testSymbol(contract):
	assert contract.symbol() == _symbol

def testDecimal(contract):
	assert contract.decimals() == _decimals

def testTotalSupplyIsInitialSupply(contract):
	assert contract.totalSupply() == _initialSupply

def testOwnerBalance(contract):
	assert contract.balanceOf(owner) == _initialSupply

def testTransfer(contract):
	ownerBefore = contract.balanceOf(owner)
	recipientBefore = contract.balanceOf(recipient)
	amount = 10
	contract.transfer(recipient, amount, {'from': owner})
	assert contract.balanceOf(owner) == ownerBefore - 10
	assert contract.balanceOf(recipient) == recipientBefore + 10

def testAllowance(contract):
	expectedAllowance = 0
	assert contract.allowance(owner, recipient) == expectedAllowance
	assert contract.allowance(recipient, owner) == expectedAllowance

def testApprove(contract):
	recipientToOwnerAllowance = contract.allowance(recipient, owner)
	ownerToRecipientAllowance = contract.allowance(owner, recipient)
	amount = 10
	contract.approve(recipient, amount, {'from': owner})
	assert ownerToRecipientAllowance + amount == contract.allowance(owner, recipient)
	assert recipientToOwnerAllowance == contract.allowance(recipient, owner)

def testTransferFrom(contract):
	amount = 10
	ownerBalance = contract.balanceOf(owner)
	recipientBalance = contract.balanceOf(recipient)
	thirdPartyBalance = contract.balanceOf(thirdParty)

	hasTransfered = False
	with brownie.reverts():
		contract.transferFrom(owner, thirdParty, amount, {'from': recipient})
		hasTransfered = True


	assert not hasTransfered

	contract.approve(recipient, amount, {'from': owner})
	ownerToRecipientAllowanceApproved = contract.allowance(owner, recipient)

	assert contract.transferFrom(owner, thirdParty, amount, {'from': recipient})
	assert contract.balanceOf(owner) == ownerBalance - amount
	assert contract.balanceOf(recipient) == recipientBalance
	assert contract.balanceOf(thirdParty) == thirdPartyBalance + amount


def testIncreaseAllowance(contract):
	amount = 10
	contract.approve(recipient, amount, {'from': owner})
	contract.increaseAllowance(recipient, amount, {'from': owner})
	assert contract.allowance(owner, recipient) == 2*amount

def testDecreaseAllowance(contract):
	initialAmount = 100
	amount = 10

	hasDecreasedAllowance = False
	with brownie.reverts():
		contract.decreaseAllowance(recipient, amount, {'from': owner})
		hasDecreasedAllowance = True

	assert not hasDecreasedAllowance

	contract.approve(recipient, initialAmount, {'from': owner})
	contract.decreaseAllowance(recipient, amount, {'from': owner})
	
	assert contract.allowance(owner, recipient) == initialAmount - amount