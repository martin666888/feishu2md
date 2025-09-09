#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书文档转Markdown工具 - 主程序入口

这是一个用于将飞书文档转换为Markdown格式的工具。

使用方法:
    python main.py

功能特性:
    - 支持飞书文档的各种块类型转换
    - 提供图形化用户界面
    - 支持预览和文件管理
    - 自动保存和备份功能

作者: 飞书文档转Markdown工具
版本: 1.0.0
"""

import sys
import os
import traceback
from pathlib import Path

# 在导入任何可能触发该警告的第三方库之前，屏蔽 pkg_resources 弃用警告
import warnings
warnings.filterwarnings(
    "ignore",
    message=r".*pkg_resources is deprecated as an API.*",
    category=UserWarning,
)

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
except ImportError:
    print("错误: 无法导入PyQt6模块")
    print("请确保PyQt6已正确安装")
    sys.exit(1)

try:
    from src.app_controller import AppController
except ImportError as e:
    print(f"错误: 无法导入应用程序模块: {e}")
    print("请确保所有依赖包已正确安装")
    sys.exit(1)


def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = [
        ('lark_oapi', 'lark-oapi'),
        ('requests', 'requests'),
        ('PyQt6', 'PyQt6')
    ]
    
    missing_packages = []
    
    for package_name, pip_name in required_packages:
        try:
            __import__(package_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        error_msg = f"""缺少以下依赖包:
{', '.join(missing_packages)}

请运行以下命令安装:
pip install {' '.join(missing_packages)}

或者使用uv安装:
uv add {' '.join(missing_packages)}"""
        
        print(error_msg)
        
        # 如果PyQt6可用，显示图形化错误消息
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "依赖包缺失", error_msg)
        except:
            pass
        
        return False
    
    return True


def setup_environment():
    """设置运行环境"""
    # 设置工作目录为项目根目录
    os.chdir(project_root)
    
    # 创建必要的目录
    directories = [
        'output',
        'temp',
        'backups'
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)


def main():
    """主函数"""
    app_controller = None
    
    try:
        print("飞书文档转Markdown工具 v1.0.0")
        print("正在启动...")
        
        # 检查依赖包
        if not check_dependencies():
            return 1
        
        # 设置环境
        setup_environment()
        
        # 创建并运行应用程序
        app_controller = AppController()
        
        print("应用程序启动成功")
        print("请在GUI界面中进行操作")
        
        # 运行应用程序
        exit_code = app_controller.run()
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
        return 0
        
    except Exception as e:
        error_msg = f"程序运行出错: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        
        # 尝试显示图形化错误消息
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "程序错误", error_msg)
        except:
            pass
        
        return 1
    
    finally:
        # 确保应用程序正确关闭
        if app_controller:
            try:
                app_controller.shutdown()
            except:
                pass


if __name__ == "__main__":
    # 设置异常处理
    sys.excepthook = lambda exc_type, exc_value, exc_traceback: (
        traceback.print_exception(exc_type, exc_value, exc_traceback),
        input("按Enter键退出...") if sys.stdin.isatty() else None
    )
    
    # 运行主程序
    exit_code = main()
    sys.exit(exit_code)
