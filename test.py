import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("当前设备:", device)  # 应输出 "cpu"
