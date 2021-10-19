import os
import discord
import random
import math
import numpy as np
from replit import db
from uptime import keep_alive
from discord.ext import commands
import asyncio

game = discord.Game("something, probably")
bot = commands.Bot(command_prefix = "&")

#------

#deck is a random list of 1-52
#hand is a list of lists of the form [suit,val,numval], i.e. a list of card params
hcp_dict = {"A":4,"K":3,"Q":2,"J":1}

def get_hcp(hand):
    val = 0
    for item in hand:
        val+=max(item[2]-8,0)
    return val

num_to_suit = {1:"Spade",2:"Heart",3:"Diamond",4:"Club"}
num_to_val = {12:"A",11:"K",10:"Q",9:"J",8:"T",7:"9",6:"8",5:"7",4:"6",3:"5",2:"4",1:"3",0:"2"}
sort_order = {b:a for a,b in num_to_val.items()}

class card():
    def __init__(self,num):
        suitnum = math.ceil(num/13)
        self.suit = num_to_suit[suitnum]
        self.val = num_to_val[num%13]
        self.numval = num%13


#change list of numbers into a hand "object"
def hand_read(p):
    hand = []
    for item in p:
        temp_card = card(item)
        hand.append([temp_card.suit,temp_card.val,
        temp_card.numval])
    return hand

#sort the hand after returning a hand "object"
def hand_sort(hand):
    s_list = []
    h_list = []
    d_list = []
    c_list = []
    suit_to_bins = {"Spade":s_list,"Heart":h_list,"Diamond":d_list,"Club":c_list}
    
    #sort cards by suit
    for suit,val,trash in hand:
        suit_to_bins[suit].append(val)
    hand_list = (s_list,h_list,d_list,c_list)
    
    
    #sort within suits
    for x in hand_list:
        x.sort(key = lambda x:sort_order[x], reverse = True)
    
    return hand_list
        
def deal(display = False):
    deck = list(np.arange(1,53))

    random.shuffle(deck)
    hp1 = hand_read(deck[0:13])
    hp2 = hand_read(deck[13:26])
    hp3 = hand_read(deck[26:39])
    hp4 = hand_read(deck[39:52])

    p1 = hand_sort(hp1)
    p2 = hand_sort(hp2)
    p3 = hand_sort(hp3)
    p4 = hand_sort(hp4)
    hands_dealt = [p1,p2,p3,p4]
    #suit distributions by hand
    
    dist1 = [len(p1[0]),len(p1[1]),len(p1[2]),len(p1[3])]
    dist2 = [len(p2[0]),len(p2[1]),len(p2[2]),len(p2[3])]
    dist3 = [len(p3[0]),len(p3[1]),len(p3[2]),len(p3[3])]
    dist4 = [len(p4[0]),len(p4[1]),len(p4[2]),len(p4[3])]
    dist_list = [dist1,dist2,dist3,dist4]
    
    hcp1 = get_hcp(hp1)
    hcp2 = get_hcp(hp2)
    hcp3 = get_hcp(hp3)
    hcp4 = get_hcp(hp4)
    hcp_list = [hcp1,hcp2,hcp3,hcp4]
    
    if display:
        mapping = {0:"N",1:"E",2:"S",3:"W"}
        for i,x in enumerate(hands_dealt):
            print(f"{mapping[i]}:\n")
            dh(x)
    
  
    return [hands_dealt,hcp_list,dist_list]

balanced = [[4,3,3,3],[5,3,3,2],[4,4,3,2]]

def m1():
    hands_dealt,hcp_list,dist_list = deal()
    #enum here is used to artificially map to the players
    declarer = False
    while not declarer:
        for i,hcp in enumerate(hcp_list):
            if 12<=hcp_list[i]<=21:
                if dist_list[i][0] < 5 and dist_list[i][1]<5:
                    print(dist_list)
                    declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                    n = (i+2)%4
                    partner = [hands_dealt[n],hcp_list[n],dist_list[n]]
                    print(declarer[1])
                    break
            hands_dealt,hcp_list,dist_list = deal()
                              
    return declarer,partner

def NT1():
    hands_dealt,hcp_list,dist_list = deal()
    #enum here is used to artificially map to the players
    declarer = False
    while not declarer:
        for i,hcp in enumerate(hcp_list):
            if 15<=hcp_list[i]<=17:
                if sorted(dist_list[i], reverse = True) in balanced:
                    declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                    n = (i+2)%4
                    partner = [hands_dealt[n],hcp_list[n],dist_list[n]]
                    print(declarer[1])
                    break
            hands_dealt,hcp_list,dist_list = deal()
                              
    return declarer,partner

