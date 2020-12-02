from brownie import accounts, TWGGame, TWGToken, TWGMarket
from brownie.convert import to_bytes
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
    global card1InitialStock
    global card2InitialStock
    card1InitialStock = 420
    card2InitialStock = 69

    global card1UnitPriceInit
    global card2UnitPriceInit
    card1UnitPriceMarkup = Wei("10 gwei")
    card2UnitPriceMarkup = Wei("10 gwei")


    global player1StoreCard1Stock
    global player1StoreCard2Stock
    player1StoreCard1Stock = 10
    player1StoreCard2Stock = 20

    global card1UnitPriceMarkup
    global card2UnitPriceMarkup
    card1UnitPriceMarkup = Wei("100 gwei")
    card2UnitPriceMarkup = Wei("150 gwei")

@pytest.fixture
def gameContract():
    return TWGGame.deploy(TWGMarket.deploy( TWGToken.deploy(url, {'from': owner}).address, {'from': owner}).address, {'from':owner})


def testStockCards(gameContract):
    #1 : Game owner prints cards
    #2 : Game owner puts all the printed cards up for sale on the marketplace
    #3 : Player1 purchases cards from the game owner's shop
    #4 : Game owner withdraws his earnings
    #5 : Player1 puts cards up for sale, at a markup
    #6 : Player2 attempts to purchase Player1's cards with insufficient funds
    #7 : Player3 over-purchases Player1's card1s and gets his change back
    pass