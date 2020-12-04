from brownie import accounts, Wei, TWGMarket, TWGToken
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


    global card1TransferAmount
    global card2TransferAmount
    card1TransferAmount = 1
    card2TransferAmount = 2

    global card1UnitPrice
    global card2UnitPrice
    card1UnitPrice = Wei("100 gwei")
    card2UnitPrice = Wei("150 gwei")

@pytest.fixture
def marketContract():
    return TWGMarket.deploy(TWGToken.deploy(url, {'from':owner}).address, {'from': owner})

def testChangeTokenContract(marketContract):
    #saving the old token contract address, generating a new token contract, changing the token contract address, checking if the change was successful
    oldTokenAddress = marketContract.getTokenContractAddress()
    newAddress = TWGToken.deploy(url, {'from': owner})
    marketContract.setTokenContractAddress(newAddress, {'from':owner})
    assert marketContract.getTokenContractAddress() == newAddress



def testERC1155Receiver(marketContract):
    #Retrieve the token contract, print some cards, transfer them to the market contract
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())
    tokenContract.printTo(owner, cardId1, card1Amount, {'from':owner})
    bytesValue = to_bytes(card1UnitPrice)
    tokenContract.safeTransferFrom(owner, marketContract.address, cardId1, card1TransferAmount, bytesValue, {'from': owner})

    assert tokenContract.balanceOf(marketContract.address, cardId1) == card1TransferAmount

    #the market contract should only accept ERC1155 transfers from the ERC1155 defined by setTokenContractAddress (or in the constructor)
    #the "fake" contract should not be able to transfer tokens to the market
    fakeTokenContract = TWGToken.deploy(url, {'from': player1})
    fakeTokenContract.printTo(player1, cardId1, card1Amount, {'from':player1})
    try:
        fakeTokenContract.safeTransferFrom(player1, marketContract.address, cardId1, card1TransferAmount, bytesValue)
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False


def testERC1155BatchReceiver(marketContract):
    card1TransferAmount = 1
    card2TransferAmount = 2

    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())
    tokenContract.printTo(owner, cardId1, card1Amount, {'from':owner})
    tokenContract.printTo(owner, cardId2, card2Amount, {'from':owner})

    bytesValue = to_bytes(card1UnitPrice) + to_bytes(card2UnitPrice)

    print(bytesValue)

    tokenContract.safeBatchTransferFrom(owner, marketContract.address, [cardId1, cardId2], [card1TransferAmount, card2TransferAmount], bytesValue, {'from': owner})

    assert tokenContract.balanceOfBatch([marketContract.address, marketContract.address], [cardId1, cardId2]) == (card1TransferAmount,card2TransferAmount)



    fakeTokenContract = TWGToken.deploy(url, {'from': player1})
    fakeTokenContract.printTo(player1, cardId1, card1Amount, {'from':player1})
    fakeTokenContract.printTo(player1, cardId2, card2Amount, {'from':player1})

    try:
        fakeTokenContract.safeBatchTransferFrom(player1, marketContract.address, [cardId1, cardId2], [card1TransferAmount, card2TransferAmount], bytesValue, {'from': player1})
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False

    prices = marketContract.getProductUnitPrices(cardId1)
    offers = marketContract.getProductOffers(cardId1, prices[0])
    assert prices[0] == card1UnitPrice
    assert offers.dict() == {'amounts': (card1TransferAmount,), "sellers": (owner.address,)}
    prices = marketContract.getProductUnitPrices(cardId2)
    offers = marketContract.getProductOffers(cardId2, prices[0])
    assert prices[0] == card2UnitPrice
    assert offers.dict() == {'amounts': (card2TransferAmount,), "sellers": (owner.address,)}


def testAddProduct(marketContract):

    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())

    #scenario
    printCards(tokenContract)
    transferCardsToMarket(marketContract, tokenContract)
    

    prices = marketContract.getProductUnitPrices(cardId1)
    print(prices)
    assert prices[0] == card1UnitPrice
    assert len(prices) == 1
    offer = marketContract.getProductOffers(cardId1, prices[0])
    expected = {'amounts': (card1TransferAmount,), "sellers": (player1.address,)}
    print(offer.dict())
    print(expected)
    assert offer.dict() == expected

    offer = marketContract.getProductBestOffers(cardId1)
    assert offer[0] == card1UnitPrice
    assert offer[1].dict() == expected



def testBalanceOf(marketContract):
    assert marketContract.balanceOf(player1.address) == marketContract.balanceOf(player2.address) == 0
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())
    printCards(tokenContract)
    transferCardsToMarket(marketContract, tokenContract)

    assert marketContract.balanceOf(player1.address) == marketContract.balanceOf(player2.address) == 0


def testBuyProduct(marketContract):
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())

    #scenario
    printCards(tokenContract)
    transferCardsToMarket(marketContract, tokenContract)

    try:
        marketContract.purchase(cardId1, card1UnitPrice, player1.address, card1TransferAmount, {'from': player2, 'value': '0'})
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False


    balanceBuyerBefore = player1.balance()
    balanceContractBefore = marketContract.balance()
    marketContract.purchase(cardId1, card1UnitPrice, player1.address, card1TransferAmount, {'from': player2, 'value': card1UnitPrice*card1TransferAmount})
    assert player2.balance() <= balanceBuyerBefore - card1UnitPrice*card1TransferAmount
    assert marketContract.balanceOf(player1.address) == card1UnitPrice*card1TransferAmount
    assert marketContract.balance() == balanceContractBefore + card1UnitPrice*card1TransferAmount
    assert tokenContract.balanceOf(player2.address, cardId1) == card1TransferAmount

def testWithdrawFunds(marketContract):
    tokenContract = TWGToken.at(marketContract.getTokenContractAddress())

    sellerBalanceBefore = player1.balance()

    #scenario
    printCards(tokenContract)
    transferCardsToMarket(marketContract, tokenContract)
    player2BuysCard1FromPlayer1(marketContract)


    marketContract.withdrawFunds({"from": player1})
    assert marketContract.balanceOf(player1.address) == 0
    assert marketContract.balance() == 0
    assert player1.balance() == sellerBalanceBefore + card1UnitPrice






#Scenario functions (not tests)

def printCards(tokenContract):
    tokenContract.printTo(player1, cardId1, card1Amount, {'from':owner})
    tokenContract.printTo(player2, cardId2, card2Amount, {'from':owner})

def transferCardsToMarket(marketContract, tokenContract):
    unitPrice = to_bytes(card1UnitPrice)
    tokenContract.safeTransferFrom(player1, marketContract.address, cardId1, card1TransferAmount, unitPrice, {'from': player1})

def player2BuysCard1FromPlayer1(marketContract):
    marketContract.purchase(cardId1, card1UnitPrice, player1.address, card1TransferAmount, {'from': player2, 'value': card1UnitPrice*card1TransferAmount})