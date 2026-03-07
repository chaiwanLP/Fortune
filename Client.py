from customtkinter import *
from PIL import Image, ImageDraw, ImageFilter
import random
import os
import threading
import socket
import math

set_appearance_mode("light")
set_default_color_theme("green")
set_widget_scaling(1.2)   # ขยาย widget พอดีๆ
set_window_scaling(1.2)   # ขยายทั้งหน้าต่าง

# ─────────────────────────────────────────
#  Server Config
# ─────────────────────────────────────────
SERVER_IP   = "127.0.0.1"
SERVER_PORT = 5000
UDP_TIMEOUT = 5

CATEGORY_TO_SERVER_KEY = {
    "overall": "general",
    "love":    "love",
    "money":   "money",
    "work":    "education",
}


def udp_ask_fortune(category_key: str) -> str | None:
    server_key = CATEGORY_TO_SERVER_KEY.get(category_key, "general")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(UDP_TIMEOUT)
        sock.sendto(server_key.encode("utf-8"), (SERVER_IP, SERVER_PORT))
        data, _ = sock.recvfrom(4096)
        sock.close()
        return data.decode("utf-8")
    except Exception as e:
        print(f"[UDP ERROR] {e}")
        return None


# ─────────────────────────────────────────
#  ฟอนต์กลาง - ปรับปรุงใหม่ทั้งหมด
# ─────────────────────────────────────────
FONTS = {
    # หัวข้อหลัก
    "display_large": ("Kanit", 36, "bold"),      # หัวข้อแอปใหญ่
    "display": ("Kanit", 32, "bold"),            # หัวข้อแอป
    
    # หัวข้อหน้า
    "title_large": ("Kanit", 24, "bold"),        # หัวข้อใหญ่
    "title": ("Kanit", 20, "bold"),              # หัวข้อปกติ
    "title_small": ("Kanit", 18, "bold"),        # หัวข้อเล็ก
    
    # เนื้อหา
    "body_large": ("Kanit", 16),                  # เนื้อหาใหญ่
    "body": ("Kanit", 15),                        # เนื้อหาปกติ
    "body_small": ("Kanit", 14),                  # เนื้อหาเล็ก
    "caption": ("Kanit", 13),                     # คำอธิบาย
    "caption_small": ("Kanit", 12),               # คำอธิบายเล็ก
    
    # ปุ่ม
    "button_large": ("Kanit", 16, "bold"),       # ปุ่มใหญ่
    "button": ("Kanit", 15, "bold"),              # ปุ่มปกติ
    "button_small": ("Kanit", 13, "bold"),        # ปุ่มเล็ก
    
    # พิเศษ
    "badge": ("Kanit", 14, "bold"),               # badge
    "quote": ("Kanit", 14, "italic"),             # คำคม
    "emoji_large": ("Arial", 60),                 # emoji ใหญ่
    "emoji_medium": ("Arial", 48),                # emoji กลาง
    "emoji_small": ("Arial", 32),                 # emoji เล็ก
}

# จัดกลุ่มฟอนต์ให้เรียกใช้งานง่าย
F_APP_TITLE = FONTS["display"]
F_PAGE_TITLE = FONTS["title_large"]
F_SUBTITLE = FONTS["body"]
F_CARD_TITLE = FONTS["title_small"]
F_CARD_DESC = FONTS["caption"]
F_BTN_MAIN = FONTS["button_large"]
F_BTN_SEC = FONTS["button"]
F_BTN_SMALL = FONTS["button_small"]
F_ZODIAC_NAME = FONTS["title_large"]
F_ZODIAC_DATE = FONTS["caption"]
F_FORTUNE_H = FONTS["title"]
F_FORTUNE_B = FONTS["body_large"]
F_LUCKY_KEY = FONTS["caption"]
F_LUCKY_VAL = FONTS["body"]
F_BADGE = FONTS["badge"]
F_ICON_BIG = FONTS["emoji_large"]
F_ICON_CAT = FONTS["emoji_medium"]
F_QUOTE = FONTS["quote"]
F_BODY = FONTS["body"]  # ✅ เพิ่มบรรทัดนี้เข้าไป


