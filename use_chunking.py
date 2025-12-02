#!/usr/bin/env python3
"""使用 chunking.py 中的方法分析 objectname.md"""
import re
import json
from typing import Dict, Any


class DocumentAnalyzer:
    """文档结构分析器"""
    
    def __init__(self):
        # 初始化正则表达式模式
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$')  # 匹配 # 标题
        self.table_pattern = re.compile(r'^\|.+\|')  # 匹配表格行
        self.list_item_pattern = re.compile(r'^[\s]*[-*+]\s+|^\s*\d+\.\s+')  # 匹配列表项
    
    def _analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """Analyze document structure for better chunking decisions."""
        lines = content.split('\n')
        
        structure = {
            'headers': [],
            'code_blocks': [],
            'tables': [],
            'lists': [],
            'paragraphs': [],
            'total_lines': len(lines)
        }
        
        in_code_block = False
        in_table = False
        in_front_matter = False  # YAML front matter
        current_list = None
        current_paragraph = None  # 当前段落
        
        for i, line in enumerate(lines):
            is_special = False
            
            # YAML Front Matter (--- 包围的内容)
            if line.strip() == '---':
                if not in_front_matter:
                    in_front_matter = True
                else:
                    in_front_matter = False
                is_special = True
                continue
            
            if in_front_matter:
                is_special = True
                continue
            
            # Headers
            header_match = self.header_pattern.match(line)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2).strip()
                structure['headers'].append({
                    'line': i,
                    'level': level,
                    'text': text
                })
                is_special = True
                # 结束当前段落
                if current_paragraph is not None:
                    current_paragraph['end'] = i - 1
                    structure['paragraphs'].append(current_paragraph)
                    current_paragraph = None
                continue
            
            # Code blocks
            if line.strip().startswith('```'):
                if not in_code_block:
                    code_start = i
                    in_code_block = True
                    # 结束当前段落
                    if current_paragraph is not None:
                        current_paragraph['end'] = i - 1
                        structure['paragraphs'].append(current_paragraph)
                        current_paragraph = None
                else:
                    structure['code_blocks'].append({
                        'start': code_start,
                        'end': i
                    })
                    in_code_block = False
                is_special = True
                continue
            
            if in_code_block:
                is_special = True
                continue
            
            # Tables
            if self.table_pattern.match(line):
                if not in_table:
                    table_start = i
                    in_table = True
                    # 结束当前段落
                    if current_paragraph is not None:
                        current_paragraph['end'] = i - 1
                        structure['paragraphs'].append(current_paragraph)
                        current_paragraph = None
                is_special = True
            elif in_table and not line.strip():
                structure['tables'].append({
                    'start': table_start,
                    'end': i - 1
                })
                in_table = False
                is_special = True
            
            if in_table:
                is_special = True
                continue
            
            # Lists
            list_match = self.list_item_pattern.match(line)
            if list_match:
                if current_list is None:
                    current_list = {'start': i, 'items': []}
                    # 结束当前段落
                    if current_paragraph is not None:
                        current_paragraph['end'] = i - 1
                        structure['paragraphs'].append(current_paragraph)
                        current_paragraph = None
                current_list['items'].append(i)
                is_special = True
            elif current_list and not line.strip().startswith(' '):
                # End of list
                current_list['end'] = i - 1
                structure['lists'].append(current_list)
                current_list = None
            
            if current_list is not None:
                is_special = True
                continue
            
            # 段落识别：不是特殊结构，不是空行
            if not is_special:
                if line.strip():  # 非空行
                    if current_paragraph is None:
                        current_paragraph = {'start': i, 'end': i}
                    else:
                        current_paragraph['end'] = i
                else:  # 空行，结束当前段落
                    if current_paragraph is not None:
                        structure['paragraphs'].append(current_paragraph)
                        current_paragraph = None
        
        # Handle unclosed structures
        if in_table:
            structure['tables'].append({'start': table_start, 'end': len(lines) - 1})
        if current_list:
            current_list['end'] = len(lines) - 1
            structure['lists'].append(current_list)
        if current_paragraph:
            current_paragraph['end'] = len(lines) - 1
            structure['paragraphs'].append(current_paragraph)
        
        return structure


if __name__ == "__main__":
    # 创建分析器实例
    analyzer = DocumentAnalyzer()
    
    # 读取 objectname.md 文件
    filename = "objectname.md"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分析文档结构
        structure = analyzer._analyze_document_structure(content)
        
        # 输出 structure（JSON 格式，便于查看）
        print(json.dumps(structure, ensure_ascii=False, indent=2))
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {filename}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

