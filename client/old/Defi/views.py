
from django.shortcuts import render
from django.http import HttpResponse
import Defi.web3_handler




def view(request):
	return render(request, "Defi.html", {"address": Defi.web3_handler.contract.address, "abi": Defi.web3_handler.contract.abi, "gasPrice": 0})



		