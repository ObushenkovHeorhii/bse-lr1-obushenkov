import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from datetime import datetime
import os

# --- КОЛЬОРОВА ПАЛІТРА ТА СТИЛІ (Slate & Emerald Theme) ---
BG_DARK = "#0F172A"       # Slate 900
BG_CARD = "#1E293B"       # Slate 800
BG_INPUT = "#334155"      # Slate 700
FG_LIGHT = "#F8FAFC"      # Slate 50
FG_MUTED = "#94A3B8"      # Slate 400
ACCENT_GREEN = "#10B981"  # Emerald 500
ACCENT_GREEN_HOVER = "#059669" # Emerald 600
ACCENT_BLUE = "#3B82F6"   # Blue 500
ACCENT_BLUE_HOVER = "#2563EB"  # Blue 600
ACCENT_RED = "#EF4444"    # Red 500
ACCENT_RED_HOVER = "#DC2626"  # Red 600
BORDER_COLOR = "#475569"  # Slate 600

FONT_TITLE = ("Helvetica", 16, "bold")
FONT_SUBTITLE = ("Helvetica", 10)
FONT_LABEL = ("Helvetica", 9, "bold")
FONT_INPUT = ("Helvetica", 10)
FONT_BUTTON = ("Helvetica", 10, "bold")
FONT_PREVIEW = ("Courier New", 10)

# --- УКРАЇНСЬКИЙ АЛФАВІТ ДЛЯ СОРТУВАННЯ ---
UKRAINIAN_ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"

def ukrainian_sort_key(text):
    """
    Повертає ключ для правильного сортування українських слів.
    Враховує специфічні літери (Ґ, Є, І, Ї) у вірній послідовності.
    """
    key = []
    clean_text = text.strip().lower()
    for char in clean_text:
        idx = UKRAINIAN_ALPHABET.find(char)
        if idx != -1:
            key.append(idx)
        else:
            # Символи поза алфавітом (цифри, латиниця, розділові знаки)
            # розміщуються після українських літер
            key.append(len(UKRAINIAN_ALPHABET) + ord(char))
    return key


# --- ФУНКЦІЇ ФОРМАТУВАННЯ ---

def clean_author_name(name):
    """Очищення та форматування імені автора (додавання пробілів після крапок)."""
    name = re.sub(r'\s+', ' ', name.strip())
    # Додаємо пробіл після крапок ініціалів, якщо немає наступного символу
    name = re.sub(r'([А-ЯІЇЄҐ]\.)\s*(?=[А-ЯІЇЄҐ])', r'\1 ', name)
    name = re.sub(r'([А-ЯІЇЄҐ]\.)\s*([А-ЯІЇЄҐ]\.)', r'\1 \2', name)
    return name

def parse_authors(authors_str):
    """Розділяє рядок авторів на список окремих відформатованих імен."""
    if not authors_str:
        return []
    # Розділяємо за комами чи крапками з комою
    raw_authors = re.split(r'[,;]\s*', authors_str)
    return [clean_author_name(a) for a in raw_authors if a.strip()]

def swap_name_to_initials_first(name):
    """Перетворює 'Прізвище І. О.' на 'І. О. Прізвище' для списку відповідальності."""
    name = clean_author_name(name)
    # Збіг для формату "Прізвище І. О." або "Прізвище І."
    match = re.match(r'^([А-ЯІЇЄҐа-яіїєґ\-\']+)\s+([А-ЯІЇЄҐ]\.\s*(?:[А-ЯІЇЄҐ]\.)?)$', name)
    if match:
        return f"{match.group(2)} {match.group(1)}"
    return name

def format_book(authors, title, subtitle, city, publisher, year, pages):
    res = ""
    # 1-3 автори: виводяться перед назвою
    if authors and len(authors) <= 3:
        res += ", ".join(authors) + ". "
    
    res += title
    
    if subtitle:
        res += " : " + subtitle
        
    # 4+ авторів: опис під назвою, перший автор зазначається за косою рискою
    if authors and len(authors) >= 4:
        first_author_swapped = swap_name_to_initials_first(authors[0])
        res += " / " + first_author_swapped + " та ін."
        
    pub_part = ""
    if city:
        pub_part += city
    if publisher:
        if pub_part:
            pub_part += " : " + publisher
        else:
            pub_part += publisher
    if year:
        if pub_part:
            pub_part += ", " + year
        else:
            pub_part += year
            
    if pub_part:
        res += ". " + pub_part
        
    if pages:
        res += ". " + pages + " с."
        
    if not res.endswith("."):
        res += "."
        
    res = re.sub(r'\.\s*\.', '.', res)
    return res.strip()

