from brownie import Greeter, Defi, ERC20Token, SimpleStorage, SimpleTextStorage, Whitelist,Faucet, accounts
from .django_deploy import djangoDeploy

def main():
	
	#deploying to blockchain
	accounts.default = accounts[0]
	contract = Defi.deploy({'from': accounts.default})
	#djangoDeploy("Defi", contract)
