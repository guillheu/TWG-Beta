from brownie import accounts, Wei, TWGGame, TWGToken, TWGMarket
from brownie.convert import to_bytes
from brownie.exceptions import *
import brownie
import pytest

@pytest.fixture(autouse=True)
def setupVariables():
    global owner
    global player1
    global player2
    global player3
    owner = accounts[0]
    player1 = accounts[1]
    player2 = accounts[2]
    player3 = accounts[3]
    global url
    url = "http://inferno.zapto.org/TWG/{id}"

    global card1
    global card2
    card1 = {}
    card2 = {}
    global cardType
    cardType = 0

    card1['name'] = "Princess of the Sloths"
    card2['name'] = "Some thicc maiden"
    card1['id'] = "0x0003000000000000000000000000000000000000000000000000000000000000"  #: card #0 with rarity of 3 : legendary
    card2['id'] = "0x0001000000000000000000000000000000000000000000000000000000000001"  #: card #1 with rarity of 1 : rare
    card1['rarity'] = 3
    card2['rarity'] = 1
    card1['initialStock'] = 420
    card2['initialStock'] = 69
    card1['unitPriceInit'] = Wei("10 gwei")
    card2['unitPriceInit'] = Wei("10 gwei")
    card1['unitPriceMarkup'] = Wei("100 gwei")
    card2['unitPriceMarkup'] = Wei("150 gwei")
    card1['player1StoreAmount'] = 10
    card2['player1StoreAmount'] = 20


@pytest.fixture
def gameContract():
    return TWGGame.deploy(TWGMarket.deploy( TWGToken.deploy(url, {'from': owner}).address, {'from': owner}).address, {'from':owner})


def testStockCards(gameContract):
    marketContract = TWGMarket.at(gameContract.getMarketContractAddress())
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())
    #0 : Game owner designs new cards
    tx = gameContract.listNewAsset(cardType, card1['rarity'], {'from':owner})
    assert tx.return_value == card1['id']
    tx = gameContract.listNewAsset(cardType, card2['rarity'], {'from':owner})
    assert tx.return_value == card2['id']
    #1 : Game owner prints cards
    tokenContract.printTo(owner.address, card1['id'], card1['initialStock'])
    tokenContract.printTo(owner.address, card2['id'], card2['initialStock'])
    #2 : Game owner puts all the printed cards up for sale on the marketplace
    cardIds = [card1['id'], card2['id']]
    cardAmounts = [card1['initialStock'], card2['initialStock']]
    valueData = to_bytes(card1['unitPriceInit']) + to_bytes(card2['unitPriceInit']) 
    tokenContract.safeBatchTransferFrom(owner.address, marketContract.address, cardIds, cardAmounts, valueData, {'from': owner})
    #3 : Player1 purchases cards from the game owner's shop
    card1Prices = marketContract.getProductUnitPrices(card1['id'])
    card1Offers = marketContract.getProductOffers(card1['id'], card1Prices[0])
    card2PriceAndOffers = marketContract.getProductBestOffers(card2['id'])

    marketContract.purchase(card1['id'], card1Prices[0], card1Offers['sellers'][0], card1['player1StoreAmount'], {'from':player1, 'value': card1['unitPriceInit']*card1['player1StoreAmount']})
    marketContract.purchase(card2['id'], card2PriceAndOffers[0], card2PriceAndOffers[1]['sellers'][0], card2['player1StoreAmount'], {'from':player1, 'value': card2['unitPriceInit']*card2['player1StoreAmount']})

    #4 : Game owner withdraws his earnings
    marketContract.withdrawFunds({'from':owner})

    #5 : Player1 puts cards up for sale, at a markup
    #note : cardIds are the same as the previous batch transfer, cardAmounts change, so does valueData
    cardAmounts = [card1['player1StoreAmount'], card2['player1StoreAmount']]
    valueData = to_bytes(card1['unitPriceMarkup']) + to_bytes(card2['unitPriceMarkup']) 
    tokenContract.safeBatchTransferFrom(player1.address, marketContract.address, cardIds, cardAmounts, valueData, {'from': player1})

    #6 : Player2 attempts to purchase Player1's cards with insufficient funds

    card1Prices = marketContract.getProductUnitPrices(card1['id'])
    card1Offers = marketContract.getProductOffers(card1['id'], card1Prices[1])
    card2Prices = marketContract.getProductUnitPrices(card2['id'])
    card2Offers = marketContract.getProductOffers(card2['id'], card2Prices[1])

    try:
        marketContract.purchase(card1['id'], card1Prices[1], card1Offers['sellers'][0], card1['player1StoreAmount'], {'from':player2, 'value': card1['unitPriceInit']*card1['player1StoreAmount']})
        marketContract.purchase(card2['id'], card2Prices[1], card2Offers['sellers'][0], card2['player1StoreAmount'], {'from':player2, 'value': card2['unitPriceInit']*card2['player1StoreAmount']})
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False

    print(card1Prices)
    print(card1Offers)

    assert card1Prices[1] == card1['unitPriceMarkup']
    assert card1Offers['sellers'][0] == player1.address

    #7 : Player3 over-purchases Player1's card1s and gets his change back
    oldBalance = player3.balance()
    marketContract.purchase(card1['id'], card1Prices[1], card1Offers['sellers'][0], card1['player1StoreAmount'], {'from':player3, 'value': Wei("1 ether")})
    marketContract.purchase(card2['id'], card2Prices[1], card2Offers['sellers'][0], card2['player1StoreAmount'], {'from':player3, 'value': Wei("1 ether")})
    #This last assertion will likely fail if running these tests on a non-local network (where gas price > 0)
    assert player3.balance() > oldBalance - Wei("2 ether")

    #checking token balances:
    #The market contract should still own the unsold card copies, initial stock minus the amount purchased by player1
    assert tokenContract.balanceOf(marketContract, card1['id']) == card1['initialStock'] - card1['player1StoreAmount']
    assert tokenContract.balanceOf(marketContract, card2['id']) == card2['initialStock'] - card2['player1StoreAmount']
    assert tokenContract.balanceOf(owner,          card1['id']) == 0
    assert tokenContract.balanceOf(owner,          card2['id']) == 0
    assert tokenContract.balanceOf(player1,        card1['id']) == 0
    assert tokenContract.balanceOf(player1,        card2['id']) == 0
    assert tokenContract.balanceOf(player2,        card1['id']) == 0
    assert tokenContract.balanceOf(player2,        card2['id']) == 0
    assert tokenContract.balanceOf(player3,        card1['id']) == card1['player1StoreAmount']
    assert tokenContract.balanceOf(player3,        card2['id']) == card2['player1StoreAmount']


