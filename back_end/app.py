from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import json
from flask import Flask, request, jsonify, send_file, send_from_directory, redirect, url_for
from functions.detect_img import detect_img, save_json, save_detection_result_to_db
from functions.control_chart import generate_control_chart_data
from functions.email_utils import send_control_chart_alert
from flask_cors import CORS, cross_origin
from datetime import datetime
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_url_path='/results',static_folder='./static/results')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

# 全局变量：跟踪上一次处理的最大图片id，用于防止重复发送邮件
last_processed_max_id = 0

# 定义数据库模型
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    hasDefects = db.Column(db.Boolean)
    detection_total_cnts = db.Column(db.Integer, default=0)
    detection_classes = db.Column(db.Text)  # JSON字符串存储缺陷类别列表
    detection_boxes = db.Column(db.Text)  # JSON字符串存储检测框坐标
    detection_scores = db.Column(db.Text)  # JSON字符串存储置信度分数
    captureTime = db.Column(db.DateTime)

    def __init__(self, name, hasDefects, captureTime, detection_total_cnts=0, detection_classes=None, detection_boxes=None, detection_scores=None):
        self.name = name
        self.hasDefects = hasDefects
        self.detection_total_cnts = detection_total_cnts
        self.detection_classes = json.dumps(detection_classes) if detection_classes else '[]'
        self.detection_boxes = json.dumps(detection_boxes) if detection_boxes else '[]'
        self.detection_scores = json.dumps(detection_scores) if detection_scores else '[]'
        self.captureTime = captureTime

    def get_detection_classes(self):
        """获取缺陷类别列表"""
        try:
            return json.loads(self.detection_classes) if self.detection_classes else []
        except:
            return []

    def get_detection_boxes(self):
        """获取检测框坐标列表"""
        try:
            return json.loads(self.detection_boxes) if self.detection_boxes else []
        except:
            return []

    def get_detection_scores(self):
        """获取置信度分数列表"""
        try:
            return json.loads(self.detection_scores) if self.detection_scores else []
        except:
            return []

# 邮箱设置模型
class EmailSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, email):
        self.email = email
        self.updated_at = datetime.now()

# 定义Schema
class ImageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Image
        load_instance = True

image_schema = ImageSchema()
images_schema = ImageSchema(many=True)

# 创建数据库表
with app.app_context():
    db.create_all()
    
    # 初始化邮箱设置
    if not EmailSettings.query.first():
        default_email = EmailSettings(email='2395365918@qq.com')
        db.session.add(default_email)
        db.session.commit()

# 跨域设置
CORS(app, supports_credentials=True, resources={r'/*': {'origins': '*'}})
socketio = SocketIO(app)

# 设置保存检测结果图片的目录
image_result_folder = os.path.join(app.static_folder, 'images')
json_result_folder = os.path.join(app.static_folder, 'jsons')

@app.route('/results/images/<path:filename>')
def send_results_images(filename):
    return send_from_directory(image_result_folder, filename)

@app.route('/results/jsons/<path:filename>')
def send_results_jsons(filename):
    return send_from_directory(json_result_folder, filename)