def M1():
    hands_dealt,hcp_list,dist_list = deal()
    #enum here is used to artificially map to the players
    declarer = False
    while not declarer:
        for i,hcp in enumerate(hcp_list):
            if 12<=hcp_list[i]<=21:
                if dist_list[i][0] >= 5 or dist_list[i][1]>=5:
                    print(dist_list)
                    declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                    n = (i+2)%4
                    partner = [hands_dealt[n],hcp_list[n],dist_list[n]]
                    print(declarer[1])
                    break
            hands_dealt,hcp_list,dist_list = deal()
                              
    return declarer,partner

###DUE TO THE LINEAR NATURE OF THE SYSTEM, IT IS VERY SLIGHTLY MORE LIKELY TO GENERATE SPADE FIT HANDS

def M1ns(): #one major, no support
    hands_dealt,hcp_list,dist_list = deal()
    #enum here is used to artificially map to the players
    declarer = False
    while not declarer:
        for i,hcp in enumerate(hcp_list):
            if 12<=hcp_list[i]<=21:
                if dist_list[i][0] >= 5 or dist_list[i][1]>=5:
                    s_long = (dist_list[i][0]>=5)
                    h_long = (dist_list[i][1]>=5)
                    ##check for spade fit
                    for player,dist in enumerate(dist_list):
                      if player !=i and s_long:
                        if dist_list[player][0]<=2:
                          declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                          partner = [hands_dealt[player],hcp_list[player],dist_list[player]]
                          print(declarer[1])
                          break
                    ##check for heart fit
                    print(dist_list)
                    for player,dist in enumerate(dist_list):
                      if player !=i and h_long:
                        if dist_list[player][1]<=2:
                          declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                          partner = [hands_dealt[player],hcp_list[player],dist_list[player]]
                          print(declarer[1])
                          break

            hands_dealt,hcp_list,dist_list = deal()
                              
    return declarer,partner

def M1ts(): #one major, three support
    hands_dealt,hcp_list,dist_list = deal()
    #enum here is used to artificially map to the players
    declarer = False
    while not declarer:
        for i,hcp in enumerate(hcp_list):
            if 12<=hcp_list[i]<=21:
                if dist_list[i][0] >= 5 or dist_list[i][1]>=5:
                    s_long = (dist_list[i][0]>=5)
                    h_long = (dist_list[i][1]>=5)
                    ##check for spade fit
                    for player,dist in enumerate(dist_list):
                      if player !=i and s_long:
                        if dist_list[player][0]==3:
                          declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                          partner = [hands_dealt[player],hcp_list[player],dist_list[player]]
                          print(declarer[1])
                          break
                    ##check for heart fit
                    print(dist_list)
                    for player,dist in enumerate(dist_list):
                      if player !=i and h_long:
                        if dist_list[player][1]==3:
                          declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                          partner = [hands_dealt[player],hcp_list[player],dist_list[player]]
                          print(declarer[1])
                          break

            hands_dealt,hcp_list,dist_list = deal()
                              
    return declarer,partner    

def M1fs(): #one major, four support
    hands_dealt,hcp_list,dist_list = deal()
    #enum here is used to artificially map to the players
    declarer = False
    while not declarer:
        for i,hcp in enumerate(hcp_list):
            if 12<=hcp_list[i]<=21:
                if dist_list[i][0] >= 5 or dist_list[i][1]>=5:
                    s_long = (dist_list[i][0]>=5)
                    h_long = (dist_list[i][1]>=5)
                    ##check for spade fit
                    for player,dist in enumerate(dist_list):
                      if player !=i and s_long:
                        if dist_list[player][0]==4:
                          declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                          partner = [hands_dealt[player],hcp_list[player],dist_list[player]]
                          print(declarer[1])
                          break
                    ##check for heart fit
                    print(dist_list)
                    for player,dist in enumerate(dist_list):
                      if player !=i and h_long:
                        if dist_list[player][1]==4:
                          declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                          partner = [hands_dealt[player],hcp_list[player],dist_list[player]]
                          print(declarer[1])
                          break

            hands_dealt,hcp_list,dist_list = deal()
                              
    return declarer,partner

