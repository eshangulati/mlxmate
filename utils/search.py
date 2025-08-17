"""
Semantic Search - Intelligent codebase search and understanding
Provides semantic search capabilities for finding relevant code.
"""

import re
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from fuzzywuzzy import fuzz
from collections import defaultdict


class SemanticSearch:
    """Semantic search for codebase understanding"""
    
    def __init__(self):
        self.index = {}
        self.file_contents = {}
        self.symbols = {}
        self.keywords = defaultdict(list)
    
    def index_codebase(self, root_path: str = "."):
        """Index the entire codebase for search"""
        root = Path(root_path).resolve()
        
        # Supported file extensions
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt'
        }
        
        print("🔍 Indexing codebase for semantic search...")
        
        for file_path in root.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                # Skip common directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(part in {'node_modules', '__pycache__', '.git', 'build', 'dist'} for part in file_path.parts):
                    continue
                
                self._index_file(file_path, root)
        
        print(f"✅ Indexed {len(self.index)} files for semantic search")
    
    def _index_file(self, file_path: Path, root_path: Path):
        """Index a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = str(file_path.relative_to(root_path))
            
            # Store file content
            self.file_contents[relative_path] = content
            
            # Extract and index symbols
            symbols = self._extract_symbols(content, file_path)
            self.symbols[relative_path] = symbols
            
            # Index keywords
            self._index_keywords(content, relative_path)
            
            # Create search index
            self.index[relative_path] = {
                'path': relative_path,
                'language': self._detect_language(file_path),
                'symbols': symbols,
                'content': content,
                'size': len(content),
                'lines': content.count('\n') + 1
            }
            
        except Exception as e:
            print(f"Warning: Could not index {file_path}: {e}")
    
    def _extract_symbols(self, content: str, file_path: Path) -> Dict[str, List]:
        """Extract symbols from code content"""
        symbols = {
            'functions': [],
            'classes': [],
            'variables': [],
            'imports': []
        }
        
        language = self._detect_language(file_path)
        
        if language == 'python':
            symbols = self._extract_python_symbols(content)
        elif language in ['javascript', 'typescript']:
            symbols = self._extract_js_symbols(content)
        elif language == 'java':
            symbols = self._extract_java_symbols(content)
        
        return symbols
    
    def _extract_python_symbols(self, content: str) -> Dict[str, List]:
        """Extract symbols from Python code"""
        symbols = {
            'functions': [],
            'classes': [],
            'variables': [],
            'imports': []
        }
        
        # Function definitions
        function_pattern = r'def\s+(\w+)\s*\('
        for match in re.finditer(function_pattern, content):
            symbols['functions'].append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Class definitions
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            symbols['classes'].append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Import statements
        import_patterns = [
            r'import\s+(\w+)',
            r'from\s+(\w+)\s+import',
            r'import\s+(\w+)\s+as\s+\w+'
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                symbols['imports'].append({
                    'module': match.group(1),
                    'line': content[:match.start()].count('\n') + 1
                })
        
        return symbols
    
    def _extract_js_symbols(self, content: str) -> Dict[str, List]:
        """Extract symbols from JavaScript/TypeScript code"""
        symbols = {
            'functions': [],
            'classes': [],
            'variables': [],
            'imports': []
        }
        
        # Function definitions
        function_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
            r'(\w+)\s*\([^)]*\)\s*\{'
        ]
        
        for pattern in function_patterns:
            for match in re.finditer(pattern, content):
                symbols['functions'].append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1
                })
        
        # Class definitions
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            symbols['classes'].append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Import statements
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'const\s+.*\s*=\s*require\s*\([\'"]([^\'"]+)[\'"]\)'
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                symbols['imports'].append({
                    'module': match.group(1),
                    'line': content[:match.start()].count('\n') + 1
                })
        
        return symbols
    
    def _extract_java_symbols(self, content: str) -> Dict[str, List]:
        """Extract symbols from Java code"""
        symbols = {
            'functions': [],
            'classes': [],
            'variables': [],
            'imports': []
        }
        
        # Class definitions
        class_pattern = r'(?:public\s+)?class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            symbols['classes'].append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Method definitions
        method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*\('
        for match in re.finditer(method_pattern, content):
            symbols['functions'].append({
                'name': match.group(2),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Import statements
        import_pattern = r'import\s+([^;]+);'
        for match in re.finditer(import_pattern, content):
            symbols['imports'].append({
                'module': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return symbols
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.jsx': 'javascript', '.tsx': 'typescript', '.java': 'java',
            '.cpp': 'cpp', '.c': 'c', '.h': 'c', '.hpp': 'cpp',
            '.cs': 'csharp', '.php': 'php', '.rb': 'ruby', '.go': 'go',
            '.rs': 'rust', '.swift': 'swift', '.kt': 'kotlin'
        }
        return language_map.get(ext, 'unknown')
    
    def _index_keywords(self, content: str, file_path: str):
        """Index keywords from content"""
        # Extract meaningful words (camelCase, snake_case, etc.)
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', content)
        
        for word in words:
            if len(word) > 2:  # Skip very short words
                self.keywords[word.lower()].append(file_path)
    
    def search_codebase(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search the codebase semantically"""
        query_lower = query.lower()
        results = []
        
        for file_path, file_info in self.index.items():
            score = 0
            
            # Score based on file name
            file_name = Path(file_path).name.lower()
            score += fuzz.partial_ratio(query_lower, file_name) * 0.2
            
            # Score based on content
            content_lower = file_info['content'].lower()
            score += fuzz.partial_ratio(query_lower, content_lower) * 0.3
            
            # Score based on symbols
            for symbol_type, symbols in file_info['symbols'].items():
                for symbol in symbols:
                    symbol_name = symbol.get('name', '').lower()
                    score += fuzz.partial_ratio(query_lower, symbol_name) * 0.2
            
            # Score based on keywords
            query_words = query_lower.split()
            for word in query_words:
                if word in self.keywords and file_path in self.keywords[word]:
                    score += 10
            
            # Score based on language relevance
            if any(word in query_lower for word in ['python', 'py', 'js', 'javascript', 'java', 'cpp']):
                if file_info['language'] in query_lower:
                    score += 20
            
            if score > 30:  # Minimum relevance threshold
                results.append({
                    'file_path': file_path,
                    'score': score,
                    'language': file_info['language'],
                    'symbols': file_info['symbols'],
                    'preview': self._get_content_preview(file_info['content'], query)
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def _get_content_preview(self, content: str, query: str, max_length: int = 200) -> str:
        """Get a preview of content around the query"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Find the first occurrence of the query
        pos = content_lower.find(query_lower)
        if pos == -1:
            # If not found, return the beginning
            return content[:max_length] + "..." if len(content) > max_length else content
        
        # Get context around the match
        start = max(0, pos - max_length // 2)
        end = min(len(content), pos + max_length // 2)
        
        preview = content[start:end]
        if start > 0:
            preview = "..." + preview
        if end < len(content):
            preview = preview + "..."
        
        return preview
    
    def search_functions(self, function_name: str) -> List[Dict[str, Any]]:
        """Search for specific functions"""
        results = []
        function_name_lower = function_name.lower()
        
        for file_path, file_info in self.index.items():
            for func in file_info['symbols'].get('functions', []):
                if fuzz.ratio(function_name_lower, func['name'].lower()) > 70:
                    results.append({
                        'file_path': file_path,
                        'function_name': func['name'],
                        'line': func['line'],
                        'language': file_info['language'],
                        'score': fuzz.ratio(function_name_lower, func['name'].lower())
                    })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def search_classes(self, class_name: str) -> List[Dict[str, Any]]:
        """Search for specific classes"""
        results = []
        class_name_lower = class_name.lower()
        
        for file_path, file_info in self.index.items():
            for cls in file_info['symbols'].get('classes', []):
                if fuzz.ratio(class_name_lower, cls['name'].lower()) > 70:
                    results.append({
                        'file_path': file_path,
                        'class_name': cls['name'],
                        'line': cls['line'],
                        'language': file_info['language'],
                        'score': fuzz.ratio(class_name_lower, cls['name'].lower())
                    })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def search_imports(self, module_name: str) -> List[Dict[str, Any]]:
        """Search for specific imports"""
        results = []
        module_name_lower = module_name.lower()
        
        for file_path, file_info in self.index.items():
            for imp in file_info['symbols'].get('imports', []):
                if fuzz.ratio(module_name_lower, imp['module'].lower()) > 70:
                    results.append({
                        'file_path': file_path,
                        'module': imp['module'],
                        'line': imp['line'],
                        'language': file_info['language'],
                        'score': fuzz.ratio(module_name_lower, imp['module'].lower())
                    })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def get_related_files(self, file_path: str) -> List[Dict[str, Any]]:
        """Get files related to a specific file"""
        if file_path not in self.index:
            return []
        
        file_info = self.index[file_path]
        related = []
        
        # Find files with similar imports
        imports = [imp['module'] for imp in file_info['symbols'].get('imports', [])]
        
        for other_path, other_info in self.index.items():
            if other_path == file_path:
                continue
            
            # Check for shared imports
            other_imports = [imp['module'] for imp in other_info['symbols'].get('imports', [])]
            shared_imports = set(imports) & set(other_imports)
            
            if shared_imports:
                related.append({
                    'file_path': other_path,
                    'shared_imports': list(shared_imports),
                    'language': other_info['language'],
                    'relevance': len(shared_imports)
                })
        
        related.sort(key=lambda x: x['relevance'], reverse=True)
        return related[:5]
    
    def get_codebase_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed codebase"""
        stats = {
            'total_files': len(self.index),
            'languages': {},
            'total_functions': 0,
            'total_classes': 0,
            'total_imports': 0,
            'total_lines': 0
        }
        
        for file_info in self.index.values():
            # Language stats
            lang = file_info['language']
            stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
            
            # Symbol stats
            symbols = file_info['symbols']
            stats['total_functions'] += len(symbols.get('functions', []))
            stats['total_classes'] += len(symbols.get('classes', []))
            stats['total_imports'] += len(symbols.get('imports', []))
            
            # Line count
            stats['total_lines'] += file_info['lines']
        
        return stats
    
    def clear_index(self):
        """Clear the search index"""
        self.index.clear()
        self.file_contents.clear()
        self.symbols.clear()
        self.keywords.clear()
    
    def update_file(self, file_path: str, content: str):
        """Update a file in the index"""
        file_path_obj = Path(file_path)
        
        # Remove old index entry
        if file_path in self.index:
            old_symbols = self.index[file_path]['symbols']
            for symbol_type, symbols in old_symbols.items():
                for symbol in symbols:
                    symbol_name = symbol.get('name', '').lower()
                    if symbol_name in self.keywords and file_path in self.keywords[symbol_name]:
                        self.keywords[symbol_name].remove(file_path)
        
        # Re-index the file
        self._index_file(file_path_obj, file_path_obj.parent)
    
    def remove_file(self, file_path: str):
        """Remove a file from the index"""
        if file_path in self.index:
            # Remove from main index
            del self.index[file_path]
            
            # Remove from file contents
            if file_path in self.file_contents:
                del self.file_contents[file_path]
            
            # Remove from symbols
            if file_path in self.symbols:
                del self.symbols[file_path]
            
            # Remove from keywords
            for keyword, files in self.keywords.items():
                if file_path in files:
                    files.remove(file_path)
