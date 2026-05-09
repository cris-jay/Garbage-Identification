from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import datetime
import requests
import random
import traceback
import chromadb
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts
import os
import uuid

# 注册中文字体
try:
    font_path = 'C:/Windows/Fonts/simhei.ttf'
    if os.path.exists(font_path):
        chinese_font = ttfonts.TTFont('SimHei', font_path)
        pdfmetrics.registerFont(chinese_font)
        print("中文字体注册成功")
except Exception as e:
    print(f"中文字体注册失败: {e}")

client = chromadb.PersistentClient(path="./chroma_db")
garbage_collection = client.get_collection("garbage_collection")

app = Flask(__name__)

# 百度AI接口配置
BAIDU_API_KEY = "WgbVjh6bA5AF74qV4DChu9qd"
BAIDU_SECRET_KEY = "lHiFd8KqjavU2uPxK9GWIZldUOSLLvgt"
BAIDU_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
BAIDU_GARBAGE_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v2/recycle"

baidu_access_token = None
token_expire_time = None

# 获取百度接口token（自动过期刷新）
def get_baidu_token():
    global baidu_access_token, token_expire_time
    now = datetime.datetime.now().timestamp()
    
    if baidu_access_token and token_expire_time and now < token_expire_time:
        return baidu_access_token
    
    params = {
        "grant_type": "client_credentials",
        "client_id": BAIDU_API_KEY,
        "client_secret": BAIDU_SECRET_KEY
    }
    resp = requests.get(BAIDU_TOKEN_URL, params=params)
    result = resp.json()
    
    if "access_token" not in result:
        raise Exception("百度TOKEN获取失败：" + result.get("error_msg", ""))
    
    baidu_access_token = result["access_token"]
    token_expire_time = now + result.get("expires_in", 86400) - 100
    return baidu_access_token

# ====================== 基础配置 ======================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'garbage_system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.config['JWT_SECRET_KEY'] = 'garbage_secret_2026'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=7)

mysql = MySQL(app)
jwt = JWTManager(app)

# ====================== 通用返回 ======================
def res(code=200, msg="操作成功", data=None):
    return jsonify({"code": code, "msg": msg, "data": data})

