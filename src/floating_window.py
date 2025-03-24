import tkinter as tk
import time
import threading
import baostock as bs

symbol = '002851'

class FloatingWindow:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # 去掉窗口边框
        self.root.attributes("-topmost", True)  # 窗口置顶
        self.root.geometry("200x100+100+100")  # 设置窗口大小和位置

        self.frame = tk.Frame(root, bg="lightblue", bd=2)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.label = tk.Label(self.frame, text="", font=("Helvetica", 16), bg="lightblue")
        self.label.pack(pady=20)

        self.close_button = tk.Button(self.frame, text="关闭", command=self.root.destroy, fg="white")
        self.close_button.pack(side=tk.BOTTOM, pady=10)

        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.x
        y = self.root.winfo_pointery() - self.y
        self.root.geometry(f"+{x}+{y}")

    def update_text(self, text):
        self.label.config(text=text)

def update_label_text(floating_window):
    while True:
        try:
            # 获取股票实时数据
            rs = bs.query_rt_data(code=symbol)
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if data_list:
                row = data_list[-1]
                price = float(row[5])  # 当前价格
                pre_close = float(row[4])  # 昨收价
                change_pct = (price - pre_close) / pre_close * 100
                
                text = f"股价: {price}\n涨跌: {change_pct:.2f}%"
                floating_window.update_text(text)
            else:
                floating_window.update_text("未获取到数据")
                
        except Exception as e:
            print(f"错误: {e}")
            floating_window.update_text("数据获取失败")
        
        time.sleep(1)  # 每秒更新一次


if __name__ == "__main__":
    root = tk.Tk()
    floating_window = FloatingWindow(root)

    # 使用线程来更新文本，以避免阻塞主线程
    threading.Thread(target=update_label_text, args=(floating_window,), daemon=True).start()

    root.mainloop()