def testGetCollection(gameContract):
    marketContract = TWGMarket.at(gameContract.getMarketContractAddress())
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())

    expectedOwner = {}
    expectedOwner["ids"] = []
    expectedOwner["amounts"] = []

    assert getCollection(gameContract, player1) == expectedOwner
    gameContract.listNewAsset(cardType, card1['rarity'], {'from':owner})
    tokenContract.printTo(owner, card1['id'], card1['initialStock'], {'from':owner})
    #might wanna try .dict() or .list() ; see brownie doc for function result


    expectedOwner['ids'].append(card1['id'])
    expectedOwner['amounts'].append(card1['initialStock'])

    assert getCollection(gameContract, owner) == expectedOwner
    
    tokenContract.safeTransferFrom(owner, player1, card1['id'], card1['player1StoreAmount'], "", {'from': owner})
    expectedOwner['amounts'][0] = card1['initialStock'] - card1['player1StoreAmount']

    assert getCollection(gameContract, owner) == expectedOwner

    expectedPlayer = expectedOwner
    expectedPlayer['amounts'] = [card1['player1StoreAmount']]

    assert getCollection(gameContract, player1) == expectedPlayer



    gameContract.listNewAsset(cardType, card2['rarity'], {'from':owner})
    tokenContract.printTo(player1, card2['id'], card2['player1StoreAmount'], {'from':owner})
    expectedPlayer['ids'].append(card2['id'])
    expectedPlayer['amounts'].append(card2['player1StoreAmount'])
    assert getCollection(gameContract, player1) == expectedPlayer

def getCollection(gameContract, player):
    cards = gameContract.getAssetsList(cardType)
    tokenContract = TWGToken.at(TWGMarket.at(gameContract.getMarketContractAddress()).getTokenContractAddress())
    addresses = []
    addresses = [player.address for i in range(len(cards))]
    amounts = tokenContract.balanceOfBatch(addresses, cards)
    r = {}
    r['ids'] = cards
    r['amounts'] = amounts
    return r