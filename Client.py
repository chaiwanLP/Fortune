from customtkinter import *
from PIL import Image, ImageDraw, ImageFilter
import random
import os
import threading
import socket
import math

set_appearance_mode("light")
set_default_color_theme("green")
set_widget_scaling(1.2)
set_window_scaling(1.2)

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
    server_key = CATEGORY_TO_SERVER_KEY.get(category_key, category_key)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(UDP_TIMEOUT)
        sock.sendto(server_key.strip().encode("utf-8"), (SERVER_IP, SERVER_PORT))
        data, _ = sock.recvfrom(4096)
        sock.close()
        return data.decode("utf-8")
    except Exception as e:
        print(f"[UDP ERROR] {e}")
        return None


# ─────────────────────────────────────────
#  ฟอนต์กลาง
# ─────────────────────────────────────────
FONTS = {
    "display_large": ("Kanit", 36, "bold"),
    "display": ("Kanit", 32, "bold"),
    "title_large": ("Kanit", 24, "bold"),
    "title": ("Kanit", 20, "bold"),
    "title_small": ("Kanit", 18, "bold"),
    "body_large": ("Kanit", 16),
    "body": ("Kanit", 15),
    "body_small": ("Kanit", 14),
    "caption": ("Kanit", 13),
    "caption_small": ("Kanit", 12),
    "button_large": ("Kanit", 16, "bold"),
    "button": ("Kanit", 15, "bold"),
    "button_small": ("Kanit", 13, "bold"),
    "badge": ("Kanit", 14, "bold"),
    "quote": ("Kanit", 14, "italic"),
    "emoji_large": ("Arial", 60),
    "emoji_medium": ("Arial", 48),
    "emoji_small": ("Arial", 32),
}

F_APP_TITLE  = FONTS["display"]
F_PAGE_TITLE = FONTS["title_large"]
F_SUBTITLE   = FONTS["body"]
F_CARD_TITLE = FONTS["title_small"]
F_CARD_DESC  = FONTS["caption"]
F_BTN_MAIN   = FONTS["button_large"]
F_BTN_SEC    = FONTS["button"]
F_BTN_SMALL  = FONTS["button_small"]
F_ZODIAC_NAME = FONTS["title_large"]
F_ZODIAC_DATE = FONTS["caption"]
F_FORTUNE_H  = FONTS["title"]
F_FORTUNE_B  = FONTS["body_large"]
F_BADGE      = FONTS["badge"]
F_ICON_BIG   = FONTS["emoji_large"]
F_ICON_CAT   = FONTS["emoji_medium"]
F_BODY       = FONTS["body"]

CATEGORIES = [
    {
        "key": "overall",
        "icon": "🌟",
        "label": "โดยรวม",
        "desc": "ดวงชะตาภาพรวมชีวิต",
        "color": "#F9A826",
        "light": "#FFF4E0",
        "gradient": ["#F9A826", "#FFD966"]
    },
    {
        "key": "love",
        "icon": "💖",
        "label": "ความรัก",
        "desc": "ความสัมพันธ์และหัวใจ",
        "color": "#E83A5E",
        "light": "#FFE8F0",
        "gradient": ["#E83A5E", "#FF6B8B"]
    },
    {
        "key": "money",
        "icon": "💰",
        "label": "การเงิน",
        "desc": "โชคลาภและทรัพย์สิน",
        "color": "#28A745",
        "light": "#E8F5E9",
        "gradient": ["#28A745", "#5CB85C"]
    },
    {
        "key": "work",
        "icon": "📚",
        "label": "การงาน/การเรียน",
        "desc": "อาชีพ การศึกษา และความก้าวหน้า",
        "color": "#3A7BD5",
        "light": "#E8F0FE",
        "gradient": ["#3A7BD5", "#6C9BD2"]
    },
]

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

FLOAT_EMOJIS  = ["🌸", "🌼", "🌺", "✨", "🌷", "🦋", "🐞", "🍀", "⭐", "🌟"]
TITLE_COLORS  = ["#FF1493", "#9370DB", "#4169E1", "#FF6347", "#FF69B4", "#FFD700"]
FLOWER_FILES  = ["m1.png", "m2.png", "m3.png", "m4.png", "m5.png"]