# ====================== 管理员判断 ======================
def is_admin(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT role FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        return user and user['role'] == 'admin'
    except:
        return False

# ====================== 用户登录 ======================
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')

    if not phone or not password:
        return res(400, "手机号和密码不能为空")

    cur = mysql.connection.cursor()
    cur.execute("SELECT id,status,password FROM users WHERE phone=%s", (phone,))
    user = cur.fetchone()

    if not user or user['password'] != password:
        return res(400, "手机号或密码错误")
    if user['status'] == 'disable':
        return res(403, "账号已被禁用")

    token = create_access_token(identity=str(user['id']))
    return res(200, "登录成功", {"token": token})

# ====================== 用户注册 ======================
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    nickname = data.get('nickname', '用户' + str(random.randint(1000,9999)))

    if not phone or not password:
        return res(400, "手机号和密码不能为空")

    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM users WHERE phone=%s", (phone,))
    if cur.fetchone():
        return res(400, "手机号已存在")

    cur.execute(
        "INSERT INTO users(phone,password,nickname,role,status) VALUES(%s,%s,%s,'user','normal')",
        (phone, password, nickname)
    )
    mysql.connection.commit()
    return res(200, "注册成功")

# ====================== 分类 ======================
@app.route('/api/category', methods=['GET'])
def get_category():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,name FROM category")
    return res(200, data=cur.fetchall())

@app.route('/api/garbage/list', methods=['GET'])
def garbage_list():
    category_id = request.args.get('category_id')
    if not category_id:
        return res(400, "缺少分类ID")

    # 大类ID与分类名称映射（和你的csv数据完全对应）
    category_map = {
        "1": "可回收物",
        "2": "有害垃圾",
        "3": "湿垃圾",
        "4": "干垃圾"
    }
    category_name = category_map.get(category_id, "")
    if not category_name:
        return res(400, "分类不存在")

    try:
        # 向量库按分类筛选
        result = garbage_collection.get(
            where={"category": category_name},
            include=["metadatas"]
        )
        data = []
        for meta in result["metadatas"]:
            data.append({
                "name": meta["name"],
                "category": meta["category"]
            })
        return res(200, data=data)
    except Exception as e:
        return res(500, "分类数据查询失败")

@app.route('/api/search', methods=['GET'])
@jwt_required()
def search_garbage():
    user_id = get_jwt_identity()
    q = request.args.get('q')
    if not q:
        return res(400, "请输入搜索内容")

    try:
        data = []

        # 第一步：精确文本匹配（使用 $eq 进行完全匹配）
        exact_result = garbage_collection.get(
            where={"name": {"$eq": q}},
            include=["metadatas"]
        )
        if exact_result["metadatas"]:
            for meta in exact_result["metadatas"]:
                data.append({
                    "name": meta["name"],
                    "category": meta["category"]
                })

        # 第二步：模糊匹配兜底（如果精确匹配没找到，获取所有数据进行本地过滤）
        if not data:
            all_data = garbage_collection.get(include=["metadatas"])
            q_lower = q.lower()
            for meta in all_data.get("metadatas", []):
                if meta.get("name") and q_lower in meta["name"].lower():
                    data.append({
                        "name": meta["name"],
                        "category": meta["category"]
                    })
                    if len(data) >= 10:
                        break

        # 第三步：语义搜索兜底（如果模糊匹配也没找到）
        if not data:
            results = garbage_collection.query(
                query_texts=[q],
                n_results=10,
                include=["metadatas"]
            )
            for meta in results["metadatas"][0]:
                data.append({
                    "name": meta["name"],
                    "category": meta["category"]
                })

        # 存入数据库
        if data:
            first = data[0]
            garbage_name = first["name"]
            category_name = first["category"]

            category_map = {
                "可回收物": 1,
                "有害垃圾": 2,
                "厨余垃圾": 3,
                "湿垃圾": 3,
                "干垃圾": 4,
                "其他垃圾": 4
            }
            category_id = category_map.get(category_name, 4)

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO recognition_records
                (user_id, garbage_name, category_id, confidence, image_base64, search_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, garbage_name, category_id, 1.0, "", "text_search"))
            mysql.connection.commit()

        return res(200, data=data)
    except Exception as e:
        # 关键修改：打印完整错误栈，方便定位问题
        import traceback
        print("=== 搜索接口异常 ===")
        print(traceback.format_exc())
        return res(500, f"搜索服务异常: {str(e)}")
