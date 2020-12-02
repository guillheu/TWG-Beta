
from django.shortcuts import render, redirect
from django.http import HttpResponse
import Faucet.web3_handler




def view(request):
	return render(request, "Faucet.html", {"balance" : Faucet.web3_handler.balance(), "address": Faucet.web3_handler.contract.address, "abi": Faucet.web3_handler.contract.abi, "gasPrice": Faucet.web3_handler.gasPrice, "web3URL": Faucet.web3_handler.web3URL})

def request(request):
	Faucet.web3_handler.request(request.GET['address'])
	return redirect('/Faucet/')

		