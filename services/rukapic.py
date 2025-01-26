from flask import request, render_template, Blueprint, send_file, redirect, url_for, session
import os
import torch
import uuid
import numpy as np
from torchvision.transforms.functional import normalize
from PIL import Image
from transformers import AutoModelForImageSegmentation
import torch.nn.functional as F
from skimage import io as skio
import logging

# 配置日志
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# 產生藍圖
ruakpic_bp = Blueprint('ruakpic_bp', __name__)

# 加载模型
model = AutoModelForImageSegmentation.from_pretrained("briaai/RMBG-1.4", trust_remote_code=True)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)


# 第一步
@ruakpic_bp.route('/step1', methods=['GET', 'POST'])
def ruakpic_step1():
    if request.method == 'POST':
        uploaded_file = request.files['uploaded_image']
        if uploaded_file:
            temp_path = "static/temp"
            os.makedirs(temp_path, exist_ok=True)
            unique_filename = f"{uuid.uuid4().hex}.png"
            file_path = os.path.join(temp_path, unique_filename)
            uploaded_file.save(file_path)

            # 保存文件名到 session
            session['uploaded_file_name'] = unique_filename

            # 重定向到第二步
            return redirect(url_for('ruakpic_bp.ruakpic_step2'))

    return render_template('rukapic/rukas1.html')




def preprocess_image(im: np.ndarray, model_input_size: list) -> torch.Tensor:
    if len(im.shape) < 3:
        im = im[:, :, np.newaxis]
    im_tensor = torch.tensor(im, dtype=torch.float32).permute(2, 0, 1)
    im_tensor = F.interpolate(torch.unsqueeze(im_tensor, 0), size=model_input_size, mode='bilinear')
    image = torch.divide(im_tensor, 255.0)
    image = normalize(image, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])
    return image

def postprocess_image(result: torch.Tensor, im_size: list) -> np.ndarray:
    result = torch.squeeze(F.interpolate(result, size=im_size, mode='bilinear'), 0)
    ma = torch.max(result)
    mi = torch.min(result)
    result = (result - mi) / (ma - mi)
    im_array = (result * 255).permute(1, 2, 0).cpu().data.numpy().astype(np.uint8)
    return np.squeeze(im_array)

# 第二步
@ruakpic_bp.route('/step2', methods=['GET'])
def ruakpic_step2():
    error = None
    result_image_path = None

    try:
        # 从 session 获取文件名
        file_name = session.get('uploaded_file_name')
        if not file_name:
            error = "未找到上傳的圖片，請返回上一步重新上傳。"
            return render_template('rukapic/rukas2.html', error=error)

        file_path = os.path.join("static/temp", file_name)
        if not os.path.exists(file_path):
            error = "未找到上傳的圖片，請返回上一步重新上傳。"
            return render_template('rukapic/rukas2.html', error=error)

        # 加载图片并预处理
        orig_im = skio.imread(file_path)
        orig_im_size = orig_im.shape[:2]
        model_input_size = [512, 512]  # 根据模型实际需要调整
        image = preprocess_image(orig_im, model_input_size).to(device)

        # 推理
        with torch.no_grad():
            result = model(image)

        # 后处理
        result_image = postprocess_image(result[0][0], orig_im_size)
        result_filename = f"result_{uuid.uuid4().hex}.png"
        result_path = os.path.join("static/temp", result_filename)

        # 保存处理后的图片
        pil_mask_im = Image.fromarray(result_image)
        orig_image = Image.open(file_path)
        no_bg_image = orig_image.copy()
        no_bg_image.putalpha(pil_mask_im)
        no_bg_image.save(result_path)

        # 生成图片的 URL
        result_image_path = url_for('static', filename=f"temp/{result_filename}")
    except Exception as e:
        logging.error("圖片處理失敗", exc_info=True)
        error = f"圖片處理失敗：{str(e)}"

    return render_template('rukapic/rukas2.html', result_image_path=result_image_path, error=error)


