#from gurobipy import *
#import pandas as pd
import math
import random
import timeit
import esBlockchain as bch
import time
import numpy as np

#import numpy as np
#from numpy import genfromtxt
#import matplotlib.pyplot as plt

#blockchain = bch.blockchain("http://0.0.0.0:8000")
#blockchain.getCentralCompanyPrice(blockchain.current_epoch)
start = timeit.default_timer()
#blockchain.setPriceLevel(130)
Policy=2
b = 1
type = "master"
days = 7
random.seed(a=1)

Ite = 100
Ite_Percent = 0.8
OBJ_Value = [[0 for i in range(int(Ite_Percent * Ite))] for j in range(2)]
# No. of Customers and time periods
Num_N = 4
Num_T = 12

I = [i for i in range(Num_N)]
T = [i for i in range(Num_T)]
T2 = [i for i in range(Num_T + 1)]
T3 = [i for i in range(Num_T - 1)]
J = [i for i in range(2)]

# Maximum price for power company
UBp = 7.5
# Power demand of user i at time j
if b == 1:
    MAX_Generate = 10
    Generate_Power = 1
    rho = Generate_Power * 2

    # Generation amount for user i at time j
    G = [[0 for j in T] for i in I]

    for i in I:
        Generate_Power_Percent = random.uniform(0, MAX_Generate)
        for j in T:
            if j <= Num_T / 2:
                G[i][j] = int(100 * 10 * Generate_Power_Percent * math.exp(-(j - Num_T / 4) ** 2 / ((Num_T / 12) ** 2)))
            else:
                G[i][j] = 0

    D = [[0 for j in T] for i in I]

    Morning_Percent_LB = 0.1
    Morning_Percent_UB = 0.2

    DayTime_Percent_LB = 0.02
    DayTime_Percent_UB = 0.04

    NightTime_Percent_LB = 0.5
    NightTime_Percent_UB = 1

    MidNightTime_Percent_LB = 0.02
    MidNightTime_Percent_UB = 0.04
    Demand_Percent = 0.07
    for i in I:
        Demand_Power_Percent = random.uniform(0, Demand_Percent * MAX_Generate)
        for j in T:
            if j <= Num_T / 12:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(Morning_Percent_LB * MAX_Generate,
                                                                          Morning_Percent_UB * MAX_Generate))
            elif j > Num_T / 12 and j <= Num_T / 2:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(DayTime_Percent_LB * MAX_Generate,
                                                                          DayTime_Percent_UB * MAX_Generate))
            elif j > Num_T / 2 and j <= Num_T * 3 / 4:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(NightTime_Percent_LB * MAX_Generate,
                                                                          NightTime_Percent_UB * MAX_Generate))
            else:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(MidNightTime_Percent_LB * MAX_Generate,
                                                                          MidNightTime_Percent_UB * MAX_Generate))

if b == 2:
    MAX_Generate = 10
    Generate_Power = 1
    rho = Generate_Power * 2

    # Generation amount for user i at time j
    G = [[0 for j in T] for i in I]

    for i in I:
        Generate_Power_Percent = random.uniform(0, MAX_Generate)
        for j in T:
            if j <= Num_T / 2:
                G[i][j] = int(100 * 2 * Generate_Power_Percent * math.exp(-(j - Num_T / 4) ** 2 / ((Num_T / 12) ** 2)))
            else:
                G[i][j] = 0

    D = [[0 for j in T] for i in I]

    Morning_Percent_LB = 0.5
    Morning_Percent_UB = 1

    DayTime_Percent_LB = 2
    DayTime_Percent_UB = 4

    NightTime_Percent_LB = 0.02
    NightTime_Percent_UB = 0.04

    MidNightTime_Percent_LB = 0.02
    MidNightTime_Percent_UB = 0.04
    Demand_Percent = 0.07
    for i in I:
        Demand_Power_Percent = random.uniform(0, Demand_Percent * MAX_Generate)
        for j in T:
            if j <= Num_T / 12:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(Morning_Percent_LB * MAX_Generate,
                                                                          Morning_Percent_UB * MAX_Generate))
            elif j > Num_T / 12 and j <= Num_T / 2:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(DayTime_Percent_LB * MAX_Generate,
                                                                          DayTime_Percent_UB * MAX_Generate))
            elif j > Num_T / 2 and j <= Num_T * 3 / 4:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(NightTime_Percent_LB * MAX_Generate,
                                                                          NightTime_Percent_UB * MAX_Generate))
            else:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(MidNightTime_Percent_LB * MAX_Generate,
                                                                          MidNightTime_Percent_UB * MAX_Generate))
