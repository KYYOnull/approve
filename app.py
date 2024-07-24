

from flask import Flask
from controllers import login, submit, approve, common, findPth
from flasgger import Swagger


app = Flask(__name__)  # Flask 应用实例
Swagger(app)

UPLOAD_FILE = "uploads/submit"  # 待审批目录
UPLOAD_IMG = "uploads/photos"  # ocr目录
SECRET_KEY = 'KYYO'
app.config["UPLOAD_FILE"] = UPLOAD_FILE
app.config["UPLOAD_IMG"] = UPLOAD_IMG
app.config['SECRET_KEY'] = SECRET_KEY


app.register_blueprint(login.login_bp)
app.register_blueprint(submit.submit_bp)
app.register_blueprint(approve.approve_bp)
app.register_blueprint(common.common_bp)
app.register_blueprint(findPth.findpth_bp)


if __name__ == "__main__":
    app.run(debug=True)  # host='0.0.0.0', port=5000,
