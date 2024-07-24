

from flask import Blueprint, jsonify, request, current_app
from util.tools import insertqr_word, save_pth
from util.conn import get_db_connection, close_connection
from datetime import datetime


submit_bp = Blueprint("submit", __name__)


@submit_bp.route("/submit", methods=["POST"])
def submit_document():
    """
    提交申请接口
    ---
    tags:
        - Submit API
    parameters:
        - in: formData
          name: submitter
          type: string
          required: true
          description: 成果申报人
        - in: formData
          name: tool
          type: string
          required: true
          description: 成果生产工具
        - in: formData
          name: title
          type: string
          required: true
          description: 成果标题
        - in: formData
          name: introduction
          type: string
          required: true
          description: 成果内容简介
        - in: formData
          name: date
          type: string
          required: true
          description: 成果生成日期
        - in: formData
          name: file
          type: file
          required: true
          description: 成果文件
    responses:
        200:
            description: 成功提交申请
    """
    submitter = request.form["submitter"]
    production_tool = request.form["tool"]
    title = request.form["title"]
    introduction = request.form["introduction"]
    completion_date = request.form["date"]
    file = request.files["file"]  # 将文件内容读取为二进制数据

    form_data = { # 二维码内容
        "成果申报人": submitter,
        "成果标题": title,
        "成果内容简介": introduction,
        "成果生产工具": production_tool,
        "成果生成日期": completion_date,
    }
    print("表单内容：", form_data)

    print("生成新文件名的存储路径")
    word_file_path = save_pth(file, submitter, title, current_app.config["UPLOAD_FILE"])
    
    print('要嵌入二维码的文件地址：', word_file_path)
    insertqr_word(form_data, word_file_path) # 生成二维码 嵌入文档

    conn, cursor = get_db_connection()  # 表单记录存入库
    insert_query = """
            INSERT INTO documents 
                (submitter, completion_date, production_tool, title,
                introduction, approval_status, submit_time) 
            VALUES 
                (%s,%s,%s,%s,%s,%s,%s)
        """
    cursor.execute(
        insert_query,
        (
            submitter,
            completion_date,
            production_tool,
            title,
            introduction,
            "未审批",
            datetime.now(),
        ),
    )
    close_connection(conn, cursor)
    return jsonify({"message": "申请人成果提交成功"})


@submit_bp.route("/history", methods=["GET"])
def get_history():
    
    """
    获取申请历史接口
    ---
    tags:
        - Submit API
    parameters:
        - in: query
          name: submitter
          type: string
          required: true
          description: 成果申报人
        - in: query
          name: status
          type: string
          required: true
          description: 审批状态
    responses:
        200:
            description: 成功获取申请历史，返回历史记录
    """
    
    submitter = request.args.get("submitter")
    status = request.args.get("status")
    print(submitter, status)

    conn, cursor = get_db_connection()
    query = """
        SELECT * FROM documents 
        WHERE submitter = %s AND approval_status = %s
    """
    cursor.execute(query, (submitter, status))
    results = cursor.fetchall()
    print(results)
    close_connection(conn, cursor)

    docs = []
    for result in results:
        docs.append(
            {
                "成果号": result[0],
                "成果申报人": result[1],
                "成果标题": result[4],
                "成果生成日期": result[2],
                "审批状态": result[7],
                "成果批注": result[8],
            }
        )
    print("docs", docs)
    return jsonify(docs)


# 撤回申请
@submit_bp.route("/delete", methods=["DELETE"])
def delete_document():
    """
    撤回申请接口
    ---
    tags:
        - Submit API
    parameters:
        - in: query
          name: 成果号
          type: string
          required: true
          description: 成果号
    responses:
        200:
            description: 成功删除申请
    """
    id = request.args.get("成果号")
    conn, cursor = get_db_connection()
    cursor.execute("DELETE FROM documents WHERE id = %s", (id,))
    conn.commit()
    close_connection(conn, cursor)
    return jsonify({"message": "删除成功"}), 200