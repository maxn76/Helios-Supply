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
    ws.send('{"jsonrpc": "2.0", "method": "hls_getNewestBlocks", "params": [' + '"' + hex(nblocks) + '"' + ',' + '"' + hex(p) + '"' + ',"0x","0x",true],'+id_rnd()+'}')
    result =  ws.recv()
    block = json.loads(result)
    len_block = len(block['result'])
    if len_block > 0:
        for y in range (0,len_block):
            for z in range (0,len(block['result'][y]['transactions'])):
                to_add = block['result'][y]['transactions'][z]['to']
                if to_add not in wallets:
                    wallets.append(to_add)
                    
            for z in range (0,len(block['result'][y]['receiveTransactions'])):
                to_add = block['result'][y]['receiveTransactions'][z]['to']
                if to_add not in wallets:
                    wallets.append(to_add)

            for z in range (0,len(block['result'][y]['rewardBundle'])):
                for r1 in range (0,len(block['result'][y]['rewardBundle']['rewardType1'])):
                    reward1_add = block['result'][y]['rewardBundle']['rewardType1']
    
                for r2 in range (0,len(block['result'][y]['rewardBundle']['rewardType2']['proof'])):
                    reward2_add = block['result'][y]['rewardBundle']['rewardType2']['proof'][r2]['recipientNodeWalletAddress']
                    if reward2_add not in wallets:
                        wallets.append(reward2_add)
 
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




