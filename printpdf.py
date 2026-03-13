import io
import os
import datetime
import re
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader

# ─────────────────────────────────────────
# 1. ตั้งค่าฟอนต์ (เพิ่ม Emoji Font)
# ─────────────────────────────────────────
def _get_font(size, bold=False):
    paths = [
        "C:/Windows/Fonts/THSarabunNew Bold.ttf" if bold else "C:/Windows/Fonts/THSarabunNew.ttf",
        "C:/Windows/Fonts/tahomabd.ttf" if bold else "C:/Windows/Fonts/tahoma.ttf",
    ]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def _get_emoji_font(size):
    path = "C:/Windows/Fonts/seguiemj.ttf"
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return None

# ─────────────────────────────────────────
# 2. ฟังก์ชันวาดข้อความผสม Emoji  
# ─────────────────────────────────────────
def draw_text_with_emojis(draw, text, pos, font, emoji_font, fill):
    """ วาดข้อความที่มี Emoji ผสมอยู่ โดยสลับฟอนต์ให้อัตโนมัติ """
    x, y = pos
    # แยกส่วนข้อความกับ Emoji (Regex)
    parts = re.findall(r'[^\u2600-\u27BF\U0001f300-\U0001f6ff\U0001f900-\U0001f9ff]+|[\u2600-\u27BF\U0001f300-\U0001f6ff\U0001f900-\U0001f9ff]', text)
    
    # คำนวณความกว้างทั้งหมดเพื่อหาจุดเริ่ม  
    total_w = 0
    for part in parts:
        is_emoji = re.match(r'[\u2600-\u27BF\U0001f300-\U0001f6ff\U0001f900-\U0001f9ff]', part)
        f = emoji_font if (is_emoji and emoji_font) else font
        total_w += draw.textlength(part, font=f)

    curr_x = x - (total_w / 2) # เริ่มวาดจากซ้ายเพื่อให้ผลลัพธ์อยู่กึ่งกลาง
    for part in parts:
        is_emoji = re.match(r'[\u2600-\u27BF\U0001f300-\U0001f6ff\U0001f900-\U0001f9ff]', part)
        f = emoji_font if (is_emoji and emoji_font) else font
        # วาดข้อความ/Emoji
        draw.text((curr_x, y), part, font=f, fill=fill, anchor="lm")
        curr_x += draw.textlength(part, font=f)

# ─────────────────────────────────────────
# 3. ฟังก์ชันตัดบรรทัด 
# ─────────────────────────────────────────
def break_thai_text(text, max_chars=42):
    lines = []
    while len(text) > max_chars:
        cut_point = max_chars
        space_idx = text.rfind(' ', 0, cut_point)
        if space_idx != -1 and space_idx > 10: cut_point = space_idx
        lines.append(text[:cut_point].strip())
        text = text[cut_point:].strip()
    if text: lines.append(text)
    return lines

# ─────────────────────────────────────────
# 4. ฟังก์ชันหลัก
# ─────────────────────────────────────────
def export_fortune_pdf(
    username="สมชาย",
    birth_day=15, birth_month=8, birth_year=1999,
    cat_label="ความรัก",
    zodiac_label="♌ ราศีสิงห์",
    naksat_label="ปีเถาะ 🐰",
    fortune_text="...",
    save_path="fortune_fixed_emoji.pdf"
):
    DPI = 150
    W, H = int(8.27 * DPI), int(11.69 * DPI)
    colors = {"ความรัก": "#E83A5E", "การเงิน": "#28A745", "การงาน/การเรียน": "#3A7BD5", "โดยรวม": "#F9A826"}
    main_color = colors.get(cat_label, "#9370DB")

    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # ฟอนต์ที่ต้องใช้
    f_title = _get_font(65, True)
    f_name = _get_font(50, True)
    f_info = _get_font(30)
    f_emoji = _get_emoji_font(30) # ฟอนต์สำหรับ Emoji

    # Header
    draw.rectangle([0, 0, W, 220], fill=main_color)
    draw.text((W//2, 110), "Fortune Garden", font=f_title, fill="white", anchor="mm")

    # ชื่อและข้อมูล (วาดแบบผสม Emoji)
    draw.text((W//2, 300), f"คุณ {username}", font=f_name, fill=(30, 30, 30), anchor="mm")
    
    months = ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]
    date_text = f"เกิดวันที่ {birth_day} {months[birth_month-1]} {birth_year}"
    draw.text((W//2, 360), date_text, font=f_info, fill=(100, 100, 100), anchor="mm")

    # วาดบรรทัด ราศี/นักษัตร ที่มี Emoji
    draw_text_with_emojis(draw, f"{zodiac_label}  |  {naksat_label}", (W//2, 410), f_info, f_emoji, (80, 80, 80))

    # เนื้อหาคำทำนาย
    draw.text((W//2, 520), f"คำทำนายด้าน {cat_label}", font=_get_font(42, True), fill=main_color, anchor="mm")
    
    wrapped_lines = break_thai_text(fortune_text, 42)
    y_text = 600
    for line in wrapped_lines:
        draw.text((W//2, y_text), line, font=_get_font(36), fill=(50, 50, 50), anchor="mm")
        y_text += 70

    # บันทึกเป็น PDF
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    c = rl_canvas.Canvas(save_path, pagesize=A4)
    c.drawImage(ImageReader(buf), 0, 0, width=A4[0], height=A4[1])
    c.save()
    print(f"เสร็จเรียบร้อย! Emoji ไม่เป็นสี่เหลี่ยมแล้ว: {save_path}")

if __name__ == "__main__":
    export_fortune_pdf(
        fortune_text="ช่วงนี้ความรักของคุณสดใสมาก มีเกณฑ์จะได้พบเนื้อคู่ที่รอคอยมานาน การงานราบรื่นไร้อุปสรรค"
    )