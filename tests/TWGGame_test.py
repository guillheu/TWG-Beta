from brownie import accounts, TWGGame, TWGMarket, TWGToken, Wei
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

    global pack
    pack = {}
    pack['id'] = "0x0200000000000000000000000000000000000000000000000000000000000000"
    pack['rarity'] = 0 
    pack['altId'] = "0x0200000000000000000000000000000000000000000000000000000000000001" 
    pack['name'] = "Classic card pack"
    pack['player1Amount'] = 10
    pack['player1UnpackAmount'] = 5
    pack['type'] = 2
    pack['cardAmountPerPack'] = 5
    pack['openPackCode'] = to_bytes(0xF0, 'bytes1')

    global run
    run = {}
    run['result'] = 10
    run['floorsPerPack'] = 5

@pytest.fixture
def gameContract():
    return TWGGame.deploy(TWGMarket.deploy( TWGToken.deploy(url, {'from': owner}).address, {'from': owner}).address, {'from':owner})




def testAddCard(gameContract):
    """
    1st byte = type of asset : 
        0 for card
        1 for booster
        2 for pack
    2nd byte = Rarity of the asset :
        0 for common
        1 for rare
        2 for epic
        3 for legendary
        4 for mythic
        5 for unique
    
    """
    #we should not find card1 before we add it
    assert len(gameContract.getCards()) == 0


    #adding card1, we should then find it
    tx = gameContract.listNewCard(card1['rarity'], {"from" : owner})
    #the ID automatically created should match the one pre-described
    assert tx.return_value == card1['id']
    assert gameContract.getCards()[0] == card1['id']

    #we should not find card2

    assert len(gameContract.getCards()) == 1


    #Same process for card2:


    #adding card2, we should then find it
    tx = gameContract.listNewCard(card2['rarity'], {"from" : owner})
    print(tx.return_value)
    #the ID automatically created should match the one pre-described
    assert tx.return_value == card2['id']
    cards = gameContract.getCards()
    print(cards)

    assert cards == [card1['id'], card2['id']]






def testChangeMarketContract(gameContract):
    oldMarketAddress = gameContract.getMarketContractAddress()
    tokenAddress = TWGMarket.at(oldMarketAddress).getTokenContractAddress()
    newAddress = TWGMarket.deploy(tokenAddress, {'from': owner})
    gameContract.setMarketContractAddress(newAddress, {'from':owner})
    assert gameContract.getMarketContractAddress() == newAddress

#TODO : code



def testOpenPacks(gameContract):
    marketContract = TWGMarket.at(gameContract.getMarketContractAddress())
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())

    assert pack['openPackCode'] == gameContract.getOpenPackCode()

    #We create a new pack template with its odds
    gameContract.makePack(pack["rarity"], [card1['id'], card2["id"]], [1,1])

    assert tokenContract.balanceOf(player1, pack['id']) == 0
    tokenContract.printTo(player1.address, pack['id'], pack['player1Amount'], {'from':owner})
    assert tokenContract.balanceOf(player1, pack['id']) == pack['player1Amount']

    #making sure the game contract has enough cards supply to open packs
    tx = tokenContract.printTo(gameContract.address, card1['id'], 999999999, {'from':owner})
    tokenContract.printTo(gameContract.address, card2['id'], 999999999, {'from':owner})

    print(tx.info())
    #Sending packs to the game contract will make the game contract send the cards back to the caller
    tx = tokenContract.safeTransferFrom(player1, gameContract.address, pack['id'], pack['player1UnpackAmount'], pack['openPackCode'], {'from':player1})
    #gameContract.openPacks(pack['id'], pack['player1UnpackAmount'], {'from':player1})
    print(tx.info())

    #Might wanna recode those using getCollection and adding up all the card amounts
    assert tokenContract.balanceOf(player1, pack['id']) == pack['player1Amount'] - pack['player1UnpackAmount']
    assert tokenContract.balanceOf(gameContract.address, pack['id']) == pack['player1UnpackAmount']
    assert tokenContract.balanceOf(player1, card1['id']) + tokenContract.balanceOf(player1, card2['id']) == pack['cardAmountPerPack'] * pack['player1UnpackAmount']

def IGNOREtestGetAssetsList(gameContract):
    marketContract = TWGMarket.at(gameContract.getMarketContractAddress())
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())
    gameContract.list(pack['type'], pack["id"], {'from':owner})
    gameContract.list(pack['type'], pack["altId"], {'from':owner})
    assert gameContract.getAssetsList(pack['type']) == [pack['id'], pack['altId']]
    gameContract.list(cardType, card1["id"], {'from':owner})
    gameContract.list(cardType, card1["id"], {'from':owner})
    assert gameContract.getAssetsList(cardType) == [card1['id'], cardZ['id']]

def IGNOREtestRun(gameContract):
    marketContract = TWGMarket.at(gameContract.getMarketContractAddress())
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())

    #run function should reward the player based on the listed card packs, and pick one type at random
    gameContract.run(player1.address, run['result'], {'from':owner})
    assert tokenContract.balanceOf(player1, pack['id'])


