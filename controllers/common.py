from flask import Blueprint, request, current_app, send_file
import os


common_bp = Blueprint("common", __name__)


# 共用下载接口
# GET /download?submitter=kyyo&title=一种成果
@common_bp.route("/download", methods=["GET"])
def download_doc():
    """
    公共下载接口 使用申报人名+成果名 获得审批表
    ---
    tags:
        - Common API
    parameters:
        - name: submitter
          in: query
          type: string
          required: true
          description: 申报人名
        - name: title
          in: query
          type: string
          required: true
          description: 成果名
    responses:
        200:
            description: 申报表下载
    """
    submitter = request.args.get("submitter")
    title = request.args.get("title")

    doc_name = submitter + "_" + title + ".docx"
    doc_pth = os.path.join(current_app.config["UPLOAD_FILE"], doc_name)
    print("doc_pth", doc_pth)  # uploads\submit\sdf_sdf.docx

    return send_file(doc_pth, as_attachment=True)
