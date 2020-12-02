
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import Defi.web3_handler



@csrf_exempt
def checkUserAddresses(request):
	containsPOST = False
	owner = Defi.web3_handler.owner()
	for i in request.POST:
		containsPOST = True
		address = request.POST[i]
		print(address)
		if address == owner:
			if (Defi.web3_handler.voters(address))[0]:
				return render(request, "Defi.html", getDisplayedFields(True, True))
			return render(request, "Defi.html", getDisplayedFields(True, False))
		if (Defi.web3_handler.voters(address))[0]:
			return render(request, "Defi.html", getDisplayedFields(False, True))
	if containsPOST:
		return render(request, "accessDenied.html", {})
	return render(request, "index.html", {})

def getDisplayedFields(isOwner, isVoter):
	endProposalRegistration = "hidden"
	endVotingSession = "hidden"
	startProposalRegistration = "hidden"
	startVotingSession = "hidden"
	tallyVotes = "hidden"
	registerVoter = "hidden"
	showProposals = "hidden"
	winningProposalId = "hidden"
	vote = "hidden"
	offerProposal = "hidden"
	renounceOwnership = "hidden"
	transferOwnership = "hidden"
	ownerFunctions = "hidden"
	voterFunctions = "hidden"
	workflow_msg = ""
	owner = Defi.web3_handler.owner()

	status = Defi.web3_handler.getWorkflowStatus()
	if status == "RegisteringVoters":
		workflow_msg = "Currently registering voters ; contact the contract owner to get registered"
	if status == "ProposalsRegistrationStarted":
		workflow_msg = "Currently accepting proposals from voters ; you can offer a proposal right now!"
	if status == "ProposalsRegistrationEnded":
		workflow_msg = "Proposal registrations closed! Waiting to start the voting session"
	if status == "VotingSessionStarted":
		workflow_msg = "Voting session ongoing, vote for a proposal now! (You cannot change your vote once you have voted)"
	if status == "VotingSessionEnded":
		workflow_msg = "Voting session closed, waiting to tally the votes"
	if status == "VotesTallied":
		id = Defi.web3_handler.winningProposalId()
		(desc, votes) = Defi.web3_handler.proposals(id)
		workflow_msg = "Votes tallied! the winning proposal is proposal #{0} : \"{1}\" with {2} votes".format(id, desc, votes)


	if(isOwner):
		renounceOwnership = ""
		transferOwnership = ""
		ownerFunctions =""

	if(isVoter):
		voterFunctions = ""

	workflowStatus = Defi.web3_handler.getWorkflowStatus()
	if(workflowStatus == "RegisteringVoters"):
		if(isOwner):
			startProposalRegistration = ""
			registerVoter = ""
	else:
		showProposals = ""

	if(workflowStatus == "ProposalsRegistrationStarted"):
		if(isOwner):
			endProposalRegistration = ""
		if(isVoter):
			offerProposal = ""
	else:
		pass
	if(workflowStatus == "ProposalsRegistrationEnded"):
		if(isOwner):
			startVotingSession = ""
	else:
		pass
	if(workflowStatus == "VotingSessionStarted"):
		if(isOwner):
			endVotingSession = ""
		if(isVoter):
			vote = ""
	else:
		pass
	if(workflowStatus == "VotingSessionEnded"):
		if(isOwner):
			tallyVotes = ""
	else:
		pass
	if(workflowStatus == "VotesTallied"):
		winningProposalId = ""
	else:
		pass

	return {
	"address": Defi.web3_handler.contract.address,
	"abi": Defi.web3_handler.contract.abi,
	"gasPrice": Defi.web3_handler.gasPrice,
	"balance": Defi.web3_handler.contract.balance(),
	"hide_endProposalRegistration" : "{}".format(endProposalRegistration),
	"hide_endVotingSession" : "{}".format(endVotingSession),
	"hide_offerProposal" : "{}".format(offerProposal),
	"hide_proposals" : "{}".format(showProposals),
	"hide_registerVoter" : "{}".format(registerVoter),
	"hide_startProposalRegistration" : "{}".format(startProposalRegistration),
	"hide_startVotingSession" : "{}".format(startVotingSession),
	"hide_tallyVotes" : "{}".format(tallyVotes),
	"hide_vote" : "{}".format(vote),
	"hide_winningProposalId" : "{}".format(winningProposalId),
	"hide_renounceOwnership" : "{}".format(renounceOwnership),
	"hide_transferOwnership" : "{}".format(transferOwnership),
	"hide_ownerFunctions" : "{}".format(ownerFunctions),
	"hide_voterFunctions" : "{}".format(voterFunctions),
	"workflow_msg" : "{}".format(workflow_msg),
	"owner" : "{}".format(owner),
}