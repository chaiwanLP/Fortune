from calendar import month

from customtkinter import *
from PIL import Image
import random, os, threading, socket, math
from printpdf import export_fortune_pdf

set_appearance_mode("light")
set_default_color_theme("green")
set_widget_scaling(1.2)
set_window_scaling(1.2)

# ─────────────────────────────────────────
#  Server Config
# ─────────────────────────────────────────
SERVER_IP   = "10.31.7.102"
SERVER_PORT = 5000
UDP_TIMEOUT = 5

CATEGORY_TO_SERVER_KEY = {
    "overall": "general",
    "love":    "love",
    "money":   "money",
    "work":    "education",
}

def udp_ask_fortune(category_key: str, day: int, month: int, year: int) -> str | None:
    server_key = CATEGORY_TO_SERVER_KEY.get(category_key, category_key)
    message    = f"{server_key}|{day:02d}|{month:02d}|{year}"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(UDP_TIMEOUT)
        sock.sendto(message.encode("utf-8"), (SERVER_IP, SERVER_PORT))
        data, _ = sock.recvfrom(4096)
        sock.close()
        return data.decode("utf-8")
    except Exception as e:
        print(f"[UDP ERROR] {e}")
        return None

# ─────────────────────────────────────────
#  App fonts (CustomTkinter)
# ─────────────────────────────────────────
FONTS = {
    "display":      ("Kanit", 32, "bold"),
    "title_large":  ("Kanit", 24, "bold"),
    "title":        ("Kanit", 20, "bold"),
    "title_small":  ("Kanit", 18, "bold"),
    "body_large":   ("Kanit", 16),
    "body":         ("Kanit", 15),
    "caption":      ("Kanit", 13),
    "button_large": ("Kanit", 16, "bold"),
    "button":       ("Kanit", 15, "bold"),
    "button_small": ("Kanit", 13, "bold"),
    "badge":        ("Kanit", 14, "bold"),
    "emoji_large":  ("Arial", 56),
    "emoji_medium": ("Arial", 44),
}

CATEGORIES = [
    {"key":"overall","icon":"🌟","label":"โดยรวม",        "desc":"ดวงชะตาภาพรวมชีวิต",            "color":"#F9A826","light":"#FFF4E0"},
    {"key":"love",   "icon":"💖","label":"ความรัก",        "desc":"ความสัมพันธ์และหัวใจ",           "color":"#E83A5E","light":"#FFE8F0"},
    {"key":"money",  "icon":"💰","label":"การเงิน",        "desc":"โชคลาภและทรัพย์สิน",            "color":"#28A745","light":"#E8F5E9"},
    {"key":"work",   "icon":"📚","label":"การงาน/การเรียน","desc":"อาชีพ การศึกษา และความก้าวหน้า","color":"#3A7BD5","light":"#E8F0FE"},
]

MONTHS_TH = ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน",
              "พฤษภาคม","มิถุนายน","กรกฎาคม","สิงหาคม",
              "กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]

TITLE_COLORS  = ["#FF1493", "#9370DB", "#4169E1", "#FF6347", "#FF69B4", "#FFD700"]
FLOWER_FILES  = ["m1.png", "m2.png", "m3.png", "m4.png", "m5.png"]

def adj(c: str, a: int) -> str:
    if not c.startswith("#"): return c
    return "#{:02x}{:02x}{:02x}".format(
        max(0,min(255,int(c[1:3],16)+a)),
        max(0,min(255,int(c[3:5],16)+a)),
        max(0,min(255,int(c[5:7],16)+a)),
    )

