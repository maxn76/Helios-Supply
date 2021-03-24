#!/usr/bin/env python

import os
import datetime
import time
import json
import random
import requests
import websocket
from websocket import create_connection

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
        return ws
    except:
        error[0] = "Unable to connect to " + server
        
def ws_close():
    try:
        ws.close()
    except:
        error[0] = "Unable to connect to " + server
       
def id_rnd():
    idr= random.randint(1,100000000) 
    idr= '"id":'+str(idr)
    return idr

DEBUG = False
FULL_SEARCH = False

wallets = []
balances = []

print('Creating wallets list...')
ws_con()

END = False
x = 0
chain_add = "0x6BFAf995ffce7Be6e3073dC8AAf45E445cf234e2"
wallets.append(chain_add)
w_count = 0
block_num = 0
while END == False:
    ws_con()
    ws.send('{"jsonrpc": "2.0", "method": "hls_getTransactionCount", "params": [' + '"' + str(wallets[w_count]) + '"' + ' ,"latest"],'+id_rnd()+'}')
    result =  ws.recv()
    tran_count = json.loads(result)
    ws_close()
    try:
        tran_count = tran_count['result']
       
        if len(tran_count) > 0:
            
            for a in range(0, int(tran_count,0)+1):
                ws_con()    
                ws.send('{"jsonrpc": "2.0", "method": "hls_getBlockByNumber", "params": [' + '"' + str(hex(a)) + '"' + ',' + '"' + str(wallets[w_count]) + '"' + ' ,"true"],'+id_rnd()+'}')
                result =  ws.recv()
                block = json.loads(result)
    
                try:
                    len_block = len(block['result'])
               
                    if len_block > 0:
                
                        for z in range (0,len(block['result']['transactions'])):
                            to_add = block['result']['transactions'][z]['to']
                            if to_add not in wallets:
                                wallets.append(to_add)

                        if FULL_SEARCH:
                                
                            for z in range (0,len(block['result']['receiveTransactions'])):
                                to_add = block['result']['receiveTransactions'][z]['to']
                                if to_add not in wallets:
                                    wallets.append(to_add)

                            for z in range (0,len(block['result']['rewardBundle'])):
                                for r1 in range (0,len(block['result']['rewardBundle']['rewardType1'])):
                                    reward1_add = block['result']['rewardBundle']['rewardType1']
                    
                                for r2 in range (0,len(block['result']['rewardBundle']['rewardType2']['proof'])):
                                    reward2_add = block['result']['rewardBundle']['rewardType2']['proof'][r2]['recipientNodeWalletAddress']
                                    if reward2_add not in wallets:
                                        wallets.append(reward2_add)
                        
                        if DEBUG:
                            timestamp = datetime.datetime.fromtimestamp(int(block['result']['timestamp'],0))
                            block_hash = block['result']['hash']
                            block_number = int(block['result']['number'],0)
                            print('Chain: ',wallets[w_count],' - ','timestamp: ',timestamp,' - ','block number: ',block_number,' - ','block hash: ',block_hash)
                except:
                    print('Error on block', block)
  
        
    except:
        print('Error on tran_count', tran_count)

    w_count = w_count + 1
    if w_count == len(wallets):
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
    

