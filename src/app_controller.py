"""应用程序控制器"""
import tkinter as tk
from tkinter import messagebox
import threading
import traceback
from typing import Optional

from src.api.feishu_client import FeishuAPIClient
from src.converter.markdown_converter import MarkdownConverter
from src.gui.main_window import MainWindow
from src.gui.preview_window import PreviewWindow
from src.utils.file_manager import FileManager


class AppController:
    """应用程序控制器类"""
    
    def __init__(self):
        """初始化控制器"""
        # 初始化组件
        self.api_client: Optional[FeishuAPIClient] = None
        self.converter = MarkdownConverter()
        self.file_manager = FileManager()
        
        # GUI组件
        self.root = tk.Tk()
        self.main_window = MainWindow(self.root)
        self.preview_window = PreviewWindow(self.root)
        
        # 数据
        self.current_markdown = ""
        self.current_title = ""
        self.current_doc_id = ""
        
        # 设置回调函数
        self._setup_callbacks()
        
        # 应用设置
        self._apply_settings()
    
    def _setup_callbacks(self):
        """设置回调函数"""
        self.main_window.set_convert_callback(self.start_conversion)
        self.main_window.set_preview_callback(self.show_preview)
        self.main_window.set_settings_callback(self.show_settings)
    
    def _apply_settings(self):
        """应用设置"""
        # 从文件管理器获取设置
        settings = self.file_manager.get_settings()
        
        # 应用窗口设置（如果有的话）
        # 这里可以根据需要添加更多设置
        pass
    
    def start_conversion(self, token: str, doc_id: str):
        """开始转换文档
        
        Args:
            token: 用户访问令牌
            doc_id: 文档ID
        """
        try:
            self.current_doc_id = doc_id
            
            # 更新状态
            self.main_window.log_status("开始初始化API客户端...")
            self.main_window.update_progress(10, "初始化API客户端")
            
            # 初始化API客户端
            self.api_client = FeishuAPIClient(token)
            
            # 获取文档信息
            self.main_window.log_status("获取文档信息...")
            self.main_window.update_progress(20, "获取文档信息")
            
            doc_info = self.api_client.get_document_info(doc_id)
            if not doc_info:
                raise Exception("无法获取文档信息，请检查Document ID是否正确")
            
            self.current_title = doc_info.get('title', f'Document_{doc_id[:8]}')
            self.main_window.log_status(f"文档标题: {self.current_title}")
            
            # 获取文档块列表
            self.main_window.log_status("获取文档块列表...")
            self.main_window.update_progress(40, "获取文档块列表")
            
            response = self.api_client.get_document_blocks(doc_id)
            if not response or not response.get('data', {}).get('items'):
                raise Exception("文档为空或无法获取文档内容")
            
            blocks = response['data']['items']
            self.main_window.log_status(f"获取到 {len(blocks)} 个文档块")
            
            # 转换为markdown
            self.main_window.log_status("开始转换为Markdown...")
            self.main_window.update_progress(60, "转换为Markdown")
            
            markdown_content = self.converter.convert_blocks_to_markdown(blocks)
            
            if not markdown_content.strip():
                raise Exception("转换结果为空，可能文档中没有支持的内容类型")
            
            self.current_markdown = markdown_content
            
            # 自动保存（如果启用）
            settings = self.file_manager.get_settings()
            if settings.get('auto_save', True):
                self.main_window.log_status("自动保存文件...")
                self.main_window.update_progress(80, "保存文件")
                
                # 获取用户指定的输出路径
                output_path = self.main_window.get_output_path()
                
                success, result = self.file_manager.save_markdown(
                    self.current_markdown,
                    title=self.current_title,
                    doc_id=self.current_doc_id,
                    output_path=output_path if output_path else None
                )
                
                if success:
                    self.main_window.log_status(f"文件已保存到: {result}")
                else:
                    self.main_window.log_status(f"自动保存失败: {result}", "warning")
            
            # 完成
            self.main_window.update_progress(100, "转换完成")
            self.main_window.conversion_complete(True, f"成功转换文档: {self.current_title}")
            
        except Exception as e:
            error_msg = str(e)
            self.main_window.log_status(f"转换失败: {error_msg}", "error")
            self.main_window.conversion_complete(False, error_msg)
            
            # 记录详细错误信息
            traceback.print_exc()
    
    def show_preview(self):
        """显示预览窗口"""
        if not self.current_markdown:
            messagebox.showwarning("警告", "没有可预览的内容，请先进行转换")
            return
        
        try:
            # 生成临时文件路径用于预览
            temp_filename = self.file_manager.generate_filename(
                self.current_title, 
                self.current_doc_id
            )
            
            self.preview_window.show(
                self.current_markdown, 
                temp_filename
            )
            
            self.main_window.log_status("预览窗口已打开")
            
        except Exception as e:
            error_msg = f"打开预览失败: {str(e)}"
            self.main_window.log_status(error_msg, "error")
            messagebox.showerror("错误", error_msg)
    
    def show_settings(self):
        """显示设置窗口"""
        try:
            settings_window = SettingsWindow(self.root, self.file_manager)
            settings_window.show()
        except Exception as e:
            error_msg = f"打开设置失败: {str(e)}"
            self.main_window.log_status(error_msg, "error")
            messagebox.showerror("错误", error_msg)
    
    def run(self):
        """运行应用程序"""
        try:
            # 清理临时文件
            self.file_manager.cleanup_temp_files()
            
            # 启动GUI
            self.main_window.log_status("应用程序启动完成")
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("严重错误", f"应用程序运行失败: {str(e)}")
            traceback.print_exc()
    
    def shutdown(self):
        """关闭应用程序"""
        try:
            # 清理资源
            if self.preview_window.is_open():
                self.preview_window.close()
            
            # 保存设置
            self.file_manager._save_settings()
            
            # 关闭主窗口
            self.root.quit()
            
        except Exception as e:
            print(f"关闭应用程序时出错: {e}")


