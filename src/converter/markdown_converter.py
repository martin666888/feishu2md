"""Markdown转换器模块

本模块提供了将飞书文档块结构转换为标准Markdown格式的功能。
支持多种块类型的转换，包括文本、标题、列表、代码块、表格等。
"""
import re
from enum import IntEnum
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
import logging


class BlockType(IntEnum):
    """飞书文档块类型枚举
    
    定义了飞书文档中所有支持的块类型常量。
    使用IntEnum确保类型安全性和向后兼容性。
    """
    PAGE = 1
    TEXT = 2
    HEADING1 = 3
    HEADING2 = 4
    HEADING3 = 5
    HEADING4 = 6
    HEADING5 = 7
    HEADING6 = 8
    HEADING7 = 9
    HEADING8 = 10
    HEADING9 = 11
    BULLET = 12
    ORDERED = 13
    CODE = 14
    QUOTE = 15
    EQUATION = 16
    TODO = 17
    BITABLE = 18
    CALLOUT = 19
    CHAT_CARD = 20
    DIAGRAM = 21
    DIVIDER = 22
    FILE = 23
    GRID = 24
    GRID_COLUMN = 25
    IFRAME = 26
    IMAGE = 27
    ISV = 28
    MINDNOTE = 29
    SHEET = 30
    TABLE = 31
    TABLE_CELL = 32
    VIEW = 33
    QUOTE_CONTAINER = 34
    TASK = 35
    OKR = 36
    OKR_OBJECTIVE = 37
    OKR_KEY_RESULT = 38
    OKR_PROGRESS = 39
    ADD_ONS = 40
    JIRA_ISSUE = 41
    WIKI_CATALOG = 42
    BOARD = 43
    AGENDA = 44
    UNDEFINED = 999


# 类型别名定义
BlockData = Dict[str, Any]
BlockList = List[BlockData]
BlockMap = Dict[str, BlockData]
ConverterFunction = Callable[[BlockData], str]
ElementData = Dict[str, Any]
ElementList = List[ElementData]


