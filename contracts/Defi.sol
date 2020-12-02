// SPDX-License-Identifier: MIT
pragma solidity 0.6.11;
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol";

contract Defi is Ownable{
    
    enum WorkflowStatus {
        RegisteringVoters,
        ProposalsRegistrationStarted,
        ProposalsRegistrationEnded,
        VotingSessionStarted,
        VotingSessionEnded,
        VotesTallied
    }

    struct Voter {
        bool isRegistered;
        bool hasVoted;
        uint votedProposalId;
    }

    struct Proposal {
        string description;
        uint voteCount;
    }

    event VoterRegistered(address voterAddress);
    event ProposalsRegistrationStarted();
    event ProposalsRegistrationEnded();
    event ProposalRegistered(uint proposalId);
    event VotingSessionStarted();
    event VotingSessionEnded();
    event Voted (address voter, uint proposalId);
    event VotesTallied();
    event WorkflowStatusChange(WorkflowStatus previousStatus, WorkflowStatus newStatus);

    mapping (address => Voter) public voters;
    Proposal[] public proposals;
    uint public winningProposalId;
    WorkflowStatus status = WorkflowStatus.RegisteringVoters;
    
    
    
    
    
    
    
    /**************************
    ***********Admin***********
    *********Functions*********
    **************************/
    
    function registerVoter(address _address) public onlyOwner{
        require(status == WorkflowStatus.RegisteringVoters);
        voters[_address].isRegistered = true;
        
        emit VoterRegistered(_address);
    }
    
    function tallyVotes() public onlyOwner {
        require(status == WorkflowStatus.VotingSessionEnded);
        uint currentWinnerId = 0;
        for(uint i = 1; i < proposals.length; i++){
            if(proposals[i].voteCount > proposals[currentWinnerId].voteCount){
                currentWinnerId = i;
            }
        }
        winningProposalId = currentWinnerId;
        votesTallied();
    }
    
    
    
    
    
    
    /**************************
    **********Private**********
    *********Functions*********
    **************************/
    
    
    
    function votesTallied() private {
        changeStatus(WorkflowStatus.VotesTallied);
        emit VotesTallied();
    }
        
    function changeStatus(WorkflowStatus _status) private /* Try this with the onlyOwner modifier. The question is whether an internal function call changes the msg.sender*/{
        status = _status;
        emit WorkflowStatusChange(status, _status);
    }
    
    
    /**************************
    **********Workflow*********
    *********Functions*********
    **************************/
    
    
    
    function startProposalRegistration() public onlyOwner {
        require(status == WorkflowStatus.RegisteringVoters);
        changeStatus(WorkflowStatus.ProposalsRegistrationStarted);
        emit ProposalsRegistrationStarted();
    }
    
    
    function endProposalRegistration() public onlyOwner {
        require(status == WorkflowStatus.ProposalsRegistrationStarted);
        changeStatus(WorkflowStatus.ProposalsRegistrationEnded);
        emit ProposalsRegistrationEnded();
    }
    
    function startVotingSession() public onlyOwner {
        require(status == WorkflowStatus.ProposalsRegistrationEnded);
        changeStatus(WorkflowStatus.VotingSessionStarted);
        emit VotingSessionStarted();
        
    }
    
    function endVotingSession() public onlyOwner {
        require(status == WorkflowStatus.VotingSessionStarted);
        changeStatus(WorkflowStatus.VotingSessionEnded);
        emit VotingSessionEnded();
    }
    
    
    
    
    
    
    
    
    
    /**************************
    ***********Voter***********
    *********Functions*********
    **************************/
    
    
    function offerProposal(string calldata _description) public {
        require(status == WorkflowStatus.ProposalsRegistrationStarted && voters[msg.sender].isRegistered);
        proposals.push(Proposal(_description, 0));
        emit ProposalRegistered(proposals.length);
    }
    
    function vote(uint _proposalId) public {
        require(status == WorkflowStatus.VotingSessionStarted && voters[msg.sender].isRegistered && !voters[msg.sender].hasVoted);
        voters[msg.sender].hasVoted = true;
        voters[msg.sender].votedProposalId = _proposalId;
        proposals[_proposalId].voteCount++;
        emit Voted(msg.sender, _proposalId);
    }

    function getWorkflowStatus() public view returns (string memory){
        if(status == WorkflowStatus.RegisteringVoters)
            return "RegisteringVoters";
        if(status == WorkflowStatus.ProposalsRegistrationStarted)
            return "ProposalsRegistrationStarted";
        if(status == WorkflowStatus.ProposalsRegistrationEnded)
            return "ProposalsRegistrationEnded";
        if(status == WorkflowStatus.VotingSessionStarted)
            return "VotingSessionStarted";
        if(status == WorkflowStatus.VotingSessionEnded)
            return "VotingSessionEnded";
        if(status == WorkflowStatus.VotesTallied)
            return "VotesTallied";
        
        
        
        
        
        
        
    }

    
}