class SettingsWindow:
    """设置窗口类"""
    
    def __init__(self, parent: tk.Tk, file_manager: FileManager):
        """初始化设置窗口
        
        Args:
            parent: 父窗口
            file_manager: 文件管理器
        """
        self.parent = parent
        self.file_manager = file_manager
        self.window: Optional[tk.Toplevel] = None
        
        # 设置变量
        self.settings = self.file_manager.get_settings()
        self.vars = {}
    
    def show(self):
        """显示设置窗口"""
        if self.window is None or not self.window.winfo_exists():
            self._create_window()
        else:
            self.window.lift()
            self.window.focus_force()
    
    def _create_window(self):
        """创建设置窗口"""
        from tkinter import ttk, filedialog
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("设置")
        self.window.geometry("500x400")
        self.window.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 常规设置页面
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="常规")
        
        # 自动保存设置
        self.vars['auto_save'] = tk.BooleanVar(value=self.settings.get('auto_save', True))
        ttk.Checkbutton(general_frame, text="启用自动保存", 
                       variable=self.vars['auto_save']).pack(anchor=tk.W, pady=5)
        
        # 备份设置
        self.vars['backup_enabled'] = tk.BooleanVar(value=self.settings.get('backup_enabled', True))
        ttk.Checkbutton(general_frame, text="启用文件备份", 
                       variable=self.vars['backup_enabled']).pack(anchor=tk.W, pady=5)
        
        # 默认输出目录
        ttk.Label(general_frame, text="默认输出目录:").pack(anchor=tk.W, pady=(20, 5))
        
        dir_frame = ttk.Frame(general_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        self.vars['default_output_dir'] = tk.StringVar(value=self.settings.get('default_output_dir', ''))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.vars['default_output_dir'])
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse_directory():
            directory = filedialog.askdirectory(initialdir=self.vars['default_output_dir'].get())
            if directory:
                self.vars['default_output_dir'].set(directory)
        
        ttk.Button(dir_frame, text="浏览", command=browse_directory).pack(side=tk.RIGHT)
        
        # 文件命名设置
        ttk.Label(general_frame, text="文件命名模式:").pack(anchor=tk.W, pady=(20, 5))
        
        self.vars['file_naming_pattern'] = tk.StringVar(value=self.settings.get('file_naming_pattern', '{title}_{timestamp}'))
        naming_entry = ttk.Entry(general_frame, textvariable=self.vars['file_naming_pattern'])
        naming_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(general_frame, text="可用变量: {title}, {timestamp}, {doc_id}", 
                 foreground="gray").pack(anchor=tk.W, pady=2)
        
        # 高级设置页面
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="高级")
        
        # 历史记录数量
        ttk.Label(advanced_frame, text="最大历史记录数量:").pack(anchor=tk.W, pady=(10, 5))
        
        self.vars['max_history_items'] = tk.IntVar(value=self.settings.get('max_history_items', 100))
        history_spinbox = ttk.Spinbox(advanced_frame, from_=10, to=1000, 
                                     textvariable=self.vars['max_history_items'])
        history_spinbox.pack(anchor=tk.W, pady=5)
        
        # 编码设置
        ttk.Label(advanced_frame, text="默认文件编码:").pack(anchor=tk.W, pady=(20, 5))
        
        self.vars['default_encoding'] = tk.StringVar(value=self.settings.get('default_encoding', 'utf-8'))
        encoding_combo = ttk.Combobox(advanced_frame, textvariable=self.vars['default_encoding'],
                                     values=['utf-8', 'gbk', 'ascii'], state='readonly')
        encoding_combo.pack(anchor=tk.W, pady=5)
        
        # 存储信息
        storage_info = self.file_manager.get_storage_info()
        if 'error' not in storage_info:
            info_text = f"""存储信息:
基础目录: {storage_info['base_dir']}
输出目录: {storage_info['output_dir']}
文件总数: {storage_info['total_files']}
总大小: {storage_info['total_size_mb']} MB"""
            
            ttk.Label(advanced_frame, text=info_text, foreground="gray").pack(anchor=tk.W, pady=(20, 5))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 保存按钮
        ttk.Button(button_frame, text="保存", command=self._save_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        # 重置按钮
        ttk.Button(button_frame, text="重置", command=self._reset_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        # 取消按钮
        ttk.Button(button_frame, text="取消", command=self._close).pack(side=tk.RIGHT)
        
        # 绑定事件
        self.window.protocol("WM_DELETE_WINDOW", self._close)
    
    def _save_settings(self):
        """保存设置"""
        try:
            # 收集设置
            new_settings = {}
            for key, var in self.vars.items():
                new_settings[key] = var.get()
            
            # 更新设置
            self.file_manager.update_settings(new_settings)
            
            messagebox.showinfo("成功", "设置已保存")
            self._close()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
    
    def _reset_settings(self):
        """重置设置"""
        if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
            # 重置为默认值
            default_settings = {
                'auto_save': True,
                'backup_enabled': True,
                'default_output_dir': str(self.file_manager.output_dir),
                'file_naming_pattern': '{title}_{timestamp}',
                'max_history_items': 100,
                'default_encoding': 'utf-8'
            }
            
            for key, value in default_settings.items():
                if key in self.vars:
                    self.vars[key].set(value)
    
    def _close(self):
        """关闭窗口"""
        if self.window:
            self.window.destroy()
            self.window = None