class MarkdownConverter:
    """Markdown转换器
    
    负责将飞书文档块结构转换为标准Markdown格式。
    支持文本、标题、列表、代码块、表格等多种块类型的转换。
    
    Features:
        - 支持多种块类型转换
        - 智能段落分隔处理
        - 嵌套结构支持
        - 错误处理和日志记录
        - 可配置的转换选项
    
    Example:
        >>> converter = MarkdownConverter()
        >>> markdown_text = converter.convert_blocks_to_markdown(blocks)
    """
    
    # 类级别常量
    DEFAULT_INDENT: str = "    "  # 默认缩进
    MAX_MARKDOWN_HEADING_LEVEL: int = 6  # Markdown最大标题级别
    MAX_TABLE_ROWS: int = 1000  # 表格最大行数
    MAX_TABLE_COLS: int = 50   # 表格最大列数
    
    # 代码语言映射
    CODE_LANGUAGE_MAP: Dict[int, str] = {
        1: 'plaintext',
        2: 'python',
        3: 'javascript',
        4: 'java',
        5: 'cpp',
        6: 'c',
        7: 'csharp',
        8: 'php',
        9: 'ruby',
        10: 'go',
        11: 'rust',
        12: 'swift',
        13: 'kotlin',
        14: 'typescript',
        15: 'html',
        16: 'css',
        17: 'sql',
        18: 'shell',
        19: 'bash',
        20: 'powershell',
        21: 'json',
        22: 'xml',
        23: 'yaml',
        24: 'markdown'
    }
    
    # 标题级别映射
    HEADING_LEVELS: Dict[BlockType, int] = {
        BlockType.HEADING1: 1,
        BlockType.HEADING2: 2,
        BlockType.HEADING3: 3,
        BlockType.HEADING4: 4,
        BlockType.HEADING5: 5,
        BlockType.HEADING6: 6
    }
    
    # 需要段落分隔的块类型
    PARAGRAPH_BLOCK_TYPES: Set[BlockType] = {
        BlockType.TEXT, BlockType.CODE, BlockType.QUOTE, BlockType.EQUATION,
        BlockType.HEADING1, BlockType.HEADING2, BlockType.HEADING3, 
        BlockType.HEADING4, BlockType.HEADING5, BlockType.HEADING6,
        BlockType.TABLE
    }
    
    def __init__(self) -> None:
        """初始化转换器
        
        设置日志记录器、初始化状态变量，并构建块转换器映射。
        """
        # 初始化状态
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._reset_state()
        
        # 块转换器映射 - 使用策略模式
        self._block_converters: Dict[int, Callable] = self._build_converter_mapping()
    
    def _reset_state(self) -> None:
        """重置转换器状态
        
        清除所有临时状态变量，为新的转换任务做准备。
        """
        self.list_nesting_level: int = 0  # 列表嵌套层级
    
    def _build_converter_mapping(self) -> Dict[int, Callable]:
        """构建块类型到转换器方法的映射
        
        Returns:
            块类型ID到转换器方法的映射字典
        """
        return {
            BlockType.PAGE: self._convert_page_block,
            BlockType.TEXT: self._convert_text_block,
            BlockType.HEADING1: self._convert_heading_block,
            BlockType.HEADING2: self._convert_heading_block,
            BlockType.HEADING3: self._convert_heading_block,
            BlockType.HEADING4: self._convert_heading_block,
            BlockType.HEADING5: self._convert_heading_block,
            BlockType.HEADING6: self._convert_heading_block,
            BlockType.BULLET: self._convert_bullet_block,
            BlockType.ORDERED: self._convert_ordered_block,
            BlockType.CODE: self._convert_code_block,
            BlockType.QUOTE: self._convert_quote_block,
            BlockType.TODO: self._convert_todo_block,
            BlockType.DIVIDER: self._convert_divider_block,
            BlockType.IMAGE: self._convert_image_block,
            BlockType.TABLE: self._convert_table_block,
            BlockType.TABLE_CELL: self._convert_table_cell_block,
            BlockType.EQUATION: self._convert_equation_block
        }
    
    def convert_blocks_to_markdown(self, blocks: BlockList) -> str:
        """将飞书文档块转换为Markdown格式
        
        这是转换器的主要入口方法，负责协调整个转换过程。
        
        Args:
            blocks: 飞书文档块列表，每个块包含类型、内容和层级信息
            
        Returns:
            转换后的Markdown文本字符串
            
        Raises:
            ValueError: 当输入数据无效时（如空值、格式错误等）
            TypeError: 当输入类型错误时（如非列表类型）
            
        Example:
            >>> converter = MarkdownConverter()
            >>> blocks = [{'block_type': 2, 'text': {'elements': [...]}}]
            >>> markdown = converter.convert_blocks_to_markdown(blocks)
        """
        # 重置状态
        self._reset_state()
        
        try:
            # 输入验证
            validated_blocks = self._validate_blocks(blocks)
            if not validated_blocks:
                self.logger.warning("没有有效的块数据可转换")
                return ''
            
            self.logger.info(f"开始转换 {len(validated_blocks)} 个块")
            
            # 构建块层级结构
            block_map, root_blocks = self._build_block_hierarchy(validated_blocks)
            
            # 转换根级块
            converted_blocks = self._convert_root_blocks(root_blocks, block_map)
            
            # 合并转换结果
            result = self._merge_converted_blocks(converted_blocks, root_blocks)
            
            # 清理输出
            cleaned_result = self._clean_markdown_output(result)
            
            # 记录统计信息
            self._log_conversion_stats(validated_blocks, cleaned_result)
            
            return cleaned_result
            
        except Exception as e:
            self.logger.error(f"转换过程中发生错误: {e}")
            # 在出错时也要重置状态
            self._reset_state()
            raise
    
    def _validate_blocks(self, blocks: Any) -> BlockList:
        """验证输入的块数据
        
        对输入数据进行类型检查和格式验证，确保数据的完整性和正确性。
        
        Args:
            blocks: 待验证的块数据，应为包含字典的列表
            
        Returns:
            验证后的有效块列表
            
        Raises:
            TypeError: 当输入类型不正确时
            ValueError: 当输入数据无效时（如为None）
        """
        if blocks is None:
            raise ValueError("块数据不能为None")
        
        if not isinstance(blocks, list):
            raise TypeError(f"块数据必须是列表类型，实际类型: {type(blocks).__name__}")
        
        if not blocks:
            self.logger.warning("输入的块列表为空")
            return []
        
        validated_blocks: BlockList = []
        invalid_count: int = 0
        
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                self.logger.warning(f"第 {i} 个块不是字典类型: {type(block).__name__}")
                invalid_count += 1
                continue
            
            # 检查必要字段
            if 'block_type' not in block:
                self.logger.warning(f"第 {i} 个块缺少 block_type 字段")
                invalid_count += 1
                continue
            
            block_type = block['block_type']
            if not self._validate_block_type(block_type):
                self.logger.warning(f"第 {i} 个块的类型无效: {block_type}")
                invalid_count += 1
                continue
            
            validated_blocks.append(block)
        
        if invalid_count > 0:
            self.logger.warning(f"跳过了 {invalid_count} 个无效块")
        
        self.logger.debug(f"验证完成，有效块数: {len(validated_blocks)}")
        return validated_blocks
    
    def _build_block_hierarchy(self, blocks: BlockList) -> Tuple[BlockMap, BlockList]:
        """构建块的层级关系
        
        分析块之间的父子关系，构建层级结构映射。
        
        Args:
            blocks: 已验证的块列表
            
        Returns:
            包含块映射和根级块列表的元组
            - block_map: 块ID到块数据的映射
            - root_blocks: 没有父级的根级块列表
        """
        block_map: BlockMap = {block['block_id']: block for block in blocks}
        root_blocks: BlockList = []
        
        # 找到根级块（没有父级或父级不存在的块）
        for block in blocks:
            parent_id: Optional[str] = block.get('parent_id')
            if not parent_id or parent_id not in block_map:
                root_blocks.append(block)
        
        return block_map, root_blocks
    
    def _convert_root_blocks(self, root_blocks: BlockList, block_map: BlockMap) -> List[str]:
        """转换所有根级块
        
        遍历所有根级块并进行转换，处理转换过程中的异常。
        
        Args:
            root_blocks: 根级块列表
            block_map: 所有块的映射
            
        Returns:
            转换后的文本列表
        """
        converted_blocks: List[str] = []
        for block in root_blocks:
            try:
                converted = self._convert_block(block, block_map, level=0)
                if converted:
                    converted_blocks.append(converted)
            except Exception as e:
                self.logger.warning(f"转换块 {block.get('block_id', 'unknown')} 时出错: {e}")
                # 继续处理其他块
                continue
        return converted_blocks
    
    def _merge_converted_blocks(self, converted_blocks: List[str], root_blocks: BlockList) -> str:
        """合并转换后的块并处理段落分隔
        
        将转换后的文本块合并，并在需要的地方添加段落分隔。
        
        Args:
            converted_blocks: 转换后的文本列表
            root_blocks: 对应的原始块列表
            
        Returns:
            合并后的完整Markdown文本
        """
        if not converted_blocks:
            return ""
        
        result_parts: List[str] = []
        for i, content in enumerate(converted_blocks):
            result_parts.append(content)
            
            # 检查是否需要添加段落分隔
            if i < len(converted_blocks) - 1 and i < len(root_blocks) - 1:
                current_type: Optional[int] = root_blocks[i].get('block_type')
                next_type: Optional[int] = root_blocks[i + 1].get('block_type')
                
                if self._needs_paragraph_separation(current_type, next_type):
                    result_parts.append('\n')
        
        return '\n'.join(result_parts)
    
    def _needs_paragraph_separation(self, current_type: Optional[int], next_type: Optional[int]) -> bool:
        """判断两个块之间是否需要段落分隔
        
        根据块类型判断是否需要在两个块之间添加额外的空行。
        
        Args:
            current_type: 当前块的类型
            next_type: 下一个块的类型
            
        Returns:
            如果需要段落分隔则返回True，否则返回False
        """
        if current_type is None or next_type is None:
            return False
        
        return (current_type in self.PARAGRAPH_BLOCK_TYPES or 
                next_type in self.PARAGRAPH_BLOCK_TYPES)
    
    def _clean_markdown_output(self, result: str) -> str:
        """清理Markdown输出
        
        移除多余的空行和不必要的空白字符。
        
        Args:
            result: 原始的Markdown文本
            
        Returns:
            清理后的Markdown文本
        """
        # 清理多余的空行
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()
    
    def _convert_block(self, block: BlockData, block_map: BlockMap, level: int = 0) -> str:
        """转换单个块
        
        递归转换单个块及其所有子块。
        
        Args:
            block: 要转换的块数据
            block_map: 所有块的映射，用于查找子块
            level: 当前嵌套层级，用于缩进控制
            
        Returns:
            转换后的Markdown文本
        """
        block_type: Optional[int] = block.get('block_type')
        if block_type is None:
            return ""
        
        result_lines: List[str] = []
        
        # 使用策略模式转换当前块
        content = self._convert_single_block(block, block_type, level, block_map)
        if content:
            result_lines.append(content)
        
        # 递归转换子块（表格及单元格的子内容已在表格转换中处理，这里跳过以避免重复）
        if block_type not in {BlockType.TABLE, BlockType.TABLE_CELL}:
            child_content = self._convert_child_blocks(block, block_map, level)
            if child_content:
                result_lines.extend(child_content)
        
        return '\n'.join(result_lines)
    
    def _convert_single_block(self, block: BlockData, block_type: int, level: int, block_map: BlockMap) -> str:
        """转换单个块的内容
        
        根据块类型选择合适的转换器进行转换。
        
        Args:
            block: 块数据
            block_type: 块类型ID
            level: 嵌套层级
            block_map: 所有块的映射，用于查找子块
            
        Returns:
            转换后的文本内容
        """
        try:
            # 使用转换器映射
            converter = self._block_converters.get(block_type)
            if converter:
                # 根据方法签名调用不同的转换器
                if block_type in self.HEADING_LEVELS:
                    return converter(block, block_type)
                elif block_type in {BlockType.BULLET, BlockType.ORDERED, BlockType.TODO}:
                    return converter(block, level)
                elif block_type == BlockType.DIVIDER:
                    return converter()
                elif block_type == BlockType.TABLE:
                    return converter(block, block_map)
                else:
                    return converter(block)
            else:
                # 未支持的块类型，尝试提取文本内容
                return self._convert_unsupported_block(block)
        except Exception as e:
            self.logger.warning(f"转换块类型 {block_type} 时出错: {e}")
            return ""
    
    def _convert_child_blocks(self, block: BlockData, block_map: BlockMap, level: int) -> List[str]:
        """转换子块
        
        递归转换当前块的所有子块。
        
        Args:
            block: 父块数据
            block_map: 所有块的映射
            level: 当前嵌套层级
            
        Returns:
            转换后的子块文本列表
        """
        children: List[str] = block.get('children', [])
        if not children:
            return []
        
        child_blocks: BlockList = [block_map[child_id] for child_id in children if child_id in block_map]
        result_lines: List[str] = []
        
        for i, child_block in enumerate(child_blocks):
            child_content = self._convert_block(child_block, block_map, level + 1)
            if child_content:
                result_lines.append(child_content)
                
                # 处理相邻TEXT块之间的段落分隔
                if (i < len(child_blocks) - 1 and 
                    child_block.get('block_type') == BlockType.TEXT and 
                    child_blocks[i + 1].get('block_type') == BlockType.TEXT):
                    result_lines.append('')  # 添加空行来产生段落分隔
        
        return result_lines
    
    def _convert_page_block(self, block: BlockData) -> str:
        """转换页面块
        
        Args:
            block: 页面块数据
            
        Returns:
            转换后的文本内容
        """
        page_data: Dict[str, Any] = block.get('page', {})
        elements: ElementList = page_data.get('elements', [])
        return self._convert_elements_to_text(elements)
    
    def _convert_text_block(self, block: BlockData) -> str:
        """转换文本块
        
        Args:
            block: 文本块数据
            
        Returns:
            转换后的文本内容
        """
        text_data: Dict[str, Any] = block.get('text', {})
        elements: ElementList = text_data.get('elements', [])
        return self._convert_elements_to_text(elements)
    
    def _convert_heading_block(self, block: BlockData, block_type: int) -> str:
        """转换标题块
        
        Args:
            block: 标题块数据
            block_type: 块类型ID
            
        Returns:
            转换后的Markdown标题
            
        Raises:
            ValueError: 当块类型不是有效的标题类型时
        """
        if block_type not in self.HEADING_LEVELS:
            raise ValueError(f"无效的标题块类型: {block_type}")
        
        if not isinstance(block, dict):
            self.logger.warning("标题块数据不是字典类型")
            return ''
        
        try:
            level: int = self.HEADING_LEVELS.get(BlockType(block_type), 1)
            # 限制标题级别在Markdown支持范围内
            level = min(level, self.MAX_MARKDOWN_HEADING_LEVEL)
            heading_prefix = '#' * level + ' '
            
            # 获取标题内容
            heading_key = f'heading{block_type - 2}' if block_type > BlockType.TEXT else 'heading1'
            heading_data = block.get(heading_key, {})
            
            if not isinstance(heading_data, dict):
                self.logger.warning(f"标题数据格式错误: {heading_key}")
                return ''
            
            elements = heading_data.get('elements', [])
            if not isinstance(elements, list):
                self.logger.warning("标题元素不是列表类型")
                return ''
            
            content = self._convert_elements_to_text(elements)
            return heading_prefix + content if content else ''
            
        except Exception as e:
            self.logger.error(f"转换标题块时出错: {e}")
            return ''
    
    def _convert_bullet_block(self, block: BlockData, level: int) -> str:
        """转换无序列表块
        
        Args:
            block: 列表块数据
            level: 嵌套级别
            
        Returns:
            转换后的Markdown列表项
        """
        if not isinstance(block, dict):
            self.logger.warning("无序列表块数据不是字典类型")
            return ''
        
        if not isinstance(level, int) or level < 0:
            self.logger.warning(f"无效的嵌套级别: {level}")
            level = 0
        
        try:
            bullet_data: Dict[str, Any] = block.get('bullet', {})
            if not isinstance(bullet_data, dict):
                self.logger.warning("bullet数据格式错误")
                return ''
            
            elements: ElementList = bullet_data.get('elements', [])
            if not isinstance(elements, list):
                self.logger.warning("bullet元素不是列表类型")
                return ''
            
            content = self._convert_elements_to_text(elements)
            
            if not content:
                return ''
            
            # 限制嵌套级别，避免过深的缩进
            max_level: int = 10
            level = min(level, max_level)
            indent: str = '  ' * level
            return f'{indent}- {content}'
            
        except Exception as e:
            self.logger.error(f"转换无序列表块时出错: {e}")
            return ''
    
    def _convert_ordered_block(self, block: BlockData, level: int) -> str:
        """转换有序列表块
        
        Args:
            block: 列表块数据
            level: 嵌套级别
            
        Returns:
            转换后的Markdown有序列表项
        """
        if not isinstance(block, dict):
            self.logger.warning("有序列表块数据不是字典类型")
            return ''
        
        if not isinstance(level, int) or level < 0:
            self.logger.warning(f"无效的嵌套级别: {level}")
            level = 0
        
        try:
            ordered_data: Dict[str, Any] = block.get('ordered', {})
            if not isinstance(ordered_data, dict):
                self.logger.warning("ordered数据格式错误")
                return ''
            
            elements: ElementList = ordered_data.get('elements', [])
            if not isinstance(elements, list):
                self.logger.warning("ordered元素不是列表类型")
                return ''
            
            content = self._convert_elements_to_text(elements)
            
            if not content:
                return ''
            
            # 限制嵌套级别
            max_level: int = 10
            level = min(level, max_level)
            indent: str = '  ' * level
            return f'{indent}1. {content}'
            
        except Exception as e:
            self.logger.error(f"转换有序列表块时出错: {e}")
            return ''
    
    def _convert_code_block(self, block: BlockData) -> str:
        """转换代码块
        
        Args:
            block: 代码块数据
            
        Returns:
            转换后的Markdown代码块
        """
        if not isinstance(block, dict):
            self.logger.warning("代码块数据不是字典类型")
            return ''
        
        try:
            code_data: Dict[str, Any] = block.get('code', {})
            if not isinstance(code_data, dict):
                self.logger.warning("code数据格式错误")
                return ''
            
            elements: ElementList = code_data.get('elements', [])
            if not isinstance(elements, list):
                self.logger.warning("code元素不是列表类型")
                return ''
            
            language_id: int = code_data.get('language', 1)
            if not isinstance(language_id, int):
                self.logger.warning(f"无效的语言ID: {language_id}")
                language_id = 1
            
            # 获取语言标识
            language: str = self.CODE_LANGUAGE_MAP.get(language_id, 'plaintext')
            
            # 提取代码内容
            code_content = self._convert_elements_to_text(elements, preserve_formatting=True)
            
            return f'```{language}\n{code_content}\n```'
            
        except Exception as e:
            self.logger.error(f"转换代码块时出错: {e}")
            return ''
    
    def _convert_quote_block(self, block: BlockData) -> str:
        """转换引用块
        
        Args:
            block: 引用块数据
            
        Returns:
            转换后的Markdown引用
        """
        if not isinstance(block, dict):
            self.logger.warning("引用块数据不是字典类型")
            return ''
        
        try:
            quote_data: Dict[str, Any] = block.get('quote', {})
            if not isinstance(quote_data, dict):
                self.logger.warning("quote数据格式错误")
                return ''
            
            elements: ElementList = quote_data.get('elements', [])
            if not isinstance(elements, list):
                self.logger.warning("quote元素不是列表类型")
                return ''
            
            content = self._convert_elements_to_text(elements)
            if not content:
                return ''
            
            # 为每行添加引用前缀
            lines: List[str] = content.split('\n')
            quoted_lines: List[str] = [f'> {line}' if line.strip() else '>' for line in lines]
            return '\n'.join(quoted_lines)
            
        except Exception as e:
            self.logger.error(f"转换引用块时出错: {e}")
            return ''
    
    def _convert_todo_block(self, block: BlockData, level: int) -> str:
        """转换待办事项块
        
        Args:
            block: 待办事项块数据
            level: 嵌套级别（用于缩进）
            
        Returns:
            转换后的Markdown待办事项
        """
        if not isinstance(block, dict):
            self.logger.warning("待办事项块数据不是字典类型")
            return ''
        
        if not isinstance(level, int) or level < 0:
            self.logger.warning(f"无效的嵌套级别: {level}")
            level = 0
        
        try:
            todo_data: Dict[str, Any] = block.get('todo', {})
            if not isinstance(todo_data, dict):
                self.logger.warning("todo数据格式错误")
                return ''
            
            elements: ElementList = todo_data.get('elements', [])
            if not isinstance(elements, list):
                self.logger.warning("todo元素不是列表类型")
                return ''
            
            # 获取完成状态
            is_done: bool = todo_data.get('done', False)
            if not isinstance(is_done, bool):
                self.logger.warning(f"无效的完成状态: {is_done}")
                is_done = False
            
            content = self._convert_elements_to_text(elements)
            if not content:
                return ''
            
            # 添加缩进支持
            max_level: int = 10
            level = min(level, max_level)
            indent: str = '  ' * level
            checkbox: str = '[x]' if is_done else '[ ]'
            return f'{indent}- {checkbox} {content}'
            
        except Exception as e:
            self.logger.error(f"转换待办事项块时出错: {e}")
            return ''
    
    def _convert_image_block(self, block: BlockData) -> str:
        """转换图片块
        
        Args:
            block: 图片块数据
            
        Returns:
            转换后的Markdown图片
        """
        if not isinstance(block, dict):
            self.logger.warning("图片块数据不是字典类型")
            return ''
        
        try:
            image_data: Dict[str, Any] = block.get('image', {})
            if not isinstance(image_data, dict):
                self.logger.warning("image数据格式错误")
                return ''
            
            # 获取图片token
            token: str = image_data.get('token', '')
            if not isinstance(token, str) or not token.strip():
                self.logger.warning("图片token无效")
                return ''
            
            # 获取图片宽度和高度（可选）
            width: Optional[Union[int, float]] = image_data.get('width')
            height: Optional[Union[int, float]] = image_data.get('height')
            
            # 构建图片URL
            image_url: str = f'https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/preview/{token}/'
            
            # 生成alt文本
            alt_text: str = f'image-{token[:8]}'
            
            # 如果有尺寸信息，添加到alt文本中
            if isinstance(width, (int, float)) and isinstance(height, (int, float)):
                alt_text += f' ({int(width)}x{int(height)})'
            
            return f'![{alt_text}]({image_url})'
            
        except Exception as e:
            self.logger.error(f"转换图片块时出错: {e}")
            return ''
    
    def _convert_table_block(self, block: BlockData, block_map: BlockMap = None) -> str:
        """转换表格块
        
        Args:
            block: 表格块数据 (block_type=31)
            block_map: 块映射，用于查找table_cell的children
            
        Returns:
            转换后的Markdown表格
        """
        if not isinstance(block, dict):
            self.logger.warning("表格块数据不是字典类型")
            return ''
        
        try:
            # 获取表格数据
            table_data: Optional[Dict[str, Any]] = self._get_block_data_safely(block, 'table')
            if not table_data:
                self.logger.warning("表格数据为空")
                return ''
            
            # 获取表格属性：row_size 和 column_size
            table_property = table_data.get('property', {})
            if not isinstance(table_property, dict):
                self.logger.warning("表格属性格式错误")
                return ''
            
            row_size = table_property.get('row_size', 0)
            column_size = table_property.get('column_size', 0)
            
            if row_size <= 0 or column_size <= 0:
                self.logger.warning(f"表格尺寸无效: {row_size}x{column_size}")
                return ''
            
            # 获取单元格ID列表（按行优先顺序）
            cells = table_data.get('cells', [])
            # 当cells缺失或为空时，尝试回退到children及parent_id扫描
            if not isinstance(cells, list) or len(cells) == 0:
                fallback_cells: List[str] = []
                # 优先使用当前表格块的children顺序
                child_ids = block.get('children', []) if isinstance(block, dict) else []
                if isinstance(child_ids, list) and block_map:
                    for cid in child_ids:
                        cb = block_map.get(cid)
                        if isinstance(cb, dict) and cb.get('block_type') == BlockType.TABLE_CELL:
                            fallback_cells.append(cid)
                
                # 如果children没有包含cell，尝试全局扫描同父的TABLE_CELL
                if not fallback_cells and block_map:
                    table_block_id = block.get('block_id')
                    # 先收集
                    for b_id, b in block_map.items():
                        if isinstance(b, dict) and b.get('block_type') == BlockType.TABLE_CELL and b.get('parent_id') == table_block_id:
                            fallback_cells.append(b_id)
                    # 如果存在行列索引，按行列排序
                    def _sort_key(cid: str):
                        cb = block_map.get(cid, {})
                        r = cb.get('row_index')
                        c = cb.get('column_index')
                        r = r if isinstance(r, int) else 0
                        c = c if isinstance(c, int) else 0
                        return (r, c)
                    if fallback_cells:
                        try:
                            fallback_cells.sort(key=_sort_key)
                        except Exception:
                            pass
                
                cells = fallback_cells
            
            actual_count = len(cells) if isinstance(cells, list) else 0
            expected_count = row_size * column_size
            if actual_count != expected_count:
                self.logger.warning(f"单元格数量不匹配: 期望{expected_count}，实际{actual_count}，将按可用单元格尽力渲染")
            
            # 构建表格矩阵
            table_matrix = self._build_table_matrix_new(cells, row_size, column_size, block_map)
            if not table_matrix or not any(any(row) for row in table_matrix):
                self.logger.warning("表格内容为空")
                return ''
            
            # 转换为Markdown表格
            return self._format_markdown_table(table_matrix)
            
        except Exception as e:
            self.logger.error(f"转换表格块时出错: {e}")
            return ''
    
    def _extract_table_info(self, table_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """提取表格信息
        
        Args:
            table_data: 表格数据字典
            
        Returns:
            包含表格信息的字典，如果无效则返回None
        """
        try:
            # 获取单元格数据
            cells = table_data.get('cells', [])
            if not isinstance(cells, list) or not cells:
                self.logger.warning("表格单元格数据无效")
                return None
            
            # 获取表格属性
            table_properties = table_data.get('property', {})
            if not isinstance(table_properties, dict):
                self.logger.warning("表格属性格式错误")
                table_properties = {}
            
            # 获取表格尺寸
            row_size = table_properties.get('row_size', 0)
            column_size = table_properties.get('column_size', 0)
            
            # 验证尺寸数据
            if not self._validate_table_dimensions(row_size, column_size):
                return None
            
            # 应用尺寸限制
            row_size, column_size = self._apply_table_size_limits(row_size, column_size)
            
            return {
                'cells': cells,
                'row_size': row_size,
                'column_size': column_size
            }
            
        except Exception as e:
            self.logger.error(f"提取表格信息时出错: {e}")
            return None
    
    def _validate_table_dimensions(self, row_size: Any, column_size: Any) -> bool:
        """验证表格尺寸
        
        Args:
            row_size: 行数
            column_size: 列数
            
        Returns:
            尺寸是否有效
        """
        if not isinstance(row_size, int) or not isinstance(column_size, int):
            self.logger.warning("表格尺寸数据类型无效")
            return False
        
        if row_size <= 0 or column_size <= 0:
            self.logger.warning(f"表格尺寸无效: {row_size}x{column_size}")
            return False
        
        return True
    
    def _apply_table_size_limits(self, row_size: int, column_size: int) -> Tuple[int, int]:
        """应用表格尺寸限制
        
        Args:
            row_size: 原始行数
            column_size: 原始列数
            
        Returns:
            限制后的(行数, 列数)
        """
        max_rows = self.MAX_TABLE_ROWS
        max_columns = self.MAX_TABLE_COLS
        
        original_row_size = row_size
        original_column_size = column_size
        
        row_size = min(row_size, max_rows)
        column_size = min(column_size, max_columns)
        
        if row_size != original_row_size or column_size != original_column_size:
            self.logger.warning(
                f"表格过大: {original_row_size}x{original_column_size}，"
                f"已限制为{row_size}x{column_size}"
            )
        
        return row_size, column_size
    
    def _build_table_matrix_new(self, cells: List[str], row_size: int, column_size: int, block_map: BlockMap = None) -> List[List[str]]:
        """构建表格矩阵（新版本）
        
        Args:
            cells: 单元格ID列表，按行优先顺序排列
            row_size: 行数
            column_size: 列数
            block_map: 块映射，用于查找table_cell的children
            
        Returns:
            表格内容矩阵
        """
        # 初始化表格矩阵
        matrix = [[''] * column_size for _ in range(row_size)]
        
        if not cells or not block_map:
            self.logger.warning("单元格数据或块映射为空")
            return matrix
        
        processed_cells = 0
        
        try:
            for i, cell_id in enumerate(cells):
                if not isinstance(cell_id, str) or not cell_id:
                    continue
                
                # 根据索引计算行列位置（按行优先顺序）
                row_index = i // column_size
                column_index = i % column_size
                
                # 检查索引范围
                if row_index >= row_size or column_index >= column_size:
                    continue
                
                # 获取单元格内容
                content = self._extract_table_cell_content(cell_id, block_map)
                matrix[row_index][column_index] = content
                processed_cells += 1
            
            self.logger.debug(f"成功处理 {processed_cells} 个单元格")
            
        except Exception as e:
            self.logger.error(f"构建表格矩阵时出错: {e}")
        
        return matrix
    
    def _build_table_matrix(self, cells: List[Dict[str, Any]], row_size: int, column_size: int, block_map: BlockMap = None) -> List[List[str]]:
        """构建表格矩阵（旧版本，保持兼容性）
        
        Args:
            cells: 表格单元格数据列表
            row_size: 行数
            column_size: 列数
            block_map: 块映射，用于查找table_cell的children
            
        Returns:
            表格内容矩阵
        """
        # 初始化表格矩阵
        matrix = [[''] * column_size for _ in range(row_size)]
        
        if not cells:
            self.logger.warning("单元格数据为空")
            return matrix
        
        processed_cells = 0
        invalid_cells = 0
        
        try:
            for i, cell in enumerate(cells):
                if not isinstance(cell, dict):
                    invalid_cells += 1
                    continue
                
                # 根据cells数组的索引计算单元格位置
                # cells按行优先顺序排列：第一行的所有列，然后第二行的所有列，以此类推
                row_index = i // column_size
                column_index = i % column_size
                
                # 检查索引范围
                if not self._is_valid_cell_position(row_index, column_index, row_size, column_size):
                    invalid_cells += 1
                    continue
                
                # 获取并处理单元格内容
                content = self._extract_cell_content(cell, block_map)
                matrix[row_index][column_index] = content
                processed_cells += 1
            
            if invalid_cells > 0:
                self.logger.warning(f"跳过了 {invalid_cells} 个无效单元格")
            
            self.logger.debug(f"成功处理 {processed_cells} 个单元格")
            
        except Exception as e:
            self.logger.error(f"构建表格矩阵时出错: {e}")
        
        return matrix
    
    def _extract_cell_position(self, cell: Dict[str, Any]) -> Optional[Tuple[int, int]]:
        """提取单元格位置
        
        Args:
            cell: 单元格数据
            
        Returns:
            (行索引, 列索引) 或 None
        """
        try:
            row_index = cell.get('row_index')
            column_index = cell.get('column_index')
            
            if not isinstance(row_index, int) or not isinstance(column_index, int):
                return None
            
            return row_index, column_index
            
        except Exception:
            return None
    
    def _is_valid_cell_position(self, row_index: int, column_index: int, 
                               row_size: int, column_size: int) -> bool:
        """检查单元格位置是否有效
        
        Args:
            row_index: 行索引
            column_index: 列索引
            row_size: 表格行数
            column_size: 表格列数
            
        Returns:
            位置是否有效
        """
        return (0 <= row_index < row_size and 0 <= column_index < column_size)
    
    def _extract_table_cell_content(self, cell_id: str, block_map: BlockMap) -> str:
        """提取表格单元格内容（新版本）
        
        Args:
            cell_id: 单元格块ID (block_type=32)
            block_map: 块映射
            
        Returns:
            单元格文本内容（包含基础样式的Markdown）
        """
        try:
            # 获取table_cell块 (block_type=32)
            table_cell_block = block_map.get(cell_id)
            if not table_cell_block or table_cell_block.get('block_type') != 32:
                return ''
            
            # 获取table_cell块的children
            children_ids = table_cell_block.get('children', [])
            if not children_ids:
                return ''
            
            # 从children中提取内容，优先TEXT块并支持样式
            content_parts = []
            for child_id in children_ids:
                child_block = block_map.get(child_id)
                if not child_block:
                    continue
                
                bt = child_block.get('block_type')
                
                # 文本块（带样式）
                if bt == 2:  # TEXT = 2
                    text_data = child_block.get('text', {})
                    elements = text_data.get('elements', [])
                    if isinstance(elements, list):
                        text_content = self._convert_elements_to_text(elements)
                        if isinstance(text_content, str) and text_content.strip():
                            content_parts.append(text_content.strip())
                    continue
                
                # 代码块：尽量提取为行内代码
                if bt == 14:  # CODE = 14
                    code_data = child_block.get('code', {})
                    elements = code_data.get('elements', [])
                    code_content = ''
                    if isinstance(elements, list):
                        code_content = self._convert_elements_to_text(elements, preserve_formatting=True)
                    if isinstance(code_content, str) and code_content.strip():
                        content_parts.append(f'`{code_content.strip()}`')
                    continue
                
                # 图片等其它块：放置占位符，避免丢信息
                if bt == 27:  # IMAGE（根据BlockType枚举，图片通常为该类型）
                    content_parts.append('[image]')
                    continue
                
                # 兜底：若存在text.elements，仍尝试提取
                text_data = child_block.get('text', {})
                elements = text_data.get('elements', [])
                if isinstance(elements, list):
                    text_content = self._convert_elements_to_text(elements)
                    if isinstance(text_content, str) and text_content.strip():
                        content_parts.append(text_content.strip())
            
            # 合并所有内容
            content = ' '.join(part for part in content_parts if isinstance(part, str))
            return self._sanitize_table_cell_content(content)
            
        except Exception as e:
            self.logger.warning(f"提取表格单元格内容时出错: {e}")
            return ''
    
    def _extract_text_from_elements(self, elements: List[Dict[str, Any]]) -> str:
        """从elements中提取文本内容
        
        Args:
            elements: text.elements列表
            
        Returns:
            提取的文本内容
        """
        text_parts = []
        
        try:
            for element in elements:
                if not isinstance(element, dict):
                    continue
                
                # 获取text_run内容
                text_run = element.get('text_run', {})
                if isinstance(text_run, dict):
                    content = text_run.get('content', '')
                    if isinstance(content, str) and content:
                        text_parts.append(content)
        
        except Exception as e:
            self.logger.warning(f"提取文本元素时出错: {e}")
        
        return ''.join(text_parts)
    
    def _extract_cell_content(self, cell: Dict[str, Any], block_map: BlockMap = None) -> str:
        """提取单元格内容（旧版本，保持兼容性）
        
        Args:
            cell: 单元格数据
            block_map: 块映射，用于查找table_cell的children
            
        Returns:
            单元格文本内容
        """
        try:
            # 根据用户提供的JSON结构，table_cell块的实际内容在其children中
            # cell应该是一个包含block_id的table_cell块引用
            cell_block_id = cell.get('block_id')
            if not cell_block_id or not block_map:
                return ''
            
            # 从block_map中查找table_cell块
            table_cell_block = block_map.get(cell_block_id)
            if not table_cell_block or table_cell_block.get('block_type') != 32:  # TABLE_CELL = 32
                return ''
            
            # 获取table_cell块的children
            children_ids = table_cell_block.get('children', [])
            if not children_ids:
                return ''
            
            # 从children中提取text内容
            content_parts = []
            for child_id in children_ids:
                child_block = block_map.get(child_id)
                if child_block and child_block.get('block_type') == 2:  # TEXT = 2
                    text_data = child_block.get('text', {})
                    elements = text_data.get('elements', [])
                    if isinstance(elements, list):
                        text_content = self._convert_elements_to_text(elements)
                        if text_content.strip():
                            content_parts.append(text_content)
            
            # 合并所有内容
            content = ' '.join(content_parts)
            return self._sanitize_table_cell_content(content)
            
        except Exception as e:
            self.logger.warning(f"提取单元格内容时出错: {e}")
            return ''
    
    def _sanitize_table_cell_content(self, content: str) -> str:
        """清理表格单元格内容
        
        Args:
            content: 原始内容
            
        Returns:
            清理后的内容
        """
        if not isinstance(content, str):
            return ''
        
        # 移除换行符，用空格替代
        content = content.replace('\n', ' ').replace('\r', ' ')
        
        # 转义管道符
        content = content.replace('|', '\\|')
        
        # 清理多余空格
        content = ' '.join(content.split())
        
        return content.strip()
    
    def _format_markdown_table(self, matrix: List[List[str]]) -> str:
        """格式化Markdown表格
        
        Args:
            matrix: 表格内容矩阵
            
        Returns:
            格式化后的Markdown表格字符串
        """
        if not matrix or not matrix[0]:
            self.logger.warning("表格矩阵为空")
            return ''
        
        try:
            # 确保所有行都有相同的列数
            column_count = len(matrix[0])
            normalized_matrix = self._normalize_table_matrix(matrix, column_count)
            
            # 构建表格行
            table_lines = []
            
            # 处理表头
            header_line = self._build_table_row(normalized_matrix[0])
            table_lines.append(header_line)
            
            # 添加分隔行
            separator_line = self._build_separator_row(column_count)
            table_lines.append(separator_line)
            
            # 处理数据行
            for row in normalized_matrix[1:]:
                data_line = self._build_table_row(row)
                table_lines.append(data_line)
            
            result = '\n'.join(table_lines)
            self.logger.debug(f"生成表格: {len(normalized_matrix)}行 x {column_count}列")
            
            return result
            
        except Exception as e:
            self.logger.error(f"格式化Markdown表格时出错: {e}")
            return ''
    
    def _normalize_table_matrix(self, matrix: List[List[str]], column_count: int) -> List[List[str]]:
        """标准化表格矩阵，确保所有行都有相同的列数
        
        Args:
            matrix: 原始矩阵
            column_count: 目标列数
            
        Returns:
            标准化后的矩阵
        """
        normalized = []
        
        for row in matrix:
            if len(row) < column_count:
                # 补齐缺失的列
                padded_row = row + [''] * (column_count - len(row))
            elif len(row) > column_count:
                # 截断多余的列
                padded_row = row[:column_count]
            else:
                padded_row = row[:]
            
            normalized.append(padded_row)
        
        return normalized
    
    def _build_table_row(self, row: List[str]) -> str:
        """构建表格行
        
        Args:
            row: 行数据
            
        Returns:
            格式化的表格行字符串
        """
        return '| ' + ' | '.join(row) + ' |'
    
    def _build_separator_row(self, column_count: int) -> str:
        """构建分隔行
        
        Args:
            column_count: 列数
            
        Returns:
            分隔行字符串
        """
        return '| ' + ' | '.join(['---'] * column_count) + ' |'
    
    def _convert_divider_block(self) -> str:
        """转换分割线块
        
        Returns:
            Markdown分割线
        """
        return '---'
    
    def _convert_table_cell_block(self, block: BlockData) -> str:
        """转换表格单元格块
        
        Args:
            block: 表格单元格块数据
            
        Returns:
            单元格内容（通常为空，因为单元格内容在表格块中统一处理）
        """
        # 表格单元格内容在_convert_table_block中统一处理
        # 这里返回空字符串避免重复处理
        return ''
    
    def _get_block_data_safely(self, block: BlockData, key: str) -> Optional[Dict[str, Any]]:
        """安全获取块数据
        
        Args:
            block: 块数据
            key: 数据键名
            
        Returns:
            块数据字典，如果不存在或格式错误则返回None
        """
        if not isinstance(block, dict):
            return None
        
        data: Any = block.get(key, {})
        return data if isinstance(data, dict) else None
    
    def _get_elements_safely(self, data: Dict[str, Any]) -> ElementList:
        """安全获取元素列表
        
        Args:
            data: 包含elements的数据字典
            
        Returns:
            元素列表，如果不存在或格式错误则返回空列表
        """
        if not isinstance(data, dict):
            return []
        
        elements: Any = data.get('elements', [])
        return elements if isinstance(elements, list) else []
    
    def _validate_block_type(self, block_type: Any) -> bool:
        """验证块类型是否有效
        
        Args:
            block_type: 要验证的块类型
            
        Returns:
            是否为有效的块类型
        """
        return isinstance(block_type, int) and block_type in BlockType.__members__.values()
    
    def _convert_equation_block(self, block: BlockData) -> str:
        """转换公式块
        
        Args:
            block: 公式块数据
            
        Returns:
            转换后的Markdown公式
        """
        if not isinstance(block, dict):
            self.logger.warning("公式块数据不是字典类型")
            return ''
        
        try:
            equation_data: Dict[str, Any] = block.get('equation', {})
            if not isinstance(equation_data, dict):
                self.logger.warning("equation数据格式错误")
                return ''
            
            content: str = equation_data.get('content', '')
            if not isinstance(content, str) or not content.strip():
                self.logger.warning("公式内容无效")
                return ''
            
            # 清理公式内容，移除可能的危险字符
            cleaned_content: str = content.strip()
            
            return f'$${cleaned_content}$$'
            
        except Exception as e:
            self.logger.error(f"转换公式块时出错: {e}")
            return ''
    
    def _convert_unsupported_block(self, block: BlockData) -> str:
        """转换不支持的块类型
        
        Args:
            block: 块数据
            
        Returns:
            空字符串或占位符
        """
        if not isinstance(block, dict):
            return ''
        
        block_type: Any = block.get('block_type')
        self.logger.info(f"遇到不支持的块类型: {block_type}")
        
        # 尝试提取任何可能的文本内容
        try:
            # 检查是否有通用的elements字段
            for key, value in block.items():
                if isinstance(value, dict) and 'elements' in value:
                    elements: Any = value.get('elements', [])
                    if isinstance(elements, list) and elements:
                        content: str = self._convert_elements_to_text(elements)
                        if content:
                            return f"<!-- 不支持的块类型 {block_type} -->\n{content}"
            
            return f"<!-- 不支持的块类型: {block_type} -->"
            
        except Exception as e:
            self.logger.error(f"处理不支持的块类型时出错: {e}")
            return f"<!-- 不支持的块类型: {block_type} -->"
    

    
    def _log_conversion_stats(self, blocks: BlockList, result: str) -> None:
        """记录转换统计信息
        
        Args:
            blocks: 输入的块列表
            result: 转换结果
        """
        try:
            if not self.logger.isEnabledFor(logging.INFO):
                return
            
            # 统计块类型
            block_types: Dict[Any, int] = {}
            for block in blocks:
                if isinstance(block, dict):
                    block_type: Any = block.get('block_type', 'unknown')
                    block_types[block_type] = block_types.get(block_type, 0) + 1
            
            # 统计结果
            result_lines: int = result.count('\n') + 1 if result else 0
            result_chars: int = len(result) if result else 0
            
            self.logger.info(f"转换完成 - 输入块数: {len(blocks)}, 输出行数: {result_lines}, 输出字符数: {result_chars}")
            self.logger.debug(f"块类型统计: {block_types}")
            
        except Exception as e:
            self.logger.error(f"记录转换统计信息时出错: {e}")
    
    def _convert_elements_to_text(self, elements: ElementList, preserve_formatting: bool = False) -> str:
        """将元素列表转换为文本
        
        Args:
            elements: 元素列表
            preserve_formatting: 是否保留格式（用于代码块）
            
        Returns:
            转换后的文本
            
        Raises:
            ValueError: 当元素格式不正确时
        """
        if not elements:
            return ''
        
        if not isinstance(elements, list):
            raise ValueError("elements必须是列表类型")
        
        # 使用列表收集结果，最后一次性join，提高性能
        text_parts: List[str] = []
        
        for i, element in enumerate(elements):
            try:
                converted_text: str = self._convert_single_element(element, preserve_formatting)
                if converted_text:
                    text_parts.append(converted_text)
            except Exception as e:
                self.logger.warning(f"转换第{i}个元素时出错: {e}")
                # 尝试提取基本文本内容作为备用
                fallback_text: str = self._extract_element_fallback_text(element)
                if fallback_text:
                    text_parts.append(fallback_text)
        
        return ''.join(text_parts)
    
    def _convert_single_element(self, element: ElementData, preserve_formatting: bool = False) -> str:
        """转换单个元素
        
        Args:
            element: 要转换的元素
            preserve_formatting: 是否保留格式
            
        Returns:
            转换后的文本
        """
        if not isinstance(element, dict):
            return ""
        
        # 使用策略模式处理不同类型的元素
        element_handlers: Dict[str, Callable[[ElementData], str]] = {
            'text_run': lambda e: self._convert_text_run_element(e, preserve_formatting),
            'mention_user': self._convert_mention_user_element,
            'mention_doc': self._convert_mention_doc_element,
            'equation': self._convert_equation_inline_element
        }
        
        for element_type, handler in element_handlers.items():
            if element_type in element:
                return handler(element)
        
        # 未知类型，尝试提取文本
        return self._extract_element_fallback_text(element)
    
    def _convert_text_run_element(self, element: ElementData, preserve_formatting: bool = False) -> str:
        """转换text_run元素
        
        Args:
            element: 文本运行元素
            preserve_formatting: 是否保留格式
            
        Returns:
            转换后的文本
        """
        text_run: Dict[str, Any] = element.get('text_run', {})
        content: str = text_run.get('content', '')
        
        if not content:
            return ''
        
        # 处理换行符：将\\n字符串转换为真正的换行符
        content = content.replace('\\n', '\n')
        
        if not preserve_formatting:
            style: Dict[str, Any] = text_run.get('text_element_style', {})
            content = self._apply_element_styles(content, style)
        
        return content
    
    def _apply_element_styles(self, content: str, style: Dict[str, Any]) -> str:
        """应用元素样式
        
        Args:
            content: 原始内容
            style: 样式配置
            
        Returns:
            应用样式后的内容
        """
        if not style or not content:
            return content
        
        # 处理链接（优先级最高）
        link: Dict[str, Any] = style.get('link', {})
        if link.get('url'):
            url: str = link['url']
            content = f'[{content}]({url})'
            return content
        
        # 按照Markdown优先级应用样式
        if style.get('inline_code'):
            content = f'`{content}`'
        else:
            if style.get('bold'):
                content = f'**{content}**'
            if style.get('italic'):
                content = f'*{content}*'
            if style.get('strikethrough'):
                content = f'~~{content}~~'
        
        return content
    
    def _convert_mention_user_element(self, element: ElementData) -> str:
        """转换用户提及元素
        
        Args:
            element: 用户提及元素
            
        Returns:
            转换后的用户提及文本
        """
        mention: Dict[str, Any] = element.get('mention_user', {})
        user_id: str = mention.get('user_id', '')
        return f'@{user_id}' if user_id else ''
    
    def _convert_mention_doc_element(self, element: ElementData) -> str:
        """转换文档提及元素
        
        Args:
            element: 文档提及元素
            
        Returns:
            转换后的文档链接
        """
        mention: Dict[str, Any] = element.get('mention_doc', {})
        title: str = mention.get('title', '')
        url: str = mention.get('url', '')
        
        if url and title:
            return f'[{title}]({url})'
        elif title:
            return title
        else:
            return ''
    
    def _convert_equation_inline_element(self, element: ElementData) -> str:
        """转换行内公式元素
        
        Args:
            element: 行内公式元素
            
        Returns:
            转换后的行内公式
        """
        equation: Dict[str, Any] = element.get('equation', {})
        content: str = equation.get('content', '')
        return f'${content}$' if content else ''
    
    def _extract_element_fallback_text(self, element: ElementData) -> str:
        """提取元素的备用文本内容
        
        Args:
            element: 元素数据
            
        Returns:
            提取的文本内容
        """
        if not isinstance(element, dict):
            return ''
        
        # 尝试从各种可能的字段中提取文本
        text_fields: List[str] = ['content', 'text', 'title', 'name']
        for field in text_fields:
            if field in element:
                value: Any = element[field]
                if isinstance(value, str) and value.strip():
                    return value.strip()
        
        # 尝试从嵌套对象中提取
        for key, value in element.items():
            if isinstance(value, dict):
                for text_field in text_fields:
                    if text_field in value:
                        text_value: Any = value[text_field]
                        if isinstance(text_value, str) and text_value.strip():
                            return text_value.strip()
        
        return ''