def calc_zodiac(day, month):
    ranges = [
        ((3,21),(4,19),"aries","♈ ราศีเมษ"),((4,20),(5,20),"taurus","♉ ราศีพฤษภ"),
        ((5,21),(6,20),"gemini","♊ ราศีเมถุน"),((6,21),(7,22),"cancer","♋ ราศีกรกฎ"),
        ((7,23),(8,22),"leo","♌ ราศีสิงห์"),((8,23),(9,22),"virgo","♍ ราศีกันย์"),
        ((9,23),(10,22),"libra","♎ ราศีตุล"),((10,23),(11,21),"scorpio","♏ ราศีพิจิก"),
        ((11,22),(12,21),"sagittarius","♐ ราศีธนู"),((12,22),(1,19),"capricorn","♑ ราศีมังกร"),
        ((1,20),(2,18),"aquarius","♒ ราศีกุมภ์"),((2,19),(3,20),"pisces","♓ ราศีมีน"),
    ]
    for (m1,d1),(m2,d2),key,label in ranges:
        if m1>m2:
            if (month==m1 and day>=d1) or (month==m2 and day<=d2): return key, label
        else:
            if (month==m1 and day>=d1) or (m1<month<m2) or (month==m2 and day<=d2): return key, label
    return "capricorn","♑ ราศีมังกร"

def calc_naksat(year):
    cycle = [("rat","ปีชวด 🐭"),("ox","ปีฉลู 🐂"),("tiger","ปีขาล 🐯"),
             ("rabbit","ปีเถาะ 🐰"),("dragon","ปีมะโรง 🐲"),("snake","ปีมะเส็ง 🐍"),
             ("horse","ปีมะเมีย 🐴"),("goat","ปีมะแม 🐐"),("monkey","ปีวอก 🐒"),
             ("rooster","ปีระกา 🐓"),("dog","ปีจอ 🐕"),("pig","ปีกุน 🐖")]
    key, label = cycle[(year-2020)%12]
    return key, label

