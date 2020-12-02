
from django.shortcuts import render
from django.http import HttpResponse
import SimpleStorage.web3_handler




def view(request):
	return render(request, "SimpleStorage.html", {"address": SimpleStorage.web3_handler.contract.address, "abi": SimpleStorage.web3_handler.contract.abi, "gasPrice": 0})



		