import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import queue

try:
    from playsound import playsound
except ImportError:
    messagebox.showerror("依赖缺失", "错误：'playsound' 库未安装。\n请在终端运行 'pip install playsound==1.2.2'")
    exit()

# --- 全局参数配置 ---
FOCUS_MINUTES = 90
BREAK_MINUTES = 20
MICRO_BREAK_SECONDS = 10
RANDOM_INTERVAL_MIN = 3
RANDOM_INTERVAL_MAX = 5
SOUND_FILE = 'alert.mp3'

class FocusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("专注时钟")
        self.root.geometry("400x250") # 窗口大小

        # 线程控制
        self.timer_thread = None
        self.is_running = threading.Event()
        self.is_paused = threading.Event()
        self.update_queue = queue.Queue()

        # GUI 元素
        self.status_var = tk.StringVar(value="准备就绪")
        self.timer_var = tk.StringVar(value=f"{FOCUS_MINUTES:02d}:00")
        
        # 样式
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("Status.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Timer.TLabel", font=("Helvetica", 48, "bold"))
        style.configure("TButton", font=("Helvetica", 12))

        # 布局
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, textvariable=self.status_var, style="Status.TLabel").pack(pady=5)
        ttk.Label(main_frame, textvariable=self.timer_var, style="Timer.TLabel").pack(pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)

        self.start_button = ttk.Button(button_frame, text="开始专注", command=self.start_timer)
        self.start_button.pack(side="left", padx=5)

        self.pause_button = ttk.Button(button_frame, text="暂停", command=self.toggle_pause, state="disabled")
        self.pause_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_timer, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # 启动队列处理器和窗口关闭协议
        self.process_queue()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_timer(self):
        self.is_running.set()
        self.is_paused.clear()
        
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal", text="暂停")
        self.stop_button.config(state="normal")
        
        self.timer_thread = threading.Thread(target=self.main_loop, daemon=True)
        self.timer_thread.start()

    def toggle_pause(self):
        if self.is_paused.is_set(): # 当前是暂停状态 -> 恢复
            self.is_paused.clear()
            self.pause_button.config(text="暂停")
            self.update_queue.put(("status", self.last_status))
        else: # 当前是运行状态 -> 暂停
            self.is_paused.set()
            self.pause_button.config(text="继续")
            self.last_status = self.status_var.get()
            self.update_queue.put(("status", "已暂停"))

    def stop_timer(self):
        if self.timer_thread and self.timer_thread.is_alive():
            self.is_running.clear() # 发送停止信号
            self.is_paused.clear()  # 如果在暂停状态，需要唤醒它才能结束
            self.timer_thread.join(timeout=1) # 等待线程结束

        self.reset_ui()

    def reset_ui(self):
        self.status_var.set("准备就绪")
        self.timer_var.set(f"{FOCUS_MINUTES:02d}:00")
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="暂停")
        self.stop_button.config(state="disabled")

    def main_loop(self):
        cycle_count = 1
        while self.is_running.is_set():
            self.update_queue.put(("status", f"第 {cycle_count} 轮：专注"))
            self.run_focus_session()
            if not self.is_running.is_set(): break

            self.update_queue.put(("status", "大休息"))
            self.run_countdown(BREAK_MINUTES, "🧘‍♀️ 大休息时间到！")
            if not self.is_running.is_set(): break
            cycle_count += 1
        
        # 线程结束时，重置UI
        self.update_queue.put(("reset", None))

    def run_focus_session(self):
        session_end_time = time.time() + FOCUS_MINUTES * 60
        while time.time() < session_end_time and self.is_running.is_set():
            self.check_pause()
            
            interval = random.randint(RANDOM_INTERVAL_MIN * 60, RANDOM_INTERVAL_MAX * 60)
            micro_break_time = time.time() + interval
            
            while time.time() < micro_break_time and time.time() < session_end_time and self.is_running.is_set():
                self.check_pause()
                remaining = session_end_time - time.time()
                self.update_queue.put(("timer", f"{int(remaining//60):02d}:{int(remaining%60):02d}"))
                time.sleep(1)

            if time.time() < session_end_time and self.is_running.is_set():
                self.play_sound()
                self.update_queue.put(("status", "微休息 (10秒)"))
                self.run_countdown(MICRO_BREAK_SECONDS / 60, "", is_micro=True)
                self.update_queue.put(("status", "专注中..."))
    
    def run_countdown(self, duration_minutes, end_message, is_micro=False):
        total_seconds = int(duration_minutes * 60)
        end_time = time.time() + total_seconds
        
        while time.time() < end_time and self.is_running.is_set():
            self.check_pause()
            remaining = end_time - time.time()
            if is_micro:
                self.update_queue.put(("timer", f"{int(remaining):02d}秒"))
            else:
                self.update_queue.put(("timer", f"{int(remaining//60):02d}:{int(remaining%60):02d}"))
            time.sleep(1)
        
        if self.is_running.is_set() and end_message:
            self.play_sound()
            self.play_sound()

    def check_pause(self):
        while self.is_paused.is_set() and self.is_running.is_set():
            time.sleep(0.5)

    def play_sound(self):
        try:
            threading.Thread(target=playsound, args=(SOUND_FILE,), daemon=True).start()
        except Exception as e:
            self.update_queue.put(("error", f"无法播放声音: {e}"))
            
    def process_queue(self):
        try:
            while True:
                message_type, value = self.update_queue.get_nowait()
                if message_type == "status":
                    self.status_var.set(value)
                elif message_type == "timer":
                    self.timer_var.set(value)
                elif message_type == "reset":
                    self.reset_ui()
                elif message_type == "error":
                    messagebox.showwarning("音频错误", value)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

    def on_closing(self):
        if messagebox.askokcancel("退出", "你确定要退出吗？"):
            self.is_running.clear()
            self.is_paused.clear()
            if self.timer_thread and self.timer_thread.is_alive():
                self.timer_thread.join(timeout=1)
            self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = FocusApp(root)
    root.mainloop()