# ─────────────────────────────────────────
#  App
# ─────────────────────────────────────────
class FortuneGardenApp:
    def __init__(self):
        self.app = CTk()
        self.app.title("🌸 Fortune Garden ")
        self.app.geometry("800x750+400+50")
        self.app.resizable(False, False)
        self.load_gif_frames("text_from_me.gif")
        self.selected_category = None
        self._birth_day   = 1
        self._birth_month = 1
        self._birth_year  = 2000
        self._username    = ""
        self._fortune_text = ""

        self.flower_images = []
        self.use_png = False
        self._load_flower_images()

        self._build_page1()
        self._build_page2()
        self._build_page3()
        self.show_page(self.page1)

    def _load_flower_images(self):
        for fname in FLOWER_FILES:
            if os.path.exists(fname):
                try:
                    img = Image.open(fname).resize((40,40))
                    self.flower_images.append(CTkImage(light_image=img, dark_image=img, size=(40,40)))
                    self.use_png = True
                except Exception:
                    pass

    def _add_bg(self, f): f.configure(fg_color="#FFF0F5")

    def show_page(self, target):
        for f in [self.page1, self.page2, self.page3]:
            f.place_forget()
        target.place(x=0, y=0, relwidth=1, relheight=1)

    # ══════════════════════════════════════
    #  หน้า 1 — เลือกหมวด
    # ══════════════════════════════════════
    def _build_page1(self):
        self.page1 = CTkFrame(self.app, fg_color="transparent", corner_radius=0)
        self._add_bg(self.page1)

        hdr = CTkFrame(self.page1, fg_color="transparent", height=80)
        hdr.pack(fill="x", pady=(10,0))
        if self.flower_images:
            CTkLabel(hdr, image=random.choice(self.flower_images), text="").pack(side="left", padx=20)
            CTkLabel(hdr, image=random.choice(self.flower_images), text="").pack(side="right", padx=20)
        else:
            CTkLabel(hdr, text="🌸", font=("Arial",32)).pack(side="left", padx=20)
            CTkLabel(hdr, text="🌺", font=("Arial",32)).pack(side="right", padx=20)

        self.title_label = CTkLabel(self.page1, text="🌸 Fortune Garden 🌸",
                                    font=FONTS["display"], text_color="#FF1493", fg_color="transparent")
        self.title_label.pack(pady=(5,2))
        CTkLabel(self.page1, text="ค้นหาคำทำนายตามศาสตร์แห่งดวงดาว",
                 font=FONTS["body"], text_color="#8A2BE2", fg_color="transparent").pack()
        CTkLabel(self.page1, text="✨ เลือกด้านที่อยากรู้ ✨",
                 font=FONTS["title_large"], text_color="#9932CC", fg_color="transparent").pack(pady=(10,20))

        gf = CTkFrame(self.page1, fg_color="transparent")
        gf.pack(expand=True)
        for idx, cat in enumerate(CATEGORIES):
            row, col = divmod(idx, 2)
            card = CTkFrame(gf, fg_color=cat["light"], corner_radius=25,
                            border_width=3, border_color=cat["color"], width=280, height=220)
            card.grid(row=row, column=col, padx=20, pady=20)
            card.grid_propagate(False)
            CTkLabel(card, text=cat["icon"], font=FONTS["emoji_medium"], fg_color="transparent").place(relx=0.5, y=35, anchor="n")
            CTkLabel(card, text=cat["label"], font=FONTS["title_small"], text_color=adj(cat["color"],-40), fg_color="transparent").place(relx=0.5, y=100, anchor="n")
            CTkLabel(card, text=cat["desc"], font=FONTS["caption"], text_color="#4A4A4A", fg_color="transparent", wraplength=220).place(relx=0.5, y=140, anchor="n")
            for w in [card]+list(card.winfo_children()):
                w.bind("<Button-1>", lambda e, k=cat["key"]: self._pick_category(k))
                w.configure(cursor="hand2")
            card.bind("<Enter>", lambda e, c=card, b=cat["light"]: c.configure(fg_color=adj(b,-15)))
            card.bind("<Leave>", lambda e, c=card, b=cat["light"]: c.configure(fg_color=b))

        self._create_floating_flowers(self.page1)
        self._animate_title()

    def _pick_category(self, key):
        self.selected_category = key
        cat = next(c for c in CATEGORIES if c["key"]==key)
        self.p2_cat_label.configure(text=f"{cat['icon']} {cat['label']}", text_color=adj(cat["color"],-30))
        self.show_page(self.page2)

    # ══════════════════════════════════════
    #  หน้า 2 — กรอกชื่อ + วันเกิด
    # ══════════════════════════════════════
    def _build_page2(self):
        self.page2 = CTkFrame(self.app, fg_color="transparent", corner_radius=0)
        self._add_bg(self.page2)

        bb = CTkFrame(self.page2, fg_color="transparent", height=55)
        bb.pack(fill="x", padx=15, pady=(10,0))
        CTkButton(bb, text="← กลับ", font=FONTS["button_small"],
                  fg_color="#FFFFFF", hover_color="#F0E6FF", text_color="#9370DB",
                  border_width=2, border_color="#DDA0DD", corner_radius=20, width=90, height=35,
                  command=lambda: self.show_page(self.page1)).pack(side="left")

        self.p2_cat_label = CTkLabel(self.page2, text="🌟 โดยรวม",
                                     font=FONTS["title_large"], text_color="#8A2BE2", fg_color="transparent")
        self.p2_cat_label.pack(pady=(5,2))
        CTkLabel(self.page2, text="🎂 กรอกข้อมูลของคุณ",
                 font=FONTS["title_large"], text_color="#9932CC", fg_color="transparent").pack(pady=(5,2))

        # --- ส่วนที่ปรับให้กระชับ ---
        card = CTkFrame(self.page2, fg_color="#FFFFFF", corner_radius=30,
                        border_width=2, border_color="#DDA0DD", width=500, height=380) # ลดความกว้างลง
        card.pack(pady=10)
        card.pack_propagate(False)
        
        inner = CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=40, pady=20)
        
        # ปรับการกระจายคอลัมน์ให้ชิดกัน
        inner.grid_columnconfigure((0,1,2), weight=1)

        CTkLabel(inner, text="👤 ชื่อผู้ใช้", font=FONTS["title_small"], text_color="#9370DB").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0,4))
        self.name_var = StringVar()
        CTkEntry(inner, textvariable=self.name_var, placeholder_text="กรอกชื่อของคุณ...",
                  font=FONTS["body"], height=40).grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=(0,20))

        # Label หัวคอลัมน์ วัน/เดือน/ปี
        CTkLabel(inner, text="📅 วัน", font=FONTS["caption"], text_color="#9370DB").grid(row=2, column=0, sticky="w")
        CTkLabel(inner, text="🌙 เดือน", font=FONTS["caption"], text_color="#9370DB").grid(row=2, column=1, sticky="w", padx=5)
        CTkLabel(inner, text="🗓 ปี (ค.ศ.)", font=FONTS["caption"], text_color="#9370DB").grid(row=2, column=2, sticky="w")

        self.dd_var = StringVar(value="1")
        self.dd_entry = CTkEntry(
            inner, 
            textvariable=self.dd_var, 
            width=70, 
            font=FONTS["body"],
            placeholder_text="1-31",
            justify="center"  
        )
        self.dd_entry.grid(row=3, column=0, padx=(0, 5), pady=(5, 15), sticky="ew")
        self.mm_var = StringVar(value="มกราคม")
        self.mm_combo = CTkOptionMenu(
            inner, 
            values=MONTHS_TH, 
            variable=self.mm_var,
            width=140, 
            font=FONTS["body"], 
            dropdown_font=FONTS["body"],
            dynamic_resizing=False,
            fg_color="#9370DB",      
            button_color="#7B5EA7",   
            button_hover_color="#6A1AB2"  
        )
        self.mm_combo.grid(row=3, column=1, padx=5, pady=(5, 15), sticky="ew")

        self.yyyy_var = StringVar(value="2000")
        self.yyyy_entry = CTkEntry(inner, textvariable=self.yyyy_var, placeholder_text="1999",
                                  font=FONTS["body"], width=90)
        self.yyyy_entry.grid(row=3, column=2, padx=(5, 0), pady=(5, 15), sticky="ew")

        # พรีวิว ราศี/นักษัตร
        self.bd_preview = CTkLabel(inner, text="", font=FONTS["caption"], text_color="#9370DB",
                                    fg_color="#F5F0FF", corner_radius=10, padx=10, pady=8)
        self.bd_preview.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10,0))

        self.p2_error = CTkLabel(inner, text="", font=FONTS["caption"], text_color="#FF4500")
        self.p2_error.grid(row=5, column=0, columnspan=3, pady=(5,0))

        # ผูก Event เมื่อมีการเปลี่ยนค่า
        self.dd_var.trace_add("write", lambda *a: self._update_preview())
        self.mm_var.trace_add("write", lambda *a: self._update_preview())
        self.yyyy_var.trace_add("write", lambda *a: self._update_preview())
        
        self._update_preview()

        CTkButton(self.page2, text="✨ ดูดวงของฉัน →", font=FONTS["button_large"],
                  fg_color="#9370DB", hover_color="#7B5EA7", corner_radius=30, width=280, height=55,
                  command=self._confirm_and_go).pack(pady=20)

    def _get_max_day(self, month: int, year: int) -> int:
        import calendar
        return calendar.monthrange(year, month)[1]

    def _update_preview(self):
        try:
            # ดึงค่าปีปัจจุบันก่อน ถ้ากรอกไม่ครบให้ใช้ 2000 ไปก่อนกัน Error
            y_str = self.yyyy_var.get()
            year = int(y_str) if (y_str.isdigit() and len(y_str) == 4) else 2000
            month = MONTHS_TH.index(self.mm_var.get()) + 1
            
            # คำนวณวันสูงสุดของเดือนนั้นๆ
            import calendar
            max_d = calendar.monthrange(year, month)[1]

            # อัปเดตรายการใน Dropdown วันที่
            new_days = [str(i) for i in range(1, max_d + 1)]
            if self.dd_combo.cget("values") != new_days:
                self.dd_combo.configure(values=new_days)

            # เช็คว่าวันปัจจุบันที่เลือก เกินวันสูงสุดของเดือนไหม
            current_d_str = self.dd_var.get()
            if current_d_str.isdigit():
                current_d = int(current_d_str)
                if current_d > max_d:
                    self.dd_var.set(str(max_d)) # ปรับลงมาเป็นวันสุดท้ายของเดือนนั้น
                    return # จบฟังก์ชันแล้วให้ trace รันใหม่เอง

            # แสดงผล Preview ราศี/นักษัตร
            day = int(self.dd_var.get())
            _, z = calc_zodiac(day, month)
            _, n = calc_naksat(year)
            self.bd_preview.configure(text=f"{z}  |  {n}  |  ค.ศ. {year}")
            self.p2_error.configure(text="")
        except Exception:
            self.bd_preview.configure(text="กรุณาระบุข้อมูลให้ครบถ้วน")

    def _confirm_and_go(self):
        name = self.name_var.get().strip()
        if not name:
            self.p2_error.configure(text="⚠️ กรุณากรอกชื่อก่อนค่ะ")
            return
        
        if len(name) > 50:
            self.p2_error.configure(text="⚠️ ชื่อยาวเกินไปค่ะ (ไม่เกิน 50 ตัวอักษร)")
            return
            
        try:
            # ดึงปีปัจจุบันที่เป็น ค.ศ. (เช่น 2024, 2025, 2026)
            import datetime
            current_year = datetime.datetime.now().year
            
            year = int(self.yyyy_var.get())
            
            # เปลี่ยนจาก 2026 เป็น current_year
            if not (1900 <= year <= current_year): 
                raise ValueError
                
        except ValueError:
            self.p2_error.configure(text=f"⚠️ กรุณากรอกปีให้ถูกต้อง (ค.ศ. 1900–{current_year})")
            return

        try:
            day = int(self.dd_var.get())
            month_val = MONTHS_TH.index(self.mm_var.get()) + 1 
            _, z = calc_zodiac(day, month_val)
            _, n = calc_naksat(year)
            import calendar
            max_d = calendar.monthrange(year, month_val)[1]
            if day > max_d:
                self.p2_error.configure(text=f"⚠️ เดือนนี้มีสูงสุดแค่ {max_d} วันค่ะ")
                return

        except Exception as e:
            self.p2_error.configure(text="⚠️ ข้อมูลวันที่ไม่ถูกต้อง")
            return

        self.p2_error.configure(text="")
        self._username    = name
        self._birth_day   = day
        self._birth_month = month_val  
        self._birth_year  = year
        self._fortune_text = ""
        self._show_result()

    # ══════════════════════════════════════
    #  หน้า 3 — ผลลัพธ์
    # ══════════════════════════════════════
    def _build_page3(self):
        self.page3 = CTkFrame(self.app, fg_color="transparent", corner_radius=0)
        self._add_bg(self.page3)

        # ── ส่วนบน: card ขาว ──
        self.result_card = CTkFrame(self.page3, fg_color="#FFFFFF", corner_radius=35,
                                    border_width=3, border_color="#DDA0DD", width=730, height=630)
        self.result_card.place(relx=0.5, y=15, anchor="n")
        self.result_card.pack_propagate(False)

        inner = CTkFrame(self.result_card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=25, pady=18)

        # row 0: badge หมวด
        self.r_badge = CTkLabel(inner, text="", font=FONTS["badge"], corner_radius=15, padx=14, pady=5)
        self.r_badge.pack(pady=(0,6))

        # row 1: ชื่อผู้ใช้
        self.r_name = CTkLabel(inner, text="", font=FONTS["title_large"], text_color="#3A1060")
        self.r_name.pack()

        # row 2: icon ใหญ่
        self.r_icon = CTkLabel(inner, text="🔮", font=FONTS["emoji_large"])
        self.r_icon.pack(pady=(4,2))

        # row 3: กล่อง ราศี + นักษัตร (แบบ 2 คอลัมน์)
        info_row = CTkFrame(inner, fg_color="transparent")
        info_row.pack(fill="x", pady=(2,4))

        self.r_zodiac_box = CTkFrame(info_row, fg_color="#F5F0FF", corner_radius=16,
                                     border_width=2, border_color="#C8A8E8")
        self.r_zodiac_box.pack(side="left", expand=True, fill="both", padx=(0,8), ipady=6)
        CTkLabel(self.r_zodiac_box, text="ราศี", font=FONTS["caption"], text_color="#9370DB").pack()
        self.r_zodiac_val = CTkLabel(self.r_zodiac_box, text="", font=FONTS["title"], text_color="#6A1AB2")
        self.r_zodiac_val.pack()

        self.r_naksat_box = CTkFrame(info_row, fg_color="#FFF0F8", corner_radius=16,
                                     border_width=2, border_color="#E8A8C8")
        self.r_naksat_box.pack(side="left", expand=True, fill="both", padx=(8,0), ipady=6)
        CTkLabel(self.r_naksat_box, text="ปีนักษัตร", font=FONTS["caption"], text_color="#B0306A").pack()
        self.r_naksat_val = CTkLabel(self.r_naksat_box, text="", font=FONTS["title"], text_color="#C0185A")
        self.r_naksat_val.pack()

        # row 4: วันเกิด
        self.r_bdate = CTkLabel(inner, text="", font=FONTS["caption"], text_color="#999999")
        self.r_bdate.pack(pady=(2,6))

        # row 5: เส้นคั่น
        CTkFrame(inner, height=2, fg_color="#E8D8F8").pack(fill="x", padx=20)

        # row 6: กล่องคำทำนาย (scroll ได้ถ้าข้อความยาว)
        fortune_box = CTkFrame(inner, fg_color="#FAFAFE", corner_radius=18,
                               border_width=1, border_color="#E0D0F0")
        fortune_box.pack(fill="both", expand=True, pady=(8,8))

        self.r_title = CTkLabel(fortune_box, text="กดปุ่มเพื่อรับคำทำนาย",
                                font=FONTS["title"], text_color="#6A1AB2")
        self.r_title.pack(pady=(10,4))

        self.r_body = CTkLabel(fortune_box, text="", font=FONTS["body_large"],
                               wraplength=560, justify="center", text_color="#4A2A6A")
        self.r_body.pack(pady=(0,10))

        # row 7: ปุ่ม
        btn_row = CTkFrame(inner, fg_color="transparent")
        btn_row.pack(pady=(4,0))

        self.fetch_btn = CTkButton(
            btn_row, text="🔮 รับคำทำนาย", font=FONTS["button_large"],
            fg_color="#8A2BE2", hover_color="#6A1AB2", corner_radius=28, width=200, height=44,
            command=self.fetch_fortune)
        self.fetch_btn.pack(side="left", padx=6)

        CTkButton(btn_row, text="🔄 เปลี่ยนหมวด", font=FONTS["button"],
                  fg_color="#E6E6FA", text_color="#5A3060", hover_color="#D0C0F0",
                  corner_radius=28, width=175, height=44,
                  command=lambda: self.show_page(self.page1)).pack(side="left", padx=6)

        self.pdf_btn = CTkButton(
            btn_row, text="📄 Export PDF", font=FONTS["button"],
            fg_color="#28A745", hover_color="#1E7A33", text_color="white",
            corner_radius=28, width=165, height=44,
            command=self._export_pdf, state="disabled")
        self.pdf_btn.pack(side="left", padx=6)

    def _show_result(self):
        cat = next(c for c in CATEGORIES if c["key"]==self.selected_category)
        _, z = calc_zodiac(self._birth_day, self._birth_month)
        _, n = calc_naksat(self._birth_year)

        self.result_card.configure(border_color=adj(cat["color"],+10))
        self.r_badge.configure(text=f"{cat['icon']} ดวง{cat['label']}",
                               fg_color=cat["light"], text_color=adj(cat["color"],-30))
        self.r_name.configure(text=f"✨  {self._username}  ✨")
        self.r_icon.configure(text=cat["icon"])

        self.r_zodiac_box.configure(border_color=adj(cat["color"],+20))
        self.r_zodiac_val.configure(text=z)
        self.r_naksat_box.configure(border_color=adj(cat["color"],+20))
        self.r_naksat_val.configure(text=n)

        self.r_bdate.configure(
            text=f"เกิดวันที่  {self._birth_day}  {MONTHS_TH[self._birth_month-1]}  {self._birth_year}"
        )
        self.r_title.configure(text="กดปุ่มเพื่อรับคำทำนาย", text_color="#6A1AB2")
        self.r_body.configure(text="", text_color="#4A2A6A")
        self.fetch_btn.configure(state="normal", text="🔮 รับคำทำนาย", fg_color="#8A2BE2")
        self.pdf_btn.configure(state="disabled")

        self.show_page(self.page3)

    def fetch_fortune(self):
        self.fetch_btn.configure(state="disabled", text="⏳ กำลังถามดวงดาว...", fg_color="#AAAAAA")
        self.pdf_btn.configure(state="disabled")
        cat  = self.selected_category
        d, m, y = self._birth_day, self._birth_month, self._birth_year

        def _fetch():
            result = udp_ask_fortune(cat, d, m, y)
            self.app.after(0, lambda: self._apply_fortune(result))

        threading.Thread(target=_fetch, daemon=True).start()

    def _apply_fortune(self, text: str | None):
        if text:
            # แยก suffix ราศี/นักษัตรที่ server แนบมา ออกจากคำทำนายหลัก
            parts = text.split("\n\n")
            main  = parts[0].strip()
            self._fortune_text = main

            self.r_icon.configure(text="🌟")
            self.r_title.configure(text="คำทำนายจากดวงดาว ✨", text_color="#6A1AB2")
            self.r_body.configure(text=main, text_color="#4A2A6A")
            self.pdf_btn.configure(state="normal")
        else:
            self._fortune_text = ""
            self.r_icon.configure(text="⚠️")
            self.r_title.configure(text="การเชื่อมต่อขัดข้อง", text_color="#FF4500")
            self.r_body.configure(
                text="ไม่สามารถเชื่อมต่อกับดวงดาวได้\n(กรุณาตรวจสอบว่าเปิด server.py หรือยัง)",
                text_color="#FF4500")

        self.fetch_btn.configure(state="normal", text="🔄 ดูดวงใหม่", fg_color="#8A2BE2")

    def _export_pdf(self):
        from tkinter import filedialog, messagebox
        if not self._fortune_text:
            return

        cat = next(c for c in CATEGORIES if c["key"]==self.selected_category)
        _, z = calc_zodiac(self._birth_day, self._birth_month)
        _, n = calc_naksat(self._birth_year)

        default_name = f"fortune_{self._username}_{self._birth_year}.pdf"
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files","*.pdf")],
            initialfile=default_name,
            title="บันทึกผลดวงชะตา",
        )
        if not path:
            return

        self.pdf_btn.configure(state="disabled", text="⏳ กำลังสร้าง PDF...")
        def _do():
            try:
                export_fortune_pdf(
                    username     = self._username,
                    birth_day    = self._birth_day,
                    birth_month  = self._birth_month,
                    birth_year   = self._birth_year,
                    cat_label    = cat["label"],
                    zodiac_label = z,
                    naksat_label = n,
                    fortune_text = self._fortune_text,
                    save_path    = path,
                )
                self.app.after(0, lambda: messagebox.showinfo("สำเร็จ", f"บันทึก PDF เรียบร้อยแล้ว!\n{path}"))
            except Exception as e:
                self.app.after(0, lambda: messagebox.showerror("ผิดพลาด", str(e)))
            finally:
                self.app.after(0, lambda: self.pdf_btn.configure(state="normal", text="📄 Export PDF"))

        threading.Thread(target=_do, daemon=True).start()

    # ──────────── Floating Flowers ────────────
    def _create_floating_flowers(self, parent):
        for i in range(10):
            if self.use_png and self.flower_images:
                lbl = CTkLabel(parent, image=random.choice(self.flower_images), text="", fg_color="transparent")
            else:
                lbl = CTkLabel(parent, text=random.choice(FLOAT_EMOJIS),
                               font=("Arial", random.randint(20,32)), fg_color="transparent",
                               text_color=random.choice(["#FF69B4","#9370DB","#FFA07A","#FFD700"]))
            x = random.randint(20,750)
            y = random.randint(20,650)
            lbl.place(x=x, y=y)
            self._animate_float(lbl, x, y, i)

    def _animate_float(self, lbl, sx, sy, idx):
        def go(step=0):
            ox = math.cos(step*0.1+idx)*15
            oy = math.sin(step*0.1)*20
            nx, ny = sx+ox, sy+oy
            if 10<=nx<=770 and 10<=ny<=670:
                lbl.place(x=nx, y=ny)
            self.app.after(50, lambda: go(step+1))
        go()

    def _animate_title(self):
        def cycle(i=0):
            try:
                self.title_label.configure(text_color=TITLE_COLORS[i%len(TITLE_COLORS)])
                self.app.after(1000, lambda: cycle(i+1))
            except Exception:
                pass
        cycle()

    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    FortuneGardenApp().run()