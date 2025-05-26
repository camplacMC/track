import os
import shutil
import pandas as pd
from sklearn.model_selection import train_test_split

# 读取 CSV 文件中的图片 ID 和标签
def read_csv_labels(csv_file):
    df = pd.read_csv(csv_file)
    labels = df[['id', 'breed']]
    return labels

# 重组训练集和验证集
def reorg_train_valid(original_data_dir, sorted_data_dir, labels, valid_ratio):
    train_dir = os.path.join(sorted_data_dir, 'train')
    valid_dir = os.path.join(sorted_data_dir, 'valid')

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(valid_dir, exist_ok=True)

    # 分层划分训练/验证集
    train_labels, valid_labels = train_test_split(
        labels, test_size=valid_ratio, stratify=labels['breed']
    )

    # 源文件路径改为从 'train/' 获取
    for _, row in train_labels.iterrows():
        breed_dir = os.path.join(train_dir, row['breed'])
        os.makedirs(breed_dir, exist_ok=True)
        filename = row['id'] + '.jpg'
        src_path = os.path.join(original_data_dir, 'train', filename)
        dest_path = os.path.join(breed_dir, filename)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
        else:
            print(f"[警告] 文件不存在：{src_path}")

    for _, row in valid_labels.iterrows():
        breed_dir = os.path.join(valid_dir, row['breed'])
        os.makedirs(breed_dir, exist_ok=True)
        filename = row['id'] + '.jpg'
        src_path = os.path.join(original_data_dir, 'train', filename)
        dest_path = os.path.join(breed_dir, filename)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
        else:
            print(f"[警告] 文件不存在：{src_path}")

# 重组测试集（无标签）
def reorg_test(original_data_dir, sorted_data_dir):
    test_src_dir = os.path.join(original_data_dir, 'test')
    test_dest_dir = os.path.join(sorted_data_dir, 'test')
    os.makedirs(test_dest_dir, exist_ok=True)

    for file in os.listdir(test_src_dir):
        src_path = os.path.join(test_src_dir, file)
        dest_path = os.path.join(test_dest_dir, file)
        if os.path.isfile(src_path):
            shutil.copy(src_path, dest_path)

# 数据集重组入口函数
def reorg_dog_data(original_data_dir, sorted_data_dir, valid_ratio):
    labels = read_csv_labels(os.path.join(original_data_dir, 'labels.csv'))
    reorg_train_valid(original_data_dir, sorted_data_dir, labels, valid_ratio)
    reorg_test(original_data_dir, sorted_data_dir)

# 主函数
if __name__ == "__main__":
    original_data_dir = '../dog_breed'                # 原始数据路径
    sorted_data_dir = '../dog_breed_sorted'           # 新的输出目录
    valid_ratio = 0.1                                  # 10%验证集
    batch_size = 32

    os.makedirs(sorted_data_dir, exist_ok=True)
    reorg_dog_data(original_data_dir, sorted_data_dir, valid_ratio)
