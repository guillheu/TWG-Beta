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
    global card1Upgrade
    card1 = {}
    card2 = {}
    card1Upgrade = {}
    global cardType
    cardType = 0

    card1['name'] = "Princess of the Sloths"
    card2['name'] = "Some thicc maiden"
    card1['id'] = 0x0000000000000000000000000000000000000000000000000000000000000000  #: card #0 with rarity of 0 : common
    card1['idUpgrade1'] = 0x0001000000000000000000000000000000000000000000000000000000000000
    card1['idUpgrade2'] = 0x0002000000000000000000000000000000000000000000000000000000000000
    card1['idUpgrade3'] = 0x0003000000000000000000000000000000000000000000000000000000000000
    card1['boostAmount'] = 10
    card2['id'] = 0x0001000000000000000000000000000000000000000000000000000000000001  #: card #1 with rarity of 1 : rare
    card1['rarity'] = 0
    card2['rarity'] = 1
    card1['initialStock'] = 420
    card2['initialStock'] = 69
    card1['unitPriceInit'] = Wei("10 gwei")
    card2['unitPriceInit'] = Wei("10 gwei")
    card1['unitPriceMarkup'] = Wei("100 gwei")
    card2['unitPriceMarkup'] = Wei("150 gwei")
    card1['player1StoreAmount'] = 10
    card2['player1StoreAmount'] = 20

    card1Upgrade['rarity'] = 4
    card1Upgrade['id'] = 0x0004000000000000000000000000000000000000000000000000000000000000

    global pack
    pack = {}
    pack['id'] = 0x0200000000000000000000000000000000000000000000000000000000000000
    pack['rarity'] = 0 
    pack['altId'] = 0x0200000000000000000000000000000000000000000000000000000000000001
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


    global boosterType
    global boosterRare
    global boosterEpic
    global boosterLegendary
    global boostCardsCode
    boosterType = 1
    boosterRare = {}
    boosterRare['rarity'] = 1
    boosterRare['id'] = 0x0101000000000000000000000000000000000000000000000000000000000000
    boosterEpic = {}
    boosterEpic['rarity'] = 2
    boosterEpic['id'] = 0x0102000000000000000000000000000000000000000000000000000000000000
    boosterLegendary = {}
    boosterLegendary['rarity'] = 3
    boosterLegendary['id'] = 0x0103000000000000000000000000000000000000000000000000000000000000
    boostCardsCode = to_bytes(0xF1, 'bytes1')

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
    assert len(gameContract.getAssetsList(cardType)) == 0


    #adding card1, we should then find it
    tx = gameContract.listNewAsset(cardType, card1['rarity'], {"from" : owner})
    #the ID automatically created should match the one pre-described
    assert tx.return_value == card1['id']
    assert gameContract.getAssetsList(cardType)[0] == card1['id']

    #we should not find card2

    assert len(gameContract.getAssetsList(cardType)) == 1


    #Same process for card2:


    #adding card2, we should then find it
    tx = gameContract.listNewAsset(cardType, card2['rarity'], {"from" : owner})
    print(tx.return_value)
    #the ID automatically created should match the one pre-described
    assert tx.return_value == card2['id']
    cards = gameContract.getAssetsList(cardType)
    print(cards)

    assert cards == [card1['id'], card2['id']]






def testChangeMarketContract(gameContract):
    oldMarketAddress = gameContract.getMarketContractAddress()
    tokenAddress = TWGMarket.at(oldMarketAddress).getTokenContractAddress()
    newAddress = TWGMarket.deploy(tokenAddress, {'from': owner})
    gameContract.setMarketContractAddress(newAddress, {'from':owner})
    assert gameContract.getMarketContractAddress() == newAddress





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


def testRun(gameContract):
    marketContract = TWGMarket.at(gameContract.getMarketContractAddress())
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())

    #listing packs, then printing packs to game contract
    packId = gameContract.listNewAsset(pack["type"], pack['rarity'], {'from': owner})
    tokenContract.printTo(gameContract.address, packId.return_value, 999999999, {'from':owner})

    #run function should reward the player based on the listed card packs, and pick one type at random
    gameContract.run(player1.address, run['result'], {'from':owner})
    assert tokenContract.balanceOf(player1, pack['id']) >= int(run['result']/run['floorsPerPack'])

def testGenerateCardRarityVariant(gameContract):
    marketContract = TWGMarket.at(gameContract.getMarketContractAddress())
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())

    card1Id = gameContract.listNewAsset(cardType, card1['rarity'], {'from': owner}).return_value
    print(hex(card1Id))
    print(hex(card1['id']))
    gameContract.listAssetRarityVariant(card1Id, card1Upgrade['rarity'])

    cards = gameContract.getAssetsList(cardType)
    assert gameContract.getAssetsList(cardType) == [card1['id'], card1Upgrade['id']]


    try:
        gameContract.listAssetRarityVariant(card1Id, card1Upgrade['rarity'])
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False


