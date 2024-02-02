import pandas as pd
import copy
import os
import json

class Save():
    def __init__(self):
        self.save_info = ""
        self.state = 0
        self.index = 0

    def store_info(self, info):
        self.save_info = info
    
    def save_state(self, state):
        self.state = state

    def save_index(self, index):
        self.index = index

    def load_state(self):
        return self.state

    def load_index(self):
        return self.index

    def save(self, dicts):
        print(f"dicts are {dicts}")
        # a = copy.deepcopy(dicts)
        # print(f"this is: {a}")
        # print(dicts)
        df = pd.DataFrame.from_dict(dicts, orient='index')
        if not dicts:
            print("Dataframe is empty.")
            df = pd.DataFrame()
            # df.to_csv(f"Summary {save_count}.csv")
            return
        name = ['Maklumat Pemaju', 'Ringkasan Projek', 'Pembangunan Projek', 'Lokasi Projek']
        optional = ['Link', 'Website Location']

        df_optional = df[optional]
        df_optional = df_optional.reset_index()

        feature = []
        for n in name:
            # print(n)
            data = df[n].apply(pd.Series)
            data = data.reset_index()
            if n == 'Pembangunan Projek':
                data = sort_dict(data)
            # print(data)
            feature.append(data)

        # f = df['Pembangunan Projek'].apply(pd.Series)
        # print(feature[1])
        # print(feature[2])

        f = None
        for index in range(len(feature)):
            if index+1 == len(feature):
                continue
            if f is None:
                f = feature[0]
            df = feature[index+1]
            # print("1")
            merge_df = f.merge(df, on='index', how='outer')
            f = merge_df
        
        # print(df_optional)
        # merge_df = feature[1].merge(feature[2], on='index', how='outer')
        merge_df['Kod Pemajuan'] = merge_df['Kod Pemajuan'].apply(lambda x: str(x) + ',')
        merge_df = merge_df.merge(df_optional, on='index', how='outer')
        # print(merge_df)
        # print(sort_dict(f))

        # if isinstance(save_name, str):

        if not os.path.exists(self.save_info):
            os.mkdir(self.save_info)

        counter = 1
        save_file = f"{self.save_info}/Summary {self.save_info}.csv"
        file = f"Summary {self.save_info}.csv"
        while True:
            print(counter)
            if not file in os.listdir(self.save_info):
                merge_df.to_csv(save_file)
                break
            else:
                save_file = f"{self.save_info}/Summary {self.save_info} ({counter}).csv"
                file = f"Summary {self.save_info} ({counter}).csv"
                counter += 1
        return
    
# print(df)
def sort_dict(f):
    print(f)
    # To reset the index 
    f = f.reset_index(drop=True)
    # test_df = f.iloc[0,-1]
    # print(f"fsdjonvojvsn: {test_df}")
    # if not isinstance(test_df, dict): 
    #     print("is dict")     
    #     # f.to_csv("check1.csv")
    #     return f
    # print("not dict")
    # f.to_csv("check1.csv")
    # To open up the dictionary based on index (except for the "Pembangunan Project", as it is dict of dict, where now is a dict")
    f = f.melt(id_vars="index",
            var_name='1')
    # f.to_csv("check2.csv")
    # To sort the data based on index
    f = f.sort_values(by=["index"]).reset_index(drop=True)
    # print(f"3: {f}")
    # f.to_csv("check3.csv")
    f = f.dropna()
    # f.to_csv("check4.csv")
    df = f["value"].apply(pd.Series)
    # df.to_csv("check5.csv")
    # if df
    # print(f"4: {df}")
    f = pd.concat([f["index"], df], axis=1)
    # f = f.iloc[:, :-1]
    # print(f"5: {f}")
    # f = f.drop_duplicates().reset_index(drop=True)
  
    # print(f"6: {f}")
    return f


if __name__ == "__main__":
    with open('my_dict.json', 'r') as file:
        save = Save()
        loaded_dict = json.load(file)
        save.save(loaded_dict)
