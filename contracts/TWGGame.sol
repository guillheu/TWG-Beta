//SPDX-License-Identifier: UNLICENSED

import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC1155/ERC1155.sol";
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@3.3.0/contracts/utils/EnumerableSet.sol";   //3.3 required for enumSet of bytes32
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/utils/Counters.sol";
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC1155/ERC1155Receiver.sol";
import "./TWGMarket.sol";
import "./TWGToken.sol";

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;



contract TWGGame is Ownable, ERC1155Receiver{

    /*************************************
    *****************Types****************
    *************************************/


	enum AssetType{
		Card,
		Booster,
		Pack
	}

	enum Rarity{
		Common,
		Rare,
		Epic,
		Legendary,
		Mythic,
		Unique
	}


    /*************************************
    *****************Events***************
    *************************************/

    event packOpened(address player, uint packID, uint amount, uint[] cardsInside);
    event receivedTokens(address operator, address from, uint id, uint value, bytes data);

    /*************************************
    ***********Storage variables**********
    *************************************/


	using Counters for Counters.Counter;

	mapping (AssetType => uint[]) private _assets;



						//Currently no plans to use the booster counter, but might in the future. 
						//It would mean that the kinds of boosters that exist go beyond just rarity difference
	mapping (AssetType => Counters.Counter) private _counters;


	//input = a pack ID
	//output : a weighted list of openable cards
	//the more a card shows up in the list, the more likely it is to be opened
	mapping (uint => uint[]) _packOdds;
	


	TWGMarket private _market;
	TWGToken private _token;

	uint8 openPackCode = 0xF0;

    /*************************************
    ***************Modifiers**************
    *************************************/


    modifier assetExists(AssetType _type, uint id){
    	require(containsUint(_assets[_type], id));
    	_;
    }

    modifier assetDoesNotExists(AssetType _type, uint id){
    	require(!containsUint(_assets[_type], id));
    	_;
    }

    modifier fromTokenContract{
    	require(msg.sender == address(_token));
    	_;
    }

    modifier idIsOfType(uint id, AssetType _type){
    	require(uint8(bytes32(id)[0]) == uint8(_type), "Incorrect asset type");
    	_;
    }

    /*************************************
    **********Public functions************
    *************************************/

    constructor(address marketAddress) public {
    	_market = TWGMarket(marketAddress);
    	_token = TWGToken(_market.getTokenContractAddress());
    }

	function getCards() public view returns(uint[] memory){
		return _assets[AssetType.Card];
	}

	function getBoosters() public view returns(uint[] memory){
		return _assets[AssetType.Booster];
	}

	function getPacks() public view returns(uint[] memory){
		return _assets[AssetType.Pack];
	}

	function getMarketContractAddress() public view returns(address){
		return address(_market);
	}

    function setMarketContractAddress(address TWGMarketAddress) public onlyOwner{
    	_market = TWGMarket(TWGMarketAddress);    	
    }

    function getOpenPackCode() public view returns(uint8){
    	return openPackCode;
    }


    /*************************************
    *********onlyOwner functions**********
    *************************************/

	function listNewCard(Rarity rarity) public onlyOwner returns (uint){
		uint id = createAsset(AssetType.Card, rarity);

		return id;
	}

	function makePack(Rarity rarity, uint[] calldata cards, uint[] calldata weights) public onlyOwner returns(uint) {
		require(cards.length == weights.length, "arrays must be the same length");
		uint id = createAsset(AssetType.Pack, rarity);
		_assets[AssetType.Pack].push(id);
		for(uint i = 0; i < cards.length; i++){
			for(uint j = 0; j < weights[i]; j++){
				_packOdds[id].push(cards[i]);
			}
		}
		return id;
	}


    /*************************************
    **********Private functions***********
    *************************************/

    function createAsset(AssetType _type, Rarity rarity) private returns(uint){
    	uint id = makeAssetId(_type, rarity);
		_assets[_type].push(id);
    	_counters[_type].increment();
    	return id;
    }

    function makeAssetId(AssetType _type, Rarity rarity) private view returns(uint){
    	uint id = uint(_type) * 	0x0100000000000000000000000000000000000000000000000000000000000000;
    	id += uint(rarity) * 	0x0001000000000000000000000000000000000000000000000000000000000000;
		id += _counters[_type].current();
    	return id;
    }

    function containsUint(uint[] memory table, uint seek) private pure returns (bool) {
    	for(uint i = 0; i < table.length; i++){
    		if(table[i] == seek)
    			return true;
    	}
    	return false;
    }


    				//5 = amount of cards per pack, hard-coded
    function openPack(uint id, uint nonce) private returns(uint[] memory) {
    	uint rng = uint(keccak256(abi.encodePacked(block.timestamp + id + uint(msg.sender) + nonce)));
    	uint[] memory r = new uint[](5);
    	uint length = _packOdds[id].length;
    	for(uint i = 0; i < 5; i++){
    		r[i] = _packOdds[id][rng%length];
    		rng *= rng;
    	}
    	return r;
    }


    /*************************************
    *******ERC1155Receiver functions******
    *************************************/

    function onERC1155Received(address operator, address from, uint256 id, uint256 value, bytes calldata data) external override fromTokenContract returns(bytes4){
    	if(data.length > 0){
		    if(uint8(data[0]) == openPackCode){
		    	for(uint i = 0; i < value; i++){
		    		uint[] memory cards = new uint[](5);
		    		cards = openPack(id, i);
		    		uint[] memory amounts = new uint[](5);
		    		for(uint j = 0; j < 5; j++){
		    			amounts[j] = 1;
		    		}
		    		_token.safeBatchTransferFrom(address(this), from, cards, amounts, "");
		    		emit packOpened(from, id, value, cards);
		    	}
	    	}
	    }
	    emit receivedTokens(operator, from, id, value, data);
    	return bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"));
    }

	function onERC1155BatchReceived(address operator, address from, uint256[] calldata ids, uint256[] calldata values, bytes calldata data) external override fromTokenContract returns(bytes4){

    	return bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"));
    }



}