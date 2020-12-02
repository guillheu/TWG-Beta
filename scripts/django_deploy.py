import os
import subprocess
import shutil
from .abi_translator import *

#creating django app
def djangoDeploy(name, contract):
	os.chdir("client")
	print(os.getcwd())
	if(os.path.isdir(name)):
		shutil.rmtree(name)

	else:
		subprocess.call(['./manage.py', "startapp", name])

		#updating settings.py to include newly created app in django
		f = open("client/settings.py", "r")
		contents = f.readlines()
		f.close()
		contents.insert(33, "    '{0}',\n".format(name))
		f = open("client/settings.py", "w")
		contents = "".join(contents)
		f.write(contents)
		f.close()

		#adding root url
		f = open("client/urls.py", "r")
		contents = f.readlines()
		f.close()
		contents.insert(-1, "    path('{0}/', include('{0}.urls')),\n".format(name))
		contents.insert(15, "import {0}.views\n".format(name))
		f = open("client/urls.py", "w")
		contents = "".join(contents)
		f.write(contents)
		f.close()




	#creating template folder
	os.mkdir("{0}/templates".format(name))

	#creating [CONTRACT].html
	f = open("{0}/templates/{0}.html".format(name), "w")
	f.write("<h1>{0}</h1><br><br>".format(name))
	f.write(getHTMLFields(contract.abi))
	f.close()

	#creating urls.py
	f = open("{0}/urls.py".format(name), "w")
	f.write("""
from django.contrib import admin
from django.urls import path, include
from .views import *


urlpatterns = [
	path('', view),
]
		""")
	f.close()

	#creating web3_handler.py
	f = open("{0}/web3_handler.py".format(name), "w")
	f.write("""import json
#from web3 import Web3
#now interacting with contracts using Brownie instead
from client.LoadBrownieProject import *
gasPrice = 0
contract = {1}.at("{2}")
web3URL = "http://127.0.0.1:8545"

#These functions are not used by default. They are automatically generated for your convenience
#They will allow the server to call the smart contract's functions
#Careful when using them, they WILL make you spend ETH for non view/pure transactions
#The front-end functions are defined in javascript in the ./templates/index.html file


def balance():
	return contract.balance()/10**18

""".format("TestProject", name, contract.address))

	f.write(getWeb3HandlerFunctions(contract.abi))

	f.close()

	#creating a basic view in views.py
	f = open("{0}/views.py".format(name), "w")
	f.write("""
from django.shortcuts import render
from django.http import HttpResponse
import {0}.web3_handler




def view(request):
	return render(request, "{0}.html", {{
	"address": {0}.web3_handler.contract.address,
	"abi": {0}.web3_handler.contract.abi,
	"gasPrice": {0}.web3_handler.gasPrice,
	"balance": {0}.web3_handler.contract.balance(),
	#The following attributes are used to chose whether or not to display each individual function
	#omitting them will display all the functions.
	#use them to easily pick which functions to display to the client web page by setting their value to "hidden"
	#note that it does not make the hidden functions secret, they are still visible in the html code sent to the client

{1}
}})



		""".format(name, getHiddenInViews(contract.abi)))
	f.close()

	os.chdir("..")
