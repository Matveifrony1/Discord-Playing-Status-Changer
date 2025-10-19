import customtkinter as ctk
from pypresence import Presence
import json
import os
import time
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread
import pystray
from pystray import MenuItem as item
import sys
import winreg
import webbrowser

# Определяем базовую директорию (для exe и для разработки)
if getattr(sys, 'frozen', False):
    # Для PyInstaller с --onefile ресурсы в _MEIPASS
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Создаем папку в AppData\Local для конфига
APP_DATA_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'Discord Playing Status Changer')
os.makedirs(APP_DATA_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(APP_DATA_DIR, 'profiles.json')

TRANSLATIONS = {
    "en": {
        "title": "Discord Playing Status Changer",
        "profiles": "Profiles",
        "app_id": "App ID:",
        "new": "+ New",
        "save": "Save",
        "profile_name": "Profile Name",
        "details": "Details",
        "state": "State",
        "large_image": "Large Image",
        "small_image": "Small Image",
        "key": "Key:",
        "text": "Text:",
        "button": "Button",
        "url": "URL:",
        "activate": "Activate",
        "stop": "Stop",
        "delete": "Delete Profile",
        "active": "● Active",
        "inactive": "● Inactive",
        "language": "Language",
        "show": "Show Window",
        "quit": "Quit",
        "guide": "Guide",
        "autostart": "Autostart",
        "next": "Next",
        "prev": "Previous",
        "close": "Close"
    },
    "ru": {
        "title": "Discord Playing Status Changer",
        "profiles": "Профили",
        "app_id": "App ID:",
        "new": "+ Новый",
        "save": "Сохранить",
        "profile_name": "Название профиля",
        "details": "Details",
        "state": "State",
        "large_image": "Большая картинка",
        "small_image": "Маленькая картинка",
        "key": "Key:",
        "text": "Text:",
        "button": "Кнопка",
        "url": "URL:",
        "activate": "Активировать",
        "stop": "Остановить",
        "delete": "Удалить профиль",
        "active": "● Активен",
        "inactive": "● Неактивен",
        "language": "Язык",
        "show": "Показать окно",
        "quit": "Выход",
        "guide": "Гайд",
        "autostart": "Автозагрузка",
        "next": "Далее",
        "prev": "Назад",
        "close": "Закрыть"
    }
}

class GuideWindow:
    def __init__(self, parent, images_count, title, language):
        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Устанавливаем иконку
        try:
            icon_path = os.path.join(BASE_DIR, "icon.ico")
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
        except:
            pass
        
        self.images_count = images_count
        self.current_index = 0
        self.language = language
        
        self.image_label = ctk.CTkLabel(self.window, text="")
        self.image_label.pack(fill="both", expand=True, padx=15, pady=15)
        
        nav_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.prev_btn = ctk.CTkButton(nav_frame, text=TRANSLATIONS[language]["prev"], 
                                      command=self.prev_image, width=100, height=30)
        self.prev_btn.pack(side="left", padx=5)
        
        self.page_label = ctk.CTkLabel(nav_frame, text=f"1 / {images_count}", 
                                       font=("Segoe UI", 12))
        self.page_label.pack(side="left", expand=True)
        
        self.next_btn = ctk.CTkButton(nav_frame, text=TRANSLATIONS[language]["next"], 
                                      command=self.next_image, width=100, height=30)
        self.next_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(nav_frame, text=TRANSLATIONS[language]["close"], 
                     command=self.window.destroy, width=100, height=30,
                     fg_color="#ed4245", hover_color="#c03537").pack(side="left", padx=5)
        
        self.load_image()
    
    def load_image(self):
        try:
            img_path = os.path.join(BASE_DIR, f"guide_{self.current_index + 1}.png")
            img = Image.open(img_path)
            img.thumbnail((770, 500), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
        except:
            self.image_label.configure(text=f"guide_{self.current_index + 1}.png not found", 
                                      image=None)
        
        self.page_label.configure(text=f"{self.current_index + 1} / {self.images_count}")
        self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_index < self.images_count - 1 else "disabled")
    
    def next_image(self):
        if self.current_index < self.images_count - 1:
            self.current_index += 1
            self.load_image()
    
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

class ImageGuideWindow:
    def __init__(self, parent, title, language):
        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Устанавливаем иконку
        try:
            icon_path = os.path.join(BASE_DIR, "icon.ico")
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
        except:
            pass
        
        self.images_count = 2
        self.current_index = 0
        self.language = language
        
        self.image_label = ctk.CTkLabel(self.window, text="")
        self.image_label.pack(fill="both", expand=True, padx=15, pady=15)
        
        nav_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.prev_btn = ctk.CTkButton(nav_frame, text=TRANSLATIONS[language]["prev"], 
                                      command=self.prev_image, width=100, height=30)
        self.prev_btn.pack(side="left", padx=5)
        
        self.page_label = ctk.CTkLabel(nav_frame, text=f"1 / {self.images_count}", 
                                       font=("Segoe UI", 12))
        self.page_label.pack(side="left", expand=True)
        
        self.next_btn = ctk.CTkButton(nav_frame, text=TRANSLATIONS[language]["next"], 
                                      command=self.next_image, width=100, height=30)
        self.next_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(nav_frame, text=TRANSLATIONS[language]["close"], 
                     command=self.window.destroy, width=100, height=30,
                     fg_color="#ed4245", hover_color="#c03537").pack(side="left", padx=5)
        
        self.load_image()
    
    def load_image(self):
        try:
            img_path = os.path.join(BASE_DIR, f"guide_image_{self.current_index + 1}.png")
            img = Image.open(img_path)
            img.thumbnail((770, 500), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
        except:
            self.image_label.configure(text=f"guide_image_{self.current_index + 1}.png not found", 
                                      image=None)
        
        self.page_label.configure(text=f"{self.current_index + 1} / {self.images_count}")
        self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_index < self.images_count - 1 else "disabled")
    
    def next_image(self):
        if self.current_index < self.images_count - 1:
            self.current_index += 1
            self.load_image()
    
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

class DiscordRPCManager:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Discord Playing Status Changer")
        self.app.geometry("650x500")
        self.app.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Устанавливаем иконку окна
        try:
            icon_path = os.path.join(BASE_DIR, "icon.ico")
            if os.path.exists(icon_path):
                self.app.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon load error: {e}")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.rpc = None
        self.current_profile = None
        self.profiles = self.load_profiles()
        self.language = self.profiles.get("language", "ru")
        self.tray_icon = None
        
        self.setup_ui()
        self.setup_tray()
        
        # Восстанавливаем последний активный профиль
        self.restore_last_active_profile()
        
    def t(self, key):
        return TRANSLATIONS[self.language].get(key, key)
        
    def load_profiles(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"profiles": [], "language": "ru", "autostart": False, "last_active_profile": None}
    
    def save_profiles(self):
        data = {
            "profiles": self.profiles["profiles"], 
            "language": self.language, 
            "autostart": self.profiles.get("autostart", False),
            "last_active_profile": self.profiles.get("last_active_profile")
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_exe_path(self):
        """Возвращает путь к exe файлу для автозагрузки"""
        if getattr(sys, 'frozen', False):
            return sys.executable
        else:
            return os.path.abspath(sys.argv[0])
    
    def toggle_autostart(self):
        enabled = self.autostart_var.get()
        self.profiles["autostart"] = enabled
        self.save_profiles()
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "DiscordPlayingStatusChanger"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enabled:
                exe_path = self.get_exe_path()
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}"')
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Autostart error: {e}")
    
    def restore_last_active_profile(self):
        """Восстанавливает последний активный профиль при запуске"""
        last_active = self.profiles.get("last_active_profile")
        if last_active:
            for profile in self.profiles.get("profiles", []):
                if profile.get("name") == last_active:
                    self.load_profile(profile)
                    # Небольшая задержка перед активацией
                    self.app.after(500, self.activate_profile)
                    break
    
    def save_active_profile_state(self, profile_name):
        """Сохраняет имя активного профиля"""
        self.profiles["last_active_profile"] = profile_name
        self.save_profiles()
    
    def add_context_menu(self, widget):
        menu = tk.Menu(widget, tearoff=0, bg="#2b2d31", fg="white", 
                       activebackground="#5865f2", activeforeground="white")
        
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        
        def copy():
            try:
                text = widget.selection_get()
                self.app.clipboard_clear()
                self.app.clipboard_append(text)
            except:
                pass
        
        def paste():
            try:
                text = self.app.clipboard_get()
                widget.insert(ctk.INSERT, text)
            except:
                pass
        
        def cut():
            try:
                text = widget.selection_get()
                self.app.clipboard_clear()
                self.app.clipboard_append(text)
                widget.delete(ctk.SEL_FIRST, ctk.SEL_LAST)
            except:
                pass
        
        menu.add_command(label="Копировать" if self.language == "ru" else "Copy", command=copy)
        menu.add_command(label="Вставить" if self.language == "ru" else "Paste", command=paste)
        menu.add_command(label="Вырезать" if self.language == "ru" else "Cut", command=cut)
        
        widget.bind("<Button-3>", show_menu)
    
    def change_language_ui(self):
        """Переключает язык интерфейса"""
        self.language = "en" if self.language == "ru" else "ru"
        self.profiles["language"] = self.language
        self.save_profiles()
        # Перезагружаем UI
        for widget in self.app.winfo_children():
            widget.destroy()
        self.setup_ui()
    
    def show_app_guide(self):
        webbrowser.open('https://discord.com/developers/applications')
        GuideWindow(self.app, 3, self.t("guide") + " - App ID", self.language)
    
    def show_image_guide(self):
        ImageGuideWindow(self.app, self.t("guide") + " - Images", self.language)
    
    def setup_ui(self):
        # Gradient header
        header = ctk.CTkFrame(self.app, height=45, fg_color=("#5865f2", "#4752c4"), corner_radius=0)
        header.pack(fill="x")
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="both", expand=True, padx=15, pady=8)
        
        left_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        left_frame.pack(side="left")
        
        ctk.CTkLabel(left_frame, text="✨ " + self.t("title"), 
                    font=("Segoe UI", 16, "bold"), text_color="white").pack(side="left")
        
        ctk.CTkButton(left_frame, text="📖 " + self.t("guide"), width=70, height=26,
                     font=("Segoe UI", 11, "bold"), fg_color="#3ba55d", hover_color="#2d7d46",
                     command=self.show_app_guide).pack(side="left", padx=10)
        
        self.autostart_var = ctk.BooleanVar(value=self.profiles.get("autostart", False))
        ctk.CTkCheckBox(left_frame, text=self.t("autostart"), variable=self.autostart_var,
                       font=("Segoe UI", 11), text_color="white",
                       command=self.toggle_autostart).pack(side="left")
        
        right_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        right_frame.pack(side="right")
        
        # Переключатель языка
        lang_text = "РУС ENG" if self.language == "ru" else "ENG РУС"
        ctk.CTkButton(right_frame, text=lang_text, width=70, height=26,
                     font=("Segoe UI", 10, "bold"), fg_color="#4e5058", hover_color="#6d6f78",
                     command=self.change_language_ui).pack(side="left", padx=8)
        
        self.status_label = ctk.CTkLabel(right_frame, text=self.t("inactive"), 
                                        text_color="#ed4245", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(side="left")
        
        # Main container
        main = ctk.CTkFrame(self.app, fg_color="#36393f", corner_radius=0)
        main.pack(fill="both", expand=True)
        
        # Left sidebar
        sidebar = ctk.CTkFrame(main, width=180, fg_color="#2f3136", corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        sidebar_content = ctk.CTkFrame(sidebar, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=12, pady=12)
        
        ctk.CTkLabel(sidebar_content, text="📁 " + self.t("profiles"), 
                    font=("Segoe UI", 14, "bold")).pack(pady=(0, 12))
        
        # Profile list
        self.profile_frame = ctk.CTkScrollableFrame(sidebar_content, fg_color="#202225", corner_radius=6)
        self.profile_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(btn_frame, text=self.t("new"), height=28, corner_radius=6,
                     font=("Segoe UI", 11, "bold"), fg_color="#3ba55d", hover_color="#2d7d46",
                     command=self.new_profile).pack(fill="x", pady=(0, 6))
        
        ctk.CTkButton(btn_frame, text=self.t("save"), height=28, corner_radius=6,
                     font=("Segoe UI", 11, "bold"), fg_color="#5865f2", hover_color="#4752c4",
                     command=self.save_current).pack(fill="x")
        
        # Right panel
        editor = ctk.CTkFrame(main, fg_color="#36393f", corner_radius=0)
        editor.pack(side="right", fill="both", expand=True)
        
        scroll = ctk.CTkScrollableFrame(editor, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Profile name card
        name_card = self.create_card(scroll, "🏷️ " + self.t("profile_name"))
        name_card.pack(fill="x", pady=(0, 10))
        self.name_entry = ctk.CTkEntry(name_card, height=30, corner_radius=6, font=("Segoe UI", 12),
                                       border_color="#5865f2", border_width=2)
        self.name_entry.pack(fill="x", padx=12, pady=(0, 12))
        self.add_context_menu(self.name_entry)
        
        # App ID
        ctk.CTkLabel(name_card, text="🔑 " + self.t("app_id"), 
                    font=("Segoe UI", 11), anchor="w").pack(fill="x", padx=12, pady=(0, 4))
        self.client_id_entry = ctk.CTkEntry(name_card, height=30, corner_radius=6, font=("Segoe UI", 12),
                                           border_color="#5865f2", border_width=2)
        self.client_id_entry.pack(fill="x", padx=12, pady=(0, 12))
        self.add_context_menu(self.client_id_entry)
        
        # Activity card
        activity_card = self.create_card(scroll, "🎮 Activity")
        activity_card.pack(fill="x", pady=(0, 10))
        
        content = ctk.CTkFrame(activity_card, fg_color="transparent")
        content.pack(fill="x", padx=12, pady=(0, 12))
        
        ctk.CTkLabel(content, text=self.t("details"), font=("Segoe UI", 11), anchor="w").pack(fill="x", pady=(0, 4))
        self.details_entry = ctk.CTkEntry(content, height=30, corner_radius=6, 
                                         placeholder_text="Playing a game", font=("Segoe UI", 12))
        self.details_entry.pack(fill="x", pady=(0, 8))
        self.add_context_menu(self.details_entry)
        
        ctk.CTkLabel(content, text=self.t("state"), font=("Segoe UI", 11), anchor="w").pack(fill="x", pady=(0, 4))
        self.state_entry = ctk.CTkEntry(content, height=30, corner_radius=6, 
                                       placeholder_text="In menu", font=("Segoe UI", 12))
        self.state_entry.pack(fill="x")
        self.add_context_menu(self.state_entry)
        
        # Images card
        img_card = ctk.CTkFrame(scroll, fg_color="#2f3136", corner_radius=8)
        img_card.pack(fill="x", pady=(0, 10))
        
        # Header with guide button
        header_frame = ctk.CTkFrame(img_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(10, 6))
        
        ctk.CTkLabel(header_frame, text="🖼️ Images", font=("Segoe UI", 13, "bold"), 
                    anchor="w").pack(side="left")
        
        ctk.CTkButton(header_frame, text="📖 " + self.t("guide"), width=70, height=24,
                     font=("Segoe UI", 10, "bold"), fg_color="#3ba55d", hover_color="#2d7d46",
                     command=self.show_image_guide).pack(side="left", padx=10)
        
        img_container = ctk.CTkFrame(img_card, fg_color="transparent")
        img_container.pack(fill="x", padx=12, pady=(0, 12))
        
        # Large image
        large_outer = ctk.CTkFrame(img_container, fg_color="transparent")
        large_outer.pack(side="left", fill="both", expand=True, padx=(0, 6))
        
        large_frame = self.create_mini_card(large_outer, self.t("large_image"))
        large_frame.pack(fill="x")
        
        large_content = ctk.CTkFrame(large_frame, fg_color="transparent")
        large_content.pack(fill="x", padx=10, pady=(0, 8))
        
        self.large_key_entry = ctk.CTkEntry(large_content, height=28, placeholder_text="image_key")
        self.large_key_entry.pack(fill="x", pady=(0, 6))
        self.add_context_menu(self.large_key_entry)
        
        self.large_text_entry = ctk.CTkEntry(large_content, height=28, placeholder_text="Hover text")
        self.large_text_entry.pack(fill="x")
        self.add_context_menu(self.large_text_entry)
        
        # Small image
        small_outer = ctk.CTkFrame(img_container, fg_color="transparent")
        small_outer.pack(side="left", fill="both", expand=True, padx=(6, 0))
        
        small_frame = self.create_mini_card(small_outer, self.t("small_image"))
        small_frame.pack(fill="x")
        
        small_content = ctk.CTkFrame(small_frame, fg_color="transparent")
        small_content.pack(fill="x", padx=10, pady=(0, 8))
        
        self.small_key_entry = ctk.CTkEntry(small_content, height=28, placeholder_text="image_key")
        self.small_key_entry.pack(fill="x", pady=(0, 6))
        self.add_context_menu(self.small_key_entry)
        
        self.small_text_entry = ctk.CTkEntry(small_content, height=28, placeholder_text="Hover text")
        self.small_text_entry.pack(fill="x")
        self.add_context_menu(self.small_text_entry)
        
        # Buttons card
        btn_card = self.create_card(scroll, "🔗 Buttons")
        btn_card.pack(fill="x", pady=(0, 12))
        
        btn_container = ctk.CTkFrame(btn_card, fg_color="transparent")
        btn_container.pack(fill="x", padx=12, pady=(0, 12))
        
        # Button 1
        btn1_outer = ctk.CTkFrame(btn_container, fg_color="transparent")
        btn1_outer.pack(side="left", fill="both", expand=True, padx=(0, 6))
        
        btn1_frame = self.create_mini_card(btn1_outer, self.t("button") + " 1")
        btn1_frame.pack(fill="x")
        
        btn1_content = ctk.CTkFrame(btn1_frame, fg_color="transparent")
        btn1_content.pack(fill="x", padx=10, pady=(0, 8))
        
        self.btn1_text_entry = ctk.CTkEntry(btn1_content, height=28, placeholder_text="Button text")
        self.btn1_text_entry.pack(fill="x", pady=(0, 6))
        self.add_context_menu(self.btn1_text_entry)
        
        self.btn1_url_entry = ctk.CTkEntry(btn1_content, height=28, placeholder_text="https://...")
        self.btn1_url_entry.pack(fill="x")
        self.add_context_menu(self.btn1_url_entry)
        
        # Button 2
        btn2_outer = ctk.CTkFrame(btn_container, fg_color="transparent")
        btn2_outer.pack(side="left", fill="both", expand=True, padx=(6, 0))
        
        btn2_frame = self.create_mini_card(btn2_outer, self.t("button") + " 2")
        btn2_frame.pack(fill="x")
        
        btn2_content = ctk.CTkFrame(btn2_frame, fg_color="transparent")
        btn2_content.pack(fill="x", padx=10, pady=(0, 8))
        
        self.btn2_text_entry = ctk.CTkEntry(btn2_content, height=28, placeholder_text="Button text")
        self.btn2_text_entry.pack(fill="x", pady=(0, 6))
        self.add_context_menu(self.btn2_text_entry)
        
        self.btn2_url_entry = ctk.CTkEntry(btn2_content, height=28, placeholder_text="https://...")
        self.btn2_url_entry.pack(fill="x")
        self.add_context_menu(self.btn2_url_entry)
        
        # Control buttons
        control_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        control_frame.pack(fill="x")
        
        self.activate_btn = ctk.CTkButton(control_frame, text="▶ " + self.t("activate"), height=32,
                                         font=("Segoe UI", 12, "bold"), fg_color="#3ba55d", 
                                         hover_color="#2d7d46", corner_radius=6,
                                         command=self.activate_profile)
        self.activate_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        self.stop_btn = ctk.CTkButton(control_frame, text="⏸ " + self.t("stop"), height=32,
                                     font=("Segoe UI", 12, "bold"), fg_color="#ed4245", 
                                     hover_color="#c03537", corner_radius=6,
                                     command=self.stop_rpc)
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(control_frame, text="🗑 " + self.t("delete"), height=32,
                     font=("Segoe UI", 12, "bold"), fg_color="#4e5058", 
                     hover_color="#6d6f78", corner_radius=6,
                     command=self.delete_profile).pack(side="left", fill="x", expand=True)
        
        self.refresh_profile_list()
    
    def create_card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color="#2f3136", corner_radius=8)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 13, "bold"), anchor="w").pack(
            fill="x", padx=12, pady=(10, 6))
        return card
    
    def create_mini_card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color="#202225", corner_radius=6)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 11, "bold")).pack(pady=(8, 6))
        return card
    
    def refresh_profile_list(self):
        for widget in self.profile_frame.winfo_children():
            widget.destroy()
        
        for profile in self.profiles.get("profiles", []):
            btn = ctk.CTkButton(self.profile_frame, text=profile.get("name", "Unnamed"), 
                               height=32, anchor="w", font=("Segoe UI", 11), corner_radius=5,
                               fg_color="#36393f", hover_color="#40444b",
                               command=lambda p=profile: self.load_profile(p))
            btn.pack(fill="x", pady=2)
    
    def new_profile(self):
        self.current_profile = None
        self.name_entry.delete(0, "end")
        self.client_id_entry.delete(0, "end")
        self.details_entry.delete(0, "end")
        self.state_entry.delete(0, "end")
        self.large_key_entry.delete(0, "end")
        self.large_text_entry.delete(0, "end")
        self.small_key_entry.delete(0, "end")
        self.small_text_entry.delete(0, "end")
        self.btn1_text_entry.delete(0, "end")
        self.btn1_url_entry.delete(0, "end")
        self.btn2_text_entry.delete(0, "end")
        self.btn2_url_entry.delete(0, "end")
    
    def load_profile(self, profile):
        self.current_profile = profile
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, profile.get("name", ""))
        self.client_id_entry.delete(0, "end")
        self.client_id_entry.insert(0, profile.get("client_id", ""))
        self.details_entry.delete(0, "end")
        self.details_entry.insert(0, profile.get("details", ""))
        self.state_entry.delete(0, "end")
        self.state_entry.insert(0, profile.get("state", ""))
        self.large_key_entry.delete(0, "end")
        self.large_key_entry.insert(0, profile.get("large_image", ""))
        self.large_text_entry.delete(0, "end")
        self.large_text_entry.insert(0, profile.get("large_text", ""))
        self.small_key_entry.delete(0, "end")
        self.small_key_entry.insert(0, profile.get("small_image", ""))
        self.small_text_entry.delete(0, "end")
        self.small_text_entry.insert(0, profile.get("small_text", ""))
        self.btn1_text_entry.delete(0, "end")
        self.btn1_text_entry.insert(0, profile.get("button1_text", ""))
        self.btn1_url_entry.delete(0, "end")
        self.btn1_url_entry.insert(0, profile.get("button1_url", ""))
        self.btn2_text_entry.delete(0, "end")
        self.btn2_text_entry.insert(0, profile.get("button2_text", ""))
        self.btn2_url_entry.delete(0, "end")
        self.btn2_url_entry.insert(0, profile.get("button2_url", ""))
    
    def save_current(self):
        profile_data = {
            "name": self.name_entry.get(),
            "client_id": self.client_id_entry.get(),
            "details": self.details_entry.get(),
            "state": self.state_entry.get(),
            "large_image": self.large_key_entry.get(),
            "large_text": self.large_text_entry.get(),
            "small_image": self.small_key_entry.get(),
            "small_text": self.small_text_entry.get(),
            "button1_text": self.btn1_text_entry.get(),
            "button1_url": self.btn1_url_entry.get(),
            "button2_text": self.btn2_text_entry.get(),
            "button2_url": self.btn2_url_entry.get()
        }
        
        if self.current_profile:
            idx = self.profiles["profiles"].index(self.current_profile)
            self.profiles["profiles"][idx] = profile_data
            self.current_profile = profile_data
        else:
            self.profiles["profiles"].append(profile_data)
            self.current_profile = profile_data
        
        self.save_profiles()
        self.refresh_profile_list()
    
    def delete_profile(self):
        if self.current_profile and self.current_profile in self.profiles["profiles"]:
            # Если удаляемый профиль активен, очищаем last_active_profile
            if self.profiles.get("last_active_profile") == self.current_profile.get("name"):
                self.profiles["last_active_profile"] = None
            
            self.profiles["profiles"].remove(self.current_profile)
            self.save_profiles()
            self.refresh_profile_list()
            self.new_profile()
    
    def activate_profile(self):
        client_id = self.client_id_entry.get()
        if not client_id:
            return
        
        try:
            if self.rpc:
                self.rpc.close()
            
            self.rpc = Presence(client_id)
            self.rpc.connect()
            
            activity = {
                "details": self.details_entry.get() or None,
                "state": self.state_entry.get() or None,
                "start": int(time.time())
            }
            
            if self.large_key_entry.get():
                activity["large_image"] = self.large_key_entry.get()
                activity["large_text"] = self.large_text_entry.get() or None
            
            if self.small_key_entry.get():
                activity["small_image"] = self.small_key_entry.get()
                activity["small_text"] = self.small_text_entry.get() or None
            
            buttons = []
            if self.btn1_text_entry.get() and self.btn1_url_entry.get():
                buttons.append({"label": self.btn1_text_entry.get(), "url": self.btn1_url_entry.get()})
            if self.btn2_text_entry.get() and self.btn2_url_entry.get():
                buttons.append({"label": self.btn2_text_entry.get(), "url": self.btn2_url_entry.get()})
            
            if buttons:
                activity["buttons"] = buttons
            
            self.rpc.update(**activity)
            self.status_label.configure(text=self.t("active"), text_color="#3ba55d")
            
            # Сохраняем имя активного профиля
            profile_name = self.name_entry.get()
            if profile_name:
                self.save_active_profile_state(profile_name)
            
        except Exception as e:
            print(f"Error: {e}")
    
    def stop_rpc(self):
        if self.rpc:
            self.rpc.close()
            self.rpc = None
        self.status_label.configure(text=self.t("inactive"), text_color="#ed4245")
        # Очищаем last_active_profile при остановке
        self.profiles["last_active_profile"] = None
        self.save_profiles()
    
    def setup_tray(self):
        def quit_app(icon, item):
            icon.stop()
            if self.rpc:
                self.rpc.close()
            self.app.quit()
        
        def show_window(icon, item):
            self.app.deiconify()
        
        def change_language(icon, item):
            self.language = "en" if self.language == "ru" else "ru"
            self.profiles["language"] = self.language
            self.save_profiles()
            for widget in self.app.winfo_children():
                widget.destroy()
            self.setup_ui()
        
        def toggle_autostart_tray(icon, item):
            current = self.profiles.get("autostart", False)
            self.profiles["autostart"] = not current
            self.save_profiles()
            self.autostart_var.set(not current)
            self.toggle_autostart()
        
        try:
            icon_path = os.path.join(BASE_DIR, "icon.ico")
            icon_image = Image.open(icon_path)
            icon_image = icon_image.resize((64, 64), Image.Resampling.LANCZOS)
        except:
            icon_image = Image.new('RGB', (64, 64), color='#5865f2')
        
        # Текст кнопки показывает ЦЕЛЕВОЙ язык (на какой переключимся)
        lang_label = "English" if self.language == "ru" else "Русский"
        
        menu = pystray.Menu(
            item(self.t("show"), show_window),
            item(self.t("autostart"), toggle_autostart_tray, 
                 checked=lambda item: self.profiles.get("autostart", False)),
            item(lang_label, change_language),
            item(self.t("quit"), quit_app)
        )
        
        self.tray_icon = pystray.Icon("discord_rpc", icon_image, "Discord Status", menu)
        Thread(target=self.tray_icon.run, daemon=True).start()
    
    def hide_window(self):
        self.app.withdraw()
    
    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = DiscordRPCManager()
    app.run()