# ====================== 图片AI识别 ======================
@app.route('/api/recognize/image', methods=['POST'])
@jwt_required()
def recognize_image():
    user_id = get_jwt_identity()
    data = request.json
    image_base64 = data.get('image_base64')

    if not image_base64:
        return res(400, "缺少图片数据")

    try:
        # 1. 获取百度Token
        token = get_baidu_token()
        if not token:
            return res(500, "获取百度Token失败")

        # 2. 调用百度【通用物体识别】接口（替代垃圾分类接口）
        baidu_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
        
        # 3. 正确格式：用params传token，用data传form参数（百度接口必须这样）
        resp = requests.post(
            baidu_url,
            params={"access_token": token},
            data={"image": image_base64},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        result = resp.json()
        print("百度返回原始数据：", result)  # 打印返回，方便调试

        # 4. 检查百度接口返回的错误
        if "error_code" in result:
            return res(500, f"AI识别失败：{result.get('error_msg')}")

        if not result.get("result") or len(result["result"]) == 0:
            return res(400, "未识别到物体")

        # 5. 解析识别结果，取置信度最高的结果
        top_result = result["result"][0]
        garbage_name = top_result["keyword"]
        confidence = float(top_result["score"])

        # 6. 【优化策略】先做精确文本匹配，再用语义搜索兜底
        category_name = "其他垃圾"
        matched_name = garbage_name
        match_type = "未匹配"
        
        # 获取所有数据用于精确匹配
        all_data = garbage_collection.get(include=["metadatas"])
        
        # 第一步：优先完全匹配
        if all_data["metadatas"]:
            for meta in all_data["metadatas"]:
                if meta["name"] == garbage_name:
                    category_name = meta["category"]
                    matched_name = meta["name"]
                    match_type = "完全匹配"
                    break
        
        # 第二步：如果没有完全匹配，查找包含匹配
        if match_type == "未匹配" and all_data["metadatas"]:
            for meta in all_data["metadatas"]:
                if garbage_name in meta["name"]:
                    category_name = meta["category"]
                    matched_name = meta["name"]
                    match_type = "包含匹配"
                    break
        
        # 第三步：语义搜索兜底
        if match_type == "未匹配":
            search_res = garbage_collection.query(
                query_texts=[garbage_name],
                n_results=1
            )
            if search_res["metadatas"][0] and len(search_res["metadatas"][0]) > 0:
                category_name = search_res["metadatas"][0][0]["category"]
                matched_name = search_res["metadatas"][0][0]["name"]
                match_type = "语义匹配"
        
        print(f"匹配结果：{garbage_name} -> {matched_name} ({category_name}) [{match_type}]")

        # 分类名称 → 转 ID
        category_map = {
            "可回收物": 1,
            "有害垃圾": 2,
            "厨余垃圾": 3,
            "湿垃圾": 3,
            "干垃圾": 4,
            "其他垃圾": 4
        }
        category_id = category_map.get(category_name, 4)
        desc = f"识别结果：{garbage_name}，属于：{category_name}"

        # 7. 保存识别记录到数据库
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO recognition_records
            (user_id, garbage_name, category_id, confidence, image_base64)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, garbage_name, category_id, confidence, image_base64))
        mysql.connection.commit()

        return res(200, "识别成功", {
            "name": garbage_name,
            "category": ['可回收物','有害垃圾','厨余垃圾','其他垃圾'][category_id-1],
            "category_id": category_id,
            "confidence": round(confidence, 2),
            "desc": desc
        })

    except Exception as e:
        print("识别接口报错：", traceback.format_exc())
        return res(500, f"服务异常：{str(e)}")