def format_article(authors, title, journal, year, volume, number, pages):
    res = ""
    if authors:
        res += ", ".join(authors) + ". "
        
    res += title + ". "
    res += journal + ". "
    res += year + ". "
    
    vol_num = []
    if volume:
        vol_num.append(f"Т. {volume}")
    if number:
        vol_num.append(f"№ {number}")
        
    if vol_num:
        res += ", ".join(vol_num) + ". "
        
    if pages:
        res += f"С. {pages}."
        
    if not res.endswith("."):
        res += "."
        
    res = re.sub(r'\.\s*\.', '.', res)
    return res.strip()

def format_web(authors, title, site_name, url, access_date):
    res = ""
    if authors:
        res += ", ".join(authors) + ". "
        
    res += title
    
    if site_name:
        res += " : " + site_name
        
    if url:
        res += f". URL: {url}"
        
    if access_date:
        res += f" (дата звернення: {access_date})"
        
    if not res.endswith("."):
        res += "."
        
    res = re.sub(r'\.\s*\.', '.', res)
    return res.strip()

def format_conference(authors, title, collection, conf_loc, conf_date, city, publisher, year, pages):
    res = ""
    if authors:
        res += ", ".join(authors) + ". "
        
    res += title + ". "
    res += collection
    
    conf_details = []
    if conf_loc:
        conf_details.append(conf_loc)
    if conf_date:
        conf_details.append(conf_date)
        
    if conf_details:
        res += " : матеріали наук.-практ. конф. (" + ", ".join(conf_details) + ")"
    else:
        res += " : матеріали наук.-практ. конф."
        
    pub_part = ""
    if city:
        pub_part += city
    if publisher:
        if pub_part:
            pub_part += " : " + publisher
        else:
            pub_part += publisher
    if year:
        if pub_part:
            pub_part += ", " + year
        else:
            pub_part += year
            
    if pub_part:
        res += ". " + pub_part
        
    if pages:
        res += ". С. " + pages
        
    if not res.endswith("."):
        res += "."
        
    res = re.sub(r'\.\s*\.', '.', res)
    return res.strip()

def format_dissertation(author, title, work_type, degree, specialty, institution, city, year, pages):
    res = ""
    if author:
        res += author + ". "
        
    res += title
    
    if work_type == "автореферат":
        res += " : автореф. дис. на здобуття наук. ступеня " + degree
    else:
        res += " : дис. ... " + degree
        
    if specialty:
        res += " : " + specialty
        
    if institution:
        res += " / " + institution
        
    loc_part = ""
    if city:
        loc_part += city
    if year:
        if loc_part:
            loc_part += ", " + year
        else:
            loc_part += year
            
    if loc_part:
        res += ". " + loc_part
        
    if pages:
        res += ". " + pages + " с."
        
    if not res.endswith("."):
        res += "."
        
    res = re.sub(r'\.\s*\.', '.', res)
    return res.strip()


# --- КЛАС ГОЛОВНОГО ВІКНА ПРОГРАМИ ---

class ReferenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Оформлювач джерел ДСТУ 8302:2015")
        self.root.geometry("1020x680")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)
        
        # Центрування вікна
        self.center_window(1020, 680)
        
        # Сховище джерел
        self.sources_list = []
        
        # Ініціалізація інтерфейсу
        self.setup_ui()
        
        # Встановлення початкової вкладки
        self.select_tab("book")
        self.autofill_dates()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - 40
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # 1. Заголовок програми
        self.header_frame = tk.Frame(self.root, bg=BG_CARD, height=70, bd=0, highlightthickness=0)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.header_frame.pack_propagate(False)
        
        # Декоративна лінія знизу заголовка
        self.header_line = tk.Frame(self.root, bg=ACCENT_GREEN, height=3, bd=0)
        self.header_line.pack(fill=tk.X, side=tk.TOP)
        
        title_label = tk.Label(
            self.header_frame, 
            text="Оформлення джерел за ДСТУ 8302:2015", 
            font=FONT_TITLE, 
            bg=BG_CARD, 
            fg=FG_LIGHT
        )
        title_label.pack(anchor=tk.W, padx=25, pady=(12, 2))
        
        subtitle_label = tk.Label(
            self.header_frame, 
            text="Швидке створення бібліографічних посилань для наукових робіт та курсових", 
            font=FONT_SUBTITLE, 
            bg=BG_CARD, 
            fg=FG_MUTED
        )
        subtitle_label.pack(anchor=tk.W, padx=25)
        
        # Головний контейнер на два стовпчики
        self.main_container = tk.Frame(self.root, bg=BG_DARK)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=5, minsize=480)
        self.main_container.grid_columnconfigure(1, weight=5, minsize=480)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # --- ЛІВА ПАНЕЛЬ (Введення параметрів) ---
        self.left_panel = tk.Frame(self.main_container, bg=BG_CARD, bd=1, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Заголовок панелі та Кнопки Вкладок
        self.tabs_container = tk.Frame(self.left_panel, bg=BG_CARD)
        self.tabs_container.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        self.tab_buttons = {}
        tab_names = [
            ("book", "Книга"),
            ("article", "Стаття"),
            ("web", "Веб-сайт"),
            ("conf", "Конференція"),
            ("diss", "Дисертація")
        ]
        
        for code, label in tab_names:
            btn = tk.Button(
                self.tabs_container, 
                text=label,
                font=FONT_BUTTON,
                bg=BG_INPUT,
                fg=FG_LIGHT,
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=6,
                cursor="hand2",
                command=lambda c=code: self.select_tab(c)
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            self.setup_hover(btn, BG_INPUT, BORDER_COLOR)
            self.tab_buttons[code] = btn
            
        # Контейнер для полів форми
        self.form_container = tk.Frame(self.left_panel, bg=BG_CARD)
        self.form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.setup_forms()
        
        # Панель Дій форми (Генерація, Попередній перегляд)
        self.preview_container = tk.Frame(self.left_panel, bg=BG_CARD)
        self.preview_container.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=20)
        
        preview_title = tk.Label(self.preview_container, text="ПОПЕРЕДНІЙ ПЕРЕГЛЯД ПОСИЛАННЯ", font=FONT_LABEL, bg=BG_CARD, fg=FG_MUTED)
        preview_title.pack(anchor=tk.W, pady=(0, 5))
        
        self.preview_text = tk.Text(
            self.preview_container, 
            height=3, 
            font=FONT_PREVIEW, 
            bg=BG_INPUT, 
            fg=FG_LIGHT, 
            bd=0, 
            highlightbackground=BORDER_COLOR, 
            highlightthickness=1,
            wrap=tk.WORD,
            padx=8,
            pady=8
        )
        self.preview_text.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки знизу форми
        self.action_btn_container = tk.Frame(self.preview_container, bg=BG_CARD)
        self.action_btn_container.pack(fill=tk.X)
        
        self.btn_generate = tk.Button(
            self.action_btn_container, 
            text="Згенерувати", 
            font=FONT_BUTTON, 
            bg=ACCENT_BLUE, 
            fg=FG_LIGHT, 
            relief=tk.FLAT, 
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.generate_current_reference
        )
        self.btn_generate.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.setup_hover(self.btn_generate, ACCENT_BLUE, ACCENT_BLUE_HOVER)
        
        self.btn_add = tk.Button(
            self.action_btn_container, 
            text="Додати до списку", 
            font=FONT_BUTTON, 
            bg=ACCENT_GREEN, 
            fg=FG_LIGHT, 
            relief=tk.FLAT, 
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.add_to_list
        )
        self.btn_add.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.setup_hover(self.btn_add, ACCENT_GREEN, ACCENT_GREEN_HOVER)
        
        
        # --- СПРАВА ПАНЕЛЬ (Керування списком) ---
        self.right_panel = tk.Frame(self.main_container, bg=BG_CARD, bd=1, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        list_title_container = tk.Frame(self.right_panel, bg=BG_CARD)
        list_title_container.pack(fill=tk.X, padx=20, pady=(15, 5))
        
        list_title = tk.Label(list_title_container, text="БІБЛІОГРАФІЧНИЙ СПИСОК", font=FONT_LABEL, bg=BG_CARD, fg=FG_LIGHT)
        list_title.pack(side=tk.LEFT)
        
        self.list_count_label = tk.Label(list_title_container, text="(0 джерел)", font=FONT_SUBTITLE, bg=BG_CARD, fg=FG_MUTED)
        self.list_count_label.pack(side=tk.LEFT, padx=5)
        
        # Список джерел (Listbox + Scrollbar)
        self.list_frame = tk.Frame(self.right_panel, bg=BG_CARD)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            self.list_frame,
            font=FONT_INPUT,
            bg=BG_INPUT,
            fg=FG_LIGHT,
            bd=0,
            highlightthickness=0,
            selectbackground=ACCENT_GREEN,
            selectforeground=FG_LIGHT,
            yscrollcommand=self.scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.listbox.yview)
        
        # Керування списком кнопок
        self.list_actions_container = tk.Frame(self.right_panel, bg=BG_CARD)
        self.list_actions_container.pack(fill=tk.X, padx=20, pady=20)
        
        # Рядок 1 кнопок керування
        self.row1_buttons = tk.Frame(self.list_actions_container, bg=BG_CARD)
        self.row1_buttons.pack(fill=tk.X, pady=(0, 8))
        
        self.btn_copy_selected = tk.Button(
            self.row1_buttons, 
            text="Копіювати виділене", 
            font=FONT_BUTTON, 
            bg=BG_INPUT, 
            fg=FG_LIGHT, 
            relief=tk.FLAT, 
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self.copy_selected
        )
        self.btn_copy_selected.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.setup_hover(self.btn_copy_selected, BG_INPUT, BORDER_COLOR)
        
        self.btn_copy_all = tk.Button(
            self.row1_buttons, 
            text="Копіювати весь список", 
            font=FONT_BUTTON, 
            bg=ACCENT_BLUE, 
            fg=FG_LIGHT, 
            relief=tk.FLAT, 
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self.copy_all_sources
        )
        self.btn_copy_all.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        self.setup_hover(self.btn_copy_all, ACCENT_BLUE, ACCENT_BLUE_HOVER)
        
        # Рядок 2 кнопок керування
        self.row2_buttons = tk.Frame(self.list_actions_container, bg=BG_CARD)
        self.row2_buttons.pack(fill=tk.X)
        
        self.btn_sort = tk.Button(
            self.row2_buttons, 
            text="Сортувати за А-Я", 
            font=FONT_BUTTON, 
            bg=ACCENT_GREEN, 
            fg=FG_LIGHT, 
            relief=tk.FLAT, 
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self.sort_list
        )
        self.btn_sort.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.setup_hover(self.btn_sort, ACCENT_GREEN, ACCENT_GREEN_HOVER)
        
        self.btn_save_file = tk.Button(
            self.row2_buttons, 
            text="Зберегти у файл", 
            font=FONT_BUTTON, 
            bg=BG_INPUT, 
            fg=FG_LIGHT, 
            relief=tk.FLAT, 
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self.save_to_file
        )
        self.btn_save_file.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.setup_hover(self.btn_save_file, BG_INPUT, BORDER_COLOR)
        
        self.btn_delete = tk.Button(
            self.row2_buttons, 
            text="Видалити", 
            font=FONT_BUTTON, 
            bg=ACCENT_RED, 
            fg=FG_LIGHT, 
            relief=tk.FLAT, 
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self.delete_selected
        )
        self.btn_delete.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        self.setup_hover(self.btn_delete, ACCENT_RED, ACCENT_RED_HOVER)
        
        # Зв'язуємо гарячу клавішу Delete для швидкого видалення
        self.listbox.bind("<Delete>", lambda event: self.delete_selected())
        
        # 3. Статус бар знизу
        self.status_frame = tk.Frame(self.root, bg=BG_DARK, height=25)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="Програма готова до роботи. Оберіть тип джерела та заповніть поля.", 
            font=("Helvetica", 8), 
            bg=BG_DARK, 
            fg=FG_MUTED
        )
        self.status_label.pack(side=tk.LEFT, padx=20)

    # --- СТВОРЕННЯ ПОЛІВ ФОРМИ ---
    
    def setup_forms(self):
        # Зберігаємо всі поля форми в словниках для кожного типу
        self.form_vars = {
            "book": {}, "article": {}, "web": {}, "conf": {}, "diss": {}
        }
        self.form_frames = {}
        
        # --- ФОРМА: КНИГА ---
        f_book = tk.Frame(self.form_container, bg=BG_CARD)
        self.form_frames["book"] = f_book
        
        self.form_vars["book"]["authors"] = self.create_form_field(f_book, "Автори (напр. Крушельницька О. В., Мельничук Д. П.):", 0)
        self.form_vars["book"]["title"] = self.create_form_field(f_book, "Назва книги (напр. Управління персоналом):", 1)
        self.form_vars["book"]["subtitle"] = self.create_form_field(f_book, "Відомості / Підзаголовок (напр. навч. посібник):", 2)
        self.form_vars["book"]["city"] = self.create_form_field(f_book, "Місто видання (напр. Київ):", 3)
        self.form_vars["book"]["publisher"] = self.create_form_field(f_book, "Видавництво (напр. Кондор):", 4)
        self.form_vars["book"]["year"] = self.create_form_field(f_book, "Рік видання (напр. 2017):", 5)
        self.form_vars["book"]["pages"] = self.create_form_field(f_book, "Кількість сторінок (напр. 256):", 6)
        
        # --- ФОРМА: СТАТТЯ ---
        f_art = tk.Frame(self.form_container, bg=BG_CARD)
        self.form_frames["article"] = f_art
        
        self.form_vars["article"]["authors"] = self.create_form_field(f_art, "Автори статті:", 0)
        self.form_vars["article"]["title"] = self.create_form_field(f_art, "Назва статті:", 1)
        self.form_vars["article"]["journal"] = self.create_form_field(f_art, "Назва журналу / періодичного видання:", 2)
        self.form_vars["article"]["year"] = self.create_form_field(f_art, "Рік видання:", 3)
        self.form_vars["article"]["volume"] = self.create_form_field(f_art, "Том (якщо є):", 4)
        self.form_vars["article"]["number"] = self.create_form_field(f_art, "Номер журналу / Випуск (напр. 1 або № 1):", 5)
        self.form_vars["article"]["pages"] = self.create_form_field(f_art, "Діапазон сторінок (напр. 121-130):", 6)
        
        # --- ФОРМА: ВЕБ-САЙТ ---
        f_web = tk.Frame(self.form_container, bg=BG_CARD)
        self.form_frames["web"] = f_web
        
        self.form_vars["web"]["authors"] = self.create_form_field(f_web, "Автори або організація (якщо є):", 0)
        self.form_vars["web"]["title"] = self.create_form_field(f_web, "Назва публікації / матеріалу сторінки:", 1)
        self.form_vars["web"]["site_name"] = self.create_form_field(f_web, "Назва веб-сайту (напр. Kyiv Dictionary):", 2)
        self.form_vars["web"]["url"] = self.create_form_field(f_web, "Посилання (URL):", 3)
        
        # Поле дати звернення з кнопкою "Сьогодні"
        date_label_frame = tk.Frame(f_web, bg=BG_CARD)
        date_label_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 2))
        
        lbl = tk.Label(date_label_frame, text="Дата звернення (ДД.ММ.РРРР):", font=FONT_LABEL, bg=BG_CARD, fg=FG_MUTED)
        lbl.pack(side=tk.LEFT)
        
        self.form_vars["web"]["access_date"] = tk.StringVar()
        
        date_input_frame = tk.Frame(f_web, bg=BG_CARD)
        date_input_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        entry = tk.Entry(
            date_input_frame, 
            textvariable=self.form_vars["web"]["access_date"], 
            font=FONT_INPUT,
            bg=BG_INPUT,
            fg=FG_LIGHT,
            bd=0,
            insertbackground=FG_LIGHT,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        
        btn_today = tk.Button(
            date_input_frame, 
            text="Сьогодні", 
            font=("Helvetica", 8, "bold"), 
            bg=BG_INPUT, 
            fg=ACCENT_BLUE,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            cursor="hand2",
            command=self.set_today_date
        )
        btn_today.pack(side=tk.RIGHT, padx=(5, 0))
        self.setup_hover(btn_today, BG_INPUT, BORDER_COLOR)
        
        # --- ФОРМА: КОНФЕРЕНЦІЯ ---
        f_conf = tk.Frame(self.form_container, bg=BG_CARD)
        self.form_frames["conf"] = f_conf
        
        self.form_vars["conf"]["authors"] = self.create_form_field(f_conf, "Автори доповіді:", 0)
        self.form_vars["conf"]["title"] = self.create_form_field(f_conf, "Назва доповіді:", 1)
        self.form_vars["conf"]["collection"] = self.create_form_field(f_conf, "Назва збірника матеріалів конф.:", 2)
        self.form_vars["conf"]["conf_loc"] = self.create_form_field(f_conf, "Місце проведення конф. (напр. Харків, Україна):", 3)
        self.form_vars["conf"]["conf_date"] = self.create_form_field(f_conf, "Дата проведення конф. (напр. 15-16 травня 2026 р.):", 4)
        self.form_vars["conf"]["city"] = self.create_form_field(f_conf, "Місто видання збірника:", 5)
        self.form_vars["conf"]["publisher"] = self.create_form_field(f_conf, "Видавництво / Організатор:", 6)
        self.form_vars["conf"]["year"] = self.create_form_field(f_conf, "Рік видання збірника:", 7)
        self.form_vars["conf"]["pages"] = self.create_form_field(f_conf, "Сторінки доповіді (напр. 45-48):", 8)
        
        # --- ФОРМА: ДИСЕРТАЦІЯ ---
        f_diss = tk.Frame(self.form_container, bg=BG_CARD)
        self.form_frames["diss"] = f_diss
        
        self.form_vars["diss"]["author"] = self.create_form_field(f_diss, "Автор дисертації (Прізвище І. О.):", 0)
        self.form_vars["diss"]["title"] = self.create_form_field(f_diss, "Назва роботи:", 1)
        
        # Вибір типу роботи (Дисертація / Автореферат)
        lbl_type = tk.Label(f_diss, text="Тип роботи:", font=FONT_LABEL, bg=BG_CARD, fg=FG_MUTED)
        lbl_type.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 2))
        
        self.form_vars["diss"]["work_type"] = tk.StringVar(value="дисертація")
        
        type_frame = tk.Frame(f_diss, bg=BG_CARD)
        type_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        r_diss = tk.Radiobutton(
            type_frame, text="Дисертація", variable=self.form_vars["diss"]["work_type"], 
            value="дисертація", bg=BG_CARD, fg=FG_LIGHT, selectcolor=BG_INPUT,
            activebackground=BG_CARD, activeforeground=FG_LIGHT, font=FONT_INPUT
        )
        r_diss.pack(side=tk.LEFT, padx=(0, 20))
        
        r_auto = tk.Radiobutton(
            type_frame, text="Автореферат дисертації", variable=self.form_vars["diss"]["work_type"], 
            value="автореферат", bg=BG_CARD, fg=FG_LIGHT, selectcolor=BG_INPUT,
            activebackground=BG_CARD, activeforeground=FG_LIGHT, font=FONT_INPUT
        )
        r_auto.pack(side=tk.LEFT)
        
        self.form_vars["diss"]["degree"] = self.create_form_field(f_diss, "Науковий ступінь (напр. канд. техн. наук):", 4)
        self.form_vars["diss"]["specialty"] = self.create_form_field(f_diss, "Шифр спеціальності (напр. 05.13.06):", 5)
        self.form_vars["diss"]["institution"] = self.create_form_field(f_diss, "Установа захисту (повна назва):", 6)
        self.form_vars["diss"]["city"] = self.create_form_field(f_diss, "Місто захисту/видання:", 7)
        self.form_vars["diss"]["year"] = self.create_form_field(f_diss, "Рік:", 8)
        self.form_vars["diss"]["pages"] = self.create_form_field(f_diss, "Кількість сторінок (напр. 180):", 9)
        
        # Налаштовуємо розтягування колонок у всіх внутрішніх фреймах
        for frame in self.form_frames.values():
            frame.grid_columnconfigure(0, weight=1)

    def create_form_field(self, parent_frame, label_text, row_num):
        """Допоміжна функція для створення тексту та вікна вводу."""
        lbl = tk.Label(parent_frame, text=label_text, font=FONT_LABEL, bg=BG_CARD, fg=FG_MUTED)
        lbl.grid(row=row_num*2, column=0, columnspan=2, sticky="w", pady=(8, 2))
        
        var = tk.StringVar()
        
        # Додаємо Entry з красивими рамками
        entry = tk.Entry(
            parent_frame, 
            textvariable=var, 
            font=FONT_INPUT,
            bg=BG_INPUT,
            fg=FG_LIGHT,
            bd=0,
            insertbackground=FG_LIGHT,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        entry.grid(row=row_num*2+1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        # Щоб поле вводу виглядало трішки більшим по висоті
        entry.config(highlightcolor=ACCENT_GREEN)
        return var


    # --- КЕРУВАННЯ ВКЛАДКАМИ ---
    
    def select_tab(self, tab_code):
        """Перемикає видиму вкладку форми введення."""
        self.active_tab = tab_code
        
        # Оновлення кнопок вкладок
        for code, btn in self.tab_buttons.items():
            if code == tab_code:
                btn.config(bg=ACCENT_GREEN)
                # Скасовуємо ефект ховеру для активної вкладки
                btn.bind("<Enter>", lambda e: None)
                btn.bind("<Leave>", lambda e: None)
            else:
                btn.config(bg=BG_INPUT)
                self.setup_hover(btn, BG_INPUT, BORDER_COLOR)
                
        # Показати відповідний фрейм
        for code, frame in self.form_frames.items():
            if code == tab_code:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()
                
        # Очистити попередній перегляд при перемиканні
        self.set_preview_text("")

    # --- ЕФЕКТИ ХОВЕРУ ТА МІКРО-АНІМАЦІЇ ---
    
    def setup_hover(self, widget, normal_bg, hover_bg):
        """Налаштовує зміну кольору кнопки при наведенні курсору."""
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))

    def set_today_date(self):
        """Встановлює сьогоднішню дату в полі дати звернення."""
        today = datetime.now().strftime("%d.%m.%Y")
        self.form_vars["web"]["access_date"].set(today)

    def autofill_dates(self):
        """Автоматично заповнює дату при відкритті програми."""
        self.set_today_date()

    def set_status(self, text, is_error=False):
        """Оновлює повідомлення в статус барі."""
        color = ACCENT_RED if is_error else FG_MUTED
        self.status_label.config(text=text, fg=color)

    def set_preview_text(self, text):
        """Встановлює текст у вікні попереднього перегляду."""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", text)
        self.preview_text.config(state=tk.DISABLED)


    # --- ЛОГІКА ЗБОРУ ДАНИХ ТА ГЕНЕРАЦІЇ ---
    
    def get_formatted_reference(self):
        """Збирає введені дані та форматує посилання відповідно до вкладки."""
        code = self.active_tab
        vars_dict = self.form_vars[code]
        
        # 1. КНИГА
        if code == "book":
            title = vars_dict["title"].get().strip()
            if not title:
                self.set_status("Помилка: Назва книги є обов'язковим полем!", is_error=True)
                return None
                
            authors = parse_authors(vars_dict["authors"].get())
            subtitle = vars_dict["subtitle"].get().strip()
            city = vars_dict["city"].get().strip()
            publisher = vars_dict["publisher"].get().strip()
            year = vars_dict["year"].get().strip()
            pages = vars_dict["pages"].get().strip()
            
            return format_book(authors, title, subtitle, city, publisher, year, pages)
            
        # 2. СТАТТЯ
        elif code == "article":
            title = vars_dict["title"].get().strip()
            journal = vars_dict["journal"].get().strip()
            if not title or not journal:
                self.set_status("Помилка: Назва статті та Назва журналу є обов'язковими!", is_error=True)
                return None
                
            authors = parse_authors(vars_dict["authors"].get())
            year = vars_dict["year"].get().strip()
            volume = vars_dict["volume"].get().strip()
            number = vars_dict["number"].get().strip()
            pages = vars_dict["pages"].get().strip()
            
            return format_article(authors, title, journal, year, volume, number, pages)
            
        # 3. ВЕБ-САЙТ
        elif code == "web":
            title = vars_dict["title"].get().strip()
            url = vars_dict["url"].get().strip()
            if not title or not url:
                self.set_status("Помилка: Назва матеріалу та URL є обов'язковими!", is_error=True)
                return None
                
            authors = parse_authors(vars_dict["authors"].get())
            site_name = vars_dict["site_name"].get().strip()
            access_date = vars_dict["access_date"].get().strip()
            
            return format_web(authors, title, site_name, url, access_date)
            
        # 4. КОНФЕРЕНЦІЯ
        elif code == "conf":
            title = vars_dict["title"].get().strip()
            collection = vars_dict["collection"].get().strip()
            if not title or not collection:
                self.set_status("Помилка: Назва доповіді та Назва збірника матеріалів є обов'язковими!", is_error=True)
                return None
                
            authors = parse_authors(vars_dict["authors"].get())
            conf_loc = vars_dict["conf_loc"].get().strip()
            conf_date = vars_dict["conf_date"].get().strip()
            city = vars_dict["city"].get().strip()
            publisher = vars_dict["publisher"].get().strip()
            year = vars_dict["year"].get().strip()
            pages = vars_dict["pages"].get().strip()
            
            return format_conference(authors, title, collection, conf_loc, conf_date, city, publisher, year, pages)
            
        # 5. ДИСЕРТАЦІЯ
        elif code == "diss":
            title = vars_dict["title"].get().strip()
            author = vars_dict["author"].get().strip()
            if not title or not author:
                self.set_status("Помилка: Автор та Назва дисертації є обов'язковими!", is_error=True)
                return None
                
            work_type = vars_dict["work_type"].get()
            degree = vars_dict["degree"].get().strip()
            specialty = vars_dict["specialty"].get().strip()
            institution = vars_dict["institution"].get().strip()
            city = vars_dict["city"].get().strip()
            year = vars_dict["year"].get().strip()
            pages = vars_dict["pages"].get().strip()
            
            # Автор для дисертацій вказується як один відформатований автор
            formatted_author = clean_author_name(author)
            
            return format_dissertation(formatted_author, title, work_type, degree, specialty, institution, city, year, pages)
            
        return None

    def generate_current_reference(self):
        """Кнопка 'Згенерувати': форматує і показує посилання у полі прев'ю."""
        ref = self.get_formatted_reference()
        if ref:
            self.set_preview_text(ref)
            self.set_status("Посилання успішно згенеровано.")
            # Автоматично копіюємо в буфер обміну
            self.root.clipboard_clear()
            self.root.clipboard_append(ref)
            self.root.update()
            self.set_status("Згенеровано та скопійовано в буфер обміну!")

    def add_to_list(self):
        """Кнопка 'Додати до списку': додає посилання до списку літератури."""
        ref = self.get_formatted_reference()
        if ref:
            if ref in self.sources_list:
                self.set_status("Це джерело вже є в списку!", is_error=True)
                return
                
            self.sources_list.append(ref)
            self.update_listbox()
            self.set_preview_text(ref)
            self.set_status("Джерело додано до списку.")
            
            # Очищуємо поля поточної форми, окрім міст / років / дат для швидкого вводу наступних
            self.clear_some_inputs()
            
    def clear_some_inputs(self):
        """Очищує основні текстові поля для швидкого введення нового джерела."""
        code = self.active_tab
        vars_dict = self.form_vars[code]
        
        # Очищуємо автори та назви, але зберігаємо загальні поля (місто, рік, видавництво)
        if "authors" in vars_dict:
            vars_dict["authors"].set("")
        if "author" in vars_dict:
            vars_dict["author"].set("")
        if "title" in vars_dict:
            vars_dict["title"].set("")
        if "subtitle" in vars_dict:
            vars_dict["subtitle"].set("")
        if "url" in vars_dict:
            vars_dict["url"].set("")
        if "pages" in vars_dict:
            vars_dict["pages"].set("")


    # --- КЕРУВАННЯ СПИСКОМ ДЖЕРЕЛ ---
    
    def update_listbox(self):
        """Оновлює відображення Listbox відповідно до масиву sources_list."""
        self.listbox.delete(0, tk.END)
        for src in self.sources_list:
            self.listbox.insert(tk.END, src)
            
        count = len(self.sources_list)
        self.list_count_label.config(text=f"({count} джерел)")

    def delete_selected(self):
        """Видаляє виділене джерело зі списку."""
        try:
            selected_idx = self.listbox.curselection()
            if not selected_idx:
                self.set_status("Помилка: Оберіть джерело для видалення!", is_error=True)
                return
                
            idx = selected_idx[0]
            val = self.listbox.get(idx)
            self.sources_list.remove(val)
            self.update_listbox()
            self.set_status("Джерело вилучено зі списку.")
        except Exception as e:
            self.set_status(f"Помилка при видаленні: {str(e)}", is_error=True)

    def copy_selected(self):
        """Копіює виділене джерело в буфер обміну."""
        try:
            selected_idx = self.listbox.curselection()
            if not selected_idx:
                self.set_status("Помилка: Спочатку виділіть джерело у списку!", is_error=True)
                return
                
            idx = selected_idx[0]
            val = self.listbox.get(idx)
            
            self.root.clipboard_clear()
            self.root.clipboard_append(val)
            self.root.update()
            self.set_status("Вибране посилання скопійовано!")
        except Exception as e:
            self.set_status(f"Помилка копіювання: {str(e)}", is_error=True)

    def copy_all_sources(self):
        """Копіює весь список літератури (кожен запис з нового рядка)."""
        if not self.sources_list:
            self.set_status("Помилка: Список літератури порожній!", is_error=True)
            return
            
        full_text = "\n".join(self.sources_list)
        self.root.clipboard_clear()
        self.root.clipboard_append(full_text)
        self.root.update()
        self.set_status("Весь список успішно скопійовано в буфер!")

    def sort_list(self):
        """Сортує список за українським алфавітом (інтелектуальне сортування)."""
        if not self.sources_list:
            self.set_status("Помилка: Список літератури порожній!", is_error=True)
            return
            
        # Сортуємо список за допомогою нашого кастомного українського ключа
        self.sources_list.sort(key=ukrainian_sort_key)
        self.update_listbox()
        self.set_status("Список успішно відсортовано за українським алфавітом!")

    def save_to_file(self):
        """Зберігає список літератури у текстовий файл."""
        if not self.sources_list:
            self.set_status("Помилка: Список літератури порожній!", is_error=True)
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")],
            title="Зберегти бібліографічний список"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    for i, src in enumerate(self.sources_list, 1):
                        f.write(f"{i}. {src}\n")
                self.set_status(f"Список збережено у файл: {os.path.basename(file_path)}")
            except Exception as e:
                self.set_status(f"Помилка при збереженні: {str(e)}", is_error=True)


if __name__ == "__main__":
    root = tk.Tk()
    
    # Застосуємо стиль ttk для скролбару та деяких базових речей
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "TScrollbar", 
        gripcount=0, 
        background=BG_INPUT, 
        troughcolor=BG_CARD, 
        bordercolor=BORDER_COLOR, 
        arrowcolor=FG_LIGHT
    )
    
    app = ReferenceApp(root)
    root.mainloop()
