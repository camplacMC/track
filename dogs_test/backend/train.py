import os
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.amp import autocast, GradScaler
from tqdm import tqdm

# 获取 ResNet50 模型
def get_net(devices, num_classes=120):
    weights = ResNet50_Weights.DEFAULT
    model = resnet50(weights=weights)

    # 冻结除最后一层之外的参数
    for name, param in model.named_parameters():
        if "layer4" not in name and "fc" not in name:
            param.requires_grad = False

    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(512, num_classes)
    )
    return model.to(devices[0])

# 解冻前一层
def unfreeze_previous_layer(net, current_unfrozen):
    layer_names = ['layer3', 'layer2', 'layer1', 'conv1']
    if current_unfrozen < len(layer_names):
        name_to_unfreeze = layer_names[current_unfrozen]
        for name, param in net.named_parameters():
            if name.startswith(name_to_unfreeze):
                param.requires_grad = True
        print(f"🔓 Unfroze {name_to_unfreeze}")
        return current_unfrozen + 1
    return current_unfrozen

# 评估模型准确率
def evaluate_accuracy(data_iter, net, device):
    net.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for X, y in data_iter:
            X, y = X.to(device), y.to(device)
            outputs = net(X)
            _, predicted = torch.max(outputs, 1)
            total += y.size(0)
            correct += (predicted == y).sum().item()
    return correct / total

# 训练模型
def train(net, train_iter, valid_iter, num_epochs, lr, weight_decay, devices,
          save_path, patience=5, early_stop_threshold=0.98):
    net = net.to(devices[0])
    loss_fn = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, net.parameters()), lr=lr, weight_decay=weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=num_epochs)
    scaler = GradScaler()

    best_acc = 0.0
    epochs_without_improvement = 0
    current_unfrozen = 0

    for epoch in range(num_epochs):
        net.train()
        total_loss = 0.0
        for X, y in tqdm(train_iter, desc=f"Epoch {epoch+1}/{num_epochs}"):
            X, y = X.to(devices[0]), y.to(devices[0])
            optimizer.zero_grad()
            with autocast('cuda'):
                y_hat = net(X)
                loss = loss_fn(y_hat, y)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            total_loss += loss.item()

        train_acc = evaluate_accuracy(train_iter, net, devices[0])
        val_acc = evaluate_accuracy(valid_iter, net, devices[0])

        tqdm.write(f"Epoch {epoch+1}, Loss: {total_loss:.4f}, Train Acc: {train_acc:.4f}, Val Acc: {val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(net.state_dict(), save_path)
            tqdm.write(f"✅ Saved best model to {save_path} (accuracy: {best_acc:.4f})")
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= patience:
            current_unfrozen = unfreeze_previous_layer(net, current_unfrozen)
            optimizer = optim.AdamW(filter(lambda p: p.requires_grad, net.parameters()), lr=lr, weight_decay=weight_decay)
            tqdm.write(f"🔁 Reconfigured optimizer after unfreezing.")
            epochs_without_improvement = 0

        if best_acc >= early_stop_threshold:
            tqdm.write(f"⏹ Early stopping triggered at accuracy {best_acc:.4f}")
            break

        scheduler.step()

# 主函数
if __name__ == "__main__":
    num_epochs = 600
    learning_rate = 1e-3
    weight_decay = 1e-4
    batch_size = 128
    num_classes = 120
    MODEL_PATH = 'dog_breed_best_model.pth'
    patience = 5
    early_stop_threshold = 0.98

    devices = [torch.device(f"cuda:{i}") for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else [torch.device("cpu")]
    print(f"Using devices: {devices}")

    data_dir = '../dog_breed_sorted'
    train_dir = os.path.join(data_dir, 'train')
    valid_dir = os.path.join(data_dir, 'valid')

    transform_train = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.08, 1.0), ratio=(3.0 / 4.0, 4.0 / 3.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    transform_valid = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_dataset = torchvision.datasets.ImageFolder(train_dir, transform=transform_train)
    valid_dataset = torchvision.datasets.ImageFolder(valid_dir, transform=transform_valid)

    train_iter = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    valid_iter = DataLoader(valid_dataset, batch_size=batch_size, shuffle=False, num_workers=4)

    net = get_net(devices, num_classes)
    train(net, train_iter, valid_iter, num_epochs, learning_rate, weight_decay,
          devices, MODEL_PATH, patience, early_stop_threshold)