# ====================== 5.2 获取个人识别历史 ======================
@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    """获取当前登录用户的识别历史记录"""
    user_id = get_jwt_identity()
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, garbage_name, category_id, confidence, image_base64, create_time 
            FROM recognition_records 
            WHERE user_id=%s 
            ORDER BY create_time DESC
        """, (int(user_id),))
        records = cur.fetchall()

        # 把category_id转成名称，方便前端展示
        category_map = {
            1: "可回收物",
            2: "有害垃圾",
            3: "厨余垃圾",
            4: "其他垃圾"
        }
        data = []
        for r in records:
            data.append({
                "id": r["id"],
                "garbage_name": r["garbage_name"],
                "category_id": r["category_id"],
                "category_name": category_map.get(r["category_id"], "其他垃圾"),
                "confidence": round(r["confidence"], 2),
                "image_base64": r["image_base64"],
                "create_time": r["create_time"].strftime("%Y-%m-%d %H:%M:%S")
            })

        return res(200, "获取成功", data)
    except Exception as e:
        print("获取历史记录失败：", str(e))
        return res(500, "获取历史记录失败")

# ====================== 5.3 生成月度识别报告 ======================
REPORT_DIR = "./reports"
os.makedirs(REPORT_DIR, exist_ok=True)

@app.route('/api/report/generate', methods=['POST'])
@jwt_required()
def generate_report():
    """生成月度识别报告并返回下载地址"""
    user_id = get_jwt_identity()
    data = request.json
    month = data.get("month")  # 格式：2026-04

    if not month or len(month) != 7:
        return res(400, "月份参数格式错误，应为 2026-04")

    try:
        cur = mysql.connection.cursor()
        # 查询该用户该月的识别记录
        cur.execute("""
            SELECT garbage_name, category_id, confidence, create_time 
            FROM recognition_records 
            WHERE user_id=%s AND DATE_FORMAT(create_time, '%%Y-%%m')=%s
            ORDER BY create_time
        """, (int(user_id), month))
        records = cur.fetchall()

        if not records:
            return res(400, "该月份无识别记录，无法生成报告")

        # 统计数据
        total_count = len(records)
        category_count = {1:0, 2:0, 3:0, 4:0}
        category_map = {
            1: "可回收物",
            2: "有害垃圾",
            3: "厨余垃圾",
            4: "其他垃圾"
        }
        avg_confidence = 0
        for r in records:
            category_count[r["category_id"]] += 1
            avg_confidence += r["confidence"]
        avg_confidence = round(avg_confidence / total_count, 2)

        # 生成PDF文件
        pdf_filename = f"report_{user_id}_{month}_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(REPORT_DIR, pdf_filename)

        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        c.setFont("SimHei", 18)
        c.drawCentredString(width/2, height-50, "垃圾分类识别月度报告")
        c.setFont("SimHei", 12)
        c.drawCentredString(width/2, height-80, f"统计月份：{month}")
        c.drawCentredString(width/2, height-100, f"用户ID：{user_id}")

        # 统计信息
        c.setFont("SimHei", 14)
        c.drawString(50, height-150, "一、统计概况")
        c.setFont("SimHei", 12)
        c.drawString(70, height-180, f"识别总次数：{total_count} 次")
        c.drawString(70, height-200, f"平均置信度：{avg_confidence}")

        # 分类统计
        y_pos = height-230
        c.setFont("SimHei", 14)
        c.drawString(50, y_pos, "二、分类统计")
        y_pos -= 30
        c.setFont("SimHei", 12)
        for cid, cnt in category_count.items():
            if cnt > 0:
                c.drawString(70, y_pos, f"{category_map[cid]}：{cnt} 次")
                y_pos -= 20

        # 识别记录列表
        y_pos -= 20
        c.setFont("SimHei", 14)
        c.drawString(50, y_pos, "三、识别记录")
        y_pos -= 30
        c.setFont("SimHei", 10)
        for r in records[:20]:  # 最多显示20条
            time_str = r["create_time"].strftime("%Y-%m-%d %H:%M")
            line = f"{time_str} | {r['garbage_name']} | {category_map[r['category_id']]} | 置信度：{round(r['confidence'],2)}"
            c.drawString(70, y_pos, line)
            y_pos -= 15
            if y_pos < 50:
                c.showPage()
                y_pos = height-50

        c.save()

        # 构建可访问的下载地址（本地测试用）
        download_url = f"http://localhost:5000/reports/{pdf_filename}"

        return res(200, "报告生成成功", {
            "download_url": download_url,
            "month": month,
            "total_count": total_count,
            "avg_confidence": avg_confidence
        })

    except Exception as e:
        print("生成报告失败：", traceback.format_exc())
        return res(500, "生成报告失败")

# 提供静态文件访问，让前端能下载PDF
from flask import send_from_directory
@app.route('/reports/<filename>')
def download_report(filename):
    return send_from_directory(REPORT_DIR, filename)    

# ====================== 反馈 ======================
@app.route('/api/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    try:
        user_id = get_jwt_identity()
        data = request.json

        if not data:
            return res(400, "请求体不能为空")

        # 只保留：correct_category、content
        correct_category = data.get('correct_category')
        content = data.get('content', '')

        if not correct_category:
            return res(400, "缺少正确分类信息")

        # user_id 转 int
        user_id = int(user_id)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO feedbacks
            (user_id, correct_category, content, status)
            VALUES (%s, %s, %s, 'pending')
        """, (user_id, correct_category, content))
        mysql.connection.commit()
        cur.close()

        return res(200, "反馈提交成功")

    except ValueError:
        return res(400, "参数类型错误")
    except Exception as e:
        print("反馈提交失败：", traceback.format_exc())
        return res(500, f"提交失败：{str(e)}")

# ====================== 文章 ======================
@app.route('/api/article/list', methods=['GET'])
def article_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,title,cover,view,create_time FROM articles ORDER BY id DESC")
    return res(200, data=cur.fetchall())

