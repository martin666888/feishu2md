"""预览窗口模块"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
from typing import Optional


class PreviewWindow:
    """预览窗口类"""
    
    def __init__(self, parent: tk.Tk):
        """初始化预览窗口
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.window: Optional[tk.Toplevel] = None
        self.markdown_content = ""
        self.file_path = ""
        
    def show(self, markdown_content: str, file_path: str = ""):
        """显示预览窗口
        
        Args:
            markdown_content: markdown内容
            file_path: 文件路径（可选）
        """
        self.markdown_content = markdown_content
        self.file_path = file_path
        
        if self.window is None or not self.window.winfo_exists():
            self._create_window()
        else:
            self.window.lift()
            self.window.focus_force()
        
        # 更新内容
        self._update_content()
    
    def _create_window(self):
        """创建预览窗口"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Markdown预览")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        # 设置窗口图标（与主窗口一致）
        try:
            # self.window.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 工具栏
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 保存按钮
        self.save_btn = ttk.Button(toolbar_frame, text="保存为...", 
                                 command=self.save_as)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 另存为按钮
        self.save_copy_btn = ttk.Button(toolbar_frame, text="另存为", 
                                      command=self.save_copy)
        self.save_copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 复制到剪贴板按钮
        self.copy_btn = ttk.Button(toolbar_frame, text="复制到剪贴板", 
                                 command=self.copy_to_clipboard)
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(toolbar_frame, text="刷新", 
                                    command=self.refresh)
        self.refresh_btn.pack(side=tk.LEFT)
        
        # 关闭按钮
        self.close_btn = ttk.Button(toolbar_frame, text="关闭", 
                                  command=self.close)
        self.close_btn.pack(side=tk.RIGHT)
        
        # 文件信息标签
        self.file_info_label = ttk.Label(toolbar_frame, text="", 
                                       foreground="gray")
        self.file_info_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # 创建Notebook用于切换视图
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Markdown源码视图
        self.source_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.source_frame, text="Markdown源码")
        
        # 源码文本区域
        self.source_text = scrolledtext.ScrolledText(
            self.source_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 10),
            tabs='1c'
        )
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 渲染预览视图（简单的HTML-like显示）
        self.preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_frame, text="预览")
        
        # 预览文本区域
        self.preview_text = scrolledtext.ScrolledText(
            self.preview_frame, 
            wrap=tk.WORD, 
            font=('Arial', 10),
            state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 统计信息框架
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 统计信息标签
        self.stats_label = ttk.Label(stats_frame, text="", foreground="gray")
        self.stats_label.pack(side=tk.LEFT)
        
        # 绑定事件
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        
        # 配置文本区域的语法高亮（简单版本）
        self._setup_syntax_highlighting()
    
    def _setup_syntax_highlighting(self):
        """设置简单的语法高亮"""
        # 配置标签样式
        self.source_text.tag_configure("heading", font=('Consolas', 10, 'bold'), foreground="#0066CC")
        self.source_text.tag_configure("bold", font=('Consolas', 10, 'bold'))
        self.source_text.tag_configure("italic", font=('Consolas', 10, 'italic'))
        self.source_text.tag_configure("code", font=('Consolas', 9), background="#F5F5F5")
        self.source_text.tag_configure("link", foreground="#0066CC", underline=True)
        self.source_text.tag_configure("list", foreground="#666666")
    
    def _update_content(self):
        """更新内容显示"""
        if not self.window or not self.window.winfo_exists():
            return
        
        # 更新源码视图
        self.source_text.delete(1.0, tk.END)
        self.source_text.insert(1.0, self.markdown_content)
        
        # 应用简单的语法高亮
        self._apply_syntax_highlighting()
        
        # 更新预览视图
        self._update_preview()
        
        # 更新文件信息
        if self.file_path:
            filename = os.path.basename(self.file_path)
            self.file_info_label.config(text=f"文件: {filename}")
        else:
            self.file_info_label.config(text="未保存")
        
        # 更新统计信息
        self._update_stats()
    
    def _apply_syntax_highlighting(self):
        """应用简单的语法高亮"""
        content = self.source_text.get(1.0, tk.END)
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            
            # 标题
            if line.startswith('#'):
                self.source_text.tag_add("heading", line_start, line_end)
            
            # 粗体
            if '**' in line:
                start_pos = 0
                while True:
                    start_idx = line.find('**', start_pos)
                    if start_idx == -1:
                        break
                    end_idx = line.find('**', start_idx + 2)
                    if end_idx == -1:
                        break
                    
                    tag_start = f"{i+1}.{start_idx}"
                    tag_end = f"{i+1}.{end_idx + 2}"
                    self.source_text.tag_add("bold", tag_start, tag_end)
                    start_pos = end_idx + 2
            
            # 代码块
            if '`' in line:
                start_pos = 0
                while True:
                    start_idx = line.find('`', start_pos)
                    if start_idx == -1:
                        break
                    end_idx = line.find('`', start_idx + 1)
                    if end_idx == -1:
                        break
                    
                    tag_start = f"{i+1}.{start_idx}"
                    tag_end = f"{i+1}.{end_idx + 1}"
                    self.source_text.tag_add("code", tag_start, tag_end)
                    start_pos = end_idx + 1
            
            # 链接
            if '[' in line and '](' in line:
                self.source_text.tag_add("link", line_start, line_end)
            
            # 列表
            if line.strip().startswith(('-', '*', '+')) or line.strip().startswith(tuple(f"{i}." for i in range(10))):
                self.source_text.tag_add("list", line_start, line_end)
    
    def _update_preview(self):
        """更新预览视图（简单的文本渲染）"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        # 简单的markdown渲染
        lines = self.markdown_content.split('\n')
        rendered_lines = []
        
        for line in lines:
            # 处理标题
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('# ').strip()
                rendered_lines.append('\n' + '=' * (6 - level) + f" {title} " + '=' * (6 - level) + '\n')
            
            # 处理粗体
            elif '**' in line:
                rendered_line = line.replace('**', '')
                rendered_lines.append(rendered_line)
            
            # 处理代码块
            elif line.strip().startswith('```'):
                if line.strip() == '```':
                    rendered_lines.append('--- 代码块结束 ---')
                else:
                    lang = line.strip()[3:]
                    rendered_lines.append(f'--- 代码块开始 ({lang}) ---')
            
            # 处理列表
            elif line.strip().startswith(('-', '*', '+')):
                item = line.strip()[1:].strip()
                rendered_lines.append(f"• {item}")
            
            # 处理有序列表
            elif any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
                rendered_lines.append(line)
            
            # 普通文本
            else:
                rendered_lines.append(line)
        
        preview_content = '\n'.join(rendered_lines)
        self.preview_text.insert(1.0, preview_content)
        self.preview_text.config(state=tk.DISABLED)
    
    def _update_stats(self):
        """更新统计信息"""
        if not self.markdown_content:
            self.stats_label.config(text="")
            return
        
        lines = len(self.markdown_content.split('\n'))
        chars = len(self.markdown_content)
        words = len(self.markdown_content.split())
        
        stats_text = f"行数: {lines} | 字符数: {chars} | 单词数: {words}"
        self.stats_label.config(text=stats_text)
    
    def save_as(self):
        """另存为文件"""
        if not self.markdown_content:
            messagebox.showwarning("警告", "没有内容可保存")
            return
        
        # 获取默认文件名
        default_name = "document.md"
        if self.file_path:
            default_name = os.path.basename(self.file_path)
        
        file_path = filedialog.asksaveasfilename(
            title="保存Markdown文件",
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")],
            initialname=default_name
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.markdown_content)
                
                self.file_path = file_path
                self._update_content()  # 更新文件信息显示
                messagebox.showinfo("成功", f"文件已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {str(e)}")
    
    def save_copy(self):
        """保存副本"""
        if not self.markdown_content:
            messagebox.showwarning("警告", "没有内容可保存")
            return
        
        # 生成默认文件名
        if self.file_path:
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            default_name = f"{base_name}_copy.md"
        else:
            default_name = "document_copy.md"
        
        file_path = filedialog.asksaveasfilename(
            title="保存副本",
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")],
            initialname=default_name
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.markdown_content)
                
                messagebox.showinfo("成功", f"副本已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存副本失败: {str(e)}")
    
    def copy_to_clipboard(self):
        """复制到剪贴板"""
        if not self.markdown_content:
            messagebox.showwarning("警告", "没有内容可复制")
            return
        
        try:
            self.window.clipboard_clear()
            self.window.clipboard_append(self.markdown_content)
            messagebox.showinfo("成功", "内容已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def refresh(self):
        """刷新显示"""
        self._update_content()
        messagebox.showinfo("提示", "预览已刷新")
    
    def close(self):
        """关闭窗口"""
        if self.window:
            self.window.destroy()
            self.window = None
    
    def is_open(self) -> bool:
        """检查窗口是否打开"""
        return self.window is not None and self.window.winfo_exists()