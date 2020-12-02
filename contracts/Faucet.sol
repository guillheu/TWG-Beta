// SPDX-License-Identifier: MIT
pragma solidity 0.6.11;

contract Faucet {
   mapping (address => uint) public timeouts;
   
   function request(address addr) public returns (bool){
       require(timeouts[addr] <= block.timestamp, "Not yet ready");
       timeouts[msg.sender] = block.timestamp + 86400;
       (bool success,) = addr.call{value: 10 ether}("");
       if(!success)
       		revert();
       return success;
   }

   receive() external payable{}

}
