import os
import pandas as pd
import openpyxl
import numpy as np

import argparse

def merge(method, states=None):
    states = pd.read_excel("New folder/Code.xlsx")
    states = states.columns[1:]
    print(states)

    # for state in states:
    #     if not os.path.exists(state):
    #         print(f"Warning: Folder {state} is not exist")
    #         continue
    #     folder = os.listdir(state)

    if method == 0:
        files = os.listdir()
        folders = []
        # name = "kodpemajuanall"
        name = "Kod Pemajuan"
        # folders = ["Kod Pemajuan" in f for f in files]
        for f in files:
            if name in f:
                print(f)
                folders.append(f)
        print(folders)

        for folder in folders:
            data = pd.DataFrame()
            files = os.listdir(folder)
            for file in files:
                if ".csv" in file:
                    path = f"{folder}/{file}"
                    print(path)
                    info = pd.read_csv(path, index_col=0)
                    print(f"this is {info}")
                    data = pd.concat([data, info], ignore_index=True)
                    # if data.empty:
                    print(data)
            location = os.path.exists(f"{folder}/{folder}.csv")
            counter = 0
            dest = f"{folder}/{folder}.csv"
            while location:
                counter += 1
                dest = f"{folder}/{folder} ({counter}).csv"
                location = os.path.exists(dest)
            # print(location)
            data.to_csv(dest)
            data = []
    if method == 1:
        names = "kodpemajuanall"
        name = "Kod Pemajuan"

        files = os.listdir(names)
        # folders = []

        data = pd.DataFrame()
        for file in files:
            if ".csv" in file:
                path = f"{names}/{file}"
                print(path)
                info = pd.read_csv(path, index_col=0)
                print(f"this is {info}")
                data = pd.concat([data, info], ignore_index=True)
                # if data.empty:
                print(data)
        location = os.path.exists(f"{names}/{name}.csv")
        counter = 0
        dest = f"{names}/{name}.csv"
        while location:
            counter += 1
            dest = f"{names}/{name} ({counter}).csv"
            location = os.path.exists(dest)
        # print(location)
        data.to_csv(dest)
        # data = []        
        # break
                # print(p)

        # print(path)

# states = states.loc[:, ["Johor"]]

# states = states['Johor'].dropna().unique()
# print(len(states))

# check = pd.read_excel("Johor/Johor.xlsx")
# code = check.loc[:, ["Kod Pemajuan"]]
# print(len(code["Kod Pemajuan"].unique()))

def opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--method", type=int, default=0)

    return parser.parse_args()

def main():
    args = opt()
    merge(args.method)

if __name__ == "__main__":
    main()