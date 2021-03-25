import os
import datetime
import time
import json
import random
import requests
import websocket
from websocket import create_connection

start_time = datetime.datetime.now()

time.sleep(2)


end_time = datetime.datetime.now()

wallets = ["wallet1","wallet2","wallet3","wallet4","wallet5","wallet6"]

print('Creating wallet.dat file')
def writedata():
    data = {
            "start_time": str(start_time),
            "end_time": str(end_time),
            "circ_supply": 123432423.32321312,
            "wallets": wallets,
            }
    with open('test.json', 'w') as f:
        json.dump(data, f, sort_keys = False, indent = 4, ensure_ascii=False)

writedata()
def readdata():
    with open('test.json') as json_file:
        data = json.load(json_file)
        print(data['start_time'])
        print(data['end_time'])
        print(data['wallets'][5])
readdata()
