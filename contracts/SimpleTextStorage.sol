// SPDX-License-Identifier: MIT
pragma solidity 0.6.11;
 
contract SimpleTextStorage {
   string data;
 
   function set(string memory x) public {
       data = x;
   }
 
   function get() public view returns (string memory) {
       return data;
   }
}