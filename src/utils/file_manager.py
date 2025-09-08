"""文件管理模块"""
import os
import json
import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class FileManager:
    """文件管理器类"""
    
    def __init__(self, base_dir: str = None):
        """初始化文件管理器
        
        Args:
            base_dir: 基础目录，默认为用户文档目录下的feishu2md文件夹
        """
        if base_dir is None:
            # 默认保存到用户文档目录
            home_dir = Path.home()
            self.base_dir = home_dir / "Documents" / "Feishu2MD"
        else:
            self.base_dir = Path(base_dir)
        
        # 确保目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 子目录
        self.output_dir = self.base_dir / "output"
        self.temp_dir = self.base_dir / "temp"
        self.config_dir = self.base_dir / "config"
        
        # 创建子目录
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        # 配置文件路径
        self.config_file = self.config_dir / "settings.json"
        self.history_file = self.config_dir / "history.json"
        
        # 加载配置
        self.settings = self._load_settings()
        self.history = self._load_history()
    
    def _load_settings(self) -> Dict:
        """加载设置"""
        default_settings = {
            "default_output_dir": str(self.output_dir),
            "auto_save": True,
            "backup_enabled": True,
            "max_history_items": 100,
            "file_naming_pattern": "{title}_{timestamp}",
            "default_encoding": "utf-8"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # 合并默认设置
                default_settings.update(settings)
                return default_settings
            except Exception as e:
                print(f"加载设置失败: {e}，使用默认设置")
        
        return default_settings
    
    def _save_settings(self):
        """保存设置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def _load_history(self) -> List[Dict]:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载历史记录失败: {e}")
        
        return []
    
    def _save_history(self):
        """保存历史记录"""
        try:
            # 限制历史记录数量
            max_items = self.settings.get("max_history_items", 100)
            if len(self.history) > max_items:
                self.history = self.history[-max_items:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def generate_filename(self, title: str = "", doc_id: str = "", 
                         extension: str = ".md") -> str:
        """生成文件名
        
        Args:
            title: 文档标题
            doc_id: 文档ID
            extension: 文件扩展名
            
        Returns:
            生成的文件名
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 清理标题，移除不合法的文件名字符
        if title:
            clean_title = self._clean_filename(title)
        else:
            clean_title = "document"
        
        # 根据命名模式生成文件名
        pattern = self.settings.get("file_naming_pattern", "{title}_{timestamp}")
        
        filename = pattern.format(
            title=clean_title,
            timestamp=timestamp,
            doc_id=doc_id[:8] if doc_id else "unknown"
        )
        
        return filename + extension
    
    def _clean_filename(self, filename: str) -> str:
        """清理文件名，移除不合法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # Windows不允许的字符
        invalid_chars = '<>:"/\\|?*'
        
        cleaned = filename
        for char in invalid_chars:
            cleaned = cleaned.replace(char, '_')
        
        # 移除多余的空格和点
        cleaned = cleaned.strip('. ')
        
        # 限制长度
        if len(cleaned) > 100:
            cleaned = cleaned[:100]
        
        return cleaned or "document"
    
    def save_markdown(self, content: str, filename: str = None, 
                     title: str = "", doc_id: str = "", 
                     output_path: str = None) -> Tuple[bool, str]:
        """保存markdown文件
        
        Args:
            content: markdown内容
            filename: 文件名（可选）
            title: 文档标题
            doc_id: 文档ID
            output_path: 输出路径（可以是目录或完整文件路径）
            
        Returns:
            (成功标志, 文件路径或错误信息)
        """
        try:
            # 处理输出路径
            if output_path:
                output_path_obj = Path(output_path)
                
                # 判断是目录还是文件路径
                if output_path.endswith(('.md', '.txt')) or '.' in output_path_obj.name:
                    # 是完整文件路径
                    save_dir = output_path_obj.parent
                    filename = output_path_obj.name
                else:
                    # 是目录路径
                    save_dir = output_path_obj
                    if not filename:
                        filename = self.generate_filename(title, doc_id)
            else:
                # 使用默认目录
                save_dir = Path(self.settings.get("default_output_dir", self.output_dir))
                if not filename:
                    filename = self.generate_filename(title, doc_id)
            
            # 确保目录存在
            save_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = save_dir / filename
            
            # 如果文件已存在，生成新的文件名
            counter = 1
            original_path = file_path
            while file_path.exists():
                name_part = original_path.stem
                ext_part = original_path.suffix
                file_path = save_dir / f"{name_part}_{counter}{ext_part}"
                counter += 1
            
            # 保存文件
            encoding = self.settings.get("default_encoding", "utf-8")
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # 创建备份（如果启用）
            if self.settings.get("backup_enabled", True):
                self._create_backup(file_path, content)
            
            # 添加到历史记录
            self._add_to_history({
                "file_path": str(file_path),
                "title": title,
                "doc_id": doc_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "file_size": len(content.encode(encoding))
            })
            
            return True, str(file_path)
            
        except Exception as e:
            return False, f"保存文件失败: {str(e)}"
    
    def _create_backup(self, file_path: Path, content: str):
        """创建备份文件
        
        Args:
            file_path: 原文件路径
            content: 文件内容
        """
        try:
            backup_dir = self.base_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_filename
            
            encoding = self.settings.get("default_encoding", "utf-8")
            with open(backup_path, 'w', encoding=encoding) as f:
                f.write(content)
                
        except Exception as e:
            print(f"创建备份失败: {e}")
    
    def _add_to_history(self, record: Dict):
        """添加到历史记录
        
        Args:
            record: 历史记录项
        """
        self.history.append(record)
        self._save_history()
    
    def get_history(self, limit: int = None) -> List[Dict]:
        """获取历史记录
        
        Args:
            limit: 限制返回数量
            
        Returns:
            历史记录列表
        """
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self._save_history()
    
    def get_recent_files(self, limit: int = 10) -> List[Dict]:
        """获取最近的文件
        
        Args:
            limit: 限制返回数量
            
        Returns:
            最近文件列表
        """
        recent = []
        for record in reversed(self.history[-limit:]):
            file_path = record.get("file_path")
            if file_path and os.path.exists(file_path):
                recent.append(record)
        
        return recent
    
    def delete_file(self, file_path: str) -> Tuple[bool, str]:
        """删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            (成功标志, 错误信息)
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                
                # 从历史记录中移除
                self.history = [h for h in self.history if h.get("file_path") != file_path]
                self._save_history()
                
                return True, "文件删除成功"
            else:
                return False, "文件不存在"
                
        except Exception as e:
            return False, f"删除文件失败: {str(e)}"
    
    def read_file(self, file_path: str) -> Tuple[bool, str]:
        """读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            (成功标志, 文件内容或错误信息)
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False, "文件不存在"
            
            encoding = self.settings.get("default_encoding", "utf-8")
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return True, content
            
        except Exception as e:
            return False, f"读取文件失败: {str(e)}"
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": path.suffix,
                "full_path": str(path.absolute())
            }
            
        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    # 删除超过1天的临时文件
                    if (datetime.datetime.now().timestamp() - file_path.stat().st_mtime) > 86400:
                        file_path.unlink()
        except Exception as e:
            print(f"清理临时文件失败: {e}")
    
    def get_settings(self) -> Dict:
        """获取设置"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict):
        """更新设置
        
        Args:
            new_settings: 新的设置
        """
        self.settings.update(new_settings)
        self._save_settings()
    
    def get_storage_info(self) -> Dict:
        """获取存储信息"""
        try:
            total_files = len(list(self.output_dir.glob("**/*")))
            total_size = sum(f.stat().st_size for f in self.output_dir.glob("**/*") if f.is_file())
            
            return {
                "base_dir": str(self.base_dir),
                "output_dir": str(self.output_dir),
                "total_files": total_files,
                "total_size": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2)
            }
        except Exception as e:
            return {"error": str(e)}