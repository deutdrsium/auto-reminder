import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, settings_manager, app_instance):
        super().__init__(parent)
        self.title("设置")
        self.geometry("450x300")
        self.resizable(False, False)

        self.settings_manager = settings_manager
        self.app = app_instance # 主应用的实例，用于回调

        # 使窗口成为模态窗口
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill="both")

        # 使用 grid 布局
        frame.columnconfigure(1, weight=1)
        
        # 定义设置项
        settings_fields = {
            "focus_minutes": "专注时长 (分钟):",
            "break_minutes": "休息时长 (分钟):",
            "micro_break_seconds": "微休息时长 (秒):",
            "random_interval_min": "随机间隔最小 (分钟):",
            "random_interval_max": "随机间隔最大 (分钟):",
        }
        
        self.entries = {}
        row_num = 0
        for key, text in settings_fields.items():
            label = ttk.Label(frame, text=text)
            label.grid(row=row_num, column=0, sticky="w", pady=5, padx=5)
            
            entry = ttk.Entry(frame, width=10)
            entry.grid(row=row_num, column=1, sticky="w", padx=5)
            self.entries[key] = entry
            row_num += 1

        # 声音文件选择
        ttk.Label(frame, text="提示音文件:").grid(row=row_num, column=0, sticky="w", pady=5, padx=5)
        self.sound_file_var = tk.StringVar()
        sound_frame = ttk.Frame(frame)
        sound_frame.grid(row=row_num, column=1, sticky="ew")
        
        sound_entry = ttk.Entry(sound_frame, textvariable=self.sound_file_var, state="readonly")
        sound_entry.pack(side="left", expand=True, fill="x")
        browse_button = ttk.Button(sound_frame, text="浏览...", command=self.browse_sound_file)
        browse_button.pack(side="left", padx=5)
        
        # 按钮
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="保存", command=self.save_and_close).pack(side="right", padx=5)
        ttk.Button(button_frame, text="取消", command=self.destroy).pack(side="right")

    def load_settings(self):
        """加载当前设置到输入框"""
        for key, entry in self.entries.items():
            entry.insert(0, str(self.settings_manager.get(key)))
        self.sound_file_var.set(self.settings_manager.get("sound_file"))

    def browse_sound_file(self):
        filepath = filedialog.askopenfilename(
            title="选择提示音文件",
            filetypes=[("音频文件", "*.mp3 *.wav"), ("所有文件", "*.*")]
        )
        if filepath:
            self.sound_file_var.set(filepath)

    def save_and_close(self):
        """验证、保存设置并关闭窗口"""
        new_settings = {}
        try:
            for key, entry in self.entries.items():
                new_settings[key] = int(entry.get())
            
            new_settings["sound_file"] = self.sound_file_var.get()
            
            # 简单验证
            if new_settings["random_interval_min"] >= new_settings["random_interval_max"]:
                messagebox.showerror("输入错误", "最小间隔必须小于最大间隔。")
                return

        except ValueError:
            messagebox.showerror("输入错误", "所有时长和间隔必须是整数。")
            return
        
        self.settings_manager.save_settings(new_settings)
        self.app.on_settings_changed() # 通知主应用设置已更改
        self.destroy()