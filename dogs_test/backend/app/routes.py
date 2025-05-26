import pytz
from flask import send_file
from flask import send_from_directory
from .predict import predict_video_breeds
import os
import json
import numpy as np
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from .predict import predict_multiple_dogs
from .model import allowed_file
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
# 创建 Flask 蓝图
routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_video_file(filename):
    allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def convert_np_types(obj):
    """
    递归函数，将所有 numpy.float32 或 numpy.float64 转换为原生 Python float。
    """
    if isinstance(obj, dict):
        return {key: convert_np_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_np_types(item) for item in obj]
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)  # 转换为 Python 的 float 类型
    return obj
# 上传图片接口

load_dotenv(dotenv_path=r"D:\dogs_test\backend\minio.env")  # 加载 .env 文件

routes = Blueprint('routes', __name__)

# 本地上传目录用于临时保存文件
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#MINIO配置
minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),          # 正确：读取 MINIO_ENDPOINT 变量
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)

UPLOAD_BUCKET = "uploads"
HISTORY_BUCKET = "history"
VIDEO_BUCKET = "video"

# 自动创建 bucket（如果不存在）
for bucket in [UPLOAD_BUCKET, HISTORY_BUCKET]:
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)

def convert_np_types(obj):
    if isinstance(obj, dict):
        return {k: convert_np_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np_types(i) for i in obj]
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    return obj

# 上传图片接口
@routes.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400

@routes.route('/api/recognize', methods=['POST'])
def recognize_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        local_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(local_path)

        predictions, encoded_img = predict_multiple_dogs(local_path)
        predictions = convert_np_types(predictions)

        # 上传图片到 MinIO
        minio_client.fput_object(UPLOAD_BUCKET, filename, local_path)

        # 使用安全格式的时间戳（避免冒号）
        tz = pytz.timezone("Asia/Shanghai")
        timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")  # 用于文件名

        # 构建历史记录 JSON
        record = {
            "timestamp": timestamp,
            "upload_object": filename,
            "predictions": predictions
        }

        record_json = json.dumps(record)
        json_name = f"{os.path.splitext(filename)[0]}_{timestamp}.json"
        json_path = os.path.join(UPLOAD_FOLDER, json_name)

        with open(json_path, "w") as f:
            f.write(record_json)

        minio_client.fput_object(HISTORY_BUCKET, json_name, json_path)

        # 清理临时文件
        os.remove(local_path)
        os.remove(json_path)

        return jsonify({"predictions": predictions, "image": encoded_img}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400

@routes.route('/api/history', methods=['GET'])
def get_history():
    records = []
    for obj in minio_client.list_objects(HISTORY_BUCKET):
        try:
            response = minio_client.get_object(HISTORY_BUCKET, obj.object_name)
            record = json.loads(response.read())
            # 图片记录
            if "upload_object" in record:
                url = minio_client.presigned_get_object(UPLOAD_BUCKET, record["upload_object"])
                record["file_url"] = url
                record["is_video"] = False

            # 视频记录
            elif "video_object" in record:
                url = minio_client.presigned_get_object(VIDEO_BUCKET, record["video_object"])
                record["file_url"] = url
                record["is_video"] = True
            records.append(record)
        except S3Error as e:
            print(f"读取记录出错: {e}")
    # 按时间排序（新记录在前）
    records.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify(records), 200

@routes.route('/api/history', methods=['DELETE'])
def delete_history():
    data = request.get_json()
    json_name = data.get("json_name")
    image_name = data.get("image_name")
    try:
        if json_name:
            minio_client.remove_object(HISTORY_BUCKET, json_name)
        if image_name:
            minio_client.remove_object(UPLOAD_BUCKET, image_name)
        return jsonify({"message": "记录删除成功"}), 200
    except S3Error as e:
        print(f"删除失败: {e}")
        return jsonify({"error": "删除失败"}), 500


@routes.route('/api/upload_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "不符合格式"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_video_file(file.filename):
        filename = secure_filename(file.filename)
        video_dir = os.path.join(UPLOAD_FOLDER, 'videos')
        os.makedirs(video_dir, exist_ok=True)
        file_path = os.path.join(video_dir, filename)
        file.save(file_path)

        return jsonify({
            "message": "视频上传成功",
            "file_path": file_path
        }), 200
    else:
        return jsonify({"error": "Invalid video file type"}), 400

@routes.route('/api/recognize_video', methods=['POST'])
def recognize_video():
    data = request.get_json()
    file_path = data.get("file_path")

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "传入格式错误"}), 400

    input_path = os.path.abspath(file_path)
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    tz = pytz.timezone("Asia/Shanghai")
    timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")  # 用于文件名

    fixed_fps_path = os.path.join("videos", f"{name}_{timestamp}_15fps.mp4")
    os.makedirs(os.path.dirname(fixed_fps_path), exist_ok=True)

    # 转为15fps
    success = convert_to_fixed_fps(input_path, fixed_fps_path, target_fps=15)
    if not success:
        return jsonify({"error": "帧率转换失败"}), 500

    output_filename = f"{name}_{timestamp}_output.mp4"
    output_path = os.path.abspath(os.path.join("videos", output_filename))

    # 视频识别逻辑：使用转换后的文件
    predictions = predict_video_breeds(fixed_fps_path, output_path)
    predictions = convert_np_types(predictions)

    # 上传到 MinIO
    try:
        if not minio_client.bucket_exists(VIDEO_BUCKET):
            minio_client.make_bucket(VIDEO_BUCKET)
        minio_client.fput_object(VIDEO_BUCKET, output_filename, output_path)

        record = {
            "timestamp": timestamp,
            "video_object": output_filename,
            "predictions": predictions
        }

        json_name = f"{name}_{timestamp}.json"
        json_path = os.path.join("videos", json_name)
        with open(json_path, "w") as f:
            json.dump(record, f)
        minio_client.fput_object(HISTORY_BUCKET, json_name, json_path)
        os.remove(json_path)

    except S3Error as e:
        print(f"MinIO上传失败: {e}")
        return jsonify({"error": "视频或记录上传失败"}), 500

    print("上传成功")
    return send_file(
        output_path,
        as_attachment=True,
        download_name=output_filename,
        mimetype="video/mp4"
    )

def convert_to_fixed_fps(input_path, output_path, target_fps=15):
    import cv2
    try:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return False

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        input_fps = cap.get(cv2.CAP_PROP_FPS)
        if input_fps == 0:
            input_fps = 30
        frame_interval = int(round(input_fps / target_fps))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % frame_interval == 0:
                out.write(frame)
            frame_count += 1

        cap.release()
        out.release()
        return True
    except Exception as e:
        print(f"帧率转换失败: {e}")
        return False