def M1Fs(): #one major, five support
    hands_dealt,hcp_list,dist_list = deal()
    #enum here is used to artificially map to the players
    declarer = False
    while not declarer:
        for i,hcp in enumerate(hcp_list):
            if 12<=hcp_list[i]<=21:
                if dist_list[i][0] >= 5 or dist_list[i][1]>=5:
                    s_long = (dist_list[i][0]>=5)
                    h_long = (dist_list[i][1]>=5)
                    ##check for spade fit
                    for player,dist in enumerate(dist_list):
                      if player !=i and s_long:
                        if dist_list[player][0]>=5:
                          declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                          partner = [hands_dealt[player],hcp_list[player],dist_list[player]]
                          print(declarer[1])
                          break
                    ##check for heart fit
                    print(dist_list)
                    for player,dist in enumerate(dist_list):
                      if player !=i and h_long:
                        if dist_list[player][1]>=5:
                          declarer = [hands_dealt[i],hcp_list[i],dist_list[i]]
                          partner = [hands_dealt[player],hcp_list[player],dist_list[player]]
                          print(declarer[1])
                          break

            hands_dealt,hcp_list,dist_list = deal()
                              
    return declarer,partner  
        
def dh(hand): #display hand
    flat_h = []
    for x in hand:
        flat = ""
        for y in x:
            flat+=y
        flat_h.append(flat)
   # h_content = (f"S: {flat_h[0]}\nH: {flat_h[1]}\nD: {flat_h[2]}\nC: {flat_h[3]}")
    h_content=""
    pad = random.randint(13,20)
    form = "{0: <"+str(pad)+"}"
    h_content+=form.format(f"S: {flat_h[0]}")
    h_content+="\n"

    pad = random.randint(13,20)
    form = "{0: <"+str(pad)+"}"
    h_content+=form.format(f"H: {flat_h[1]}")
    h_content+="\n"

    pad = random.randint(13,20)
    form = "{0: <"+str(pad)+"}"
    h_content+=form.format(f"D: {flat_h[2]}")
    h_content+="\n"

    pad = random.randint(13,20)
    form = "{0: <"+str(pad)+"}"
    h_content+=form.format(f"C: {flat_h[3]}")
    h_content+="\n"
    
    print(h_content)
    return h_content

#-------

#opening log
@bot.event
async def on_connect():
    print('Successfully Logged In')


@bot.event
async def on_ready():
    print('Bot ready')
    await bot.change_presence(status = discord.Status.online, activity = game)

@bot.command(name = "deal", aliases = ['d'])
async def dealcom(ctx, opener = "1NT"):
  print('deal command detected')
  if opener =="1NT":
    print("Generating 1NT hand")
    d,p = NT1()
    dec = dh(d[0])
    part = dh(p[0])
    message=f"\nDeclarer Hand:\n||{dec}||\n\nPartner Hand:\n||{part}||"
    await ctx.send(message)
  elif opener == "1M":
    print("Generating 1M hand")
    d,p = M1()
    dec = dh(d[0])
    part = dh(p[0])
    message=f"\nDeclarer Hand:\n||{dec}||\n\nPartner Hand:\n||{part}||"
    await ctx.send(message)
  elif opener == "1Mns":
    print("Generating 1M hand (no support opposite)")
    d,p = M1ns()
    dec = dh(d[0])
    part = dh(p[0])
    message=f"\nDeclarer Hand:\n||{dec}||\n\nPartner Hand:\n||{part}||"
    await ctx.send(message)
  elif opener == "1M3s":
    print("Generating 1M hand (three support opposite)")
    d,p = M1ts()
    dec = dh(d[0])
    part = dh(p[0])
    message=f"\nDeclarer Hand:\n||{dec}||\n\nPartner Hand:\n||{part}||"
    await ctx.send(message)
  elif opener == "1M4s":
    print("Generating 1M hand (four support opposite)")
    d,p = M1fs()
    dec = dh(d[0])
    part = dh(p[0])
    message=f"\nDeclarer Hand:\n||{dec}||\n\nPartner Hand:\n||{part}||"
    await ctx.send(message)
  elif opener == "1M5s":
    print("Generating 1M hand (five support opposite)")
    d,p = M1Fs()
    dec = dh(d[0])
    part = dh(p[0])
    message=f"\nDeclarer Hand:\n||{dec}||\n\nPartner Hand:\n||{part}||"
    await ctx.send(message)
  elif opener == "1m":
    print("Generating 1m hand...")
    d,p = m1()
    dec = dh(d[0])
    part = dh(p[0])
    message=f"\nDeclarer Hand:\n||{dec}||\n\nPartner Hand:\n||{part}||"
    await ctx.send(message)

keep_alive()
bot.run(os.environ['token'])