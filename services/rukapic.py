from flask import request, render_template, Blueprint, redirect, url_for, session
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
from diffusers import StableDiffusionXLImg2ImgPipeline
from diffusers.utils import load_image

# 配置日誌
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# 創建藍圖
ruakpic_bp = Blueprint('ruakpic_bp', __name__)

# 設定快取路徑
HF_CACHE_DIR = r"D:\暫時\huggingface_cache"
os.environ["HF_HOME"] = HF_CACHE_DIR

# 臨時檔案夾路徑
TEMP_PATH = os.path.join(r"C:\Users\berry\Desktop\test\winterloveruka\static", "temp")
os.makedirs(TEMP_PATH, exist_ok=True)

# 加載分割模型
model = AutoModelForImageSegmentation.from_pretrained("briaai/RMBG-1.4", trust_remote_code=True)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)

# 圖像預處理函數
def preprocess_image(im: np.ndarray, model_input_size: list) -> torch.Tensor:
    if len(im.shape) < 3:
        im = im[:, :, np.newaxis]
    im_tensor = torch.tensor(im, dtype=torch.float32).permute(2, 0, 1)
    im_tensor = F.interpolate(torch.unsqueeze(im_tensor, 0), size=model_input_size, mode='bilinear')
    image = torch.divide(im_tensor, 255.0)
    image = normalize(image, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])
    return image

# 圖像後處理函數
def postprocess_image(result: torch.Tensor, im_size: list) -> np.ndarray:
    result = torch.squeeze(F.interpolate(result, size=im_size, mode='bilinear'), 0)
    ma = torch.max(result)
    mi = torch.min(result)
    result = (result - mi) / (ma - mi)
    im_array = (result * 255).permute(1, 2, 0).cpu().data.numpy().astype(np.uint8)
    return np.squeeze(im_array)

# 第一步：上傳圖片
@ruakpic_bp.route('/step1', methods=['GET', 'POST'])
def ruakpic_step1():
    if request.method == 'POST':
        uploaded_file = request.files['uploaded_image']
        if uploaded_file:
            unique_filename = f"{uuid.uuid4().hex}.png"
            file_path = os.path.join(TEMP_PATH, unique_filename)
            uploaded_file.save(file_path)

            # 將檔案名稱保存至 session
            session['uploaded_file_name'] = unique_filename
            return redirect(url_for('ruakpic_bp.ruakpic_step2'))

    return render_template('rukapic/rukas1.html')

# 第二步：處理圖片
@ruakpic_bp.route('/step2', methods=['GET'])
def ruakpic_step2():
    error = None
    result_image_path = None

    try:
        file_name = session.get('uploaded_file_name')
        if not file_name:
            raise FileNotFoundError("未找到上傳的圖片，請返回上一步重新上傳。")

        file_path = os.path.join(TEMP_PATH, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError("未找到上傳的圖片，請返回上一步重新上傳。")

        # 加載並處理圖片
        orig_im = skio.imread(file_path)
        orig_im_size = orig_im.shape[:2]
        model_input_size = [512, 512]
        image = preprocess_image(orig_im, model_input_size).to(device)

        # 推理
        with torch.no_grad():
            result = model(image)

        # 後處理
        result_image = postprocess_image(result[0][0], orig_im_size)
        result_filename = f"result_{uuid.uuid4().hex}.png"
        result_path = os.path.join(TEMP_PATH, result_filename)

        # 保存處理後的圖片
        pil_mask_im = Image.fromarray(result_image)
        orig_image = Image.open(file_path)
        no_bg_image = orig_image.copy()
        no_bg_image.putalpha(pil_mask_im)
        no_bg_image.save(result_path)

        result_image_path = url_for('static', filename=f"temp/{result_filename}")
    except Exception as e:
        logging.error("圖片處理失敗", exc_info=True)
        error = str(e)

    return render_template('rukapic/rukas2.html', result_image_path=result_image_path, error=error)

# 第三步：輸入關鍵字
@ruakpic_bp.route('/step3', methods=['GET', 'POST'])
def ruakpic_step3():
    if request.method == 'POST':
        prompt = request.form.get('prompt', 'a simple photo')
        session['prompt'] = prompt
        return redirect(url_for('ruakpic_bp.ruakpic_step5'))

    return render_template('rukapic/rukas3.html')

# 第五步：生成圖像
@ruakpic_bp.route('/step5', methods=['GET'])
def ruakpic_step5():
    error = None
    generated_image_path = None

    try:
        file_name = session.get('uploaded_file_name')
        prompt = session.get('prompt', 'a simple photo')

        if not file_name:
            raise FileNotFoundError("未找到上傳的圖片，請返回上一步重新上傳。")

        file_path = os.path.join(TEMP_PATH, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError("未找到上傳的圖片，請返回上一步重新上傳。")

        # 加載初始圖像
        init_image = load_image(file_path)

        # 加載生成模型
        pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-refiner-1.0",
            torch_dtype=torch.float16,  # 使用 float16 提高 GPU 性能
            cache_dir=HF_CACHE_DIR
        )

        # 檢查 GPU 是否可用
        if torch.cuda.is_available():
            pipe.to("cuda")  # 將模型加載到 GPU
            print("模型已加載至 GPU。")
        else:
            raise RuntimeError("未檢測到 NVIDIA GPU，請確保有可用的 GPU 並安裝正確的驅動程序。")

        # 使用用戶輸入的 prompt 生成圖像
        images = pipe(prompt, image=init_image).images

        # 保存生成的圖像
        generated_filename = f"generated_{uuid.uuid4().hex}.png"
        result_path = os.path.join(TEMP_PATH, generated_filename)
        images[0].save(result_path)

        # 轉換為靜態文件的 URL
        generated_image_path = url_for('static', filename=f"temp/{generated_filename}")
    except Exception as e:
        logging.error("圖片生成失敗", exc_info=True)
        error = f"圖片生成失敗：{e}"

    return render_template('rukapic/rukas5.html', generated_image_path=generated_image_path, error=error)
