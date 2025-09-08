"""设置窗口模块 - PyQt6版本"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, 
                            QPushButton, QLabel, QLineEdit, QSpinBox, 
                            QComboBox, QTabWidget, QCheckBox, QFileDialog,
                            QMessageBox, QFormLayout, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt
import os
from typing import Optional, Dict, Any


class SettingsWindow(QDialog):
    """设置窗口类 - PyQt6版本"""
    
    def __init__(self, file_manager, parent=None):
        """初始化设置窗口
        
        Args:
            file_manager: 文件管理器
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.file_manager = file_manager
        
        # 设置变量
        self.settings = self.file_manager.get_settings()
        self.vars = {}
        
        # 设置窗口属性
        self.setup_window()
        
        # 初始化UI
        self.init_ui()
        
        # 设置连接
        self.setup_connections()
        
        # 加载当前设置
        self.load_settings()
    
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("设置")
        self.setGeometry(200, 200, 500, 400)
        
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
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建Notebook
        self.tab_widget = QTabWidget()
        
        # 常规设置页面
        self.general_tab = QWidget()
        general_layout = QVBoxLayout(self.general_tab)
        general_layout.setContentsMargins(10, 10, 10, 10)
        
        # 自动保存设置
        self.vars['auto_save'] = QCheckBox("启用自动保存")
        general_layout.addWidget(self.vars['auto_save'])
        
        # 备份设置
        self.vars['backup_enabled'] = QCheckBox("启用文件备份")
        general_layout.addWidget(self.vars['backup_enabled'])
        
        # 默认输出目录
        dir_group = QGroupBox("默认输出目录")
        dir_layout = QHBoxLayout(dir_group)
        
        self.vars['default_output_dir'] = QLineEdit()
        dir_layout.addWidget(self.vars['default_output_dir'])
        
        self.browse_dir_btn = QPushButton("浏览")
        dir_layout.addWidget(self.browse_dir_btn)
        
        general_layout.addWidget(dir_group)
        
        # 文件命名设置
        naming_group = QGroupBox("文件命名模式")
        naming_layout = QVBoxLayout(naming_group)
        
        self.vars['file_naming_pattern'] = QLineEdit()
        naming_layout.addWidget(self.vars['file_naming_pattern'])
        
        pattern_hint = QLabel("可用变量: {title}, {timestamp}, {doc_id}")
        pattern_hint.setStyleSheet("color: gray;")
        naming_layout.addWidget(pattern_hint)
        
        general_layout.addWidget(naming_group)
        general_layout.addStretch()
        
        self.tab_widget.addTab(self.general_tab, "常规")
        
        # 高级设置页面
        self.advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(self.advanced_tab)
        advanced_layout.setContentsMargins(10, 10, 10, 10)
        
        # 历史记录数量
        history_group = QGroupBox("历史记录")
        history_form = QFormLayout(history_group)
        
        self.vars['max_history_items'] = QSpinBox()
        self.vars['max_history_items'].setRange(10, 1000)
        history_form.addRow("最大历史记录数量:", self.vars['max_history_items'])
        
        advanced_layout.addWidget(history_group)
        
        # 编码设置
        encoding_group = QGroupBox("文件设置")
        encoding_form = QFormLayout(encoding_group)
        
        self.vars['default_encoding'] = QComboBox()
        self.vars['default_encoding'].addItems(['utf-8', 'gbk', 'ascii'])
        encoding_form.addRow("默认文件编码:", self.vars['default_encoding'])
        
        advanced_layout.addWidget(encoding_group)
        
        # 存储信息
        storage_group = QGroupBox("存储信息")
        storage_layout = QVBoxLayout(storage_group)
        
        storage_info = self.file_manager.get_storage_info()
        if 'error' not in storage_info:
            info_text = f"""基础目录: {storage_info['base_dir']}
输出目录: {storage_info['output_dir']}
文件总数: {storage_info['total_files']}
总大小: {storage_info['total_size_mb']} MB"""
            
            self.storage_info_label = QLabel(info_text)
            self.storage_info_label.setStyleSheet("color: gray;")
            self.storage_info_label.setWordWrap(True)
            storage_layout.addWidget(self.storage_info_label)
        else:
            self.storage_info_label = QLabel("无法获取存储信息")
            self.storage_info_label.setStyleSheet("color: red;")
            storage_layout.addWidget(self.storage_info_label)
        
        advanced_layout.addWidget(storage_group)
        advanced_layout.addStretch()
        
        self.tab_widget.addTab(self.advanced_tab, "高级")
        
        main_layout.addWidget(self.tab_widget)
        
        # 按钮框架
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("保存")
        self.reset_btn = QPushButton("重置")
        self.cancel_btn = QPushButton("取消")
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
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
            
            QLineEdit, QComboBox, QSpinBox {
                padding: 5px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
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
        """)
    
    def setup_connections(self):
        """设置信号槽连接"""
        # 按钮点击事件
        self.save_btn.clicked.connect(self.save_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
        self.cancel_btn.clicked.connect(self.close)
        self.browse_dir_btn.clicked.connect(self.browse_directory)
    
    def load_settings(self):
        """加载当前设置"""
        # 自动保存
        self.vars['auto_save'].setChecked(self.settings.get('auto_save', True))
        
        # 备份设置
        self.vars['backup_enabled'].setChecked(self.settings.get('backup_enabled', True))
        
        # 默认输出目录
        self.vars['default_output_dir'].setText(self.settings.get('default_output_dir', ''))
        
        # 文件命名模式
        self.vars['file_naming_pattern'].setText(self.settings.get('file_naming_pattern', '{title}_{timestamp}'))
        
        # 历史记录数量
        self.vars['max_history_items'].setValue(self.settings.get('max_history_items', 100))
        
        # 默认编码
        encoding = self.settings.get('default_encoding', 'utf-8')
        index = self.vars['default_encoding'].findText(encoding)
        if index >= 0:
            self.vars['default_encoding'].setCurrentIndex(index)
    
    def save_settings(self):
        """保存设置"""
        try:
            # 收集设置
            new_settings = {}
            
            # 自动保存
            new_settings['auto_save'] = self.vars['auto_save'].isChecked()
            
            # 备份设置
            new_settings['backup_enabled'] = self.vars['backup_enabled'].isChecked()
            
            # 默认输出目录
            new_settings['default_output_dir'] = self.vars['default_output_dir'].text().strip()
            
            # 文件命名模式
            new_settings['file_naming_pattern'] = self.vars['file_naming_pattern'].text().strip()
            
            # 历史记录数量
            new_settings['max_history_items'] = self.vars['max_history_items'].value()
            
            # 默认编码
            new_settings['default_encoding'] = self.vars['default_encoding'].currentText()
            
            # 更新设置
            self.file_manager.update_settings(new_settings)
            
            QMessageBox.information(self, "成功", "设置已保存")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
    
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self, 
            "确认", 
            "确定要重置所有设置吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 重置为默认值
            default_settings = {
                'auto_save': True,
                'backup_enabled': True,
                'default_output_dir': str(self.file_manager.output_dir),
                'file_naming_pattern': '{title}_{timestamp}',
                'max_history_items': 100,
                'default_encoding': 'utf-8'
            }
            
            # 应用默认设置
            self.vars['auto_save'].setChecked(default_settings['auto_save'])
            self.vars['backup_enabled'].setChecked(default_settings['backup_enabled'])
            self.vars['default_output_dir'].setText(default_settings['default_output_dir'])
            self.vars['file_naming_pattern'].setText(default_settings['file_naming_pattern'])
            self.vars['max_history_items'].setValue(default_settings['max_history_items'])
            
            encoding = default_settings['default_encoding']
            index = self.vars['default_encoding'].findText(encoding)
            if index >= 0:
                self.vars['default_encoding'].setCurrentIndex(index)
    
    def browse_directory(self):
        """浏览目录"""
        current_dir = self.vars['default_output_dir'].text().strip()
        if not current_dir or not os.path.exists(current_dir):
            current_dir = os.path.expanduser("~")
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择默认输出目录",
            current_dir
        )
        
        if directory:
            self.vars['default_output_dir'].setText(directory)
    
    def show(self):
        """显示设置窗口"""
        # 重新加载设置
        self.settings = self.file_manager.get_settings()
        self.load_settings()
        
        # 更新存储信息
        storage_info = self.file_manager.get_storage_info()
        if 'error' not in storage_info:
            info_text = f"""基础目录: {storage_info['base_dir']}
输出目录: {storage_info['output_dir']}
文件总数: {storage_info['total_files']}
总大小: {storage_info['total_size_mb']} MB"""
            self.storage_info_label.setText(info_text)
            self.storage_info_label.setStyleSheet("color: gray;")
        else:
            self.storage_info_label.setText("无法获取存储信息")
            self.storage_info_label.setStyleSheet("color: red;")
        
        # 显示窗口
        super().show()
        
        # 激活窗口
        self.raise_()
        self.activateWindow()