@app.route('/api/article/detail/<int:id>', methods=['GET'])
def article_detail(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE articles SET view=view+1 WHERE id=%s", (id,))
    mysql.connection.commit()

    cur.execute("SELECT title,content,author,view,create_time FROM articles WHERE id=%s", (id,))
    return res(200, data=cur.fetchone())
# ====================== 文章管理 - 删除文章 ======================
@app.route('/api/admin/article/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def article_delete(id):
    user_id = get_jwt_identity()
    # 仅管理员可删除
    if not is_admin(user_id):
        return res(403, "无管理员权限")

    try:
        cur = mysql.connection.cursor()
        # 先判断文章是否存在
        cur.execute("SELECT id FROM articles WHERE id=%s", (id,))
        article = cur.fetchone()
        if not article:
            return res(404, "文章不存在")

        # 执行删除
        cur.execute("DELETE FROM articles WHERE id=%s", (id,))
        mysql.connection.commit()
        return res(200, "删除成功")
    except Exception as e:
        print("删除文章失败：", traceback.format_exc())
        return res(500, "删除失败")

# ====================== 管理后台（全部修复权限） ======================
# ====================== 数据大屏接口（完整实现） ======================
@app.route('/api/admin/dashboard/screen', methods=['GET'])
@jwt_required()
def admin_dashboard_screen():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return res(403, "无管理员权限")

    cur = mysql.connection.cursor()
    try:
        # 1. 基础统计卡片
        # 总用户数
        cur.execute("SELECT COUNT(*) AS total FROM users")
        total_users = cur.fetchone()['total']

        # 总识别次数
        cur.execute("SELECT COUNT(*) AS total FROM recognition_records")
        total_recognitions = cur.fetchone()['total']

        # 待处理反馈
        cur.execute("SELECT COUNT(*) AS total FROM feedbacks WHERE status='pending'")
        pending_feedbacks = cur.fetchone()['total']

        # 已处理反馈
        cur.execute("SELECT COUNT(*) AS total FROM feedbacks WHERE status!='pending'")
        handled_feedbacks = cur.fetchone()['total']

        # 2. 垃圾分类识别统计（饼图）
        cur.execute("""
            SELECT category_id, COUNT(*) AS count
            FROM recognition_records
            GROUP BY category_id
        """)
        category_raw = cur.fetchall()
        category_map = {1: "可回收物", 2: "有害垃圾", 3: "湿垃圾", 4: "干垃圾"}
        category_stats = []
        for item in category_raw:
            cid = item['category_id']
            category_stats.append({
                "name": category_map.get(cid, "干垃圾"),
                "value": item['count']
            })

        # 3. 近7天识别趋势（折线图）
        cur.execute("""
            SELECT DATE(create_time) AS date, COUNT(*) AS count
            FROM recognition_records
            WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
            GROUP BY DATE(create_time)
            ORDER BY DATE(create_time)
        """)
        trend_data = cur.fetchall()

        # 4. 识别最多的垃圾TOP10（柱状图）
        cur.execute("""
            SELECT garbage_name, COUNT(*) AS count
            FROM recognition_records
            GROUP BY garbage_name
            ORDER BY count DESC
            LIMIT 10
        """)
        top_garbage = cur.fetchall()

        # 5. 反馈状态统计
        cur.execute("""
            SELECT status, COUNT(*) AS count
            FROM feedbacks
            GROUP BY status
        """)
        feedback_status = cur.fetchall()

        # 6. 本月识别量
        cur.execute("""
            SELECT COUNT(*) AS count
            FROM recognition_records
            WHERE DATE_FORMAT(create_time, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')
        """)
        month_count = cur.fetchone()['count']

        return res(200, "数据大屏获取成功", {
            "cards": {
                "total_users": total_users,
                "total_recognitions": total_recognitions,
                "pending_feedbacks": pending_feedbacks,
                "handled_feedbacks": handled_feedbacks,
                "month_count": month_count
            },
            "category_stats": category_stats,
            "trend_7d": trend_data,
            "top_garbage": top_garbage,
            "feedback_status": feedback_status
        })

    except Exception as e:
        print("数据大屏异常：", traceback.format_exc())
        return res(500, "数据大屏获取失败")
    finally:
        cur.close()

# ====================== 反馈（纠错板块 - 完整版） ======================

# 管理员 - 获取反馈列表（修复：关联用户信息 + 统一返回格式）
@app.route('/api/admin/feedback/list', methods=['GET'])
@jwt_required()
def admin_feedback_list():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return res(403, "无权限")
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT f.id, f.user_id, u.phone, u.nickname, 
                   f.correct_category, f.content, f.status, 
                   f.audit_result, f.create_time 
            FROM feedbacks f
            LEFT JOIN users u ON f.user_id = u.id
            ORDER BY f.create_time DESC
        """)
        feedback_list = cur.fetchall()
        cur.close()
        return res(200, "获取成功", feedback_list)
    except Exception as e:
        print("获取反馈列表失败：", traceback.format_exc())
        return res(500, "获取失败")

# 管理员 - 审核反馈（最终兼容版）
@app.route('/api/admin/feedback/<int:id>/audit', methods=['PUT'])
@jwt_required()
def audit_feedback(id):
    admin_id = get_jwt_identity()
    try:
        if not is_admin(admin_id):
            return res(403, "无管理员权限")

        data = request.json
        status = data.get('status')
        audit_result = data.get('audit_result', '').strip()

        # 兼容前端传参：approved → resolved
        if status == "approved":
            status = "resolved"

        # 校验状态
        if status not in ['resolved', 'rejected']:
            return res(400, "状态只能是 resolved 或 rejected")

        # 驳回必须填原因
        if status == 'rejected' and not audit_result:
            return res(400, "驳回必须填写原因")

        cur = mysql.connection.cursor()
        cur.execute("SELECT status FROM feedbacks WHERE id=%s", (id,))
        record = cur.fetchone()
        
        if not record:
            return res(404, "反馈不存在")
        if record['status'] != 'pending':
            return res(400, "已处理，无法重复审核")

        # 更新数据库
        cur.execute("""
            UPDATE feedbacks 
            SET status=%s, audit_result=%s, admin_id=%s
            WHERE id=%s
        """, (status, audit_result, int(admin_id), id))
        mysql.connection.commit()
        cur.close()

        return res(200, "审核成功", {
            "id": id,
            "status": status
        })

    except Exception as e:
        print(traceback.format_exc())
        return res(500, "审核失败")
    
#管理员查询
@app.route('/api/admin/garbage/list', methods=['GET'])
@jwt_required()
def admin_garbage_list():
    if not is_admin(get_jwt_identity()):
        return res(403, "无权限")
    try:
        res_data = garbage_collection.get(include=["metadatas"])
        data = []
        for idx, mid in enumerate(res_data["ids"]):
            data.append({
                "id": mid,
                "name": res_data["metadatas"][idx]["name"],
                "category": res_data["metadatas"][idx]["category"]
            })
        return res(200, data=data)
    except:
        return res(500, "获取失败")

#管理员增加
@app.route('/api/admin/garbage/add', methods=['POST'])
@jwt_required()
def admin_garbage_add():
    if not is_admin(get_jwt_identity()):
        return res(403, "无权限")
    data = request.json
    name = data.get("name")
    category = data.get("category")
    if not name or not category:
        return res(400, "参数不全")

    import uuid
    new_id = str(uuid.uuid4())
    doc_text = f"{name} 属于 {category}"

    garbage_collection.add(
        ids=[new_id],
        documents=[doc_text],
        metadatas=[{"name": name, "category": category}]
    )
    return res(200, "添加成功")

# 修改垃圾
@app.route('/api/admin/garbage/<gid>/edit', methods=['PUT'])
@jwt_required()
def admin_garbage_edit(gid):
    if not is_admin(get_jwt_identity()):
        return res(403, "无权限")
    data = request.json
    name = data.get("name")
    category = data.get("category")
    if not name or not category:
        return res(400, "参数不全")

    doc_text = f"{name} 属于 {category}"
    garbage_collection.update(
        ids=[gid],
        documents=[doc_text],
        metadatas=[{"name": name, "category": category}]
    )
    return res(200, "修改成功")

# 删除垃圾
@app.route('/api/admin/garbage/<gid>/delete', methods=['DELETE'])
@jwt_required()
def admin_garbage_delete(gid):
    if not is_admin(get_jwt_identity()):
        return res(403, "无权限")
    garbage_collection.delete(ids=[gid])
    return res(200, "删除成功")

@app.route('/api/admin/article/publish', methods=['POST'])
@jwt_required()
def article_publish():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return res(403, "无权限")
        
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO articles(title,cover,content,author)
        VALUES(%s,%s,%s,%s)
    """, (data['title'], data.get('cover',''), data['content'], data.get('author','管理员')))
    mysql.connection.commit()
    return res(200, "发布成功")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)