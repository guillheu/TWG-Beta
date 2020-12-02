//SPDX-License-Identifier: UNLICENSED

import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC1155/ERC1155.sol";
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@3.3.0/contracts/utils/EnumerableSet.sol";   //3.3 required for enumSet of bytes32
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/utils/Counters.sol";
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC1155/ERC1155Receiver.sol";
import "./TWGToken.sol";

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;




contract TWGMarket is ERC1155Receiver, Ownable{

    /*************************************
    *****************Types****************
    *************************************/

    struct ProductOffers {
    	address[] sellers;
    	uint[] amounts;
    }

    /*************************************
    ***********Storage variables**********
    *************************************/

    TWGToken private _token;
    mapping (uint => mapping (uint => ProductOffers)) private _productOffers;		//product offer for each price for each product ID
    mapping (uint => uint[]) private _unitPrices;									//listing of all the prices for each product ID
    mapping (address => uint) private _balances;


    /*************************************
    ***************Modifiers**************
    *************************************/

    modifier fromTokenContract{
    	require(msg.sender == address(_token));
    	_;
    }

    modifier callerHasFunds{
    	require(_balances[msg.sender] > 0);
    	_;
    }

    /*************************************
    **********Public functions************
    *************************************/

    constructor(address TWGTokenAddress) public {
    	_token = TWGToken(TWGTokenAddress);
    }

    function getTokenContractAddress() public view returns(address){
    	return address(_token);
    }

    function setTokenContractAddress(address TWGTokenAddress) public onlyOwner{
    	_token = TWGToken(TWGTokenAddress);    	
    }

    function getProductUnitPrices(uint id) public view returns (uint[] memory){
    	return _unitPrices[id];
    }

    function getProductBestOffer(uint id) public view returns(uint, ProductOffers memory){
    	uint price = _unitPrices[id][0];
    	return (price, _productOffers[id][price]);
    }

    function getProductOffers(uint id, uint price) public view returns(ProductOffers memory) {
    	return _productOffers[id][price];
    }

    function balanceOf(address seller) public view returns(uint){
    	return _balances[seller];
    }

    function purchase(uint id, uint unitPrice, address seller, uint amount) public payable {
    	require(amount*unitPrice <= msg.value, "not enough ETH for this purchase");
    	uint sellerOfferIndex = inOffersFindSellerIndex(_productOffers[id][unitPrice], seller);
    	require(_productOffers[id][unitPrice].amounts[sellerOfferIndex] >= amount, "not enough in stock");

    	//ERC1155 transfer
    	_token.safeTransferFrom(address(this), msg.sender, id, amount, "");

    	//removing amount from offers listing
    	if(_productOffers[id][unitPrice].amounts[sellerOfferIndex] > amount) {
    		_productOffers[id][unitPrice].amounts[sellerOfferIndex] -= amount;
    	}
    	else {
    		//unlisting seller offer, since amount = 0
    		delete _productOffers[id][unitPrice].amounts[sellerOfferIndex];
    		delete _productOffers[id][unitPrice].sellers[sellerOfferIndex];

    		//if this was the last offer at this price
    		if(_productOffers[id][unitPrice].sellers.length == 0)
    			//unlist the price
    			delete _unitPrices[id][unitPrice];
    	}

    	if(amount*unitPrice < msg.value) {
    		(bool success, ) = msg.sender.call{value: msg.value - amount*unitPrice}("");
    	}

    	_balances[seller] += amount*unitPrice;
    }

    function withdrawFunds() public callerHasFunds {
    	uint amount = _balances[msg.sender];
    	_balances[msg.sender] = 0;
    	(bool success,) = msg.sender.call.value(amount)("");
    	if(!success)
    		revert();
    }

    /*************************************
    *******ERC1155Receiver functions******
    *************************************/

    function onERC1155Received(address operator, address from, uint256 id, uint256 value, bytes calldata data) external override fromTokenContract returns(bytes4){
    	require(data.length == 32);

    	uint unitPrice = bytesToUint(data);

    	if(!containsPrice(id, unitPrice))
    		_unitPrices[id].push(unitPrice);

    	_productOffers[id][unitPrice].sellers.push(operator);
    	_productOffers[id][unitPrice].amounts.push(value);

    	return bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"));
    }

	function onERC1155BatchReceived(address operator, address from, uint256[] calldata ids, uint256[] calldata values, bytes calldata data) external override fromTokenContract returns(bytes4){
		require(data.length == ids.length * 32);
    	return bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"));
    }

    function containsPrice(uint id, uint price) internal view returns(bool){
    	for(uint i = 0; i < _unitPrices[id].length; i++){
    		if(_unitPrices[id][i] == price)
    			return true;
    	}
    	return false;
    }

    function inOffersFindSellerIndex(ProductOffers memory offers, address seller) internal pure returns(uint){
    	for(uint i = 0; i < offers.sellers.length; i++)
    		if(offers.sellers[i] == seller)
    			return i;
    	revert("Seller not found for this product offer");
    }

	function bytesToUint(bytes memory b) private view returns (uint256){
        uint256 number;
        for(uint i=0;i<b.length;i++){
            number += uint8(b[i])*(2**(8*(b.length-(i+1))));
        }
        return number;
    }

}