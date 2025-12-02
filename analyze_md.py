#!/usr/bin/env python3
"""分析 Markdown 文档结构"""
import re
from typing import Dict, Any


def analyze_document_structure(content: str) -> Dict[str, Any]:
    """Analyze document structure for better chunking decisions."""
    lines = content.split('\n')
    
    # 正则表达式模式
    header_pattern = re.compile(r'^(#{1,6})\s+(.+)$')  # 匹配 # 标题
    table_pattern = re.compile(r'^\|.+\|')  # 匹配表格行
    list_item_pattern = re.compile(r'^[\s]*[-*+]\s+|^\s*\d+\.\s+')  # 匹配列表项
    
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
    current_list = None
    
    for i, line in enumerate(lines):
        # Headers
        header_match = header_pattern.match(line)
        if header_match:
            level = len(header_match.group(1))
            text = header_match.group(2).strip()
            structure['headers'].append({
                'line': i,
                'level': level,
                'text': text
            })
            continue
        
        # Code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                code_start = i
                in_code_block = True
            else:
                structure['code_blocks'].append({
                    'start': code_start,
                    'end': i
                })
                in_code_block = False
            continue
        
        # Tables
        if table_pattern.match(line):
            if not in_table:
                table_start = i
                in_table = True
        elif in_table and not line.strip():
            structure['tables'].append({
                'start': table_start,
                'end': i - 1
            })
            in_table = False
        
        # Lists
        list_match = list_item_pattern.match(line)
        if list_match:
            if current_list is None:
                current_list = {'start': i, 'items': []}
            current_list['items'].append(i)
        elif current_list and not line.strip().startswith(' '):
            # End of list
            current_list['end'] = i - 1
            structure['lists'].append(current_list)
            current_list = None
    
    # Handle unclosed structures
    if in_table:
        structure['tables'].append({'start': table_start, 'end': len(lines) - 1})
    if current_list:
        current_list['end'] = len(lines) - 1
        structure['lists'].append(current_list)
    
    return structure


def print_analysis(structure: Dict[str, Any], filename: str):
    """打印分析结果"""
    print(f"\n{'='*60}")
    print(f"文档结构分析: {filename}")
    print(f"{'='*60}\n")
    
    print(f"📄 总行数: {structure['total_lines']}\n")
    
    # 标题统计
    print(f"📑 标题统计: {len(structure['headers'])} 个")
    if structure['headers']:
        print("\n标题列表:")
        for header in structure['headers']:
            indent = "  " * (header['level'] - 1)
            print(f"  {indent}L{header['level']} [{header['line']:4d}] {header['text']}")
    print()
    
    # 代码块统计
    print(f"💻 代码块统计: {len(structure['code_blocks'])} 个")
    if structure['code_blocks']:
        print("\n代码块位置:")
        for i, block in enumerate(structure['code_blocks'], 1):
            print(f"  [{i}] 行 {block['start']} - {block['end']} (共 {block['end'] - block['start'] + 1} 行)")
    print()
    
    # 表格统计
    print(f"📊 表格统计: {len(structure['tables'])} 个")
    if structure['tables']:
        print("\n表格位置:")
        for i, table in enumerate(structure['tables'], 1):
            print(f"  [{i}] 行 {table['start']} - {table['end']} (共 {table['end'] - table['start'] + 1} 行)")
    print()
    
    # 列表统计
    print(f"📋 列表统计: {len(structure['lists'])} 个")
    if structure['lists']:
        print("\n列表位置:")
        for i, lst in enumerate(structure['lists'], 1):
            print(f"  [{i}] 行 {lst['start']} - {lst['end']} (共 {len(lst['items'])} 项)")
    print()
    
    # 结构概览
    print(f"{'='*60}")
    print("结构概览:")
    print(f"{'='*60}")
    print(f"  • 一级标题 (H1): {sum(1 for h in structure['headers'] if h['level'] == 1)} 个")
    print(f"  • 二级标题 (H2): {sum(1 for h in structure['headers'] if h['level'] == 2)} 个")
    print(f"  • 三级标题 (H3): {sum(1 for h in structure['headers'] if h['level'] == 3)} 个")
    print(f"  • 代码块: {len(structure['code_blocks'])} 个")
    print(f"  • 表格: {len(structure['tables'])} 个")
    print(f"  • 列表: {len(structure['lists'])} 个")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # 读取文件
    filename = "objectname.md"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分析文档结构
        structure = analyze_document_structure(content)
        
        # 打印分析结果
        print_analysis(structure, filename)
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {filename}")
    except Exception as e:
        print(f"错误: {e}")

