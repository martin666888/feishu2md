"""应用程序控制器 - PyQt6版本"""
import sys
import threading
import traceback
import os
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtGui import QIcon

from src.api.feishu_client import FeishuAPIClient
from src.converter.markdown_converter import MarkdownConverter
from src.gui.main_window import MainWindow
from src.gui.preview_window import PreviewWindow
from src.gui.settings_window import SettingsWindow
from src.utils.file_manager import FileManager

# 在打包(onefile)与开发环境中均可用的资源路径解析函数
from pathlib import Path

def resource_path(relative_path: str) -> str:
    """获取资源文件的实际路径，兼容PyInstaller onefile和开发环境"""
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        # 项目根目录：当前文件位于 src/ 下，父级即为项目根
        base_path = Path(__file__).resolve().parent.parent
    return str(Path(base_path) / relative_path)


class AppController(QObject):
    """应用程序控制器类 - PyQt6版本"""
    
    def __init__(self):
        """初始化控制器"""
        super().__init__()
        
        # 初始化组件
        self.api_client: Optional[FeishuAPIClient] = None
        self.converter = MarkdownConverter()
        self.file_manager = FileManager()
        
        # 创建QApplication实例
        self.app = QApplication(sys.argv)
        
        # 设置全局应用图标（窗口会继承该图标）
        try:
            icon_path = resource_path("icon.ico")
            self.app.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass
        
        # GUI组件
        self.main_window = MainWindow()
        self.preview_window = PreviewWindow(self.main_window)
        self.settings_window = SettingsWindow(self.file_manager, self.main_window)
        
        # 确保各窗口也显式设置图标（在某些Windows环境下更稳妥）
        try:
            icon = self.app.windowIcon()
            self.main_window.setWindowIcon(icon)
            self.preview_window.setWindowIcon(icon)
            self.settings_window.setWindowIcon(icon)
        except Exception:
            pass
        
        # 注入“默认目录提供器”：读取设置中的 default_output_dir
        self.main_window.set_default_dir_provider(
            lambda: self.file_manager.get_settings().get('default_output_dir') or str(self.file_manager.output_dir)
        )
        # 立即用设置里的默认目录刷新主界面输出路径
        self.main_window.use_default_path()
        
        # 数据
        self.current_markdown = ""
        self.current_title = ""
        self.current_doc_id = ""
        
        # 设置信号槽连接
        self._setup_connections()
        
        # 应用设置
        self._apply_settings()
    
    def _setup_connections(self):
        """设置信号槽连接"""
        # 主窗口信号连接到控制器槽函数
        self.main_window.conversion_started.connect(self.handle_conversion_started)
        self.main_window.preview_requested.connect(self.handle_preview_requested)
        self.main_window.settings_requested.connect(self.handle_settings_requested)
    
    def _apply_settings(self):
        """应用设置"""
        # 从文件管理器获取设置
        settings = self.file_manager.get_settings()
        
        # 应用窗口设置（如果有的话）
        # 这里可以根据需要添加更多设置
        pass
    
    @pyqtSlot(str, str)
    def handle_conversion_started(self, token: str, doc_id: str):
        """处理转换开始信号
        
        Args:
            token: 用户访问令牌
            doc_id: 文档ID
        """
        # 在新线程中执行转换
        thread = threading.Thread(target=self._conversion_thread, args=(token, doc_id))
        thread.daemon = True
        thread.start()
    
    def _conversion_thread(self, token: str, doc_id: str):
        """转换线程"""
        try:
            self.current_doc_id = doc_id
            
            # 更新状态
            self._update_progress_gui(10, "初始化API客户端")
            
            # 初始化API客户端
            self.api_client = FeishuAPIClient(token)
            
            # 获取文档信息
            self._update_progress_gui(20, "获取文档信息")
            
            doc_info = self.api_client.get_document_info(doc_id)
            if not doc_info:
                raise Exception("无法获取文档信息，请检查Document ID是否正确")
            
            self.current_title = doc_info.get('title', f'Document_{doc_id[:8]}')
            self._update_status_gui(f"文档标题: {self.current_title}")
            
            # 获取文档块列表
            self._update_progress_gui(40, "获取文档块列表")
            
            response = self.api_client.get_document_blocks(doc_id)
            if not response or not response.get('data', {}).get('items'):
                raise Exception("文档为空或无法获取文档内容")
            
            blocks = response['data']['items']
            self._update_status_gui(f"获取到 {len(blocks)} 个文档块")
            
            # 转换为markdown
            self._update_progress_gui(60, "转换为Markdown")
            
            markdown_content = self.converter.convert_blocks_to_markdown(blocks)
            
            if not markdown_content.strip():
                raise Exception("转换结果为空，可能文档中没有支持的内容类型")
            
            self.current_markdown = markdown_content
            
            # 自动保存（如果启用）
            settings = self.file_manager.get_settings()
            if settings.get('auto_save', True):
                self._update_progress_gui(80, "保存文件")
                
                # 获取用户指定的输出路径
                output_path = self.main_window.get_output_path()
                
                success, result = self.file_manager.save_markdown(
                    self.current_markdown,
                    title=self.current_title,
                    doc_id=self.current_doc_id,
                    output_path=output_path if output_path else None
                )
                
                if success:
                    self._update_status_gui(f"文件已保存到: {result}")
                else:
                    self._update_status_gui(f"自动保存失败: {result}", "warning")
            
            # 完成
            self._update_progress_gui(100, "转换完成")
            self._update_conversion_complete_gui(True, f"成功转换文档: {self.current_title}")
            
        except Exception as e:
            error_msg = str(e)
            friendly_msg = self._format_friendly_error(error_msg)
            self._update_status_gui(friendly_msg, "error")
            self._update_conversion_complete_gui(False, friendly_msg)
            
            # 记录详细错误信息
            traceback.print_exc()

    def _format_friendly_error(self, error_msg: str) -> str:
        """将底层异常信息转化为更友好的提示文案"""
        msg_lower = error_msg.lower()
        # 飞书参数错误：99992402 或者包含中文提示
        if ("99992402" in error_msg) or ("请求参数缺失" in error_msg) or ("请求参数有误" in error_msg):
            return "document_id不对或请求参数有误（错误码 99992402），请检查输入的文档ID。"
        # 令牌过期：99991677 或相似英文提示
        if ("99991677" in error_msg) or ("authentication token expired" in msg_lower) or ("token expired" in msg_lower) or ("access token expired" in msg_lower):
            return "认证失败：用户访问令牌已过期（错误码 99991677），请重新获取或更新 User Access Token。"
        # 认证失败
        if ("401" in error_msg) or ("unauthorized" in msg_lower) or ("invalid token" in msg_lower):
            return "认证失败，请检查用户访问令牌（token）是否正确或已过期。"
        # 超时或网络问题
        if ("timeout" in msg_lower) or ("timed out" in msg_lower) or ("connection" in msg_lower and "error" in msg_lower):
            return "网络异常或超时，请检查网络后重试。"
        # 默认回退
        return f"转换失败: {error_msg}"
    
    def _update_progress_gui(self, value: float, message: str = ""):
        """线程安全的进度更新"""
        # 使用QMetaObject.invokeMethod或信号来安全更新GUI
        self.main_window.progress_updated.emit(value, message)
    
    def _update_status_gui(self, message: str, level: str = "info"):
        """线程安全的状态更新"""
        # 使用QMetaObject.invokeMethod或信号来安全更新GUI
        self.main_window.status_logged.emit(message, level)
    
    def _update_conversion_complete_gui(self, success: bool, message: str = ""):
        """线程安全的转换完成更新"""
        # 使用QMetaObject.invokeMethod或信号来安全更新GUI
        self.main_window.conversion_complete.emit(success, message)
    
    @pyqtSlot()
    def handle_preview_requested(self):
        """处理预览请求信号"""
        if not self.current_markdown:
            QMessageBox.warning(self.main_window, "警告", "没有可预览的内容，请先进行转换")
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
            
            self._update_status_gui("预览窗口已打开")
            
        except Exception as e:
            error_msg = f"打开预览失败: {str(e)}"
            self._update_status_gui(error_msg, "error")
            QMessageBox.critical(self.main_window, "错误", error_msg)
    
    @pyqtSlot()
    def handle_settings_requested(self):
        """处理设置请求信号"""
        try:
            self.settings_window.show()
        except Exception as e:
            error_msg = f"打开设置失败: {str(e)}"
            self._update_status_gui(error_msg, "error")
            QMessageBox.critical(self.main_window, "错误", error_msg)
    
    def run(self):
        """运行应用程序"""
        try:
            # 清理临时文件
            self.file_manager.cleanup_temp_files()
            
            # 显示主窗口
            self.main_window.show()
            
            # 启动GUI
            self._update_status_gui("应用程序启动完成")
            
            # 运行应用程序事件循环
            return self.app.exec()
            
        except Exception as e:
            QMessageBox.critical(None, "严重错误", f"应用程序运行失败: {str(e)}")
            traceback.print_exc()
            return 1
    
    def shutdown(self):
        """关闭应用程序"""
        try:
            # 清理资源
            if self.preview_window.is_open():
                self.preview_window.close()
            
            if self.settings_window.isVisible():
                self.settings_window.close()
            
            # 保存设置
            self.file_manager._save_settings()
            
            # 关闭应用程序
            self.app.quit()
            
        except Exception as e:
            print(f"关闭应用程序时出错: {e}")
