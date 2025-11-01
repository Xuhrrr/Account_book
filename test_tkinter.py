import tkinter as tk

print("Tkinter 导入成功!")
root = tk.Tk()
root.title("测试窗口")
label = tk.Label(root, text="Tkinter 图形界面工作正常!")
label.pack(pady=20)
button = tk.Button(root, text="关闭", command=root.destroy)
button.pack(pady=10)
root.mainloop()