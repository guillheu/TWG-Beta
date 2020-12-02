
from django.shortcuts import render
from django.http import HttpResponse
import SimpleTextStorage.web3_handler




def view(request):
	return render(request, "SimpleTextStorage.html", {"address": SimpleTextStorage.web3_handler.contract.address, "abi": SimpleTextStorage.web3_handler.contract.abi, "gasPrice": 0})



		