
from django.shortcuts import render
from django.http import HttpResponse
import Whitelist.web3_handler




def view(request):
	return render(request, "Whitelist.html", {"address": Whitelist.web3_handler.contract.address, "abi": Whitelist.web3_handler.contract.abi, "gasPrice": 0})



		