"""主窗口GUI模块 - PyQt6版本"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QProgressBar, 
                            QTextEdit, QCheckBox, QFrame, QFileDialog,
                            QMessageBox, QFormLayout, QGroupBox)
from PyQt6.QtCore import pyqtSignal, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QFont
import os
from typing import Optional, Callable
import datetime


class MainWindow(QMainWindow):
    """主窗口类 - PyQt6版本"""
    
    # 定义信号
    conversion_started = pyqtSignal(str, str)  # token, doc_id
    preview_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    progress_updated = pyqtSignal(float, str)  # value, message
    conversion_complete = pyqtSignal(bool, str)  # success, message
    status_logged = pyqtSignal(str, str)  # message, level
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 状态变量
        self.is_converting = False
        
        # 设置窗口属性
        self.setup_window()
        
        # 初始化UI
        self.init_ui()
        
        # 设置连接
        self.setup_connections()
        
        # 初始化状态
        self.log_status("应用程序已启动，请输入Token和Document ID")
    
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("飞书文档转Markdown工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口图标（如果有的话）
        try:
            # self.setWindowIcon(QIcon('icon.ico'))
            pass
        except:
            pass
    
    def init_ui(self):
        """初始化界面组件"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("飞书文档转Markdown工具")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 输入区域
        input_group = QGroupBox("输入信息")
        input_layout = QFormLayout(input_group)
        
        # User Access Token输入
        token_layout = QHBoxLayout()
        self.token_entry = QLineEdit()
        self.token_entry.setEchoMode(QLineEdit.EchoMode.Password)
        token_layout.addWidget(self.token_entry)
        
        self.show_token_checkbox = QCheckBox("显示")
        token_layout.addWidget(self.show_token_checkbox)
        
        input_layout.addRow("User Access Token:", token_layout)
        
        # Document ID输入
        self.doc_id_entry = QLineEdit()
        input_layout.addRow("Document ID:", self.doc_id_entry)
        
        # 输出路径选择
        output_path_layout = QHBoxLayout()
        self.output_path_entry = QLineEdit()
        output_path_layout.addWidget(self.output_path_entry)
        
        self.browse_btn = QPushButton("浏览")
        self.default_path_btn = QPushButton("默认")
        output_path_layout.addWidget(self.browse_btn)
        output_path_layout.addWidget(self.default_path_btn)
        
        input_layout.addRow("输出路径:", output_path_layout)
        
        # 输入验证提示
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: red;")
        input_layout.addRow("", self.validation_label)
        
        main_layout.addWidget(input_group)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setProperty("class", "primary-button")
        
        self.preview_btn = QPushButton("预览结果")
        self.preview_btn.setEnabled(False)
        
        self.settings_btn = QPushButton("设置")
        
        control_layout.addWidget(self.convert_btn)
        control_layout.addWidget(self.preview_btn)
        control_layout.addWidget(self.settings_btn)
        control_layout.addStretch()
        
        main_layout.addLayout(control_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # 状态显示区域
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(300)
        status_layout.addWidget(self.status_text)
        
        main_layout.addWidget(status_group)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        
        self.clear_log_btn = QPushButton("清空日志")
        self.about_btn = QPushButton("关于")
        
        bottom_layout.addWidget(self.clear_log_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.about_btn)
        
        main_layout.addLayout(bottom_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            
            QGroupBox {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
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
            
            QPushButton[class="primary-button"] {
                background-color: #2F54EB;
                color: white;
                border: 1px solid #2F54EB;
            }
            
            QPushButton[class="primary-button"]:hover {
                background-color: #4056D1;
            }
            
            QPushButton[class="primary-button"]:pressed {
                background-color: #3448C7;
            }
            
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #999999;
                border: 1px solid #d9d9d9;
            }
            
            QLineEdit {
                padding: 5px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
            }
            
            QTextEdit {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 5px;
            }
            
            QProgressBar {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #2F54EB;
            }
        """)
        
        # 初始化输出路径为默认值
        self.use_default_path()
    
    def setup_connections(self):
        """设置信号槽连接"""
        # 按钮点击事件
        self.convert_btn.clicked.connect(self.start_conversion)
        self.preview_btn.clicked.connect(self.show_preview)
        self.settings_btn.clicked.connect(self.show_settings)
        self.browse_btn.clicked.connect(self.browse_output_path)
        self.default_path_btn.clicked.connect(self.use_default_path)
        self.clear_log_btn.clicked.connect(self.clear_status_log)
        self.about_btn.clicked.connect(self.show_about)
        
        # 输入验证
        self.token_entry.textChanged.connect(self.validate_inputs)
        self.doc_id_entry.textChanged.connect(self.validate_inputs)
        
        # 显示/隐藏token
        self.show_token_checkbox.toggled.connect(self.toggle_token_visibility)
        
        # 内部信号连接
        self.progress_updated.connect(self.on_update_progress)
        self.conversion_complete.connect(self.on_conversion_complete)
        self.status_logged.connect(self.on_log_status)
    
    def toggle_token_visibility(self, checked: bool):
        """切换token显示/隐藏"""
        if checked:
            self.token_entry.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.token_entry.setEchoMode(QLineEdit.EchoMode.Password)
    
    def validate_inputs(self):
        """验证输入"""
        token = self.token_entry.text().strip()
        doc_id = self.doc_id_entry.text().strip()
        
        # 清空之前的验证信息
        self.validation_label.setText("")
        
        # 验证token
        if token and not token.startswith('u-'):
            self.validation_label.setText("Token格式错误，应以'u-'开头")
            self.convert_btn.setEnabled(False)
            return
        
        # 验证document_id
        if doc_id and len(doc_id) < 10:
            self.validation_label.setText("Document ID格式错误，长度过短")
            self.convert_btn.setEnabled(False)
            return
        
        # 检查是否都已填写
        if token and doc_id:
            self.convert_btn.setEnabled(True)
        else:
            self.convert_btn.setEnabled(False)
    
    def start_conversion(self):
        """开始转换"""
        if self.is_converting:
            return
        
        token = self.token_entry.text().strip()
        doc_id = self.doc_id_entry.text().strip()
        
        if not token or not doc_id:
            QMessageBox.warning(self, "错误", "请填写完整的Token和Document ID")
            return
        
        # 禁用转换按钮
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText("转换中...")
        self.is_converting = True
        
        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 发射信号
        self.conversion_started.emit(token, doc_id)
    
    @pyqtSlot(bool, str)
    def on_conversion_complete(self, success: bool, message: str = ""):
        """转换完成槽函数"""
        self.is_converting = False
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText("开始转换")
        
        if success:
            self.progress_bar.setValue(100)
            self.preview_btn.setEnabled(True)
            self.log_status(f"转换成功: {message}", "success")
            QMessageBox.information(self, "成功", "文档转换完成！")
        else:
            self.progress_bar.setValue(0)
            self.log_status(f"转换失败: {message}", "error")
            QMessageBox.critical(self, "错误", f"转换失败: {message}")
    
    @pyqtSlot(float, str)
    def on_update_progress(self, value: float, message: str = ""):
        """更新进度槽函数"""
        self.progress_bar.setValue(int(value))
        if message:
            self.log_status(message)
    
    @pyqtSlot(str, str)
    def on_log_status(self, message: str, level: str = "info"):
        """状态日志槽函数"""
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
        self.status_text.append(f'<span style="color:{color}">[{timestamp}] {message}</span>')
        
        # 滚动到底部
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def show_preview(self):
        """显示预览"""
        self.preview_requested.emit()
    
    def show_settings(self):
        """显示设置"""
        self.settings_requested.emit()
    
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
        
        QMessageBox.about(self, "关于", about_text)
    
    def log_status(self, message: str, level: str = "info"):
        """记录状态日志
        
        Args:
            message: 日志消息
            level: 日志级别 (info, success, warning, error)
        """
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
        self.status_text.append(f'<span style="color:{color}">[{timestamp}] {message}</span>')
        
        # 滚动到底部
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_status_log(self):
        """清空状态日志"""
        self.status_text.clear()
        self.log_status("日志已清空")
    
    def get_token(self) -> str:
        """获取当前输入的token"""
        return self.token_entry.text().strip()
    
    def get_document_id(self) -> str:
        """获取当前输入的document_id"""
        return self.doc_id_entry.text().strip()
    
    def set_token(self, token: str):
        """设置token"""
        self.token_entry.setText(token)
    
    def set_document_id(self, doc_id: str):
        """设置document_id"""
        self.doc_id_entry.setText(doc_id)
    
    def browse_output_path(self):
        """浏览输出路径"""
        # 获取当前路径作为初始目录
        current_path = self.output_path_entry.text().strip()
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
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择输出文件路径",
            initial_dir + "/" + initial_file if initial_file else initial_dir,
            "Markdown文件 (*.md);;文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            self.output_path_entry.setText(file_path)
            self.log_status(f"已选择输出路径: {file_path}")
    
    def use_default_path(self):
        """使用默认输出路径"""
        from pathlib import Path
        default_dir = Path.home() / "Documents" / "Feishu2MD" / "output"
        self.output_path_entry.setText(str(default_dir))
        self.log_status(f"已设置为默认输出路径: {default_dir}")
    
    def get_output_path(self) -> str:
        """获取当前设置的输出路径"""
        return self.output_path_entry.text().strip()
    
    def set_output_path(self, path: str):
        """设置输出路径"""
        self.output_path_entry.setText(path)
