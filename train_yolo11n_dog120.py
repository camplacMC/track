import torch
from ultralytics import YOLO


# 确保训练代码在 `if __name__ == '__main__':` 语句块中
if __name__ == '__main__':
    # 加载预训练的模型
    model = YOLO('yolo11n.pt')

    # 设置训练数据集路径和配置文件
    data_path = 'dog120.yaml'  # 数据集配置文件路径
    epochs = 120  # 设置训练轮数
    imgsz = 640  # 设置图像尺寸
    batch_size = 16  # 设置批量大小
    device = 0  # 使用GPU，如果没有GPU，设置为 -1 以使用CPU
    workers = 4  # 设置数据加载时使用的工作线程数
    save_dir = 'runs/train'  # 保存训练模型的目录

    try:
        print(f"开始训练，数据集配置文件: {data_path}，训练轮数: {epochs}")

        # 开始训练
        model.train(
            data=data_path,         # 配置文件
            epochs=epochs,          # 训练轮数
            imgsz=imgsz,            # 图像尺寸
            batch=batch_size,       # 批量大小
            device=device,          # 使用的设备（GPU 或 CPU）
            workers=workers,        # 数据加载的工作线程数
            save=True,              # 保存训练后的模型
            project=save_dir,       # 保存路径（可以自定义保存的文件夹）
            name='dog120_model'     # 训练结果文件夹名称（自动生成时间戳后缀）
        )

        print("训练完成，模型已保存！")
    except Exception as e:
        print(f"训练过程中发生错误: {e}")
