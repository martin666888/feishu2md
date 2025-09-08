"""预览窗口模块 - PyQt6版本"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, 
                            QPushButton, QTextEdit, QTabWidget, QLabel,
                            QFileDialog, QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import os
import re
from typing import Optional


class MarkdownHighlighter(QSyntaxHighlighter):
    """Markdown语法高亮器"""
    
    def __init__(self, document):
        super().__init__(document)
        
        # 定义格式
        self.heading_format = QTextCharFormat()
        self.heading_format.setFontWeight(QFont.Weight.Bold)
        self.heading_format.setForeground(QColor("#0066CC"))
        
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Weight.Bold)
        
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        
        self.code_format = QTextCharFormat()
        self.code_format.setFontFamily("Consolas")
        self.code_format.setFontPointSize(10)
        self.code_format.setBackground(QColor("#F5F5F5"))
        
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor("#0066CC"))
        self.link_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#666666"))
        
        # 定义规则
        self.rules = [
            # 标题
            (r'^#{1,6}\s+.+$', self.heading_format),
            # 粗体
            (r'\*\*[^*]+\*\*', self.bold_format),
            # 斜体
            (r'\*[^*]+\*', self.italic_format),
            # 行内代码
            (r'`[^`]+`', self.code_format),
            # 链接
            (r'\[.+\]\(.+\)', self.link_format),
            # 无序列表
            (r'^[\-\*]\s+.+$', self.list_format),
            # 有序列表
            (r'^\d+\.\s+.+$', self.list_format),
        ]
    
    def highlightBlock(self, text: str):
        """高亮文本块"""
        for pattern, format in self.rules:
            regex = QRegularExpression(pattern)
            matches = regex.globalMatch(text)
            
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class PreviewWindow(QDialog):
    """预览窗口类 - PyQt6版本"""
    
    def __init__(self, parent=None):
        """初始化预览窗口
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.markdown_content = ""
        self.file_path = ""
        
        # 设置窗口属性
        self.setup_window()
        
        # 初始化UI
        self.init_ui()
        
        # 设置连接
        self.setup_connections()
    
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("Markdown预览")
        self.setGeometry(150, 150, 900, 700)
        self.setModal(False)  # 非模态对话框
        
        # 设置窗口图标（如果有的话）
        try:
            # self.setWindowIcon(QIcon('icon.ico'))
            pass
        except:
            pass
    
    def init_ui(self):
        """初始化界面组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("保存为...")
        self.save_copy_btn = QPushButton("另存为")
        self.copy_btn = QPushButton("复制到剪贴板")
        self.refresh_btn = QPushButton("刷新")
        
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addWidget(self.save_copy_btn)
        toolbar_layout.addWidget(self.copy_btn)
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        toolbar_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        # 文件信息标签
        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet("color: gray;")
        toolbar_layout.addWidget(self.file_info_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 创建Notebook用于切换视图
        self.tab_widget = QTabWidget()
        
        # Markdown源码视图
        self.source_widget = QWidget()
        source_layout = QVBoxLayout(self.source_widget)
        source_layout.setContentsMargins(5, 5, 5, 5)
        
        self.source_text = QTextEdit()
        self.source_text.setFont(QFont("Consolas", 10))
        self.source_text.setTabStopDistance(40)  # 设置制表符距离
        
        # 设置语法高亮
        self.highlighter = MarkdownHighlighter(self.source_text.document())
        
        source_layout.addWidget(self.source_text)
        self.tab_widget.addTab(self.source_widget, "Markdown源码")
        
        # 渲染预览视图
        self.preview_widget = QWidget()
        preview_layout = QVBoxLayout(self.preview_widget)
        preview_layout.setContentsMargins(5, 5, 5, 5)
        
        self.preview_text = QTextEdit()
        self.preview_text.setFont(QFont("Arial", 10))
        self.preview_text.setReadOnly(True)
        
        preview_layout.addWidget(self.preview_text)
        self.tab_widget.addTab(self.preview_widget, "预览")
        
        splitter.addWidget(self.tab_widget)
        
        # 统计信息框架
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: gray;")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        
        splitter.addWidget(stats_widget)
        
        # 设置分割器比例
        splitter.setSizes([600, 50])
        
        main_layout.addWidget(splitter)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            
            QPushButton {
                min-width: 80px;
                padding: 5px 15px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                background-color: #ffffff;
            }
            
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            
            QPushButton:pressed {
                background-color: #e6e6e6;
            }
            
            QTextEdit {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 5px;
            }
            
            QTabWidget::pane {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #d9d9d9;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 5px 15px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            
            QSplitter::handle {
                background-color: #d9d9d9;
                height: 2px;
            }
        """)
    
    def setup_connections(self):
        """设置信号槽连接"""
        # 按钮点击事件
        self.save_btn.clicked.connect(self.save_as)
        self.save_copy_btn.clicked.connect(self.save_copy)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.refresh_btn.clicked.connect(self.refresh)
        self.close_btn.clicked.connect(self.close)
        
        # 标签切换事件
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def show(self, markdown_content: str = "", file_path: str = ""):
        """显示预览窗口
        
        Args:
            markdown_content: markdown内容
            file_path: 文件路径（可选）
        """
        self.markdown_content = markdown_content
        self.file_path = file_path
        
        # 更新内容
        self._update_content()
        
        # 显示窗口
        super().show()
        
        # 激活窗口
        self.raise_()
        self.activateWindow()
    
    def _update_content(self):
        """更新内容显示"""
        # 更新源码视图
        self.source_text.setPlainText(self.markdown_content)
        
        # 更新预览视图
        self._update_preview()
        
        # 更新文件信息
        if self.file_path:
            filename = os.path.basename(self.file_path)
            self.file_info_label.setText(f"文件: {filename}")
        else:
            self.file_info_label.setText("未保存")
        
        # 更新统计信息
        self._update_stats()
    
    def _update_preview(self):
        """更新预览视图（简单的文本渲染）"""
        if not self.markdown_content:
            self.preview_text.clear()
            return
        
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
        self.preview_text.setPlainText(preview_content)
    
    def _update_stats(self):
        """更新统计信息"""
        if not self.markdown_content:
            self.stats_label.setText("")
            return
        
        lines = len(self.markdown_content.split('\n'))
        chars = len(self.markdown_content)
        words = len(self.markdown_content.split())
        
        stats_text = f"行数: {lines} | 字符数: {chars} | 单词数: {words}"
        self.stats_label.setText(stats_text)
    
    def on_tab_changed(self, index: int):
        """标签切换事件"""
        # 如果切换到源码标签，重新应用语法高亮
        if index == 0:  # 源码标签
            # 重新应用高亮
            self.highlighter.rehighlight()
    
    def save_as(self):
        """另存为文件"""
        if not self.markdown_content:
            QMessageBox.warning(self, "警告", "没有内容可保存")
            return
        
        # 获取默认文件名
        default_name = "document.md"
        if self.file_path:
            default_name = os.path.basename(self.file_path)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存Markdown文件",
            default_name,
            "Markdown文件 (*.md);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.markdown_content)
                
                self.file_path = file_path
                self._update_content()  # 更新文件信息显示
                QMessageBox.information(self, "成功", f"文件已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件失败: {str(e)}")
    
    def save_copy(self):
        """保存副本"""
        if not self.markdown_content:
            QMessageBox.warning(self, "警告", "没有内容可保存")
            return
        
        # 生成默认文件名
        if self.file_path:
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            default_name = f"{base_name}_copy.md"
        else:
            default_name = "document_copy.md"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存副本",
            default_name,
            "Markdown文件 (*.md);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.markdown_content)
                
                QMessageBox.information(self, "成功", f"副本已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存副本失败: {str(e)}")
    
    def copy_to_clipboard(self):
        """复制到剪贴板"""
        if not self.markdown_content:
            QMessageBox.warning(self, "警告", "没有内容可复制")
            return
        
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.markdown_content)
            QMessageBox.information(self, "成功", "内容已复制到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败: {str(e)}")
    
    def refresh(self):
        """刷新显示"""
        self._update_content()
        QMessageBox.information(self, "提示", "预览已刷新")
    
    def is_open(self) -> bool:
        """检查窗口是否打开"""
        return self.isVisible()