if b == 3:
    MAX_Generate = 10
    Generate_Power = 1
    rho = Generate_Power * 2

    # Generation amount for user i at time j
    G = [[0 for j in T] for i in I]

    for i in I:
        Generate_Power_Percent = random.uniform(0, MAX_Generate)
        for j in T:
            if j <= Num_T / 2:
                G[i][j] = int(100 * 5 * Generate_Power_Percent * math.exp(-(j - Num_T / 4) ** 2 / ((Num_T / 12) ** 2)))
            else:
                G[i][j] = 0

    D = [[0 for j in T] for i in I]

    Morning_Percent_LB = 1
    Morning_Percent_UB = 2

    DayTime_Percent_LB = 1
    DayTime_Percent_UB = 2

    NightTime_Percent_LB = 1
    NightTime_Percent_UB = 2

    MidNightTime_Percent_LB = 1
    MidNightTime_Percent_UB = 2
    Demand_Percent = 0.07
    for i in I:
        Demand_Power_Percent = random.uniform(0, Demand_Percent * MAX_Generate)
        for j in T:
            if j <= Num_T / 12:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(Morning_Percent_LB * MAX_Generate,
                                                                          Morning_Percent_UB * MAX_Generate))
            elif j > Num_T / 12 and j <= Num_T / 2:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(DayTime_Percent_LB * MAX_Generate,
                                                                          DayTime_Percent_UB * MAX_Generate))
            elif j > Num_T / 2 and j <= Num_T * 3 / 4:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(NightTime_Percent_LB * MAX_Generate,
                                                                          NightTime_Percent_UB * MAX_Generate))
            else:
                D[i][j] = int(100 * Demand_Power_Percent * random.uniform(MidNightTime_Percent_LB * MAX_Generate,
                                                                          MidNightTime_Percent_UB * MAX_Generate))

# Loss of transaction rate
Transaction_Loss = 0
Ratio = [[1 for j in I] for i in I]
for i in I:
    for j in I:
        if i != j:
            Ratio[i][j] = 1 - random.uniform(0, Transaction_Loss)

# Battery capacity of user i
Capacityi = [0 for i in I]
for i in I:
    Capacityi[i] = int(100 * random.uniform(0, random.uniform(10, 20) * MAX_Generate))

# Initial power amount left in battery from yesterday for user i
Inital_Percent = 0.1
R_0 = [0 for i in I]
for i in I:
    R_0[i] = int(random.uniform(0, Inital_Percent * Capacityi[i]))

# Customer selling pirce of user i
Customer_Sell_Price_LB = 1
Customer_Sell_Price_UB = 1.5
LB_p = [0 for i in I]
for i in I:
    LB_p[i] = int(100 * random.uniform(Customer_Sell_Price_LB, Customer_Sell_Price_UB))

# Power company selling price is Pt, and cost is Cost_c, unit profit is Pt-Cost_c
Pt = 1.2 * 100
Cost_c = 0.5 * 100

BigM = 10000
BigM1 = 100000
BigM2 = sum(Capacityi[i] for i in range(Num_N))
print("Data Generated")


print("Rest amount from yestarday is",R_0)
# print("Selling price for users is",LB_p)
# print("Battery capacity is ",Capacityi)
print("Generation amount is", G)
print("Demand amount is", D)

print("User_Sell is ", User_Sell)
print("User_Buy is", User_Buy)

end = timeit.default_timer()
print("Total Time Spend is", end - start)
