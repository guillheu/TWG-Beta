from brownie import accounts, Wei, TWGToken
from brownie.convert import to_bytes
from brownie.exceptions import *
import brownie
import pytest


@pytest.fixture
def contract():
    global owner
    global player1
    global player2
    global player3
    owner = accounts[0]
    player1 = accounts[1]
    player2 = accounts[2]
    player3 = accounts[3]

    global cardId1
    global cardId2
    cardId1 = "0x0003000000000000000000000000000000000000000000000000000000000000"
    cardId2 = "0x0001000000000000000000000000000000000000000000000000000000000001"

    global card1Amount
    global card2Amount
    card1Amount = 420
    card2Amount = 69

    contract = TWGToken.deploy('http://inferno.zapto.org/TWG/{id}', {'from':owner})
    return contract




def testPrintTo(contract):
    try:
        contract.printTo(player1, cardId1, card1Amount, {'from' : player1})
        assert False
    except(VirtualMachineError):
        assert True
    else:
        assert False


    accounts = [player1, player2, player3]
    tokens = [cardId1, cardId1, cardId1]
    balances = contract.balanceOfBatch(accounts, tokens)
    for balance in balances:
        assert balance == 0
    contract.printTo(owner, cardId1, card1Amount, {'from' : owner})
    assert contract.balanceOf(owner, cardId1) == card1Amount
    assert contract.balanceOf(player1, cardId1) == 0
    contract.printTo(player1, cardId2, card2Amount, {'from' : owner})
    assert contract.balanceOf(owner, cardId2) == 0
    assert contract.balanceOf(player1, cardId2) == card2Amount



