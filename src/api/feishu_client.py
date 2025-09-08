"""飞书API客户端模块"""
import json
from typing import Dict, List, Optional, Any
from lark_oapi import Client, RequestOption
from lark_oapi.api.docx import *
from lark_oapi.api.docx.v1 import *
from lark_oapi.core.model import BaseResponse


class FeishuAPIClient:
    """飞书API客户端"""
    
    def __init__(self, user_access_token: str):
        """初始化客户端
        
        Args:
            user_access_token: 用户访问令牌
        """
        self.client = Client.builder().enable_set_token(True).build()
        self.user_access_token = user_access_token
    
    def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """获取文档信息
        
        Args:
            document_id: 文档ID
            
        Returns:
            包含文档信息的字典
            
        Raises:
            Exception: API调用失败时抛出异常
        """
        try:
            # 构建请求
            request = GetDocumentRequest.builder() \
                .document_id(document_id) \
                .build()
            
            # 构建请求选项，设置用户访问令牌
            option = RequestOption.builder().user_access_token(self.user_access_token).build()
            
            # 发起请求
            response: GetDocumentResponse = self.client.docx.v1.document.get(request, option)
            
            # 检查响应
            if not response.success():
                raise Exception(f"API调用失败: {response.code} - {response.msg}")
            
            # 返回文档信息
            document = response.data.document
            return {
                'document_id': document.document_id,
                'revision_id': document.revision_id,
                'title': document.title or f'Document_{document_id[:8]}'
            }
            
        except Exception as e:
            raise Exception(f"获取文档信息失败: {str(e)}")
    
    def get_document_blocks(self, document_id: str, page_size: int = 500) -> Dict[str, Any]:
        """获取文档块列表
        
        Args:
            document_id: 文档ID
            page_size: 分页大小，默认500
            
        Returns:
            包含文档块数据的字典
            
        Raises:
            Exception: API调用失败时抛出异常
        """
        try:
            # 构建请求
            request = ListDocumentBlockRequest.builder() \
                .document_id(document_id) \
                .page_size(page_size) \
                .build()
            
            # 构建请求选项，设置用户访问令牌
            option = RequestOption.builder().user_access_token(self.user_access_token).build()
            
            # 发起请求
            response: ListDocumentBlockResponse = self.client.docx.v1.document_block.list(request, option)
            
            # 检查响应
            if not response.success():
                raise Exception(f"API调用失败: {response.code} - {response.msg}")
            
            # 返回数据
            result = {
                'code': response.code,
                'msg': response.msg,
                'data': {
                    'has_more': response.data.has_more,
                    'page_token': response.data.page_token,
                    'items': []
                }
            }
            
            # 转换块数据
            if response.data.items:
                for block in response.data.items:
                    block_data = {
                        'block_id': block.block_id,
                        'block_type': block.block_type,
                        'parent_id': block.parent_id,
                        'children': block.children or []
                    }
                    
                    # 根据块类型添加内容
                    if hasattr(block, 'page') and block.page:
                        block_data['page'] = self._convert_page_data(block.page)
                    elif hasattr(block, 'text') and block.text:
                        block_data['text'] = self._convert_text_data(block.text)
                    elif hasattr(block, 'heading1') and block.heading1:
                        block_data['heading1'] = self._convert_text_data(block.heading1)
                    elif hasattr(block, 'heading2') and block.heading2:
                        block_data['heading2'] = self._convert_text_data(block.heading2)
                    elif hasattr(block, 'heading3') and block.heading3:
                        block_data['heading3'] = self._convert_text_data(block.heading3)
                    elif hasattr(block, 'heading4') and block.heading4:
                        block_data['heading4'] = self._convert_text_data(block.heading4)
                    elif hasattr(block, 'heading5') and block.heading5:
                        block_data['heading5'] = self._convert_text_data(block.heading5)
                    elif hasattr(block, 'heading6') and block.heading6:
                        block_data['heading6'] = self._convert_text_data(block.heading6)
                    elif hasattr(block, 'bullet') and block.bullet:
                        block_data['bullet'] = self._convert_text_data(block.bullet)
                    elif hasattr(block, 'ordered') and block.ordered:
                        block_data['ordered'] = self._convert_text_data(block.ordered)
                    elif hasattr(block, 'code') and block.code:
                        block_data['code'] = self._convert_code_data(block.code)
                    elif hasattr(block, 'quote') and block.quote:
                        block_data['quote'] = self._convert_text_data(block.quote)
                    elif hasattr(block, 'todo') and block.todo:
                        block_data['todo'] = self._convert_todo_data(block.todo)
                    elif hasattr(block, 'divider') and block.divider:
                        block_data['divider'] = {}
                    elif hasattr(block, 'image') and block.image:
                        block_data['image'] = self._convert_image_data(block.image)
                    elif hasattr(block, 'table') and block.table:
                        block_data['table'] = self._convert_table_data(block.table)
                    elif hasattr(block, 'table_cell') and block.table_cell:
                        block_data['table_cell'] = self._convert_table_cell_data(block.table_cell)
                    
                    result['data']['items'].append(block_data)
            
            return result
            
        except Exception as e:
            raise Exception(f"获取文档块失败: {str(e)}")
    
    def _convert_page_data(self, page) -> Dict[str, Any]:
        """转换页面数据"""
        return {
            'elements': self._convert_elements(page.elements) if page.elements else []
        }
    
    def _convert_text_data(self, text) -> Dict[str, Any]:
        """转换文本数据"""
        return {
            'elements': self._convert_elements(text.elements) if text.elements else [],
            'style': self._convert_text_style(text.style) if hasattr(text, 'style') and text.style else {}
        }
    
    def _convert_code_data(self, code) -> Dict[str, Any]:
        """转换代码块数据"""
        return {
            'language': code.language if hasattr(code, 'language') else 1,
            'elements': self._convert_elements(code.elements) if code.elements else []
        }
    
    def _convert_todo_data(self, todo) -> Dict[str, Any]:
        """转换待办数据"""
        return {
            'checked': todo.checked if hasattr(todo, 'checked') else False,
            'elements': self._convert_elements(todo.elements) if todo.elements else []
        }
    
    def _convert_image_data(self, image) -> Dict[str, Any]:
        """转换图片数据"""
        return {
            'token': image.token if hasattr(image, 'token') else '',
            'width': image.width if hasattr(image, 'width') else 0,
            'height': image.height if hasattr(image, 'height') else 0
        }
    
    def _convert_table_data(self, table) -> Dict[str, Any]:
        """转换表格数据"""
        return {
            'property': {
                'row_size': table.property.row_size if hasattr(table, 'property') and hasattr(table.property, 'row_size') else 0,
                'column_size': table.property.column_size if hasattr(table, 'property') and hasattr(table.property, 'column_size') else 0
            }
        }
    
    def _convert_table_cell_data(self, table_cell) -> Dict[str, Any]:
        """转换表格单元格数据
        
        TableCell对象本身不包含内容，实际内容在其children块中。
        根据飞书API的设计，table_cell块的内容通过children关联。
        """
        return {}
    
    def _convert_elements(self, elements) -> List[Dict[str, Any]]:
        """转换元素列表"""
        result = []
        if not elements:
            return result
            
        for element in elements:
            element_data = {}
            
            if hasattr(element, 'text_run') and element.text_run:
                element_data['text_run'] = {
                    'content': element.text_run.content or '',
                    'text_element_style': self._convert_text_element_style(element.text_run.text_element_style) if element.text_run.text_element_style else {}
                }
            elif hasattr(element, 'mention_user') and element.mention_user:
                element_data['mention_user'] = {
                    'user_id': element.mention_user.user_id or '',
                    'text_element_style': self._convert_text_element_style(element.mention_user.text_element_style) if element.mention_user.text_element_style else {}
                }
            elif hasattr(element, 'mention_doc') and element.mention_doc:
                element_data['mention_doc'] = {
                    'token': element.mention_doc.token or '',
                    'obj_type': element.mention_doc.obj_type or 0,
                    'url': element.mention_doc.url or '',
                    'title': element.mention_doc.title or '',
                    'text_element_style': self._convert_text_element_style(element.mention_doc.text_element_style) if element.mention_doc.text_element_style else {}
                }
            elif hasattr(element, 'equation') and element.equation:
                element_data['equation'] = {
                    'content': element.equation.content or ''
                }
            
            if element_data:
                result.append(element_data)
        
        return result
    
    def _convert_text_element_style(self, style) -> Dict[str, Any]:
        """转换文本元素样式"""
        if not style:
            return {}
            
        return {
            'bold': getattr(style, 'bold', False),
            'italic': getattr(style, 'italic', False),
            'strikethrough': getattr(style, 'strikethrough', False),
            'underline': getattr(style, 'underline', False),
            'inline_code': getattr(style, 'inline_code', False),
            'background_color': getattr(style, 'background_color', 0),
            'text_color': getattr(style, 'text_color', 0),
            'link': {
                'url': style.link.url if hasattr(style, 'link') and style.link and hasattr(style.link, 'url') else ''
            } if hasattr(style, 'link') and style.link else {}
        }
    
    def _convert_text_style(self, style) -> Dict[str, Any]:
        """转换文本样式"""
        if not style:
            return {}
            
        return {
            'align': getattr(style, 'align', 1),
            'done': getattr(style, 'done', False),
            'folded': getattr(style, 'folded', False),
            'language': getattr(style, 'language', 1),
            'wrap': getattr(style, 'wrap', False)
        }
    
    def get_all_blocks(self, document_id: str) -> List[Dict[str, Any]]:
        """获取文档的所有块（处理分页）
        
        Args:
            document_id: 文档ID
            
        Returns:
            所有文档块的列表
        """
        all_blocks = []
        page_token = None
        
        while True:
            # 构建请求
            request_builder = ListDocumentBlockRequest.builder().document_id(document_id).page_size(500)
            if page_token:
                request_builder.page_token(page_token)
            
            request = request_builder.build()
            
            # 构建请求选项，设置用户访问令牌
            option = RequestOption.builder().user_access_token(self.user_access_token).build()
            
            # 发起请求
            response: ListDocumentBlockResponse = self.client.docx.v1.document_block.list(request, option)
            
            if not response.success():
                raise Exception(f"API调用失败: {response.code} - {response.msg}")
            
            # 添加当前页的块
            if response.data.items:
                for block in response.data.items:
                    block_data = {
                        'block_id': block.block_id,
                        'block_type': block.block_type,
                        'parent_id': block.parent_id,
                        'children': block.children or []
                    }
                    
                    # 添加块内容（复用之前的转换逻辑）
                    if hasattr(block, 'page') and block.page:
                        block_data['page'] = self._convert_page_data(block.page)
                    elif hasattr(block, 'text') and block.text:
                        block_data['text'] = self._convert_text_data(block.text)
                    # ... 其他块类型的处理逻辑与get_document_blocks相同
                    
                    all_blocks.append(block_data)
            
            # 检查是否还有更多数据
            if not response.data.has_more:
                break
                
            page_token = response.data.page_token
        
        return all_blocks