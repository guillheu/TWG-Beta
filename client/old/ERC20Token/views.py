
from django.shortcuts import render
from django.http import HttpResponse
import ERC20Token.web3_handler




def view(request):
	return render(request, "ERC20Token.html", {"address": ERC20Token.web3_handler.contract.address, "abi": ERC20Token.web3_handler.contract.abi, "gasPrice": 0})



		