# ─────────────────────────────────────────
#  ข้อมูลคงที่ (ปรับปรุงสีให้สวยขึ้น)
# ─────────────────────────────────────────
CATEGORIES = [
    {
        "key": "overall",
        "icon": "🌟",
        "label": "โดยรวม",
        "desc": "ดวงชะตาภาพรวมชีวิต",
        "color": "#F9A826",  # ทองสวย
        "light": "#FFF4E0",
        "gradient": ["#F9A826", "#FFD966"]
    },
    {
        "key": "love",
        "icon": "💖",
        "label": "ความรัก",
        "desc": "ความสัมพันธ์และหัวใจ",
        "color": "#E83A5E",  # ชมพูสวย
        "light": "#FFE8F0",
        "gradient": ["#E83A5E", "#FF6B8B"]
    },
    {
        "key": "money",
        "icon": "💰",
        "label": "การเงิน",
        "desc": "โชคลาภและทรัพย์สิน",
        "color": "#28A745",  # เขียวสวย
        "light": "#E8F5E9",
        "gradient": ["#28A745", "#5CB85C"]
    },
    {
        "key": "work",
        "icon": "📚",
        "label": "การงาน/การเรียน",
        "desc": "อาชีพ การศึกษา และความก้าวหน้า",
        "color": "#3A7BD5",  # น้ำเงินสวย
        "light": "#E8F0FE",
        "gradient": ["#3A7BD5", "#6C9BD2"]
    },
]

FORTUNES: dict[str, list[dict]] = {
    "overall": [
        {
            "icon": "🌟", 
            "title": "โชคดีที่สุดในวันนี้ ✨",
            "body": "วันนี้ดาวเคราะห์เรียงตัวเป็นมงคล\nสิ่งที่ตั้งใจไว้มีโอกาสสำเร็จสูงมาก\nอย่าลังเลที่จะลงมือทำในสิ่งที่ฝันไว้",
            "lucky_color": "🔴 สีแดง", 
            "lucky_number": "7", 
            "lucky_day": "วันอังคาร",
            "advice": "ความเชื่อมั่นคือกุญแจสู่ความสำเร็จ"
        },
        {
            "icon": "🌈", 
            "title": "มีความสุขสมหวัง 💫",
            "body": "พลังงานดีๆ ล้อมรอบคุณอยู่ในวันนี้\nทุกสิ่งที่คุณปรารถนาใกล้จะสมหวังแล้ว\nรอยยิ้มของคุณส่งต่อความสุขให้คนรอบข้าง",
            "lucky_color": "🌸 สีชมพูอ่อน", 
            "lucky_number": "6", 
            "lucky_day": "วันอาทิตย์",
            "advice": "ความสุขเล็กๆ คือของขวัญล้ำค่า"
        },
        {
            "icon": "✨", 
            "title": "สมหวังดังใจ 💕",
            "body": "จงเชื่อมั่นในพลังของตัวเองให้มากขึ้น\nความคิดบวกดึงดูดสิ่งดีๆ เข้ามาในชีวิต\nความฝันที่ตั้งใจไว้กำลังจะเป็นจริง",
            "lucky_color": "⚪ สีขาว", 
            "lucky_number": "11", 
            "lucky_day": "วันอาทิตย์",
            "advice": "คิดบวก ชีวิตก็บวก"
        },
        {
            "icon": "⭐", 
            "title": "พบเจอแต่สิ่งดีๆ 🌠",
            "body": "วันนี้เหมาะสำหรับการเริ่มต้นสิ่งใหม่\nคนรอบข้างพร้อมสนับสนุนคุณเต็มที่\nโอกาสดีๆ รอคุณอยู่ข้างนอก",
            "lucky_color": "🟡 สีส้มอ่อน", 
            "lucky_number": "1", 
            "lucky_day": "วันจันทร์",
            "advice": "ทุกวันคือการเริ่มต้นใหม่"
        },
    ],
    "love": [
        {
            "icon": "💖", 
            "title": "ความรักกำลังมาเยือน 💕",
            "body": "บุคคลพิเศษอาจปรากฏตัวในชีวิตคุณเร็วๆ นี้\nเปิดใจและแสดงตัวตนที่แท้จริงออกมา\nความสัมพันธ์ที่ดีเริ่มจากความจริงใจ",
            "lucky_color": "🩷 สีชมพู", 
            "lucky_number": "2", 
            "lucky_day": "วันศุกร์",
            "advice": "รักแท้ต้องการเวลาและความเข้าใจ"
        },
        {
            "icon": "🌹", 
            "title": "ความรักหวานชื่น 🥰",
            "body": "ความสัมพันธ์ของคุณกำลังพัฒนาไปในทางที่ดี\nบอกรักกันมากๆ และใส่ใจในรายละเอียดเล็กๆ\nความรักที่แท้จริงเติบโตจากการดูแลกัน",
            "lucky_color": "🔴 สีแดง", 
            "lucky_number": "14", 
            "lucky_day": "วันศุกร์",
            "advice": "รักคือการให้โดยไม่หวังผล"
        },
    ],
    "money": [
        {
            "icon": "💰", 
            "title": "การเงินดี มีโชคลาภ 💎",
            "body": "ดวงการเงินพุ่งสูงในช่วงนี้ อาจได้รับเงินพิเศษ\nหรือโอกาสทางธุรกิจที่น่าสนใจกำลังจะเข้ามา\nแต่ควรวางแผนใช้จ่ายอย่างรอบคอบด้วย",
            "lucky_color": "💛 สีเหลืองทอง", 
            "lucky_number": "8", 
            "lucky_day": "วันพุธ",
            "advice": "เงินทองเป็นของนอกกาย แต่จำเป็น"
        },
        {
            "icon": "🎉", 
            "title": "โชคลาภกำลังมา 🍀",
            "body": "ห้ามพลาดโอกาสที่กำลังจะมาถึงในเร็วๆ นี้\nอาจเป็นข่าวดีจากคนที่ไม่คาดฝัน\nเตรียมตัวให้พร้อมและเปิดรับสิ่งดีๆ",
            "lucky_color": "🟢 สีเขียว", 
            "lucky_number": "9", 
            "lucky_day": "วันเสาร์",
            "advice": "โอกาสมาแล้ว ต้องรีบคว้าไว้"
        },
    ],
    "work": [
        {
            "icon": "📚", 
            "title": "การงานก้าวหน้า 📈",
            "body": "ความพยายามของคุณกำลังจะออกดอกผล\nหัวหน้าหรือผู้ใหญ่มองเห็นคุณค่าในตัวคุณ\nอดทนและมุ่งมั่นต่อไป ความสำเร็จอยู่ไม่ไกล",
            "lucky_color": "🟤 สีน้ำตาล", 
            "lucky_number": "4", 
            "lucky_day": "วันพฤหัสบดี",
            "advice": "ความสำเร็จไม่มีลัด แต่มีทางเสมอ"
        },
        {
            "icon": "🏆", 
            "title": "ความสำเร็จอยู่ใกล้ 🎯",
            "body": "โปรเจกต์หรืองานที่ทำอยู่กำลังใกล้เสร็จสมบูรณ์\nผลงานของคุณจะได้รับการยอมรับจากคนรอบข้าง\nอย่าหยุดพัฒนาทักษะของตัวเอง",
            "lucky_color": "🔵 สีฟ้า", 
            "lucky_number": "1", 
            "lucky_day": "วันจันทร์",
            "advice": "จงภูมิใจในทุกก้าวที่เดินมา"
        },
    ],
}