@app.route('/detectByImg', methods=['POST'])
@cross_origin()
def detect_by_img():
    """
        --检测图片--
        收到前端返回图片文件类型 调用检测
        :return:检测后结果图片
        """
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    file_name, _ = os.path.splitext(file.filename)
    path = os.path.join('./images', file.filename)
    file.save(path)

    try:
        result = detect_img(path, file_name)
        image_result_path = os.path.join(image_result_folder, f"{file_name}.png")
        save_json(result, json_result_folder, file_name)
        save_detection_result_to_db(result)
        return send_file(image_result_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images', methods=['GET'])
def get_images():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')

    query = Image.query

    if startDate and endDate:
        query = query.filter(Image.captureTime.between(startDate, endDate))
    
    images = query.all()
    result = [
        {
            'id': image.id,
            'name': image.name,
            'hasDefects': image.hasDefects,
            'detection_total_cnts': image.detection_total_cnts,
            'detection_classes': image.get_detection_classes(),
            'detection_boxes': image.get_detection_boxes(),
            'detection_scores': image.get_detection_scores(),
            'captureTime': image.captureTime.isoformat()
        }
        for image in images
    ]
    return jsonify(result)

@app.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    image = Image.query.get_or_404(image_id)
    return image_schema.jsonify(image)

@app.route('/images', methods=['POST'])
def add_image():
    try:
        name = request.json['name']
        hasDefects = request.json['hasDefects']
        captureTime = datetime.strptime(request.json['captureTime'], '%Y-%m-%d %H:%M:%S.%f')

        new_image = Image(name, hasDefects, captureTime)
        db.session.add(new_image)
        db.session.commit()

        return image_schema.jsonify(new_image)
    except KeyError as e:
        return jsonify({"error": f"Missing key: {e}"}), 400
    except ValueError:
        return jsonify({"error": "Invalid datetime format"}), 400

@app.route('/images/detection_results', methods=['POST'])
def save_detection_result():
    try:
        data = request.json
        name = data['name']
        hasDefects = data['hasDefects']
        captureTime = datetime.strptime(data['captureTime'], '%Y-%m-%d %H:%M:%S.%f')
        
        # 获取检测详细信息
        detection_total_cnts = data.get('detection_total_cnts', 0)
        detection_classes = data.get('detection_classes', [])
        detection_boxes = data.get('detection_boxes', [])
        detection_scores = data.get('detection_scores', [])

        new_image = Image(
            name=name, 
            hasDefects=hasDefects, 
            captureTime=captureTime,
            detection_total_cnts=detection_total_cnts,
            detection_classes=detection_classes,
            detection_boxes=detection_boxes,
            detection_scores=detection_scores
        )
        db.session.add(new_image)
        db.session.commit()

        return jsonify({"message": "Detection result saved successfully."}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing key: {e}"}), 400
    except ValueError:
        return jsonify({"error": "Invalid datetime format"}), 400

@app.route('/email-settings', methods=['GET'])
def get_email_settings():
    """
    获取当前邮箱设置
    """
    try:
        # 尝试从数据库获取邮箱设置
        email_setting = EmailSettings.query.first()
        
        if email_setting:
            return jsonify({
                "email": email_setting.email,
                "updated_at": email_setting.updated_at.isoformat()
            }), 200
        else:
            # 如果没有记录，返回默认邮箱
            return jsonify({
                "email": "2395365918@qq.com",
                "updated_at": datetime.now().isoformat()
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/email-settings', methods=['PUT'])
def update_email_settings():
    """
    更新邮箱设置
    """
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Missing email field"}), 400
        
        # 验证邮箱格式
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # 检查数据库中是否已有记录
        email_setting = EmailSettings.query.first()
        
        if email_setting:
            # 更新现有记录
            email_setting.email = email
        else:
            # 创建新记录
            email_setting = EmailSettings(email)
            db.session.add(email_setting)
        
        db.session.commit()
        
        return jsonify({
            "email": email_setting.email,
            "updated_at": email_setting.updated_at.isoformat(),
            "message": "Email settings updated successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# 添加静态文件服务
@app.route('/')
def index():
    return send_from_directory('../front_end/dist', 'index.html')

@app.route('/control-chart-data', methods=['GET'])
@cross_origin()
def get_control_chart_data():
    """
    获取控制图数据
    按照U图控制图的要求，每3张PCB为一个样本进行计算
    返回最近25组数据，包含所有8个异常规则的检测结果
    只有当数据库中最大id变化时才发送异常报警邮件
    """
    try:
        # 获取当前数据库中最大的图片id
        current_max_id = db.session.query(db.func.max(Image.id)).scalar() or 0
        
        # 获取足够的检测数据以生成25组样本，按时间排序
        # 假设每组3张，至少需要获取75-100张图片
        # 替换原代码：获取数据 + 按时间排序 + 分组
        # 新逻辑：按 id 分组 + 固定起点（id % 3 == 0）
        images = Image.query.order_by(Image.id.desc()).limit(100).all()  # 按 id 降序取最新100条

        if not images:
            return jsonify({"error": "No data available"}), 404

        # 按组号分组（组号 = (id - 1) // 3，确保 id=3,6,9 为组起点）
        grouped = {}
        for img in images:
            group_id = (img.id - 1) // 3  # 例如：id=3 → (3-1)//3=0, id=4→(4-1)//3=1 → 但需固定起点
            if group_id not in grouped:
                grouped[group_id] = []
            grouped[group_id].append(img)

        # 按组号降序排序（组号大 → 数据新），只取最近25组
        group_ids = sorted(grouped.keys(), reverse=True)
        if len(group_ids) > 25:
            group_ids = group_ids[:25]

        # 构建样本列表（每个组为一个样本），并反转顺序（使样本0是最早数据）
        samples = [grouped[gid] for gid in group_ids]  # [最新组, ... , 最早组]
        samples = samples[::-1]  # 反转 → [最早组, ... , 最新组]（符合控制图时间顺序）
        
        # 计算每个样本的缺陷数和检验单位大小
        c_list = []  # 每个样本的缺陷数
        n_list = []  # 每个样本的检验单位大小（这里用PCB数量表示）
        sample_times = []  # 每个样本的时间
        sample_defects_details = []  # 每个样本的详细缺陷信息
        
        for sample in samples:
            total_defects = sum(img.detection_total_cnts for img in sample)
            sample_size = len(sample)
            
            c_list.append(total_defects)
            n_list.append(float(sample_size))
            # 使用样本中最新的时间作为样本时间
            sample_times.append(sample[-1].captureTime.isoformat())
            
            # 记录样本的详细缺陷信息
            defects_info = {
                'sample_size': sample_size,
                'total_defects': total_defects,
                'defects_per_pcb': [img.detection_total_cnts for img in sample],
                'pcb_names': [img.name for img in sample],
                'capture_times': [img.captureTime.isoformat() for img in sample]
            }
            sample_defects_details.append(defects_info)
        
        # 使用control_chart.py中的函数计算控制图数据
        chart_data = generate_control_chart_data(c_list, n_list)
        
        # 添加样本时间信息和详细缺陷信息
        chart_data['sample_times'] = sample_times
        chart_data['sample_defects_details'] = sample_defects_details
        chart_data['message'] = '控制图数据包含所有8个异常规则检测结果'
        
        # 检查是否有异常点，且数据库中最大id发生变化，才发送报警邮件
        global last_processed_max_id
        if chart_data['abnormal_points'] and current_max_id != last_processed_max_id:
            # 准备异常数据
            abnormal_data = {
                'abnormal_points': chart_data['abnormal_points'],
                'sample_defects_details': chart_data['sample_defects_details'],
                'u_list': chart_data['u_list'],
                'c_list': chart_data['c_list'],
                'n_list': chart_data['n_list'],
                'center_line': chart_data['center_line'],
                'ucl_list': chart_data['ucl_list'],
                'lcl_list': chart_data['lcl_list']
            }
            
            # 从数据库获取收件人邮箱
            email_setting = EmailSettings.query.first()
            recipient_email = email_setting.email if email_setting else '2395365918@qq.com'
            
            # 发送异常报警邮件
            send_control_chart_alert(abnormal_data, recipient_email)
            # 更新上一次处理的最大id
            last_processed_max_id = current_max_id
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../front_end/dist', path)

if __name__ == '__main__':
    socketio.run(app, host="localhost", debug=True, port=5000, allow_unsafe_werkzeug=True)
