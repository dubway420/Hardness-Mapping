import pandas as pd
import numpy as np
from openpyxl import Workbook

df = pd.read_csv("CCT_PM_0-2Cs-1.csv", encoding='utf-16', sep='\t', header=0)

keys = df.keys()

x = df[keys[5]].values
y = df[keys[6]].values

hardnesses = df[keys[7]].values

x_unique = np.unique(x)
y_unique = np.unique(y)

x_length = x_unique.shape[0]
y_length = y_unique.shape[0]

map = np.zeros([x_length, y_length])

for x_value in x:

    i = np.argwhere(x_unique==x_value)[0][0]
    
    # The indices of the values where x is equal to the x value in this iteration 
    x_match_ind = np.argwhere(x==x_value)

    hardness = hardnesses[x_match_ind]

    y_values = y[x_match_ind]

    for y_value, hardness_value in zip(y_values, hardness):

        j = np.argwhere(y_unique==y_value)[0][0]

        map[i, j] = hardness_value


wb = Workbook()
ws = wb.active   


first_row_list = map[0].tolist()

first_row_list.insert(0, " ")

ws.append(first_row_list)

wb.save("test.xlsx")