ZODIAC_DATA = [
    ("♈ เมษ",   "🔥 ธาตุไฟ | กล้าหาญ", "#FF6B8B"),
    ("♉ พฤษภ",  "🌱 ธาตุดิน | มั่นคง", "#8BC34A"),
    ("♊ เมถุน", "☁️ ธาตุลม | ช่างคิด", "#FFB347"),
    ("♋ กรกฎ",  "💧 ธาตุน้ำ | อ่อนโยน", "#4FC3F7"),
    ("♌ สิงห์", "🔥 ธาตุไฟ | ผู้นำ", "#FFA726"),
    ("♍ กันย์", "🌱 ธาตุดิน | เจ้าระเบียบ", "#66BB6A"),
    ("♎ ตุล",   "☁️ ธาตุลม | ยุติธรรม", "#BA68C8"),
    ("♏ พิจิก", "💧 ธาตุน้ำ | ลึกลับ", "#EF5350"),
    ("♐ ธนู",   "🔥 ธาตุไฟ | รักอิสระ", "#7E57C2"),
    ("♑ มังกร", "🌱 ธาตุดิน | มุ่งมั่น", "#5C6BC0"),
    ("♒ กุมภ์", "☁️ ธาตุลม | สร้างสรรค์", "#26C6DA"),
    ("♓ มีน",   "💧 ธาตุน้ำ | ช่างฝัน", "#7986CB"),
]

FLOAT_EMOJIS = ["🌸", "🌼", "🌺", "✨", "🌷", "🦋", "🐞", "🍀", "⭐", "🌟"]
TITLE_COLORS = ["#FF1493", "#9370DB", "#4169E1", "#FF6347", "#FF69B4", "#FFD700"]
FLOWER_FILES = ["m1.png", "m2.png", "m3.png", "m4.png", "m5.png"]


# ─────────────────────────────────────────
#  Helper Functions
# ─────────────────────────────────────────
def adjust_color(hex_color: str, amount: int) -> str:
    if not hex_color.startswith("#"):
        return hex_color
    try:
        r = max(0, min(255, int(hex_color[1:3], 16) + amount))
        g = max(0, min(255, int(hex_color[3:5], 16) + amount))
        b = max(0, min(255, int(hex_color[5:7], 16) + amount))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


