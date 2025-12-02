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
        current_list = None
        
        for i, line in enumerate(lines):
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
            if self.table_pattern.match(line):
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
            list_match = self.list_item_pattern.match(line)
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