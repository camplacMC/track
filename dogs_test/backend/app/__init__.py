from flask import Flask
from .routes import routes  # 导入定义的路由蓝图
from flask_cors import CORS

def create_app():
    # 创建 Flask 应用
    app = Flask(__name__)

    # 设置应用配置（例如数据库、上传路径等）
    app.config['UPLOAD_FOLDER'] = './uploads'  # 设置上传文件夹路径

    # 注册蓝图
    app.register_blueprint(routes)
    CORS(app)  # 启用 CORS
    return app
