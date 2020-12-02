from brownie import *

p = project.load('../', name="TestProject")
p.load_config()
from brownie.project.TestProject import *
network.connect('development')

