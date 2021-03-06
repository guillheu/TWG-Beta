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
    uint8 boostCardsCode = 0xF1;
	uint8 floorsForAPack = 5;

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

	function getMarketContractAddress() public view returns(address){
		return address(_market);
	}

    function setMarketContractAddress(address TWGMarketAddress) public onlyOwner{
    	_market = TWGMarket(TWGMarketAddress);    	
    }

    function getOpenPackCode() public view returns(uint8){
    	return openPackCode;
    }

    function getBoostCardsCode() public view returns(uint8){
        return boostCardsCode;
    }

    function getAssetsList(AssetType _type) public view returns (uint[] memory) {
    	return _assets[_type];
    }


    /*************************************
    *********onlyOwner functions**********
    *************************************/

	function listNewAsset(AssetType _type, Rarity rarity) public onlyOwner returns (uint){
		uint id = createAsset(_type, rarity);
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

	function run(address player, uint floors) public onlyOwner {
		uint packRewardId = _assets[AssetType.Pack][0];
		uint amount = floors/floorsForAPack;
		_token.safeTransferFrom(address(this), player, packRewardId, amount, "");
	}


    function listAssetRarityVariant(uint id, Rarity newRarity) public onlyOwner returns(uint) {
        uint finalId = generateAssetRarityVariant(id, newRarity);
        AssetType _type = getTypeFromId(id);
        require(!containsUint(_assets[_type], finalId));
        _assets[_type].push(finalId);
        return finalId;
    }
    /*************************************
    **********Private functions***********
    *************************************/

    function generateAssetRarityVariant(uint id, Rarity newRarity) private view returns(uint) {
        AssetType _type = getTypeFromId(id);
        bytes memory idBytes = abi.encodePacked(id);
        idBytes[0] = 0x00;
        idBytes[1] = 0x00;
        id = bytesToUint(idBytes);
        uint finalId = makeAssetId(_type, newRarity, id);

        return finalId;
    }

    function createAsset(AssetType _type, Rarity rarity) private returns(uint){
    	uint id = makeAssetId(_type, rarity, _counters[_type].current());
		_assets[_type].push(id);
    	_counters[_type].increment();
    	return id;
    }

    function makeAssetId(AssetType _type, Rarity rarity, uint uniqueID) private view returns(uint){
    	uint id = uint(_type) * 	0x0100000000000000000000000000000000000000000000000000000000000000;
    	id += uint(rarity) * 	0x0001000000000000000000000000000000000000000000000000000000000000;
		id += uniqueID;
    	return id;
    }

    function containsUint(uint[] memory table, uint seek) private pure returns (bool) {
    	for(uint i = 0; i < table.length; i++){
    		if(table[i] == seek){
    			return true;
    		}
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

	function bytesToUint(bytes memory b) private pure returns (uint256){
        uint256 number;
        for(uint i=0;i<b.length;i++){
            number = number + uint8(b[i])*(2**(8*(b.length-(i+1))));
        }
        return number;
    }

    function onReceiveCheckDataCode(address operator, address from, uint256[] memory ids, uint256[] memory values, bytes calldata data) private {
        if(uint8(data[0]) == openPackCode){
            for(uint h = 0; h < values.length; h++){
                for(uint i = 0; i < values[h]; i++){
                    uint[] memory cards = new uint[](5);
                    cards = openPack(ids[h], i);
                    uint[] memory amounts = new uint[](5);
                    for(uint j = 0; j < 5; j++){
                        amounts[j] = 1;
                    }
                    _token.safeBatchTransferFrom(address(this), from, cards, amounts, "");
                    emit packOpened(from, ids[h], values[h], cards);
                }
            }
        }
        else if(uint8(data[0]) == boostCardsCode){
            require(ids.length % 2 == 0, "Should send as many card transfers as boosters'");
            uint[] memory boostedCards = new uint[](ids.length/2);
            uint[] memory amounts = new uint[](values.length/2);
            for(uint i = 0; i < ids.length/2; i++){
                require(values[i] == values[i + values.length/2], "need as many cards as boosters");
                require(getTypeFromId(ids[i]) == AssetType.Card, "first half of transfers must be cards");
                require(getTypeFromId(ids[i + ids.length/2]) == AssetType.Booster, "second half of transfers must be boosters");
                require(uint8(getRarityFromId(ids[i])) == uint8(getRarityFromId(ids[i+ids.length/2]))-1, "booster rarity must be one tier higher than card's");
                boostedCards[i] = generateAssetRarityVariant(ids[i], getRarityFromId(ids[i+ids.length/2]));
                amounts[i] = values[i];
            }
            _token.safeBatchTransferFrom(address(this), from, boostedCards, amounts, "");
        }
    }


    function getTypeFromId(uint id) private pure returns(AssetType) {
        bytes memory idBytes = abi.encodePacked(id);
        AssetType _type;
        if(idBytes[0] == 0x00)
            _type = AssetType.Card;
        if(idBytes[0] == 0x01)
            _type = AssetType.Booster;
        if(idBytes[0] == 0x02)
            _type = AssetType.Pack;
        return _type;
    }

    function getRarityFromId(uint id) private pure returns(Rarity) {
        bytes memory idBytes = abi.encodePacked(id);
        Rarity rarity;
        if(idBytes[1] == 0x00)
            rarity = Rarity.Common;
        if(idBytes[1] == 0x01)
            rarity = Rarity.Rare;
        if(idBytes[1] == 0x02)
            rarity = Rarity.Epic;
        if(idBytes[1] == 0x03)
            rarity = Rarity.Legendary;
        if(idBytes[1] == 0x04)
            rarity = Rarity.Mythic;
        if(idBytes[1] == 0x05)
            rarity = Rarity.Unique;
        return rarity;
    }

    /*************************************
    *******ERC1155Receiver functions******
    *************************************/

    function onERC1155Received(address operator, address from, uint256 id, uint256 value, bytes calldata data) external override fromTokenContract returns(bytes4){
    	if(data.length > 0){
            uint256[] memory ids = new uint256[](1);
            ids[0] = id;
            uint256[] memory values = new uint256[](1);
            values[0] = value;
            onReceiveCheckDataCode(operator, from, ids, values, data);
	    }
	    emit receivedTokens(operator, from, id, value, data);
    	return bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"));
    }

	function onERC1155BatchReceived(address operator, address from, uint256[] calldata ids, uint256[] calldata values, bytes calldata data) external override fromTokenContract returns(bytes4){

        if(data.length > 0){
            onReceiveCheckDataCode(operator, from, ids, values, data);
        }
    	return bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"));
    }



}