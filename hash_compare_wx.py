import wx
import socket
import threading
import os
import sys
import time
import tempfile
import subprocess
import win32api, win32con, win32gui, win32event
from hash_compare import compare_hashes

MUTEX_NAME = "Global\\HashCompareMutex"
SERVER_PORT = 7573
BUFFER_SIZE = 1024
ADDRESS = ('localhost', SERVER_PORT)

class HashCompareApp(wx.Frame):
    def __init__(self, initial_file1="", initial_file2="", server_socket=None):
        super().__init__(None, title="哈希对比", size=(337, 220), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX) | wx.STAY_ON_TOP)

        self.temp_file = None
        self.swap_flag = False
        self.server_socket = server_socket
        
        pnl = wx.Panel(self, size=(400, 150))

        # 原文件输入框和浏览按钮
        wx.StaticText(pnl, label="原文件", pos=(20, 10))
        self.file1_input = wx.TextCtrl(pnl, pos=(20, 30), size=(250, 25))
        browse1_btn = wx.Button(pnl, label="...", pos=(275, 30), size=(25, 25))
        browse1_btn.Bind(wx.EVT_BUTTON, self.on_browse1)

        # 新文件输入框和浏览按钮
        wx.StaticText(pnl, label="新文件", pos=(20, 70))
        self.file2_input = wx.TextCtrl(pnl, pos=(20, 90), size=(250, 25))
        browse2_btn = wx.Button(pnl, label="...", pos=(275, 90), size=(25, 25))
        browse2_btn.Bind(wx.EVT_BUTTON, self.on_browse2)

        # 交换按钮
        swap_btn = wx.Button(pnl, label="交换", pos=(20, 140), size=(70, 25))
        swap_btn.Bind(wx.EVT_BUTTON, self.on_swap)

        # 取消和确定按钮
        cancel_btn = wx.Button(pnl, label="取消", pos=(160, 140), size=(70, 25))
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        ok_btn = wx.Button(pnl, label="确定", pos=(230, 140), size=(70, 25))
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)

        # 设置整个窗口的拖拽功能
        self.SetDropTarget(FileDropTarget(self.file1_input, self.file2_input, self))

        # 初始化文件输入框
        if initial_file1:
            self.file1_input.SetValue(initial_file1)
        if initial_file2:
            self.file2_input.SetValue(initial_file2)

        # 启动线程来监听来自其他实例的消息
        if self.server_socket:
            self.server_thread = threading.Thread(target=self.listen_for_connections, daemon=True)
            self.server_thread.start()

        self.Center()
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_browse1(self, event):
        with wx.FileDialog(self, "选择原文件") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.file1_input.SetValue(dlg.GetPath())

    def on_browse2(self, event):
        with wx.FileDialog(self, "选择新文件") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.file2_input.SetValue(dlg.GetPath())

    def on_swap(self, event):
        file1 = self.file1_input.GetValue()
        file2 = self.file2_input.GetValue()
        self.file1_input.SetValue(file2)
        self.file2_input.SetValue(file1)

    def on_cancel(self, event):
        self.Close()

    def on_ok(self, event):
        file1 = self.file1_input.GetValue()
        file2 = self.file2_input.GetValue()

        if not file1 or not file2:
            wx.MessageBox("请先选择原文件和新文件路径", "错误", wx.ICON_ERROR)
            return

        start_time = time.time()
        print("处理中...")

        # 创建一个临时文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        output_file = self.temp_file.name

        compare_hashes(file1, file2, output_file)

        end_time = time.time()
        print(f"对比完成，共耗时 {end_time - start_time:.2f} 秒")

        # 使用默认文本编辑器打开临时文件
        subprocess.Popen(['notepad', output_file])

    def on_close(self, event):
        # 删除临时文件
        if self.temp_file:
            self.temp_file.close()
            os.remove(self.temp_file.name)
        self.Destroy()

    def process_dragged_file(self, filename):
        """处理从其他实例拖入的文件"""
        if not self.file1_input.GetValue():
            self.file1_input.SetValue(filename)
            self.file1_input.SetFocus()
        elif not self.file2_input.GetValue():
            self.file2_input.SetValue(filename)
            self.file2_input.SetFocus()
        else:
            if self.swap_flag:
                self.file1_input.SetValue(filename)
                self.file1_input.SetFocus()
            else:
                self.file2_input.SetValue(filename)
                self.file2_input.SetFocus()
            self.swap_flag = not self.swap_flag

    def listen_for_connections(self):
        """监听来自其他实例的连接"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(ADDRESS)
            s.listen()
            while True:
                conn, _ = s.accept()
                with conn:
                    data = conn.recv(BUFFER_SIZE)
                    if data:
                        file_path = data.decode('utf-8')
                        wx.CallAfter(self.process_dragged_file, file_path)

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, file1_input, file2_input, parent):
        super().__init__()
        self.file1_input: wx.TextCtrl = file1_input
        self.file2_input: wx.TextCtrl = file2_input
        self.parent = parent
        self.drop_count = 0

    def OnDropFiles(self, x, y, filenames):
        if not self.file1_input.GetValue():
            self.file1_input.SetValue(filenames[0])
            self.file1_input.SetFocus()
        elif not self.file2_input.GetValue():
            self.file2_input.SetValue(filenames[0])
            self.file2_input.SetFocus()
        else:
            if self.drop_count % 2 == 0:
                self.file1_input.SetValue(filenames[0])
                self.file1_input.SetFocus()
            else:
                self.file2_input.SetValue(filenames[0])
                self.file2_input.SetFocus()
            self.drop_count += 1
        return True  

def main():
    # 创建全局命名互斥锁
    mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
    initial_file1 = sys.argv[1] if len(sys.argv) > 1 else ""
    initial_file2 = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if win32api.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(ADDRESS)
                for file_path in sys.argv[1:]:
                    s.sendall(file_path.encode('utf-8'))

            hwnd = win32gui.FindWindow(None, "哈希对比")
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
        finally:
            sys.exit(0)

    # 当前实例是服务器端
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setblocking(False)  # 设置非阻塞模式
    except OSError:
        server_socket = None

    app = wx.App(False)
    frame = HashCompareApp(initial_file1, initial_file2, server_socket)
    frame.Show()
    app.MainLoop()

    win32api.CloseHandle(mutex)

if __name__ == "__main__":
    main()
