import json
#from web3 import Web3
#now interacting with contracts using Brownie instead
from client.LoadBrownieProject import *
gasPrice = 0
contract = Defi.at("0x1cFC5Ab6Eba73c2C0Deff4B9db666CCef66cD323")


#These functions are not used by default. They are automatically generated for your convenience
#They will allow the server to call the smart contract's functions
#Careful when using them, they WILL make you spend ETH for non view/pure transactions
#The front-end functions are defined in javascript in the ./templates/index.html file


def balance():
	return contract.balance()/10**18

def endProposalRegistration():
	return contract.endProposalRegistration(  {'from': accounts[0]})

def endVotingSession():
	return contract.endVotingSession(  {'from': accounts[0]})

def getWorkflowStatus():
	return contract.getWorkflowStatus()

def offerProposal(__description  ):
	return contract.offerProposal(__description  , {'from': accounts[0]})

def owner():
	return contract.owner()

def proposals(_):
	return contract.proposals(_)

def registerVoter(__address  ):
	return contract.registerVoter(__address  , {'from': accounts[0]})

def renounceOwnership():
	return contract.renounceOwnership(  {'from': accounts[0]})

def startProposalRegistration():
	return contract.startProposalRegistration(  {'from': accounts[0]})

def startVotingSession():
	return contract.startVotingSession(  {'from': accounts[0]})

def tallyVotes():
	return contract.tallyVotes(  {'from': accounts[0]})

def transferOwnership(_newOwner  ):
	return contract.transferOwnership(_newOwner  , {'from': accounts[0]})

def vote(__proposalId  ):
	return contract.vote(__proposalId  , {'from': accounts[0]})

def voters(_):
	return contract.voters(_)

def winningProposalId():
	return contract.winningProposalId()

