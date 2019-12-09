#from gurobipy import *
#import pandas as pd
import math
import random
import timeit
import esBlockchain as bch
import time
#import numpy as np
#from numpy import genfromtxt
#import matplotlib.pyplot as plt

blockchain = bch.blockchain("http://10.42.0.1:8000")
blockchain.getCentralCompanyPrice(blockchain.current_epoch)
start = timeit.default_timer()
blockchain.getCurrentEpoch()
Policy=2
type = "slave"

Ite=100
Ite_Percent=0.8
OBJ_Value=[[0 for i in range(int(Ite_Percent*Ite))] for j in range(2)]



random.seed(a=2)

#No. of Customers and time periods
Num_N=4
Num_T=12

I=[i for i in range(Num_N)]
T=[i for i in range(Num_T)]
T2=[i for i in range(Num_T+1)]
T3=[i for i in range(Num_T-1)]
J=[i for i in range(2)]

#Maximum price for power company
UBp=7.5



MAX_Generate=10
Generate_Power=1
rho=Generate_Power*2

#Generation amount for user i at time j
G=[[0 for j in T] for i in I]

for i in I:
    Generate_Power_Percent=random.uniform(0,MAX_Generate)
    for j in T:
        if j<=Num_T/2:
            G[i][j]=int(100*Generate_Power_Percent*math.exp(-(j-Num_T/4)**2/((Num_T/12)**2)))
        else:
            G[i][j]=0

#     for i in I:
#         for j in T:
#             G[i][j]=random.uniform(0, random.uniform(0, Generate_Power)*MAX_Generate)

# for i in I:
#     for j in T:
#         G[i][j]=G[i][j]/10

#Power demand of user i at time j
D=[[0 for j in T] for i in I]

Morning_Percent_LB=0.1
Morning_Percent_UB=0.2

DayTime_Percent_LB=0.02
DayTime_Percent_UB=0.04

NightTime_Percent_LB=0.5
NightTime_Percent_UB=1

MidNightTime_Percent_LB=0.02
MidNightTime_Percent_UB=0.04
Demand_Percent=0.07
for i in I:
    Demand_Power_Percent=random.uniform(0,Demand_Percent*MAX_Generate)
    for j in T:
        if j<=Num_T/12:            
            D[i][j]=int(100*Demand_Power_Percent*random.uniform(Morning_Percent_LB*MAX_Generate, Morning_Percent_UB*MAX_Generate))
        elif j>Num_T/12 and j<=Num_T/2:
            D[i][j]=int(100*Demand_Power_Percent*random.uniform(DayTime_Percent_LB*MAX_Generate, DayTime_Percent_UB*MAX_Generate))
        elif j>Num_T/2 and j<=Num_T*3/4:
            D[i][j]=int(100*Demand_Power_Percent*random.uniform(NightTime_Percent_LB*MAX_Generate, NightTime_Percent_UB*MAX_Generate))
        else:
            D[i][j]=int(100*Demand_Power_Percent*random.uniform(MidNightTime_Percent_LB*MAX_Generate, MidNightTime_Percent_UB*MAX_Generate))

# for i in I:
#     for j in T:
#         D[i][j]=random.uniform(0, random.uniform(0, rho)*MAX_Generate)

#Loss of transaction rate
Transaction_Loss=0       
Ratio=[[1 for j in I] for i in I]
for i in I:
    for j in I:
        if i!=j:
            Ratio[i][j]=1-random.uniform(0, Transaction_Loss)
            
#Battery capacity of user i
Capacityi=[0 for i in I]
for i in I:
    Capacityi[i]=int(100*random.uniform(0, random.uniform(10, 20)*MAX_Generate))

#Initial power amount left in battery from yesterday for user i
Inital_Percent=0.1
R_0=[0 for i in I]
for i in I:
    R_0[i]=int(random.uniform(0,Inital_Percent*Capacityi[i]))

#Customer selling pirce of user i
Customer_Sell_Price_LB=1
Customer_Sell_Price_UB=1.5
LB_p=[0 for i in I]
for i in I:
    LB_p[i]=int(100*random.uniform(Customer_Sell_Price_LB, Customer_Sell_Price_UB))

#Power company selling price is Pt, and cost is Cost_c, unit profit is Pt-Cost_c
Pt=1.2*100
Cost_c=0.5*100



BigM=10000
BigM1=100000
BigM2=sum(Capacityi[i] for i in range(Num_N))
print("Data Generated")

#Sell and buy amount for user to push to blockchain
User_Sell=[[0 for j in T] for i in I]
User_Buy=[[0 for j in T] for i in I]

#Policy 1
if Policy==1:
    R_1=R_0