def adjust_color(hex_color: str, amount: int) -> str:
    if not hex_color.startswith("#"):
        return hex_color
    r = max(0, min(255, int(hex_color[1:3], 16) + amount))
    g = max(0, min(255, int(hex_color[3:5], 16) + amount))
    b = max(0, min(255, int(hex_color[5:7], 16) + amount))
    return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────
#  App
# ─────────────────────────────────────────
class FortuneGardenApp:
    def __init__(self):
        self.app = CTk()
        self.app.title("🌸 Fortune Garden - ดูดวงสไตล์ญี่ปุ่น")
        self.app.geometry("800x750")
        self.app.resizable(False, False)

        self.selected_category = None
        self._current_zodiac_name = ""
        self._current_zodiac_color = "#FF6B8B"

        self.flower_images = []
        self.use_png = False
        self._load_flower_images()

        self.category_page()
        self.zodiac_page()
        self.fortune_page()

        self.show_page(self.category_frame)

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
        if hasattr(self, '_bg') and self._bg:
            CTkLabel(frame, image=self._bg, text="").place(x=0, y=0, relwidth=1, relheight=1)
        else:
            frame.configure(fg_color="#FFF0F5")

    # ──────────── Page switcher ────────────
    def show_page(self, target: CTkFrame):
        for f in [self.category_frame, self.zodiac_frame, self.fortune_frame]:
            f.place_forget()
        target.place(x=0, y=0, relwidth=1, relheight=1)

    # ──────────── Page 1: เลือกหมวด ────────────
    def category_page(self):
        self.category_frame = CTkFrame(self.app, fg_color="transparent", corner_radius=0)
        self._add_bg(self.category_frame)

        header = CTkFrame(self.category_frame, fg_color="transparent", height=80)
        header.pack(fill="x", pady=(10, 0))

        if self.flower_images:
            CTkLabel(header, image=random.choice(self.flower_images), text="").pack(side="left", padx=20)
            CTkLabel(header, image=random.choice(self.flower_images), text="").pack(side="right", padx=20)
        else:
            CTkLabel(header, text="🌸", font=("Arial", 32)).pack(side="left", padx=20)
            CTkLabel(header, text="🌺", font=("Arial", 32)).pack(side="right", padx=20)

        self.title_label = CTkLabel(
            self.category_frame,
            text="🌸 Fortune Garden 🌸",
            font=F_APP_TITLE,
            text_color="#FF1493",
            fg_color="transparent",
        )
        self.title_label.pack(pady=(5, 5))

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

        grid_frame = CTkFrame(self.category_frame, fg_color="transparent")
        grid_frame.pack(expand=True)

        for idx, cat in enumerate(CATEGORIES):
            row, col = divmod(idx, 2)

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

            CTkLabel(card, text=cat["icon"], font=F_ICON_CAT, fg_color="transparent").place(relx=0.5, y=35, anchor="n")
            CTkLabel(card, text=cat["label"], font=F_CARD_TITLE, text_color=adjust_color(cat["color"], -40), fg_color="transparent").place(relx=0.5, y=100, anchor="n")
            CTkLabel(card, text=cat["desc"], font=F_CARD_DESC, text_color="#4A4A4A", fg_color="transparent", wraplength=220).place(relx=0.5, y=140, anchor="n")

            for widget in [card] + list(card.winfo_children()):
                widget.bind("<Button-1>", lambda e, k=cat["key"], c=cat["color"]: self._select_category(k, c))
                widget.configure(cursor="hand2")

            card.bind("<Enter>", lambda e, c=card, base=cat["light"]: c.configure(fg_color=adjust_color(base, -15)))
            card.bind("<Leave>", lambda e, c=card, base=cat["light"]: c.configure(fg_color=base))

        self._create_floating_flowers(self.category_frame)
        self._animate_title()

    def _select_category(self, key: str, color: str):
        self.selected_category = key
        cat = next(c for c in CATEGORIES if c["key"] == key)
        self.zodiac_cat_label.configure(
            text=f"{cat['icon']} {cat['label']}",
            text_color=adjust_color(cat["color"], -30),
            font=F_PAGE_TITLE
        )
        self.show_page(self.zodiac_frame)

    # ──────────── Page 2: เลือกราศี ────────────
    def zodiac_page(self):
        self.zodiac_frame = CTkFrame(self.app, fg_color="transparent")
        self._add_bg(self.zodiac_frame)

        header = CTkFrame(self.zodiac_frame, fg_color="transparent", height=60)
        header.pack(fill="x", padx=15, pady=(10, 0))

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
            command=lambda: self.show_page(self.category_frame),
        ).pack(side="left")

        self.zodiac_cat_label = CTkLabel(
            self.zodiac_frame,
            text="🌟 โดยรวม",
            font=F_PAGE_TITLE,
            text_color="#8A2BE2",
            fg_color="transparent",
        )
        self.zodiac_cat_label.pack(pady=(5, 5))

        CTkLabel(
            self.zodiac_frame,
            text="✨ กดราศีเพื่อรับคำทำนาย ✨",
            font=F_SUBTITLE,
            text_color="#9932CC",
            fg_color="transparent",
        ).pack()

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
        search_frame.pack_propagate(False)

        CTkLabel(search_frame, text="🔍", font=("Arial", 18)).pack(side="left", padx=(20, 10))

        self.search_entry = CTkEntry(
            search_frame,
            placeholder_text="ค้นหาราศี...",
            font=FONTS["body_small"],
            fg_color="transparent",
            border_width=0,
            width=300,
            text_color="#4A4A4A"
        )
        self.search_entry.pack(side="left", padx=(0, 20), pady=5, fill="both", expand=True)
        self.search_entry.bind("<KeyRelease>", self._filter_zodiac)

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

    def _create_zodiac_buttons(self):
        self.zodiac_buttons = []

        for idx, (name, desc, color) in enumerate(ZODIAC_DATA):
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

            emoji = desc.split()[0]
            CTkLabel(btn_frame, text=emoji, font=("Arial", 24)).place(x=10, y=8)
            CTkLabel(btn_frame, text=name, font=F_CARD_TITLE, text_color=adjust_color(color, -40)).place(x=45, y=12)
            CTkLabel(btn_frame, text=desc, font=F_CARD_DESC, text_color="#666666", wraplength=170).place(x=10, y=50)

            btn_frame.bind("<Button-1>", lambda e, n=name, c=color: self._go_fortune(n, c))
            btn_frame.configure(cursor="hand2")

            btn_frame.bind("<Enter>", lambda e, f=btn_frame, base=color: f.configure(fg_color=adjust_color(base, +50), border_color=adjust_color(base, -20)))
            btn_frame.bind("<Leave>", lambda e, f=btn_frame, base=color: f.configure(fg_color="#FFFFFF", border_color=adjust_color(base, +20)))

            self.zodiac_buttons.append(btn_frame)

    def _filter_zodiac(self, event=None):
        search = self.search_entry.get().lower()
        for idx, btn in enumerate(self.zodiac_buttons):
            name, _, _ = ZODIAC_DATA[idx]
            if search in name.lower() or search == "":
                btn.grid()
            else:
                btn.grid_remove()

    # ──────────── Page 3: ผลคำทำนาย ────────────
    def fortune_page(self):
        self.fortune_frame = CTkFrame(self.app, fg_color="transparent")
        self._add_bg(self.fortune_frame)

        self.fortune_card = CTkFrame(
            self.fortune_frame,
            fg_color="#FFFFFF",
            corner_radius=40,
            border_width=3,
            width=700,
            height=560,
        )
        self.fortune_card.place(relx=0.5, rely=0.5, anchor="center")

        content = CTkFrame(self.fortune_card, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=25, pady=20)

        # Badge หมวดหมู่
        self.lbl_category_badge = CTkLabel(
            content,
            text="ดวงชะตาของคุณ",
            font=F_BADGE,
            corner_radius=15,
            padx=15,
            pady=6,
        )
        self.lbl_category_badge.pack(pady=(5, 10))

        # ไอคอน
        self.lbl_icon = CTkLabel(content, text="🔮", font=F_ICON_BIG)
        self.lbl_icon.pack()

        # ชื่อราศี
        self.lbl_zodiac = CTkLabel(content, text="", font=F_ZODIAC_NAME)
        self.lbl_zodiac.pack()

        # หัวข้อคำทำนาย
        self.lbl_fortune_title = CTkLabel(content, text="กดปุ่มเพื่อรับคำทำนาย", font=F_FORTUNE_H)
        self.lbl_fortune_title.pack(pady=10)

        # ข้อความคำทำนาย (มาจาก server)
        self.lbl_body = CTkLabel(
            content,
            text="✨ กดรับคำทำนายเพื่อเชื่อมต่อกับ Server ✨",
            font=F_FORTUNE_B,
            wraplength=580,
            justify="center",
        )
        self.lbl_body.pack(pady=20)

        # ปุ่มรับคำทำนาย
        self.fetch_btn = CTkButton(
            content,
            text="🔮 รับคำทำนาย",
            font=F_BTN_MAIN,
            command=self.fetch_fortune,
            corner_radius=30,
            width=250,
            height=50,
        )
        self.fetch_btn.pack(pady=10)

        # ปุ่มกลับ
        self.back_zodiac_btn = CTkButton(
            content,
            text="← เปลี่ยนราศี",
            font=F_BTN_SEC,
            fg_color="#E6E6FA",
            text_color="#5A3060",
            command=lambda: self.show_page(self.zodiac_frame),
        )
        self.back_zodiac_btn.pack(pady=5)

    def _go_fortune(self, name: str, color: str):
        self._current_zodiac_name = name
        self._current_zodiac_color = color

        cat = next((c for c in CATEGORIES if c["key"] == self.selected_category), CATEGORIES[0])
        dark_color = adjust_color(color, -50)

        self.fortune_card.configure(border_color=adjust_color(color, +10))
        self.back_zodiac_btn.configure(fg_color=color, hover_color=adjust_color(color, -20), text_color="white")

        self.lbl_category_badge.configure(
            text=f"{cat['icon']} ดวง{cat['label']}",
            fg_color=cat["light"],
            text_color=adjust_color(cat["color"], -30),
        )

        self.lbl_zodiac.configure(text=name, text_color=dark_color)
        self.lbl_icon.configure(text="🔮")
        self.lbl_fortune_title.configure(text="พร้อมรับคำทำนาย")
        self.lbl_body.configure(text="✨ ระบบเชื่อมต่อกับ Server เรียบร้อยแล้ว ✨", text_color="#4A4A4A")
        self.fetch_btn.configure(state="normal", text="🔮 รับคำทำนาย", fg_color="#8A2BE2")

        self.show_page(self.fortune_frame)

    def fetch_fortune(self):
        if not self.selected_category:
            self.lbl_body.configure(text="❌ กรุณาเลือกหมวดหมู่ก่อนรับคำทำนายค่ะ", text_color="red")
            return

        self.fetch_btn.configure(state="disabled", text="⏳ กำลังถามดวงดาว...", fg_color="#AAAAAA")
        current_cat = self.selected_category

        def fetch():
            result = udp_ask_fortune(current_cat)
            self.app.after(0, lambda: self.apply_fortune(result))

        threading.Thread(target=fetch, daemon=True).start()

    def apply_fortune(self, server_text: str | None):
        if server_text:
            icon        = "🌟"
            title       = "คำทำนายจากดวงดาว ✨"
            body        = server_text
            text_color  = "#4A4A4A"
        else:
            icon        = "⚠️"
            title       = "การเชื่อมต่อขัดข้อง"
            body        = "ขออภัย... ไม่สามารถเชื่อมต่อกับดวงดาวได้\n(กรุณาตรวจสอบว่าเปิด server.py หรือยัง)"
            text_color  = "#FF4500"

        self.lbl_icon.configure(text=icon)
        self.lbl_fortune_title.configure(text=title)
        self.lbl_body.configure(text=body, text_color=text_color)
        self.fetch_btn.configure(state="normal", text="🔄 ดูดวงใหม่", fg_color="#8A2BE2")

    # ──────────── Floating Flowers ────────────
    def _create_floating_flowers(self, parent: CTkFrame):
        self.floating_labels = []

        for i in range(10):
            if self.use_png and self.flower_images:
                lbl = CTkLabel(parent, image=random.choice(self.flower_images), text="", fg_color="transparent")
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

    # ────────────  TitleAnimation ────────────
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