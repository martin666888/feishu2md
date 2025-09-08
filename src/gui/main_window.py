"""主窗口GUI模块"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
from typing import Callable, Optional


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root: tk.Tk):
        """初始化主窗口
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.setup_window()
        self.create_widgets()
        
        # 回调函数
        self.on_convert_callback: Optional[Callable] = None
        self.on_preview_callback: Optional[Callable] = None
        self.on_settings_callback: Optional[Callable] = None
        
        # 状态变量
        self.is_converting = False
    
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("飞书文档转Markdown工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        # 设置主题颜色
        self.colors = {
            'primary': '#2F54EB',
            'success': '#52C41A',
            'error': '#FF4D4F',
            'warning': '#FAAD14',
            'background': '#FFFFFF',
            'text': '#000000',
            'border': '#D9D9D9'
        }
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="飞书文档转Markdown工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入区域框架
        input_frame = ttk.LabelFrame(main_frame, text="输入信息", padding="15")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)
        
        # User Access Token输入
        ttk.Label(input_frame, text="User Access Token:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(input_frame, textvariable=self.token_var, show="*", width=50)
        self.token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        
        # 显示/隐藏token按钮
        self.show_token_var = tk.BooleanVar()
        self.show_token_btn = ttk.Checkbutton(input_frame, text="显示", variable=self.show_token_var,
                                            command=self.toggle_token_visibility)
        self.show_token_btn.grid(row=0, column=2, padx=(10, 0), pady=(0, 10))
        
        # Document ID输入
        ttk.Label(input_frame, text="Document ID:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.doc_id_var = tk.StringVar()
        self.doc_id_entry = ttk.Entry(input_frame, textvariable=self.doc_id_var, width=50)
        self.doc_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        
        # 输出路径选择
        ttk.Label(input_frame, text="输出路径:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        # 输出路径框架
        output_path_frame = ttk.Frame(input_frame)
        output_path_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        output_path_frame.columnconfigure(0, weight=1)
        
        # 输出路径输入框
        self.output_path_var = tk.StringVar()
        self.output_path_entry = ttk.Entry(output_path_frame, textvariable=self.output_path_var, width=40)
        self.output_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 浏览按钮
        self.browse_btn = ttk.Button(output_path_frame, text="浏览", command=self.browse_output_path)
        self.browse_btn.grid(row=0, column=1)
        
        # 使用默认路径按钮
        self.default_path_btn = ttk.Button(output_path_frame, text="默认", command=self.use_default_path)
        self.default_path_btn.grid(row=0, column=2, padx=(5, 0))
        
        # 输入验证提示
        self.validation_label = ttk.Label(input_frame, text="", foreground=self.colors['error'])
        self.validation_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=(0, 20))
        
        # 转换按钮
        self.convert_btn = ttk.Button(control_frame, text="开始转换", 
                                    command=self.start_conversion,
                                    style='Accent.TButton')
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 预览按钮
        self.preview_btn = ttk.Button(control_frame, text="预览结果", 
                                    command=self.show_preview,
                                    state=tk.DISABLED)
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 设置按钮
        self.settings_btn = ttk.Button(control_frame, text="设置", 
                                     command=self.show_settings)
        self.settings_btn.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          mode='determinate', length=400)
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态显示区域
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 状态文本区域
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, width=80, 
                                                   wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 底部按钮框架
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        bottom_frame.columnconfigure(0, weight=1)
        
        # 清空日志按钮
        self.clear_log_btn = ttk.Button(bottom_frame, text="清空日志", 
                                      command=self.clear_status_log)
        self.clear_log_btn.grid(row=0, column=0, sticky=tk.W)
        
        # 关于按钮
        self.about_btn = ttk.Button(bottom_frame, text="关于", 
                                  command=self.show_about)
        self.about_btn.grid(row=0, column=1, sticky=tk.E)
        
        # 绑定事件
        self.token_var.trace('w', self.validate_inputs)
        self.doc_id_var.trace('w', self.validate_inputs)
        
        # 初始化输出路径为默认值
        self.use_default_path()
        
        # 初始化状态
        self.log_status("应用程序已启动，请输入Token和Document ID")
    
    def toggle_token_visibility(self):
        """切换token显示/隐藏"""
        if self.show_token_var.get():
            self.token_entry.config(show="")
        else:
            self.token_entry.config(show="*")
    
    def validate_inputs(self, *args):
        """验证输入"""
        token = self.token_var.get().strip()
        doc_id = self.doc_id_var.get().strip()
        
        # 清空之前的验证信息
        self.validation_label.config(text="")
        
        # 验证token
        if token and not token.startswith('u-'):
            self.validation_label.config(text="Token格式错误，应以'u-'开头")
            self.convert_btn.config(state=tk.DISABLED)
            return
        
        # 验证document_id
        if doc_id and len(doc_id) < 10:
            self.validation_label.config(text="Document ID格式错误，长度过短")
            self.convert_btn.config(state=tk.DISABLED)
            return
        
        # 检查是否都已填写
        if token and doc_id:
            self.convert_btn.config(state=tk.NORMAL)
        else:
            self.convert_btn.config(state=tk.DISABLED)
    
    def start_conversion(self):
        """开始转换"""
        if self.is_converting:
            return
        
        token = self.token_var.get().strip()
        doc_id = self.doc_id_var.get().strip()
        
        if not token or not doc_id:
            messagebox.showerror("错误", "请填写完整的Token和Document ID")
            return
        
        # 禁用转换按钮
        self.convert_btn.config(state=tk.DISABLED, text="转换中...")
        self.is_converting = True
        
        # 重置进度条
        self.progress_var.set(0)
        
        # 在新线程中执行转换
        if self.on_convert_callback:
            thread = threading.Thread(target=self._conversion_thread, 
                                     args=(token, doc_id))
            thread.daemon = True
            thread.start()
    
    def _conversion_thread(self, token: str, doc_id: str):
        """转换线程"""
        try:
            if self.on_convert_callback:
                self.on_convert_callback(token, doc_id)
        except Exception as e:
            self.root.after(0, lambda: self.conversion_error(str(e)))
    
    def conversion_complete(self, success: bool, message: str = ""):
        """转换完成回调"""
        self.is_converting = False
        self.convert_btn.config(state=tk.NORMAL, text="开始转换")
        
        if success:
            self.progress_var.set(100)
            self.preview_btn.config(state=tk.NORMAL)
            self.log_status(f"转换成功: {message}", "success")
            messagebox.showinfo("成功", "文档转换完成！")
        else:
            self.progress_var.set(0)
            self.log_status(f"转换失败: {message}", "error")
            messagebox.showerror("错误", f"转换失败: {message}")
    
    def conversion_error(self, error_message: str):
        """转换错误回调"""
        self.conversion_complete(False, error_message)
    
    def update_progress(self, value: float, message: str = ""):
        """更新进度"""
        self.progress_var.set(value)
        if message:
            self.log_status(message)
    
    def show_preview(self):
        """显示预览"""
        if self.on_preview_callback:
            self.on_preview_callback()
    
    def show_settings(self):
        """显示设置"""
        if self.on_settings_callback:
            self.on_settings_callback()
    
    def show_about(self):
        """显示关于信息"""
        about_text = """飞书文档转Markdown工具 v1.0.0

这是一个基于飞书开放平台API的桌面应用程序，
帮助用户将飞书文档快速转换为标准markdown格式文件。

功能特点：
• 支持多种块类型转换
• 保留文档格式和样式
• 提供预览和保存功能
• 简洁易用的界面

开发者：Feishu2MD Tool
版本：1.0.0"""
        
        messagebox.showinfo("关于", about_text)
    
    def log_status(self, message: str, level: str = "info"):
        """记录状态日志
        
        Args:
            message: 日志消息
            level: 日志级别 (info, success, warning, error)
        """
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # 根据级别设置颜色
        color_map = {
            'info': 'black',
            'success': 'green',
            'warning': 'orange',
            'error': 'red'
        }
        
        color = color_map.get(level, 'black')
        
        # 插入日志
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # 设置颜色（如果支持的话）
        try:
            line_start = self.status_text.index("end-2l")
            line_end = self.status_text.index("end-1l")
            self.status_text.tag_add(level, line_start, line_end)
            self.status_text.tag_config(level, foreground=color)
        except:
            pass
        
        self.status_text.config(state=tk.DISABLED)
        self.status_text.see(tk.END)
    
    def clear_status_log(self):
        """清空状态日志"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.log_status("日志已清空")
    
    def set_convert_callback(self, callback: Callable):
        """设置转换回调函数"""
        self.on_convert_callback = callback
    
    def set_preview_callback(self, callback: Callable):
        """设置预览回调函数"""
        self.on_preview_callback = callback
    
    def set_settings_callback(self, callback: Callable):
        """设置设置回调函数"""
        self.on_settings_callback = callback
    
    def get_token(self) -> str:
        """获取当前输入的token"""
        return self.token_var.get().strip()
    
    def get_document_id(self) -> str:
        """获取当前输入的document_id"""
        return self.doc_id_var.get().strip()
    
    def set_token(self, token: str):
        """设置token"""
        self.token_var.set(token)
    
    def set_document_id(self, doc_id: str):
        """设置document_id"""
        self.doc_id_var.set(doc_id)
    
    def browse_output_path(self):
        """浏览输出路径"""
        # 获取当前路径作为初始目录
        current_path = self.output_path_var.get().strip()
        if current_path and os.path.exists(current_path):
            if os.path.isfile(current_path):
                initial_dir = os.path.dirname(current_path)
                initial_file = os.path.basename(current_path)
            else:
                initial_dir = current_path
                initial_file = ""
        else:
            initial_dir = os.path.expanduser("~/Documents")
            initial_file = ""
        
        # 选择保存文件路径
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件路径",
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=".md",
            filetypes=[
                ("Markdown文件", "*.md"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.output_path_var.set(file_path)
            self.log_status(f"已选择输出路径: {file_path}")
    
    def use_default_path(self):
        """使用默认输出路径"""
        from pathlib import Path
        default_dir = Path.home() / "Documents" / "Feishu2MD" / "output"
        self.output_path_var.set(str(default_dir))
        self.log_status(f"已设置为默认输出路径: {default_dir}")
    
    def get_output_path(self) -> str:
        """获取当前设置的输出路径"""
        return self.output_path_var.get().strip()
    
    def set_output_path(self, path: str):
        """设置输出路径"""
        self.output_path_var.set(path)