import os

save_info = "Johor"
# if os.path.exists(test):
#     os.mkdir(f"{test}/Johor")
#     print(True)

if not os.path.exists(save_info):
    os.mkdir(save_info)

counter = 1
save_file = f"{save_info}/Summary {save_info}.csv"
print(os.listdir(save_info))
# while True:
#     print(counter)
#     if not save_file in os.listdir(save_info):
#         # merge_df.to_csv(save_file)
#         break
#     else:
#         save_file = f"{save_info}/Summary {save_info} ({counter}).csv"
#         counter += 1
# # return