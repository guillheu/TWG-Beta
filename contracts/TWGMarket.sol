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

    struct ProductOffer {
    	address seller;
    	uint amount;
    }

    /*************************************
    ***********Storage variables**********
    *************************************/

    TWGToken private _token;
    mapping (uint => mapping (uint => ProductOffer[])) private _productOffers;		//product offer for each price for each product ID
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

    

    function getProductOffers(uint id, uint price) public view returns(ProductOffer[] memory) {
    	return _productOffers[id][price];
    }

    function balanceOf(address seller) public view returns(uint){
    	return _balances[seller];
    }

    function purchase(uint id, uint unitPrice, address seller, uint amount) public payable {
    	require(amount*unitPrice <= msg.value, "not enough ETH for this purchase");
    	int offerIndex = inOffersFindOfferIndex(_productOffers[id][unitPrice], seller, amount);

    	require(offerIndex >= 0, "Seller not found for this product offer");
    	uint index = uint(offerIndex);
    	require(_productOffers[id][unitPrice][index].amount >= amount, "not enough in stock");

    	//ERC1155 transfer
    	_token.safeTransferFrom(address(this), msg.sender, id, amount, "");

    	//removing amount from offers listing
    	if(_productOffers[id][unitPrice][index].amount > amount) {
    		_productOffers[id][unitPrice][index].amount -= amount;
    	}
    	else {
    		//unlisting seller offer, since amount = 0
    		//delete _productOffers[id][unitPrice][index];
            _productOffers[id][unitPrice][index] = _productOffers[id][unitPrice][_productOffers[id][unitPrice].length -1];
            _productOffers[id][unitPrice].pop();

    		//if this was the last offer at this price
    		if(_productOffers[id][unitPrice].length == 0){
    			//unlist the price
    			_unitPrices[id][index] = _unitPrices[id][_unitPrices[id].length -1];
                _unitPrices[id].pop();
                delete _productOffers[id][unitPrice];
            }
    	}

    	if(amount*unitPrice < msg.value) {
    		(bool success, ) = msg.sender.call{value: msg.value - amount*unitPrice}("");
    	}

    	_balances[seller] += amount*unitPrice;
    }

    function withdrawFunds() public callerHasFunds {
    	uint amount = _balances[msg.sender];
    	_balances[msg.sender] = 0;
    	(bool success,) = msg.sender.call{value: amount}("");
    	if(!success)
    		revert();
    }


    //take tokens out of sale
    function withdrawTokens(uint id, uint unitPrice, uint amount) public {
        int offerIndex = inOffersFindOfferIndex(_productOffers[id][unitPrice], msg.sender, amount);

        require(offerIndex >= 0, "Offer not found");
        uint index = uint(offerIndex);
        require(_productOffers[id][unitPrice][index].amount >= amount, "not enough in stock");

        //ERC1155 transfer
        _token.safeTransferFrom(address(this), msg.sender, id, amount, "");

        //removing amount from offers listing
        if(_productOffers[id][unitPrice][index].amount > amount) {
            _productOffers[id][unitPrice][index].amount -= amount;
        }
        else {
            //unlisting seller offer, since amount = 0
            //delete _productOffers[id][unitPrice][index];
            _productOffers[id][unitPrice][index] = _productOffers[id][unitPrice][_productOffers[id][unitPrice].length -1];
            _productOffers[id][unitPrice].pop();

            //if this was the last offer at this price
            if(_productOffers[id][unitPrice].length == 0){
                //unlist the price
                _unitPrices[id][index] = _unitPrices[id][_unitPrices[id].length -1];
                _unitPrices[id].pop();
                delete _productOffers[id][unitPrice];
            }
        }
    }

    /*************************************
    *******ERC1155Receiver functions******
    *************************************/

    function onERC1155Received(address operator, address from, uint256 id, uint256 value, bytes calldata data) external override fromTokenContract returns(bytes4){
    	require(data.length == 32);

    	uint unitPrice = bytesToUint(data);

    	if(!containsPrice(id, unitPrice))
    		_unitPrices[id].push(unitPrice);

    	
    	_productOffers[id][unitPrice].push(ProductOffer(operator, value));

    	return bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"));
    }

	function onERC1155BatchReceived(address operator, address from, uint256[] calldata ids, uint256[] calldata values, bytes calldata data) external override fromTokenContract returns(bytes4){
		require(data.length == ids.length * 32);
		uint unitPrice;
		for(uint i = 0; i < ids.length; i++) {
			bytes memory bytesValue = new bytes(32);
			for(uint j = i*32; j < (i+1)*32; j++) {
        		bytesValue[j-i*32] = data[j];
	    	}
			unitPrice = bytesToUint(bytesValue);
			_productOffers[ids[i]][unitPrice].push(ProductOffer(operator, values[i]));
			_unitPrices[ids[i]].push(unitPrice);
		}
    	return bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"));
    }



    /*************************************
    ***********Utility functions**********
    *************************************/



    function containsPrice(uint id, uint price) internal view returns(bool){
    	for(uint i = 0; i < _unitPrices[id].length; i++){
    		if(_unitPrices[id][i] == price)
    			return true;
    	}
    	return false;
    }

    function inOffersFindOfferIndex(ProductOffer[] memory offers, address seller, uint amount) internal pure returns(int){
    	for(uint i = 0; i < offers.length; i++){
    		if(offers[i].seller == seller && offers[i].amount >= amount){
    			return int(i);
    		}
    	}
    	return -1;
    }

	function bytesToUint(bytes memory b) private view returns (uint256){
        uint256 number;
        for(uint i=0;i<b.length;i++){
            number += uint8(b[i])*(2**(8*(b.length-(i+1))));
        }
        return number;
    }


}