def load_bg(path: str, size=(800, 700)) -> CTkImage | None:
    try:
        img = Image.open(path).resize(size)
        return CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None


# ─────────────────────────────────────────
#  App
# ─────────────────────────────────────────
class FortuneGardenApp:
    def __init__(self):
        self.app = CTk()
        self.app.title("🌸 Fortune Garden - ดูดวงสไตล์ญี่ปุ่น")
        self.app.geometry("800x700")
        self.app.resizable(False, False)

        self.selected_category: str = "overall"
        self._current_zodiac_name = ""
        self._current_zodiac_color = "#FF6B8B"

        self.flower_images: list = []
        self.use_png = False
        self._load_flower_images()

        self._bg = load_bg("bg.PNG")

        self._build_category_page()
        self._build_zodiac_page()
        self._build_fortune_page()

        self._show_page(self.category_frame)

    # ──────────── Assets ────────────
    def _load_flower_images(self):
        for fname in FLOWER_FILES:
            if os.path.exists(fname):
                try:
                    img = Image.open(fname).resize((40, 40))
                    self.flower_images.append(CTkImage(light_image=img, dark_image=img, size=(40, 40)))
                    self.use_png = True
                except Exception:
                    pass

    def _add_bg(self, frame: CTkFrame):
        if self._bg:
            CTkLabel(frame, image=self._bg, text="").place(x=0, y=0, relwidth=1, relheight=1)
        else:
            frame.configure(fg_color="#FFF0F5")

    # ──────────── Page switcher ────────────
    def _show_page(self, target: CTkFrame):
        for f in [self.category_frame, self.zodiac_frame, self.fortune_frame]:
            f.place_forget()
        target.place(x=0, y=0, relwidth=1, relheight=1)

    # ──────────── Page 1: เลือกหมวด (ปรับปรุง) ────────────
    def _build_category_page(self):
        self.category_frame = CTkFrame(self.app, fg_color="transparent", corner_radius=0)
        self._add_bg(self.category_frame)

        # Header ตกแต่ง
        header = CTkFrame(self.category_frame, fg_color="transparent", height=80)
        header.pack(fill="x", pady=(10, 0))
        
        # ดอกไม้ซ้าย-ขวา
        if self.flower_images:
            CTkLabel(header, image=random.choice(self.flower_images), text="").pack(side="left", padx=20)
            CTkLabel(header, image=random.choice(self.flower_images), text="").pack(side="right", padx=20)
        else:
            CTkLabel(header, text="🌸", font=("Arial", 32)).pack(side="left", padx=20)
            CTkLabel(header, text="🌺", font=("Arial", 32)).pack(side="right", padx=20)

        # หัวข้อหลัก
        self.title_label = CTkLabel(
            self.category_frame,
            text="🌸 Fortune Garden 🌸",
            font=F_APP_TITLE,
            text_color="#FF1493",
            fg_color="transparent",
        )
        self.title_label.pack(pady=(5, 5))

        # คำอธิบาย
        CTkLabel(
            self.category_frame,
            text="ค้นหาคำทำนายตามศาสตร์แห่งดวงดาว",
            font=F_SUBTITLE,
            text_color="#8A2BE2",
            fg_color="transparent",
        ).pack()

        CTkLabel(
            self.category_frame,
            text="✨ เลือกด้านที่อยากรู้ ✨",
            font=F_PAGE_TITLE,
            text_color="#9932CC",
            fg_color="transparent",
        ).pack(pady=(10, 20))

        # Grid การ์ดหมวด
        grid_frame = CTkFrame(self.category_frame, fg_color="transparent")
        grid_frame.pack(expand=True)

        for idx, cat in enumerate(CATEGORIES):
            row, col = divmod(idx, 2)
            
            # การ์ด
            card = CTkFrame(
                grid_frame,
                fg_color=cat["light"],
                corner_radius=25,
                border_width=3,
                border_color=cat["color"],
                width=280,
                height=220,
            )
            card.grid(row=row, column=col, padx=20, pady=20)
            card.grid_propagate(False)

            # ไอคอน
            CTkLabel(
                card, 
                text=cat["icon"], 
                font=F_ICON_CAT,
                fg_color="transparent"
            ).place(relx=0.5, y=35, anchor="n")

            # ชื่อหมวด
            CTkLabel(
                card, 
                text=cat["label"], 
                font=F_CARD_TITLE,
                text_color=adjust_color(cat["color"], -40),
                fg_color="transparent"
            ).place(relx=0.5, y=100, anchor="n")

            # คำอธิบาย
            CTkLabel(
                card, 
                text=cat["desc"], 
                font=F_CARD_DESC,
                text_color="#4A4A4A",
                fg_color="transparent",
                wraplength=220
            ).place(relx=0.5, y=140, anchor="n")

            # ทำให้คลิกได้
            for widget in [card] + list(card.winfo_children()):
                widget.bind("<Button-1>", 
                    lambda e, k=cat["key"], c=cat["color"]: self._select_category(k, c))
                widget.configure(cursor="hand2")

            # Hover effect
            def on_enter(e, c=card, base=cat["light"]):
                c.configure(fg_color=adjust_color(base, -15))
            
            def on_leave(e, c=card, base=cat["light"]):
                c.configure(fg_color=base)
            
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

        self._create_floating_flowers(self.category_frame)
        self._animate_title()

    def _select_category(self, key: str, color: str):
        self.selected_category = key
        cat = next(c for c in CATEGORIES if c["key"] == key)
        
        # อัปเดตข้อความบนหน้า zodiac
        self.zodiac_cat_label.configure(
            text=f"{cat['icon']} {cat['label']}",
            text_color=adjust_color(cat["color"], -30),
            font=F_PAGE_TITLE
        )
        
        self._show_page(self.zodiac_frame)

    # ──────────── Page 2: เลือกราศี (ปรับปรุง) ────────────
    # ──────────── Page 2: เลือกราศี (ฉบับปรับปรุงระยะห่าง) ────────────
    def _build_zodiac_page(self):
        self.zodiac_frame = CTkFrame(self.app, fg_color="transparent")
        self._add_bg(self.zodiac_frame)

        # Header
        header = CTkFrame(self.zodiac_frame, fg_color="transparent", height=60)
        header.pack(fill="x", padx=15, pady=(10, 0))

        # ปุ่มกลับ
        CTkButton(
            header,
            text="← กลับ",
            font=F_BTN_SMALL,
            fg_color="#FFFFFF",
            hover_color="#F0E6FF",
            text_color="#9370DB",
            border_width=2,
            border_color="#DDA0DD",
            corner_radius=20,
            width=90,
            height=35,
            command=lambda: self._show_page(self.category_frame),
        ).pack(side="left")

        # หมวดที่เลือก
        self.zodiac_cat_label = CTkLabel(
            self.zodiac_frame,
            text="🌟 โดยรวม",
            font=F_PAGE_TITLE,
            text_color="#8A2BE2",
            fg_color="transparent",
        )
        self.zodiac_cat_label.pack(pady=(5, 5))

        # คำอธิบาย
        CTkLabel(
            self.zodiac_frame,
            text="✨ กดราศีเพื่อรับคำทำนาย ✨",
            font=F_SUBTITLE,
            text_color="#9932CC",
            fg_color="transparent",
        ).pack()

        # --- แก้ไขตรงนี้: ช่องค้นหา (Search Bar) ---
        search_frame = CTkFrame(
            self.zodiac_frame,
            fg_color="#FFFFFF",
            corner_radius=25,
            height=45,
            width=400,
            border_width=2,
            border_color="#DDA0DD"
        )
        search_frame.pack(pady=(15, 10))
        search_frame.pack_propagate(False) # ล็อคขนาด frame ไว้ไม่ให้ขยายตาม widget ข้างใน
        

        CTkLabel(search_frame, text="🔍", font=("Arial", 18)).pack(side="left", padx=(20, 10))
        
        self.search_entry = CTkEntry(
            search_frame,
            placeholder_text="ค้นหาราศี...",
            font=FONTS["body_small"], # เปลี่ยนจาก F_BODY เป็นขนาดที่เล็กลงหน่อยเพื่อไม่ให้ทับขอบ
            fg_color="transparent",
            border_width=0,
            width=300,
            text_color="#4A4A4A"
        )
        # ใช้ pady เพื่อดันให้ตัวหนังสืออยู่กึ่งกลางแนวตั้งพอดี
        self.search_entry.pack(side="left", padx=(0, 20), pady=5, fill="both", expand=True)
        self.search_entry.bind("<KeyRelease>", self._filter_zodiac)
        # ----------------------------------------

        # Scroll frame
        self.scroll_frame = CTkScrollableFrame(
            self.zodiac_frame,
            width=720,
            height=450,
            corner_radius=20,
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1",
            scrollbar_button_hover_color="#FF9AAF"
        )
        self.scroll_frame.pack(pady=10)

        self._create_zodiac_buttons()

        # ปุ่มสุ่ม
        self.random_btn = CTkButton(
            self.zodiac_frame,
            text="🎲 สุ่มราศี",
            font=F_BTN_MAIN,
            fg_color="#FF69B4",
            hover_color="#FF1493",
            text_color="#FFFFFF",
            corner_radius=30,
            width=200,
            height=45,
            command=self._random_zodiac,
        )
        self.random_btn.pack(pady=(10, 15))

    def _create_zodiac_buttons(self):
        self.zodiac_buttons = []
        
        for idx, (name, desc, color) in enumerate(ZODIAC_DATA):
            # กรอบปุ่ม
            btn_frame = CTkFrame(
                self.scroll_frame,
                fg_color="#FFFFFF",
                corner_radius=20,
                border_width=2,
                border_color=adjust_color(color, +20),
                width=200,
                height=110
            )
            btn_frame.grid(row=idx // 3, column=idx % 3, padx=12, pady=12)
            btn_frame.grid_propagate(False)

            # Emoji ธาตุ
            emoji = desc.split()[0]
            CTkLabel(
                btn_frame,
                text=emoji,
                font=("Arial", 24)
            ).place(x=10, y=8)

            # ชื่อราศี
            CTkLabel(
                btn_frame,
                text=name,
                font=F_CARD_TITLE,
                text_color=adjust_color(color, -40)
            ).place(x=45, y=12)

            # คำอธิบาย
            CTkLabel(
                btn_frame,
                text=desc,
                font=F_CARD_DESC,
                text_color="#666666",
                wraplength=170
            ).place(x=10, y=50)

            # ทำให้คลิกได้
            def on_click(e, n=name, c=color):
                self._go_fortune(n, c)
            
            btn_frame.bind("<Button-1>", on_click)
            btn_frame.configure(cursor="hand2")

            # Hover effect
            def on_enter(e, f=btn_frame, base=color):
                f.configure(
                    fg_color=adjust_color(base, +50),
                    border_color=adjust_color(base, -20)
                )
            
            def on_leave(e, f=btn_frame, base=color):
                f.configure(
                    fg_color="#FFFFFF",
                    border_color=adjust_color(base, +20)
                )
            
            btn_frame.bind("<Enter>", on_enter)
            btn_frame.bind("<Leave>", on_leave)

            self.zodiac_buttons.append(btn_frame)

    def _filter_zodiac(self, event=None):
        search = self.search_entry.get().lower()
        for idx, btn in enumerate(self.zodiac_buttons):
            name, _, _ = ZODIAC_DATA[idx]
            if search in name.lower() or search == "":
                btn.grid()
            else:
                btn.grid_remove()

    def _random_zodiac(self):
        idx = random.randint(0, len(ZODIAC_DATA) - 1)
        name, _, color = ZODIAC_DATA[idx]
        
        # Animation
        original_color = self.random_btn.cget("fg_color")
        self.random_btn.configure(fg_color="#FFD700")
        
        # Highlight
        self.zodiac_buttons[idx].configure(border_color="#FFD700", border_width=4)
        
        self.app.after(300, lambda: self.random_btn.configure(fg_color=original_color))
        self.app.after(300, lambda: self.zodiac_buttons[idx].configure(border_width=2))
        self.app.after(350, lambda: self._go_fortune(name, color))

    # ──────────── Page 3: ผลคำทำนาย (ปรับปรุง) ────────────
    def _build_fortune_page(self):
        self.fortune_frame = CTkFrame(self.app, fg_color="transparent", corner_radius=0)
        self._add_bg(self.fortune_frame)

        # การ์ดหลัก
        self.fortune_card = CTkFrame(
            self.fortune_frame,
            fg_color="#FFFFFF",
            corner_radius=40,
            border_width=3,
            border_color="#FFB6C1",
            width=700,
            height=600,
        )
        self.fortune_card.place(relx=0.5, rely=0.5, anchor="center")

        # เนื้อหา
        content = CTkFrame(self.fortune_card, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=25, pady=20)

        # Badge หมวด
        self.lbl_category_badge = CTkLabel(
            content,
            text="🌟 โดยรวม",
            font=F_BADGE,
            fg_color="#FFE4EC",
            corner_radius=15,
            text_color="#CC4477",
            padx=15,
            pady=6,
        )
        self.lbl_category_badge.pack(pady=(5, 10))

        # ไอคอนหลัก
        self.lbl_icon = CTkLabel(
            content,
            text="🔮",
            font=F_ICON_BIG,
            fg_color="transparent"
        )
        self.lbl_icon.pack(pady=(0, 5))

        # ราศี
        self.lbl_zodiac = CTkLabel(
            content,
            text="♈ เมษ",
            font=F_ZODIAC_NAME,
            text_color="#FF1493",
            fg_color="transparent"
        )
        self.lbl_zodiac.pack()

        # คำอธิบายราศี
        self.lbl_date = CTkLabel(
            content,
            text="🔥 ธาตุไฟ | กล้าหาญ",
            font=F_ZODIAC_DATE,
            text_color="#777777",
            fg_color="transparent"
        )
        self.lbl_date.pack()

        # เส้นคั่น
        CTkFrame(content, fg_color="#DDAADD", height=2, width=500).pack(pady=15)

        # หัวข้อคำทำนาย
        self.lbl_fortune_title = CTkLabel(
            content,
            text="",
            font=F_FORTUNE_H,
            text_color="#8A2BE2",
            fg_color="transparent"
        )
        self.lbl_fortune_title.pack(pady=(0, 10))

        # เนื้อหา
        self.lbl_body = CTkLabel(
            content,
            text="",
            font=F_FORTUNE_B,
            text_color="#4A4A4A",
            fg_color="transparent",
            wraplength=550,
            justify="center"
        )
        self.lbl_body.pack()

        # คำคม
        self.lbl_advice = CTkLabel(
            content,
            text="",
            font=F_QUOTE,
            text_color="#888888",
            fg_color="transparent"
        )
        self.lbl_advice.pack(pady=(10, 5))

        # กรอบสีมงคล
        self.lucky_frame = CTkFrame(content, fg_color="#F8F0FF", corner_radius=20)
        self.lucky_frame.pack(fill="x", pady=15)

        self.lucky_rows = []
        lucky_labels = [("🎨", "สีมงคล"), ("🔢", "เลขมงคล"), ("📅", "วันมงคล")]
        
        for icon, text in lucky_labels:
            row = CTkFrame(self.lucky_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=5)
            
            left = CTkFrame(row, fg_color="transparent")
            left.pack(side="left")
            
            CTkLabel(left, text=icon, font=("Arial", 16)).pack(side="left", padx=(0, 5))
            CTkLabel(left, text=text, font=F_LUCKY_KEY, text_color="#666666").pack(side="left")
            
            lbl_val = CTkLabel(row, text="-", font=F_LUCKY_VAL, text_color="#5A3060")
            lbl_val.pack(side="right")
            self.lucky_rows.append(lbl_val)

        # ปุ่มรับคำทำนาย
        self.fetch_btn = CTkButton(
            content,
            text="🔮 รับคำทำนาย",
            font=F_BTN_MAIN,
            fg_color="#8A2BE2",
            hover_color="#6A1B9A",
            text_color="#FFFFFF",
            corner_radius=30,
            width=250,
            height=50,
            command=self._fetch_fortune,
        )
        self.fetch_btn.pack(pady=(10, 5))

        # ปุ่มควบคุม
        btn_row = CTkFrame(content, fg_color="transparent")
        btn_row.pack()

        self.back_zodiac_btn = CTkButton(
            btn_row,
            text="← ราศีอื่น",
            font=F_BTN_SEC,
            fg_color="#FFB6C1",
            hover_color="#FF9AAF",
            text_color="#5A2D40",
            corner_radius=25,
            width=160,
            height=45,
            command=lambda: self._show_page(self.zodiac_frame),
        )
        self.back_zodiac_btn.pack(side="left", padx=5)

        CTkButton(
            btn_row,
            text="🏠 หน้าแรก",
            font=F_BTN_SEC,
            fg_color="#E6E6FA",
            hover_color="#D0C8F0",
            text_color="#5A3060",
            corner_radius=25,
            width=160,
            height=45,
            command=lambda: self._show_page(self.category_frame),
        ).pack(side="left", padx=5)

    def _go_fortune(self, name: str, color: str):
        self._current_zodiac_name = name
        self._current_zodiac_color = color

        # หาข้อมูลราศี
        zodiac_info = next((z for z in ZODIAC_DATA if z[0] == name), None)
        if zodiac_info:
            _, desc, _ = zodiac_info
        else:
            desc = ""

        cat = next(c for c in CATEGORIES if c["key"] == self.selected_category)
        dark_color = adjust_color(color, -50)

        # อัปเดต UI
        self.fortune_card.configure(border_color=adjust_color(color, +10))
        self.back_zodiac_btn.configure(fg_color=color, hover_color=adjust_color(color, -20))
        
        self.lbl_category_badge.configure(
            text=f"{cat['icon']} ดวง{cat['label']}",
            fg_color=cat["light"],
            text_color=adjust_color(cat["color"], -30)
        )
        
        self.lbl_zodiac.configure(text=name, text_color=dark_color)
        self.lbl_date.configure(text=desc)

        # รีเซ็ต
        self.lbl_icon.configure(text="🔮")
        self.lbl_fortune_title.configure(text="กดปุ่มเพื่อรับคำทำนาย")
        self.lbl_body.configure(text="✨ กดรับคำทำนายเพื่อเชื่อมต่อกับดวงดาว ✨")
        self.lbl_advice.configure(text="")
        
        for lbl in self.lucky_rows:
            lbl.configure(text="-")

        self.fetch_btn.configure(state="normal", text="🔮 รับคำทำนาย", fg_color="#8A2BE2")
        
        self._show_page(self.fortune_frame)

    def _fetch_fortune(self):
        cat_key = self.selected_category

        # Loading state
        self.fetch_btn.configure(state="disabled", text="⏳ กำลังเชื่อมต่อ...", fg_color="#AAAAAA")
        self.lbl_icon.configure(text="⏳")
        self.lbl_fortune_title.configure(text="กำลังดึงคำทำนาย...")
        self.lbl_body.configure(text="กรุณารอสักครู่...")

        def fetch():
            result = udp_ask_fortune(cat_key)
            self.app.after(0, lambda: self._apply_fortune(result, cat_key))

        threading.Thread(target=fetch, daemon=True).start()

    def _apply_fortune(self, server_text: str | None, cat_key: str):
        detail = random.choice(FORTUNES[cat_key])

        if server_text:
            icon = detail["icon"]
            title = detail["title"]
            body = server_text
            advice = detail.get("advice", "")
            title_color = "#8A2BE2"
            body_color = "#4A4A4A"
        else:
            icon = "⚠️"
            title = "ไม่สามารถเชื่อมต่อได้"
            body = f"กรุณาตรวจสอบ Server ที่\n{SERVER_IP}:{SERVER_PORT}"
            advice = ""
            title_color = "#CC4400"
            body_color = "#888888"
            detail = {"lucky_color": "-", "lucky_number": "-", "lucky_day": "-"}

        self.lbl_icon.configure(text=icon)
        self.lbl_fortune_title.configure(text=title, text_color=title_color)
        self.lbl_body.configure(text=body, text_color=body_color)
        self.lbl_advice.configure(text=f"“{advice}”" if advice else "")
        
        lucky_vals = [detail["lucky_color"], detail["lucky_number"], detail["lucky_day"]]
        for lbl, val in zip(self.lucky_rows, lucky_vals):
            lbl.configure(text=val)

        self.fetch_btn.configure(state="normal", text="🔄 ดูดวงใหม่", fg_color="#8A2BE2")

    # ──────────── Floating Flowers (ปรับปรุง) ────────────
    def _create_floating_flowers(self, parent: CTkFrame):
        self.floating_labels = []
        
        for i in range(10):
            if self.use_png and self.flower_images:
                lbl = CTkLabel(
                    parent,
                    image=random.choice(self.flower_images),
                    text="",
                    fg_color="transparent"
                )
            else:
                lbl = CTkLabel(
                    parent,
                    text=random.choice(FLOAT_EMOJIS),
                    font=("Arial", random.randint(20, 32)),
                    fg_color="transparent",
                    text_color=random.choice(["#FF69B4", "#9370DB", "#FFA07A", "#FFD700"]),
                )
            
            x = random.randint(20, 750)
            y = random.randint(20, 650)
            lbl.place(x=x, y=y)
            self.floating_labels.append(lbl)
            
            self._animate_float(lbl, x, y, i)

    def _animate_float(self, lbl: CTkLabel, start_x: int, start_y: int, idx: int):
        def animate(step=0):
            offset_y = math.sin(step * 0.1) * 20
            offset_x = math.cos(step * 0.1 + idx) * 15
            
            new_x = start_x + offset_x
            new_y = start_y + offset_y
            
            if 10 <= new_x <= 770 and 10 <= new_y <= 670:
                lbl.place(x=new_x, y=new_y)
            
            self.app.after(50, lambda: animate(step + 1))
        
        animate()

    # ──────────── Title Animation ────────────
    def _animate_title(self):
        def cycle(i=0):
            try:
                self.title_label.configure(text_color=TITLE_COLORS[i % len(TITLE_COLORS)])
                self.app.after(1000, lambda: cycle(i + 1))
            except Exception:
                pass
        cycle()

    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    app = FortuneGardenApp()
    app.run()