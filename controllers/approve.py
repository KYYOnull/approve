from flask import Blueprint, jsonify, request, current_app
from util.tools import ocr_paddle
from util.conn import get_db_connection, close_connection
import jwt
from datetime import datetime


approve_bp = Blueprint("approve", __name__)


@approve_bp.route("/ocr", methods=["POST"])
def ocr():
    """
    OCR识别接口
    ---
    tags:
        - Approve API
    consumes:
        - multipart/form-data
    parameters:
        - in: formData
          name: image
          type: file
          required: true
          description: 待识别的图片文件
    responses:
        200:
            description: OCR识别成功，返回识别结果
    """
    image = request.files["image"]
    photo_path = current_app.config["UPLOAD_IMG"] + "/" + image.filename
    print(photo_path)
    image.save(photo_path)
    text = ocr_paddle(photo_path)  # 识别
    print(text)
    return jsonify(text)


# 审批
@approve_bp.route("/approve", methods=["GET"])
def get_pending_document():
    """
    获取未审批文档列表接口
    ---
    tags:
        - Approve API
    responses:
        200:
            description: 成功获取未审批文档列表，返回文档信息
    """
    conn, cursor = get_db_connection()
    cursor.execute("SELECT * FROM documents WHERE approval_status = '未审批'")
    results = cursor.fetchall()  # 所有未审批
    print(results)
    close_connection(conn, cursor)

    docs = []
    for result in results:
        docs.append(
            {
                "成果号": result[0],
                "成果申报人": result[1],
                "成果标题": result[4],
                "成果内容简介": result[5],
                "成果生产工具": result[3],
                "成果生成日期": result[2],
                "审批状态": result[7],
            }
        )
    response = {"message": "拉取未审批的文档列表", "documents": docs}

    return jsonify(response)


# 提交批改
@approve_bp.route("/update", methods=["POST"])
def update_document():
    """
    提交批改接口
    ---
    tags:
        - Approve API
    parameters:
        - in: body
          name: update_data
          schema:
            type: object
            properties:
              id:
                type: string
                required: true
                description: 文档ID
              newStatus:
                type: string
                required: true
                description: 新的审批状态
              note:
                type: string
                description: 批改备注
    responses:
        200:
            description: 批改申请表提交成功
    """
    id = request.json.get("id")
    newStatus = request.json.get("newStatus")
    note = request.json.get("note")
    print(id, newStatus, note)

    token = request.cookies.get("token")
    data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    admin_username = data["username"]
    print(admin_username)

    conn, cursor = get_db_connection()
    update_query = """
        UPDATE documents
        SET approval_status=%s, note=%s, admin=%s, approval_time=%s
        WHERE id = %s
    """
    cursor.execute(update_query, (newStatus, note, admin_username, datetime.now(), id))
    print("修改成功")
    close_connection(conn, cursor)

    response = {"message": "{}批改申请表成功".format(admin_username)}
    print(response)
    return jsonify(response)
