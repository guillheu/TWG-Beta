//SPDX-License-Identifier: UNLICENSED

import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC1155/ERC1155.sol";
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@3.3.0/contracts/utils/EnumerableSet.sol";   //3.3 required for enumSet of bytes32
import "OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/utils/Counters.sol";
import "./TWGMarket.sol";

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;



contract TWGGame is Ownable{

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
	
	struct Card{
		string name;
		Rarity rarity;					//Boosting a card to the next rarity might change it's name/art/description, but not its gameplay values
		bool HoF;
	}

    /*************************************
    ***********Storage variables**********
    *************************************/


	using Counters for Counters.Counter;

	uint[] assets;
	mapping (uint => Card) private _cards;

	mapping (AssetType => Counters.Counter) private _counters;

						//Currently no plans to use the booster counter, but might in the future. 
						//It would mean that the kinds of boosters that exist go beyond just rarity difference
	TWGMarket private _market;

    /*************************************
    ***************Modifiers**************
    *************************************/

    modifier cardIsHoF(uint id){
    	require(_cards[id].HoF);
    	_;
    }

    modifier cardIsNotHoF(uint id){
    	require(!_cards[id].HoF);
    	_;
    }

    modifier cardExists(uint id){
    	require(keccak256(abi.encodePacked(_cards[id].name)) != keccak256(abi.encodePacked("")));
    	_;
    }

    modifier cardDoesNotExists(uint id){
    	require(keccak256(abi.encodePacked(_cards[id].name)) == keccak256(abi.encodePacked("")));
    	_;
    }

    /*************************************
    **********Public functions************
    *************************************/

    constructor(address marketAddress) public {
    	_market = TWGMarket(marketAddress);
    }


	function getCard(uint id) public view cardExists(id) returns(Card memory){
		return _cards[id];
	}

	function getAssets() public view returns(uint[] memory){
		return assets;
	}

	function getMarketContractAddress() public view returns(address){
		return address(_market);
	}

    function setMarketContractAddress(address TWGMarketAddress) public onlyOwner{
    	_market = TWGMarket(TWGMarketAddress);    	
    }

    /*************************************
    *********onlyOwner functions**********
    *************************************/

	function addCard(string memory name, Rarity rarity) public onlyOwner returns (uint){
		uint id = createAsset(AssetType.Card, rarity);
		_cards[id] = Card(name, rarity, false);
		return id;
	}

	function hofCard(uint id) public onlyOwner cardIsNotHoF(id) cardExists(id) {
		_cards[id].HoF = true;
	}

	function unHoFCard(uint id) public onlyOwner cardIsHoF(id) cardExists(id) {
		_cards[id].HoF = false;
	}

    /*************************************
    **********Private functions***********
    *************************************/

    function createAsset(AssetType _type, Rarity rarity) private returns(uint){
    	uint id = makeAssetId(_type, rarity);
		assets.push(id);
    	_counters[_type].increment();
    	return id;
    }

    function makeAssetId(AssetType _type, Rarity rarity) private view returns(uint){
    	uint id = uint(_type) * 	0x0100000000000000000000000000000000000000000000000000000000000000;
    	id += uint(rarity) * 	0x0001000000000000000000000000000000000000000000000000000000000000;
		id += _counters[_type].current();
    	return id;
    }




}