def testBoostCard(gameContract):
    marketContract = TWGMarket.at(gameContract.getMarketContractAddress())
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())
    card1Id = gameContract.listNewAsset(cardType, card1['rarity'], {'from': owner}).return_value
    card1IdRare = gameContract.listNewAsset(cardType, boosterRare['rarity'], {'from': owner}).return_value
    card1IdEpic = gameContract.listNewAsset(cardType, boosterEpic['rarity'], {'from': owner}).return_value
    card1IdLegendary = gameContract.listNewAsset(cardType, boosterLegendary['rarity'], {'from': owner}).return_value

    boosterRareId = gameContract.listNewAsset(boosterType, boosterRare['rarity'], {'from': owner}).return_value
    boosterEpicId = gameContract.listAssetRarityVariant(boosterRareId, boosterEpic["rarity"]).return_value
    boosterLegendaryId = gameContract.listAssetRarityVariant(boosterEpicId, boosterLegendary["rarity"]).return_value
    assert boosterRareId == boosterRare['id']
    assert boosterEpicId == boosterEpic['id']
    assert boosterLegendaryId == boosterLegendary['id']
    assert gameContract.getBoostCardsCode() == boostCardsCode

    tokenContract.printTo(player1, card1['id'], card1['initialStock'], {'from': owner})
    tokenContract.printTo(player1, boosterRare['id'], card1['boostAmount'], {'from': owner})
    tokenContract.printTo(player1, boosterEpic['id'], card1['boostAmount'], {'from': owner})
    tokenContract.printTo(player1, boosterLegendary['id'], card1['boostAmount'], {'from': owner})
    tokenContract.printTo(gameContract, card1['idUpgrade1'], 9999999, {'from': owner})
    tokenContract.printTo(gameContract, card1['idUpgrade2'], 9999999, {'from': owner})
    tokenContract.printTo(gameContract, card1['idUpgrade3'], 9999999, {'from': owner})


    tokenContract.safeBatchTransferFrom(player1, gameContract.address, [card1['id'], boosterRare["id"]], [card1['boostAmount'], card1['boostAmount']], boostCardsCode, {'from':player1})
    assert tokenContract.balanceOf(player1, card1['id']) == card1['initialStock'] - card1['boostAmount']
    assert tokenContract.balanceOf(player1, card1['idUpgrade1']) == card1['boostAmount']
    assert tokenContract.balanceOf(player1, card1['idUpgrade2']) == 0
    assert tokenContract.balanceOf(player1, card1['idUpgrade3']) == 0

    try:
        tokenContract.safeBatchTransferFrom(player1, gameContract.address, [card1['id'], boosterRare["id"]], [card1['boostAmount'], card1['boostAmount']], boostCardsCode, {'from':player1})
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False


    tokenContract.safeBatchTransferFrom(player1, gameContract.address, [card1['idUpgrade1'], boosterEpic["id"]], [card1['boostAmount'], card1['boostAmount']], boostCardsCode, {'from':player1})
    assert tokenContract.balanceOf(player1, card1['id']) == card1['initialStock'] - card1['boostAmount']
    assert tokenContract.balanceOf(player1, card1['idUpgrade1']) == 0
    assert tokenContract.balanceOf(player1, card1['idUpgrade2']) == card1['boostAmount']
    assert tokenContract.balanceOf(player1, card1['idUpgrade3']) == 0

    try:
        tokenContract.safeBatchTransferFrom(player1, gameContract.address, [card1['idUpgrade1'], boosterEpic["id"]], [card1['boostAmount'], card1['boostAmount']], boostCardsCode, {'from':player1})
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False

    tokenContract.safeBatchTransferFrom(player1, gameContract.address, [card1['idUpgrade2'], boosterLegendary["id"]], [card1['boostAmount'], card1['boostAmount']], boostCardsCode, {'from':player1})
    assert tokenContract.balanceOf(player1, card1['id']) == card1['initialStock'] - card1['boostAmount']
    assert tokenContract.balanceOf(player1, card1['idUpgrade1']) == 0
    assert tokenContract.balanceOf(player1, card1['idUpgrade2']) == 0
    assert tokenContract.balanceOf(player1, card1['idUpgrade3']) == card1['boostAmount']

    try:
        tokenContract.safeBatchTransferFrom(player1, gameContract.address, [card1['idUpgrade2'], boosterLegendary["id"]], [card1['boostAmount'], card1['boostAmount']], boostCardsCode, {'from':player1})
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False


    try:
        tokenContract.safeBatchTransferFrom(player1, gameContract.address, [card1['idUpgrade3'], boosterLegendary["id"]], [card1['boostAmount'], card1['boostAmount']], boostCardsCode, {'from':player1})
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False