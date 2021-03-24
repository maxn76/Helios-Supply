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

myserver = "ws://" + input('Insert the IP of the node: ')
serverport = "30304"
server = myserver+":"+serverport

DEBUG = False
FULL_SEARCH = False

def write_data():
    data = {
            "start_time": str(start_time),
            "end_time": str(end_time),
            "circ_supply":circ_supply,
            "wallets": wallets,
            }
    with open('wallets.json', 'w') as f:
        json.dump(data, f, sort_keys = False, indent = 4, ensure_ascii=False)

def read_data():
    try:
        with open('wallets.json') as json_file:
            data = json.load(json_file)
    except:
        data = None
    return data

def ws_con():
    global ws
    try:
        ws = create_connection(server)
        return ws
    except:
        print('Unable to connect to ' + server)
        
def ws_close():
    try:
        ws.close()
    except:
       print('Unable to connect to ' + server)
       
def id_rnd():
    idr= random.randint(1,100000000) 
    idr= '"id":'+str(idr)
    return idr

data = read_data()
if data != None:
    start_time = data['start_time']
    end_time = data['end_time']
    circ_supply = data['circ_supply']
    wallets = data['wallets']

    print('circulating supply at: ', end_time, ' - ', circ_supply)

    if datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(days = 10) >= datetime.datetime.now():
        print('No full sync needed!')
        FULL_SYNC = False
    else:
        print('Full sync required!')
        FULL_SYNC = True
else:
    print('Full sync required!')
    FULL_SYNC = True    

if FULL_SYNC:
    wallets = []
    print('Creating wallets list...')
    ws_con()

    END = False
    x = 0
    chain_add = "0x6BFAf995ffce7Be6e3073dC8AAf45E445cf234e2"
    wallets.append(chain_add)
    w_count = 0
    block_num = 0
    start_time = datetime.datetime.now()
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
    end_time = datetime.datetime.now()

else:
    balances = []
    print('Updating wallets list...')

    nblocks = 10
    END = False
    x = 0
    while END == False:
        ws_con()
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
                        
                if FULL_SEARCH:
                    
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
            
            if DEBUG:
                timestamp = datetime.datetime.fromtimestamp(int(block['result'][0]['timestamp'],0))
                block_hash = block['result'][0]['hash']
                block_number = int(block['result'][0]['number'],0)
                print('timestamp: ',timestamp,' - ','block number: ',block_number,' - ','block hash: ',block_hash)
            x = x + 1
            ws_close()
        
        else:
            END = True
            print('wallet list completed!')
 
print('Calculating sum of wallet balances')
balances = []
for w in range(0, len(wallets)):
        try:
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
        except:
            print('some error:',result)

end_time = datetime.datetime.now()
circ_supply = sum(balances)/1000000000000000000
print("HLS Circulanting Supply:", circ_supply)
write_data()