#    blockchain.getCurrentEpoch()
    for c in I:
        blockchain.setUserBalance("u1i%d" %c,"EnergyAsset",R_1[c])
        blockchain.setUserBalance("u1i%d" %c,"USDAsset", 1000000)
    Mark=[0 for i in I]
    Rest1=[[1000000  for t in T] for i in I]

    for t in T:
        for i in I:
            Rest1[i][t]=R_1[i]+G[i][t]-D[i][t]
            if Rest1[i][t]<=0:
                User_Buy[i][t]=-Rest1[i][t]
                User_Sell[i][t]=0
            elif Rest1[i][t]>=Capacityi[i]:
                User_Sell[i][t]=Rest1[i][t]-Capacityi[i]
                User_Buy[i][t]=0
        user_buy = []
        print("data for epoch %d generated" %blockchain.current_epoch)
        for i in I:
            blockchain.generateEnergy("u1i%d" %i, G[i][t])
            if User_Sell[i][t]>0:
                blockchain.openOrder("u1i%d" %i, User_Sell[i][t], LB_p[i]*User_Sell[i][t])
            else:
                user_buy.append(i)
        print("energy generated, sell orders opened")
        random.shuffle(user_buy)
        for i in user_buy:
            blockchain.buyWithMarketOrder("u1i%d" %i, User_Buy[i][t])
        print("buy orders executed")
        for i in I:
            energy_left = blockchain.getUserBalances("u1i%d" %i, blockchain.current_epoch)[1]
            if energy_left < Capacityi[i] + D[i][t]:
                blockchain.burnEnergy("u1i%d" %i, D[i][t])
                R_1[i] = energy_left - D[i][t]
            else:
                blockchain.burnEnergy("u1i%d" %i, D[i][t] + energy_left - Capacity[i])
                R_1[i] = Capacityi[i]
        print("Energy burned")
        if type == "master":
            votes = 0
            while votes < 2:
                blockchain.getNextEpochVotes()
                time.sleep(1)
            blockchain.nextEpoch()
        elif type == "slave":
            print("voting next epoch")
            blockchain.voteNextEpoch()
            print("which is %d" %blockchain.current_epoch)
            epoch = blockchain.getCurrentEpoch()
            while epoch < blockchain.current_epoch:
                time.sleep(5)
                print("wait master, his epoch is %d" %epoch)
                epoch = blockchain.getCurrentEpoch()
            print("epoch switched")
    
#Policy 2
if Policy==2:
    R_1=R_0
    for c in I:
        blockchain.setUserBalance("u1i%d" %c,"EnergyAsset", R_1[c])
        blockchain.setUserBalance("u1i%d" %c,"USDAsset", 100000000)
    Mark=[0 for i in I]
    Rest2=[[[10000 for k in T] for t in T] for i in I]
    for t in T:
        for i in I:
            for k in range(t,Num_T):
                Rest2[i][t][k]=R_1[i]+G[i][k]-D[i][k]
                if Rest2[i][t][k]<=0 and k==t:
                    User_Buy[i][t]=-Rest2[i][t][k]
                    User_Sell[i][t]=0
                    Mark[i]=1
                    break
                elif Rest2[i][t][k]>=Capacityi[i] and k==t:
                    User_Sell[i][t]=Rest2[i][t][k]-Capacityi[i]
                    User_Buy[i][t]=0
                    Mark[i]=1
                    break
                elif Rest2[i][t][k]<=0:
                    User_Buy[i][t]=0
                    User_Sell[i][t]=0
                    Mark[i]=1
                    break
                elif Rest2[i][t][k]>=Capacityi[i] and k!=t:
                    R_1[i]=Capacityi[i]
            if Mark[i]==0 and min(Rest2[i][t])>=0:
                User_Sell[i][t]=min(Rest2[i][t])
                User_Buy[i][t]=0
            elif Mark[i]==0:
                User_Sell[i][t]=0
                User_Buy[i][t]=0
        user_buy = []
        print("data for epoch %d generated" %blockchain.current_epoch)
        for i in I:
            blockchain.generateEnergy("u1i%d" %i, G[i][t])
            if User_Sell[i][t]>0:
                blockchain.openOrder("u1i%d" %i, User_Sell[i][t], LB_p[i]*User_Sell[i][t])
            else:
                user_buy.append(i)
        print("energy generated, sell orders opened")
        random.shuffle(user_buy)
        for i in user_buy:
            blockchain.buyWithMarketOrder("u1i%d" %i, User_Buy[i][t])

        print("buy orders executed")
        for i in I:
            energy_left = blockchain.getUserBalances("u1i%d" %i, blockchain.current_epoch)[1]
            if energy_left < Capacityi[i] + D[i][t]:
                blockchain.burnEnergy("u1i%d" %i, D[i][t])
                R_1[i] = energy_left - D[i][t]
            else:
                blockchain.burnEnergy("u1i%d" %i, D[i][t] + energy_left - Capacityi[i])
                R_1[i] = Capacityi[i]
        print("Energy burned")
        for i in I:
            blockchain.cancelOrder("u1i%d" %i)
        if type == "master":
            votes = 0
            while votes < 2:
                blockchain.getNextEpochVotes()
                time.sleep(1)
            blockchain.nextEpoch()
        elif type == "slave":
            print("voting next epoch")
            blockchain.voteNextEpoch()
            print("which is %d" %blockchain.current_epoch)
            epoch = blockchain.getCurrentEpoch()
            print("wait master, his epoch is %d" %epoch)
            while epoch < blockchain.current_epoch:
                time.sleep(5)
                #print("wait master, his epoch is %d" %epoch)
                epoch = blockchain.getCurrentEpoch()
            print("epoch switched")

        #--------------------------------------------------
        #Use BlockChain functions to calculate the transaction at time t
        #---------------------------------------------------------------

    #     #R_1[i]=Rest power of user i after time t

    #     for i in I:
    #         R_1[i]=#Result from blockchain
# for i in I:
#     print(sum(G[i][j] for j in T))
# print("----------------------")
# for i in I:
#     print(R_0[i]+sum(G[i][j] for j in T)-sum(D[i][j] for j in T))
# print("----------------------")

# for i in I:
#     print(sum(G[i][j] for j in T)-sum(D[i][j] for j in T))
    

    
print("Rest amount from yestarday is",R_0)
# print("Selling price for users is",LB_p)
# print("Battery capacity is ",Capacityi)
print("Generation amount is", G)
print("Demand amount is", D)

print("User_Sell is ", User_Sell)
print("User_Buy is", User_Buy)
    
end = timeit.default_timer()
print ("Total Time Spend is", end - start)
print(blockchain.transactions)
