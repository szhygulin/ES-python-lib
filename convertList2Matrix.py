import pandas as pd
import ast

def tranasctions2matrices(transactions, N, T):
    matrix_E = [[ [0 for col in range(N+1)] for col in range(N+1)] for row in range(T)]
    matrix_D = [[[0 for col in range(N+1)] for col in range(N+1)] for row in range(T)]
    for x in transactions:
        t = x[0]
        if x[1] == 'centralCompany':
            i = N
        else:
            i = int(N/3) * int(x[1][1]) + int(x[1][3:])
        j = int(N/3) * int(x[2][1]) + int(x[2][3:])
        matrix_E[t][i][j] = x[3]
        matrix_D[t][i][j] = x[4]
    return matrix_E, matrix_D

transactions = []
with open('list2.txt', 'r') as f:
    for cnt, line in enumerate(f):
        mylist = ast.literal_eval(line)
        transactions.append(mylist)

matrix_E, matrix_D = tranasctions2matrices(transactions, 12, 12)
my_df = pd.DataFrame(matrix_E)
my_df.to_csv('matrix_E.csv', index=False, header=False)
my_df = pd.DataFrame(matrix_D)
my_df.to_csv('matrix_D.csv', index=False, header=False)
