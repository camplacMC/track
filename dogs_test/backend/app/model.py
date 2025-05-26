# model.py
import torch
import torch.nn as nn
from torchvision import models

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions



# 这个函数将模型加载到内存（在 predict.py 中调用）
def load_trained_model(path='dog_breed_best_model.pth',num_classes=120, device='cpu'):
    # 检查是否有可用的 GPU，如果有则使用 GPU，否则使用 CPU
    device = torch.device('cpu')
    # 加载模型，不加载预训练的 ImageNet 权重
    model = models.resnet50(weights=None)
    # 修改全连接层，假设分类任务有 120 个类别（可根据你的实际任务修改）
    model.fc = nn.Sequential(
        nn.Linear(2048, 512),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(512, num_classes)
    )
    # 加载模型权重到指定设备（GPU 或 CPU）
    model.load_state_dict(torch.load(path, map_location=device))
    # 将模型移动到指定的设备（GPU 或 CPU）
    model.to(device)
    # 切换到评估模式
    model.eval()
    return model
