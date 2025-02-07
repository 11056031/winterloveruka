# -----------------------
# 匯入flask及db模組
# -----------------------
from flask import Flask, render_template
import logging

# -----------------------
# 匯入藍圖
# -----------------------
from services.rukapic import ruakpic_bp
from services.rukatalk import rukatalk_bp

# -----------------------
# 配置日志
# -----------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------
# 產生一個Flask網站物件
# -----------------------
app = Flask(__name__)
app.secret_key = 'ruka_jason_2002032020060203'  # 替換為隨機生成的安全密鑰

# -----------------------
# 註冊服務
# -----------------------
app.register_blueprint(ruakpic_bp, url_prefix='/rukapic')
app.register_blueprint(rukatalk_bp, url_prefix='/rukatalk')

# -----------------------
# 在網站中定義路由
# -----------------------
# 主畫面
@app.route('/')
def index():
    return render_template('index.html')

# -----------------------
# 啟動Flask網站
# -----------------------
if __name__ == '__main__':
    # 判斷模式並輸出提示
    if app.config["DEBUG"]:
        logging.info("應用正在開發模式中運行")
    else:
        logging.info("應用正在生產模式中運行")

    # 啟動應用
    app.run(debug=True)
