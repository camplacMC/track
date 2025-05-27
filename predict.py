# predict.py
import torch
from torchvision import transforms
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
from .model import load_trained_model
import pandas as pd
from .breed_mapping import breed_mapping
import io
import base64
import os  # 加上顶部导入
from datetime import datetime  # 如果你希望图像命名更加唯一
from math import sqrt
import pytz
import cv2
import numpy as np

# 加载模型
model = load_trained_model()
# 加载YOLO11n模型进行多目标检测
model_yolo = YOLO('F:/python/my_vue/backend/runs/train/dog120_model/weights/best.pt')  # 加载训练好的YOLO11n模型

# 类别索引映射
def get_breed_from_index(index):
    df = pd.read_csv('../dog_test/labels.csv')
    breeds = sorted(df['breed'].unique().tolist())  # 根据训练时的类别顺序
    return breeds[index]

# 图像预处理
predict_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
# 预测单个狗品种
def predict_single_breed(image):
    print("正在进行品种预测...")

    if not isinstance(image, Image.Image):
        image = Image.open(image).convert('RGB')
    image = image.convert("RGB")
    image = predict_transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)
        breed = get_breed_from_index(predicted.item())

    chinese_breed = breed_mapping.get(breed, breed)
    print(f"预测品种: {chinese_breed}")
    return chinese_breed, round(confidence.item(), 4)

