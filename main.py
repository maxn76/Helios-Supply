#!/usr/bin/env python

import os
import time
import json
import random
import requests
import websocket
from websocket import create_connection
import binascii

global server
global error
error = [None] * 5

myserver = "ws://" + input('Insert the IP of the node: ')
serverport = "30304"
server = myserver+":"+serverport


def ws_con():
    global ws
    try:
        ws = create_connection(server)
        error[0] = None
    except:
        error[0] = "Unable to connect to " + server
       
def id_rnd():
    idr= random.randint(1,100000000) 
    idr= '"id":'+str(idr)
    return idr



DEBUG = True

wallets = []
balances = []

print('Creating wallets list...')
ws_con()
nblocks = 10
END = False
x = 0
while END == False:
    p = x * nblocks
    
    ws.send('{"jsonrpc": "2.0", "method": "hls_getNewestBlocks", "params": [' + '"' + str(hex(nblocks)) + '"' + ',' + '"' + str(hex(p)) + '"' + ',"0x","0x","1"],'+id_rnd()+'}')
    result =  ws.recv()
    block = json.loads(result)
    len_block = len(block['result'])
    if len_block > 0:
        for y in range (0,len_block):
            for z in range (0,len(block['result'][y]['transactions'])):
                blockHash = block['result'][y]['transactions'][z]['blockHash']
                blockNumber = block['result'][y]['transactions'][z]['blockNumber']
                from_add = block['result'][y]['transactions'][z]['from']
                to_add = block['result'][y]['transactions'][z]['to']
                if DEBUG:
                    print('blockHash:',blockHash,' blockNumber: ',blockNumber)
                if from_add not in wallets:
                    wallets.append(from_add)
                if to_add not in wallets:
                    wallets.append(to_add)
        if DEBUG:
            print(x)
        x = x + 1
    else:
        END = True
        print('wallet list completed!')

print('Calculating sum of wallet balances')

for w in range(0, len(wallets)):
    
        ws.send('{"jsonrpc": "2.0", "method": "hls_getBalance", "params": ["'+wallets[w]+'","latest"],'+id_rnd()+'}')
        result =  ws.recv()
        result = json.loads(result)
        balance = result['result']
        if balance != None:
            balance = int(balance,0)
            balance = balance
            balances.append(balance)
            if DEBUG:
                print('Wallet :', wallets[w], ' balance: ', balance/1000000000000000000)
           
   
print("HLS Circulanting Supply:", sum(balances)/1000000000000000000)




