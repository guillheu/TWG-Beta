from brownie import accounts, Defi
import brownie
import pytest


@pytest.fixture
def contract():
    global owner
    owner = accounts[0]
    global voter1
    voter1 = accounts[1]
    global voter2
    voter2 = accounts[2]
    global voter3
    voter3 = accounts[3]
    contract = Defi.deploy({'from':owner})
    return contract

### step 1

def testIsVoter(contract):

    assert not contract.voters(voter1)[0]
    assert not contract.voters(voter2)[0]
    contract.registerVoter(voter1)
    contract.registerVoter(voter2)
    assert contract.voters(voter1)[0]
    assert contract.voters(voter2)[0]
    assert not contract.voters(voter3)[0]



### steps proposal test 

def testStartProposalSession(contract):
    assert contract.getWorkflowStatus() == "RegisteringVoters"
    contract.startProposalRegistration({'from': owner})
    assert contract.getWorkflowStatus() == "ProposalsRegistrationStarted"

    
def testPropose(contract):


    contract.registerVoter(voter1, {'from': owner})
    contract.registerVoter(voter2, {'from': owner})
    contract.startProposalRegistration({'from': owner})


    proposal1 = 'test1'
    proposal2 = 'test2'
    contract.offerProposal(proposal1, {'from': voter1})
    contract.offerProposal(proposal2, {'from': voter2})
    assert contract.proposals(0)[0]==proposal1
    assert contract.proposals(1)[0]==proposal2
    assert contract.proposals(0)[1]==0
    assert contract.proposals(1)[1]==0



### voting step
def testEndProposalSession(contract):
    contract.registerVoter(voter1, {'from': owner})
    contract.registerVoter(voter2, {'from': owner})
    contract.startProposalRegistration({'from': owner})
    proposal1 = 'test1'
    proposal2 = 'test2'
    contract.offerProposal(proposal1, {'from': voter1})
    contract.offerProposal(proposal2, {'from': voter2})


    assert contract.getWorkflowStatus() == "ProposalsRegistrationStarted"
    contract.endProposalRegistration({'from': owner})
    assert contract.getWorkflowStatus() == "ProposalsRegistrationEnded"


def testStartVotingSession(contract):


    contract.registerVoter(voter1, {'from': owner})
    contract.registerVoter(voter2, {'from': owner})
    contract.startProposalRegistration({'from': owner})
    proposal1 = 'test1'
    proposal2 = 'test2'
    contract.offerProposal(proposal1, {'from': voter1})
    contract.offerProposal(proposal2, {'from': voter2})
    contract.endProposalRegistration({'from': owner})


    assert contract.getWorkflowStatus() == "ProposalsRegistrationEnded"
    contract.startVotingSession({'from': owner})
    assert contract.getWorkflowStatus() == "VotingSessionStarted"



def testvote(contract):


    contract.registerVoter(voter1, {'from': owner})
    contract.registerVoter(voter2, {'from': owner})
    contract.startProposalRegistration({'from': owner})
    proposal1 = 'test1'
    proposal2 = 'test2'
    contract.offerProposal(proposal1, {'from': voter1})
    contract.offerProposal(proposal2, {'from': voter2})
    contract.endProposalRegistration({'from': owner})
    contract.startVotingSession({'from': owner})


    assert not contract.voters(voter1)[1]
    contract.vote(1, {'from': voter1})
    contract.vote(1, {'from': voter2})

    voter3HasVoted = False
    try:
        contract.vote(0, {'from': voter3})
        voter3HasVoted = True
    except:
        pass

    assert not voter3HasVoted

    assert contract.voters(voter1)[1]
    assert contract.voters(voter2)[1]
    assert contract.voters(voter1)[2] == 1
    assert contract.voters(voter2)[2] == 1
    assert contract.proposals(0)[1] == 0
    assert contract.proposals(1)[1] == 2



### count votes

def testEndVotingSession(contract):

    contract.registerVoter(voter1, {'from': owner})
    contract.registerVoter(voter2, {'from': owner})
    contract.startProposalRegistration({'from': owner})
    proposal1 = 'test1'
    proposal2 = 'test2'
    contract.offerProposal(proposal1, {'from': voter1})
    contract.offerProposal(proposal2, {'from': voter2})
    contract.endProposalRegistration({'from': owner})
    contract.startVotingSession({'from': owner})
    contract.vote(1, {'from': voter1})
    contract.vote(1, {'from': voter2})


    assert contract.getWorkflowStatus() == "VotingSessionStarted"
    contract.endVotingSession({'from': owner})
    assert contract.getWorkflowStatus() == "VotingSessionEnded"




def testVotingTallied(contract):

    contract.registerVoter(voter1, {'from': owner})
    contract.registerVoter(voter2, {'from': owner})
    contract.startProposalRegistration({'from': owner})
    proposal1 = 'test1'
    proposal2 = 'test2'
    contract.offerProposal(proposal1, {'from': voter1})
    contract.offerProposal(proposal2, {'from': voter2})
    contract.endProposalRegistration({'from': owner})
    contract.startVotingSession({'from': owner})
    contract.vote(1, {'from': voter1})
    contract.vote(1, {'from': voter2})
    contract.endVotingSession({'from': owner})


    assert contract.getWorkflowStatus() == "VotingSessionEnded"
    contract.tallyVotes({'from': owner})
    assert contract.getWorkflowStatus() == "VotesTallied"

def testTally(contract):

    contract.registerVoter(voter1, {'from': owner})
    contract.registerVoter(voter2, {'from': owner})
    contract.startProposalRegistration({'from': owner})
    proposal1 = 'test1'
    proposal2 = 'test2'
    contract.offerProposal(proposal1, {'from': voter1})
    contract.offerProposal(proposal2, {'from': voter2})
    contract.endProposalRegistration({'from': owner})
    contract.startVotingSession({'from': owner})
    contract.vote(1, {'from': voter1})
    contract.vote(1, {'from': voter2})
    contract.endVotingSession({'from': owner})
    contract.tallyVotes({'from': owner})

    assert contract.winningProposalId() == 1
    
