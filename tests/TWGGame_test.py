from brownie import accounts, TWGGame, TWGMarket, TWGToken
from brownie.convert import to_bytes
from brownie.exceptions import *
import brownie
import pytest


@pytest.fixture(autouse=True)
def setVariables():
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

    global cardName1
    global cardName2
    cardName1 = "Princess of the Sloths"
    cardName2 = "Some thicc maiden"

    global cardId1
    global cardId2
    cardId1 = "0x0003000000000000000000000000000000000000000000000000000000000000"
    cardId2 = "0x0001000000000000000000000000000000000000000000000000000000000001"

    global cardType
    cardType = 0

    global card1Rarity
    global card2Rarity
    card1Rarity = 3
    card2Rarity = 1


    global card1Amount
    global card2Amount
    card1Amount = 420
    card2Amount = 69


@pytest.fixture()
def gameContract():
    contract = TWGGame.deploy(TWGMarket.deploy(TWGToken.deploy(url, {'from': owner}).address, {'from': owner}).address, {'from':owner})
    return contract



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
    assert len(gameContract.getAssets()) == 0


    #adding card1, we should then find it
    tx = gameContract.addCard(cardName1, card1Rarity, {"from" : owner})
    print(tx.return_value)
    #the ID automatically created should match the one pre-described
    assert tx.return_value == cardId1
    card1 = gameContract.getCard(cardId1)
    print(card1)
    assert card1['name'] == cardName1
    assert card1['rarity'] == card1Rarity
    assert card1['HoF'] == False

    #we should not find card2
    try:
        card2 = gameContract.getCard(cardId2)
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False


    #Same process for card2:
    assets = gameContract.getAssets()
    assert assets == [cardId1]


    #adding card2, we should then find it
    tx = gameContract.addCard(cardName2, card2Rarity, {"from" : owner})
    print(tx.return_value)
    #the ID automatically created should match the one pre-described
    assert tx.return_value == cardId2
    card2 = gameContract.getCard(cardId2)
    print(card2)
    assert card2['name'] == cardName2
    assert card2['rarity'] == card2Rarity
    assert card2['HoF'] == False

    assets = gameContract.getAssets()
    assert assets == [cardId1, cardId2]





def testHoF(gameContract):
    #we should not be able to HoF card1 before we add it & HoF it
    try:
        gameContract.hofCard(cardId1)
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False


    #adding card1 & 2, neither should be HoF

    gameContract.addCard(cardName1, card1Rarity, {"from" : owner})
    gameContract.addCard(cardName2, card2Rarity, {"from" : owner})

    card1 = gameContract.getCard(cardId1)
    card2 = gameContract.getCard(cardId2)
    assert not card1['HoF']

    #HoF-ing card1, it should be HoF
    gameContract.hofCard(cardId1)
    card1 = gameContract.getCard(cardId1)
    assert card1['HoF']


def testChangeMarketContract(gameContract):
    oldMarketAddress = gameContract.getMarketContractAddress()
    tokenAddress = TWGMarket.at(oldMarketAddress).getTokenContractAddress()
    newAddress = TWGMarket.deploy(tokenAddress, {'from': owner})
    gameContract.setMarketContractAddress(newAddress, {'from':owner})
    assert gameContract.getMarketContractAddress() == newAddress