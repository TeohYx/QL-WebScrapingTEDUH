import pandas as pd
import numpy as np
import openpyxl
import re

def clean(value):
    # print(type(value))
    cleaned = value.replace(" ", "")
    # print(cleaned)

    cleaned = re.search(r"(\d+-\d+)", cleaned)
    if cleaned:
        cleaned = cleaned.group(1)
    return cleaned

df = pd.read_excel("Code.xlsx")
# print(df)
df['Code'] = df['Code'].apply(clean)
print(df)

df_compare = df[['Code', 'Johor']]



df_compare['Johor'][6361] = '1-1'
print(df_compare)
df_compare = df_compare[~df_compare['Johor'].isin(df_compare['Code'])]
print(df_compare)