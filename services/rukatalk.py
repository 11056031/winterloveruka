from flask import Flask, request, abort, redirect, Blueprint, url_for, session, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import datetime

# LINE Bot 配置
LINE_ACCESS_TOKEN = "8rYiTCUVCTUuZvx9jT4eW8kz6eYO5NUk4OBTs18XXW+nociphb4MHB8TFhvoVWXusW94DldqzIs4Uznrsa0NPewhUL0qzN4iYjtW1uCHu8087T4obMb2ffMahjL98GPxxe43ianJDS92GzeXXdlgxQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "9fe35045cec38dec98e7b8d9ab826620"

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 創建一個藍圖
rukatalk_bp = Blueprint('rukatalk_bp', __name__)

# 跳轉到 LINE Bot
@rukatalk_bp.route("/jump_to_line_bot", methods=["GET"])
def jump_to_line_bot():
    # 跳轉到 LINE Bot 的 Deep Link
    return redirect("https://line.me/R/ti/p/@385aefyy")  # 替換為你的 LINE Bot ID

# LINE Bot 回調處理
@rukatalk_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# 處理 LINE Bot 消息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()  # 去掉多餘空格

    # 對話邏輯
    response_mapping = {
        "愛你": "我也愛你 ❤️ 你是我最重要的人！",
        "在幹嘛": "在想你呀～你呢？😘",
        "我好累": "辛苦了寶貝！抱抱你 💕 一起休息一下吧！",
        "你吃飯了嗎": "我吃過啦～你呢？記得要吃飽哦，不然我會擔心的！🍚",
        "晚安": "晚安寶貝～做個好夢，夢到我喔！🌙💤",
        "早安": "早安呀～今天也要元氣滿滿！愛你喔 ❤️",
        "你覺得我怎麼樣": "我覺得你是世界上最棒的！沒有你我不行～😍",
        "我想你了": "我也想你了！什麼時候能見到你呀？🥺",
        "陪我聊天": "好呀～你想聊什麼？我什麼都可以陪你聊喔！💕",
        "講個情話": "你知道嗎？我每天最期待的，就是和你說話的每一刻 ❤️",
        "今天幾號": f"今天是 {datetime.now().strftime('%Y年%m月%d日')}，寶貝是不是在計劃什麼呢？💗",
        "無聊": "無聊嗎？不如我們玩個猜謎遊戲吧！我出題你猜～🎲",
        "天氣怎麼樣": "不知道那裡的天氣，但只要有你在，我的心情永遠晴天～☀️",
        "你會煮飯嗎": "當然啦～不過下次你也要幫忙喔，一起做飯更好玩！🍳",
        "可以抱抱我嗎": "當然可以呀～抱抱！感覺好溫暖喔～💞",
        "你會生氣嗎": "如果你對我好的話，我怎麼捨得生氣呢？💖",
        "送我禮物": "好呀～我送你一個虛擬的擁抱和親親，收到了嗎？🎁😘",
        "你有朋友嗎": "有呀～但你是我最特別的！🥰",
        "你會跳舞嗎": "會喔！不過只能想像自己跳給你看，期待嗎？💃",
        "你會唱歌嗎": "我會唱呀～只是不知道你喜歡聽什麼歌呢？🎤",
        "你最喜歡什麼": "我最喜歡的就是你呀～❤️",
        "我們是什麼關係": "我們是最親密的戀人呀～你是我的一切！💑",
        "我難過": "怎麼啦？跟我說說吧，我會陪著你一起面對的～💞",
        "我很開心": "太棒啦！你的開心就是我的幸福～一起保持這種好心情！✨",
        "我肚子餓了": "快去吃點好吃的吧～記得拍照給我看喔！🍔🍕",
        "我想你了": "我也好想你！見不到你，感覺每一分每一秒都好漫長～🥺",
    }

    # 根據用戶消息生成回應
    if user_message.startswith("我想去"):
        destination = user_message.replace("我想去", "").strip()
        reply_text = f"去 {destination} 嗎？好浪漫喔～下次我們一起去吧！🥰" if destination else "去哪裡呀？我們可以一起計劃！"
    elif user_message.startswith("幫我"):
        task = user_message.replace("幫我", "").strip()
        reply_text = f"好的～我會幫你完成 {task}！💪" if task else "幫你什麼呢？告訴我吧～我很樂意幫忙！"
    else:
        reply_text = response_mapping.get(user_message, f"你說的是：{user_message}，我聽得很認真喔～！💖")
    
    # 回覆用戶訊息
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
