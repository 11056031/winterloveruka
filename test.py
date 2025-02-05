"""
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("当前设备:", device)  # 应输出 "cpu"
"""
import torch
print("PyTorch 版本:", torch.__version__)
print("CUDA 是否可用:", torch.cuda.is_available())
print("設備名稱:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "無可用設備")

