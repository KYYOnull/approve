from flask import Blueprint, jsonify, request, render_template, current_app
import jwt
import datetime

login_bp = Blueprint("login", __name__)

users = {
    "applicant": [
        {"username": "王小桃", "password": "123456"},
        {"username": "DJTrump", "password": "123123"},
    ],
    "approver": [
        {"username": "玛露希尔", "password": "777777"},
        {"username": "科比欧布莱恩", "password": "666666"},
    ],
}


# 系统入口
@login_bp.route("/")
def index():
    return render_template("index.html")

# 两套登录页
@login_bp.route("/loginApplicant", methods=["GET"])
def loginApplicant():
    return render_template("loginApplicant.html")

@login_bp.route("/loginApprover", methods=["GET"])
def loginApprover():
    return render_template("loginApprover.html")


# 业务页面 申请人/审批人
@login_bp.route("/applicant", methods=["POST", "GET"])
def applicant():
    return render_template("applicant.html")


@login_bp.route("/approver")
def approver():
    return render_template("approver.html")


@login_bp.route("/login/<role>", methods=["POST"])
def login(role):  # 处理登录逻辑，包括注册和签发
    """
    登录接口
    ---
    tags:
        - Login API
    parameters:
        - name: role
          in: path
          type: string
          required: true
          description: 用户角色
        - in: body
          name: login_data
          schema:
            type: object
            properties:
              username:
                type: string
                required: true
                description: 用户名
              password:
                type: string
                required: true
                description: 密码
    responses:
        200:
            description: 登录成功
        401:
            description: 用户不存在或密码错误
    """

    data = request.get_json()
    usnm = data.get("username")
    pswd = data.get("password")

    if role not in users:
        return jsonify({"message": "不存在该身份"})

    print(users[role])
    for user in users[role]:  # for obj in lst
        if usnm == user["username"] and pswd == user["password"]:
            token = jwt.encode(
                {
                    "username": usnm,
                    "exp": datetime.datetime.now() + datetime.timedelta(hours=1),
                },
                current_app.config["SECRET_KEY"],
                algorithm="HS256",
            )

            response = jsonify({"message": "登录成功", "token": token})
            response.set_cookie("token", token)  # 放入前端 localstorage
            return response

    return jsonify({"message": "不存在该用户"})


@login_bp.route("/register", methods=["POST"])
def register():
    """
    注册接口
    ---
    tags:
        - Login API
    responses:
        401:
            description: 注册成功
    """
    return jsonify({"message": "注册成功"}), 401
