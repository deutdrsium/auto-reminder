# FocusTimerGUI 专注时钟

一个基于超节律（90分钟专注/20分钟休息）和微休息法（随机3-5分钟闭眼10秒）的图形界面专注时钟。

## 特性

- 90分钟专注 / 20分钟大休息循环。
- 专注期间，每3-5分钟随机提示音，提醒进行10秒微休息。
- 简单的图形用户界面，包含开始、暂停、停止功能。
- 使用 Python 和 Tkinter 构建。

## 如何使用

1.  从 Releases 页面下载最新的可执行文件。
2.  双击运行即可。

## 如何从源码构建

1.  克隆本仓库：`git clone https://github.com/deutdrsium/auto-reminder.git`
2.  安装依赖：`pip install playsound==1.2.2 pyinstaller`
3.  运行主程序：`python main.py`
4.  打包成可执行文件：`pyinstaller --name "FocusTimer" --onefile --windowed --add-data "alert.mp3;." main.py`