
from django.shortcuts import render
from django.http import HttpResponse
import Greeter.web3_handler




def view(request):
	return render(request, "Greeter.html", {"address": Greeter.web3_handler.contract.address, "abi": Greeter.web3_handler.contract.abi, "gasPrice": Greeter.web3_handler.gasPrice, "balance": Greeter.web3_handler.contract.balance()})



		