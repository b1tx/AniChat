import tkinter as tk
import tkinter.messagebox
from PIL import Image, ImageTk
import webbrowser
import os

import Options


class LoginApp:
    def __init__(self, add_path="./local/add.txt", recent_path="./local/recent.txt", now_path='./local/now.txt', icon_path="./local/icon.png"):
        self.add_path = add_path
        self.recent_path = recent_path
        self.now_path = now_path
        self.icon_path = icon_path

        self.window = tk.Tk()
        self.window.title('欢迎登录')
        self.window.geometry('450x300')
        self.var_usr_name = tk.StringVar()
        self.var_usr_pwd = tk.StringVar()
        self.var_pwd_visible = tk.BooleanVar()
        self.var_remember_me = tk.BooleanVar()
        self.init_ui()

    def init_ui(self):
        # 设置画布
        canvas = tk.Canvas(self.window, height=200, width=900)
        if os.path.exists(self.icon_path):
            im = Image.open(self.icon_path)
            original_width, original_height = im.size
            scale = 0.2
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            im_resized = im.resize((new_width, new_height))
            self.image_file = ImageTk.PhotoImage(im_resized)
            image = canvas.create_image(180, 40, anchor='nw', image=self.image_file)

        canvas.pack(side='top')

        # 用户名和密码输入
        tk.Label(self.window, text='用户名').place(x=100, y=150)
        tk.Label(self.window, text='密  码').place(x=100, y=190)

        self.entry_usr_name = tk.Entry(self.window, textvariable=self.var_usr_name)
        self.entry_usr_name.place(x=160, y=150)
        self.entry_usr_pwd = tk.Entry(self.window, textvariable=self.var_usr_pwd, show='*')
        self.entry_usr_pwd.place(x=160, y=190)

        # 复选框
        chk_show_pwd = tk.Checkbutton(
            self.window, text="显示密码", variable=self.var_pwd_visible, command=self.toggle_password_visibility)
        chk_show_pwd.place(x=320, y=190)
        chk_remember_me = tk.Checkbutton(self.window, text="记住我", variable=self.var_remember_me)
        chk_remember_me.place(x=320, y=150)

        # 登录和注册按钮
        self.btn_login = tk.Button(self.window, text=' 登  录 ', command=self.usr_login, state=tk.DISABLED)
        self.btn_login.place(x=150, y=230)
        btn_sign_up = tk.Button(self.window, text=' 注  册 ', command=self.usr_sign_up)
        btn_sign_up.place(x=250, y=230)

        # 初始化状态
        self.load_recent_user()
        self.update_login_button_state()
        self.var_usr_name.trace_add("write", self.update_login_button_state)
        self.var_usr_pwd.trace_add("write", self.update_login_button_state)

    def load_recent_user(self):
        if os.path.exists(self.recent_path):
            with open(self.recent_path, "r") as f:
                line = f.readline().strip()
                if line:
                    usr_name, usr_pwd = line.split(":")
                    self.var_usr_name.set(usr_name)
                    self.var_usr_pwd.set(usr_pwd)

    def load_users(self):
        users = {}
        if os.path.exists(self.add_path):
            with open(self.add_path, "r") as f:
                for line in f:
                    if line.strip():
                        username, password = line.strip().split(":")
                        users[username] = password
        return users

    def save_users(self, users):
        with open(self.add_path, 'w') as f:
            for username, password in users.items():
                f.write(f"{username}:{password}\n")

    def toggle_password_visibility(self):
        self.entry_usr_pwd.config(show='' if self.var_pwd_visible.get() else '*')

    def update_login_button_state(self, *args):
        if self.var_usr_name.get().strip() and self.var_usr_pwd.get().strip():
            self.btn_login.config(state=tk.NORMAL)
        else:
            self.btn_login.config(state=tk.DISABLED)

    def usr_login(self):
        usr_name = self.var_usr_name.get()
        usr_pwd = self.var_usr_pwd.get()
        usrs_info = self.load_users()

        if usr_name in usrs_info:
            if usrs_info[usr_name] == usr_pwd:
                tk.messagebox.showinfo('欢迎光临', f'{usr_name}：请享受聊天')
                if self.var_remember_me.get():
                    print(6)
                    with open(self.recent_path, 'w') as f:
                        f.write(f"{usr_name}:{usr_pwd}\n")
                user_folder_path = os.path.join('./static', usr_name)
                with open(self.now_path, 'w') as f:
                    f.write(f"{usr_name}:{usr_pwd}\n")
                if not os.path.exists(user_folder_path):
                    os.makedirs(user_folder_path)
                self.window.destroy()
            else:
                tk.messagebox.showerror('错误提示', '用户名或密码错误')
        else:
            is_sign_up = tk.messagebox.askyesno('提示', '该用户不存在')
            print(is_sign_up)
            if is_sign_up:
                self.usr_sign_up()

    def usr_sign_up(self):
        def register():
            username = new_usr_name.get()
            password = new_usr_pwd.get()
            confirm_password = new_usr_pwd_confirm.get()

            if password != confirm_password:
                tk.messagebox.showerror('错误', '两次输入的密码不一致')
                return

            users = self.load_users()
            if username in users:
                tk.messagebox.showerror('错误', '用户名已被注册')
            else:
                users[username] = password
                self.save_users(users)

                self.var_usr_name.set(username)
                self.var_usr_pwd.set(password)

                tk.messagebox.showinfo('提示', '注册成功')
                sign_up_window.destroy()

        sign_up_window = tk.Toplevel(self.window)
        sign_up_window.title('注册')
        sign_up_window.geometry('300x200')

        sign_up_window.transient(self.window)
        sign_up_window.grab_set()
        sign_up_window.focus_set()

        new_usr_name = tk.StringVar(value=self.var_usr_name.get())
        tk.Label(sign_up_window, text='用户名').place(x=10, y=10)
        entry_new_name = tk.Entry(sign_up_window, textvariable=new_usr_name)
        entry_new_name.place(x=100, y=10)

        new_usr_pwd = tk.StringVar()
        new_usr_pwd_confirm = tk.StringVar()

        tk.Label(sign_up_window, text='密码').place(x=10, y=50)
        tk.Entry(sign_up_window, textvariable=new_usr_pwd, show='*').place(x=100, y=50)
        tk.Label(sign_up_window, text='确认密码').place(x=10, y=90)
        tk.Entry(sign_up_window, textvariable=new_usr_pwd_confirm, show='*').place(x=100, y=90)

        tk.Button(sign_up_window, text='注册', command=register).place(x=120, y=130)

    def run(self):
        self.window.mainloop()


# 接口调用示例
if __name__ == "__main__":
    app = LoginApp()
    app.run()

