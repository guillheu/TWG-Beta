from brownie import accounts
from brownie import SimpleStorage
import pytest




@pytest.fixture
def contract():
	return SimpleStorage.deploy({'from':accounts[0]})

def test_value_change(contract):
	val = 89
	prevVal = contract.get()
	contract.set(val)
	newVal = contract.get()
	assert prevVal == 0
	assert newVal == val