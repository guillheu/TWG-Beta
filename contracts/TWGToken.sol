//SPDX-License-Identifier: UNLICENSED

import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC1155/ERC1155.sol";
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@3.3.0/contracts/utils/EnumerableSet.sol";   //3.3 required for enumSet of bytes32
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/utils/Counters.sol";


pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;




contract TWGToken is ERC1155, Ownable{
    /*
    contract must be ownable ; only the owner can register new players (this is done to avoid heavy botting ; players can register on our website with a verified email)
    game mustnt be pay to win ; someone who only want to play the game for fun should be able to without spending eons farming cards and levelling them up(assuming thats a feature we'll keep), or spending money on powerful cards
    game must be free to play ; each player will receive a basic set of cards and earn more cards as they play
    this contract must register a player's run through a single function call
    */

    constructor(string memory uri) public ERC1155(uri){}

    function printTo(address to, uint id, uint amount) public onlyOwner {
        _mint(to, id, amount, "");
    }


}