# 预测多个狗的品种
def predict_multiple_dogs(image_path):


    def compute_iou(box1, box2):
        """计算两个 YOLO 格式的 box 的 IOU (xywh 格式)"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2

        # 转换为左上角和右下角
        box1 = [x1 - w1 / 2, y1 - h1 / 2, x1 + w1 / 2, y1 + h1 / 2]
        box2 = [x2 - w2 / 2, y2 - h2 / 2, x2 + w2 / 2, y2 + h2 / 2]

        xi1 = max(box1[0], box2[0])
        yi1 = max(box1[1], box2[1])
        xi2 = min(box1[2], box2[2])
        yi2 = min(box1[3], box2[3])
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union_area = box1_area + box2_area - inter_area

        return inter_area / union_area if union_area > 0 else 0

    # 加载图片
    image = Image.open(image_path).convert("RGB")

    # 使用 YOLO 进行目标检测（使用较宽松的阈值）
    results = model_yolo(image, iou=0.6, conf=0.3)
    boxes = results[0].boxes.xywh.cpu().numpy()
    confidences = results[0].boxes.conf.cpu().numpy()
    labels = results[0].names

    print(f"检测到 {len(boxes)} 个原始目标")

    if len(boxes) == 0:
        print("没有检测到任何目标!")
        return [], None

    # 去重：非极大值抑制（简易版）
    filtered_boxes = []
    filtered_confidences = []

    for i, box in enumerate(boxes):
        is_duplicate = False
        for j, fbox in enumerate(filtered_boxes):
            if compute_iou(box, fbox) > 0.5:  # 可调节IOU阈值
                is_duplicate = True
                break
        if not is_duplicate:
            filtered_boxes.append(box)
            filtered_confidences.append(confidences[i])

    print(f"过滤后剩余 {len(filtered_boxes)} 个目标")

    predictions = []
    draw = ImageDraw.Draw(image)

    SAVE_DIR = "cropped_dogs"
    os.makedirs(SAVE_DIR, exist_ok=True)

    for i, box in enumerate(filtered_boxes):
        x, y, w, h = box
        confidence = filtered_confidences[i]

        # 扩展边界框区域
        padding = 0.15
        left = int(max(0, x - w / 2 - w * padding))
        top = int(max(0, y - h / 2 - h * padding))
        right = int(min(image.width, x + w / 2 + w * padding))
        bottom = int(min(image.height, y + h / 2 + h * padding))

        cropped_image = image.crop((left, top, right, bottom))

        # 保存裁剪图
        tz = pytz.timezone("Asia/Shanghai")
        timestamp_str = datetime.now(tz).strftime("%Y%m%d_%H%M%S")  # 用于文件名
        cropped_filename = f"dog_{i+1}_{timestamp_str}.png"
        cropped_path = os.path.join(SAVE_DIR, cropped_filename)
        cropped_image.save(cropped_path)

        # 品种识别
        breed, breed_confidence = predict_single_breed(cropped_image)

        # 绘图
        draw.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], outline="red", width=3)
        label = str(i + 1)
        text = f"{label} ({round(breed_confidence, 2)})"
        font = ImageFont.load_default()
        draw.text((x - w / 2, y - h / 2), text, fill="black", font=font)

        predictions.append({
            'label': label,
            'breed': breed_mapping.get(breed, breed),
            'confidence': float(confidence),
            'bbox': [round(val, 2) for val in box],
            'breed_confidence': float(breed_confidence)
        })

    # 转为 base64
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    encoded_img = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    return predictions, encoded_img

def predict_multiple_dogs_from_frame(frame: np.ndarray):
    def compute_iou(box1, box2):
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        box1 = [x1 - w1/2, y1 - h1/2, x1 + w1/2, y1 + h1/2]
        box2 = [x2 - w2/2, y2 - h2/2, x2 + w2/2, y2 + h2/2]
        xi1, yi1 = max(box1[0], box2[0]), max(box1[1], box2[1])
        xi2, yi2 = min(box1[2], box2[2]), min(box1[3], box2[3])
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        union_area = (box1[2]-box1[0])*(box1[3]-box1[1]) + (box2[2]-box2[0])*(box2[3]-box2[1]) - inter_area
        return inter_area / union_area if union_area > 0 else 0

    image = Image.fromarray(frame).convert("RGB")
    results = model_yolo(image, iou=0.6, conf=0.3)
    boxes = results[0].boxes.xywh.cpu().numpy()
    confidences = results[0].boxes.conf.cpu().numpy()
    if len(boxes) == 0:
        return [], image

    filtered_boxes, filtered_confidences = [], []
    for i, box in enumerate(boxes):
        if all(compute_iou(box, fbox) <= 0.5 for fbox in filtered_boxes):
            filtered_boxes.append(box)
            filtered_confidences.append(confidences[i])

    predictions = []
    draw = ImageDraw.Draw(image)
    for i, box in enumerate(filtered_boxes):
        x, y, w, h = box
        left = int(max(0, x - w/2 - w * 0.15))
        top = int(max(0, y - h/2 - h * 0.15))
        right = int(min(image.width, x + w/2 + w * 0.15))
        bottom = int(min(image.height, y + h/2 + h * 0.15))
        cropped_image = image.crop((left, top, right, bottom))
        breed, breed_confidence = predict_single_breed(cropped_image)

        font = ImageFont.truetype("simhei.ttf", size=20)
        draw.rectangle([x - w/2, y - h/2, x + w/2, y + h/2], outline="red", width=3)
        draw.text((x - w/2, y - h/2), f"{i+1} ({round(breed_confidence, 2)}) {breed}", fill="black", font=font)

        predictions.append({
            'label': str(i + 1),
            'breed': breed_mapping.get(breed, breed),
            'confidence': float(confidences[i]),
            'bbox': [round(val, 2) for val in box],
            'breed_confidence': float(breed_confidence)
        })

    return predictions, image

def predict_video_breeds(video_path, output_path):
    print(f"开始处理视频: {video_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开输入视频文件: {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or np.isnan(fps):
        fps = 25.0  # 防止帧率为 0 的情况

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 改用更兼容的编码器（可选）
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    if not out.isOpened():
        print(f"无法打开输出文件 {output_path}")
        cap.release()
        return []

    results = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 15

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_results, pil_img = predict_multiple_dogs_from_frame(rgb_frame)
            results.extend(frame_results)
            annotated_frame = np.array(pil_img)

            out.write(cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))

        except Exception as e:
            print(f"第 {frame_count} 帧处理失败: {e}")
            continue

    cap.release()
    out.release()
    print(f"视频处理完成，处理帧数: {frame_count}, 输出路径: {output_path}")
    return results



