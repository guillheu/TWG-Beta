def getWeb3HandlerFunctions(abi):
	r = ""

	for func in abi:
		if(func['type'] != 'function'):
			continue

		input = "  "
		for arg in func["inputs"]:
			input += "_" + str(arg['name']) + ", "
		input = input[:-2].strip()


		isView = False
		try:
			isView = func['stateMutability'] == 'view' or func['stateMutability'] == 'pure'
		except:
			pass
		if(isView):
			r += """def {0}({1}):
	return contract.{0}({1})
""".format(func['name'], input)


		else:
			#If we have at least one input
			input += "  "
			if(input.strip()):
				input += ", "
			r += """def {0}({2}):
	return contract.{0}({1}{{'from': accounts[0]}})
""".format(func['name'], input, input[:-2])
		r += """
"""

	return r





def getHTMLFields(abi):
	r = """{{abi|json_script:"abiScript"}}

<script type="text/javascript">


ethereum.autoRefreshOnNetworkChange = false;
abi = JSON.parse(document.getElementById("abiScript").textContent);
address = "{{address}}";
ethEnabled = false;

async function initWeb3(){
    if (window.ethereum && !window.ethEnabled) {
        const web3 = new Web3(window.ethereum);
        await window.ethereum.enable();
        window.ethEnabled = true;
		contract = web3.eth.contract(abi, address).at(address);
    }
}



"""

	#Generate JS
	for func in abi:
		if(func['type'] != 'function'):
			continue
		input = "  "
		for arg in func["inputs"]:
			input +='_' + str(arg['name']) + ", "
		input = input[:-2].strip()


		r += """

async function _{0}({1}) {{

	await initWeb3();

""".format(func['name'], input)


		#testing whether function is "view"
		isView = False
		try:
			isView = func['stateMutability'] == 'view' or func['stateMutability'] == 'pure'
		except:
			pass


		#If we have at least one input
		if(input.strip()):
			input += ", "

		if(isView):
			r += """	await contract.{0}.call({1} {{from: web3.eth.accounts[0],gasPrice: {{{{gasPrice}}}} }}, function(error , result){{""".format(func['name'], input)


		else:
			r += """	await contract.{0}.sendTransaction({1} {{from: web3.eth.accounts[0],gasPrice: {{{{gasPrice}}}} }}, function(error , result){{""".format(func['name'], input)


		r += """			if(error){{
                 document.getElementById("{0}Return").innerHTML = "there was an error";
                 console.log(error.code);
            }}
             else if(result != undefined){{
                //TODO : test this with smart contract that has a function which returns several things
                document.getElementById("{0}Return").innerHTML = result;
            }}
            else
                document.getElementById("{0}Return").innerHTML = "";

        }});
}}""".format(func["name"])

	r += "</script><br>"



	#Generate HTML
	for func in abi:
		if(func['type'] != 'function'):
			continue

		r += """
<div {{{{hide_{0} }}}}>
<h3>{0}</h3>""".format(str(func['name']))

		input = "  "
		for arg in func["inputs"]:
			input += "document.getElementById('{0}_{1}').value, ".format(str(func['name']),str(arg['name']))
			r += """{1} ({0}) : <input type="{0}" name="{2}_{1}" id="{2}_{1}"/><br>   
""".format(HTMLTypeMapping(str(arg['type'])), str(arg['name']), str(func['name']))
		r += "<br>"
		input = input[:-2].strip()

		
		r += """
<button onclick="_{0}({1});">submit</button>""".format(func['name'], input)

		r += """
<div id="{}Return"></div><br><br></div>

""".format(func['name'])

	return r


def getHiddenInViews(abi):
	r = ""
	for func in abi:
		if(func['type'] != 'function'):
			continue
		r += """	"hide_{0}" : "",
""".format(func['name'])

	return r

def HTMLTypeMapping(inputType):
	if "uint" in inputType:
		return "number"
	elif(inputType == "address" or inputType == "string"):
		return "text"