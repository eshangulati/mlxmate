"""
Codebase Analyzer - Agentic search and codebase understanding
Provides intelligent analysis of the entire codebase without manual context selection.
"""

import os
import re
import ast
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict
import git
from fuzzywuzzy import fuzz


class CodebaseAnalyzer:
    """Analyzes and understands the entire codebase structure"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.file_index = {}
        self.symbol_index = {}
        self.dependency_graph = defaultdict(set)
        self.coding_standards = {}
        self.file_watchers = {}
        self._build_index()
    
    def _build_index(self):
        """Build comprehensive index of the codebase"""
        print("🔍 Building codebase index...")
        
        for file_path in self._get_code_files():
            try:
                self._index_file(file_path)
            except Exception as e:
                print(f"Warning: Could not index {file_path}: {e}")
        
        self._analyze_dependencies()
        self._detect_coding_standards()
        print(f"✅ Indexed {len(self.file_index)} files")
    
    def _get_code_files(self) -> List[Path]:
        """Get all code files in the codebase"""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
            '.scala', '.clj', '.hs', '.ml', '.fs', '.dart', '.r', '.m', '.mm'
        }
        
        files = []
        for root, dirs, filenames in os.walk(self.root_path):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                'node_modules', '__pycache__', '.git', 'build', 'dist', 'target',
                'venv', 'env', '.venv', '.env', 'bin', 'obj'
            }]
            
            for filename in filenames:
                if Path(filename).suffix in code_extensions:
                    files.append(Path(root) / filename)
        
        return files
    
    def _index_file(self, file_path: Path):
        """Index a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = file_path.relative_to(self.root_path)
            
            # Basic file info
            self.file_index[str(relative_path)] = {
                'path': str(relative_path),
                'absolute_path': str(file_path),
                'content': content,
                'size': len(content),
                'language': self._detect_language(file_path),
                'symbols': self._extract_symbols(content, file_path),
                'imports': self._extract_imports(content, file_path),
                'functions': self._extract_functions(content, file_path),
                'classes': self._extract_classes(content, file_path),
                'comments': self._extract_comments(content, file_path),
                'last_modified': file_path.stat().st_mtime
            }
            
            # Index symbols (simplified to avoid dict key issues)
            try:
                for symbol_type, symbols in self.file_index[str(relative_path)]['symbols'].items():
                    for symbol in symbols:
                        if isinstance(symbol, dict) and 'name' in symbol:
                            symbol_name = symbol['name']
                            self.symbol_index[symbol_name] = {
                                'file': str(relative_path),
                                'type': symbol_type,
                                'line': symbol.get('line', 0)
                            }
            except Exception as e:
                print(f"Error indexing symbols for {file_path}: {e}")
                    
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
    
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
        
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbols['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or ""
                    })
                elif isinstance(node, ast.ClassDef):
                    symbols['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'docstring': ast.get_docstring(node) or ""
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        symbols['imports'].append({
                            'module': alias.name,
                            'alias': alias.asname or "",
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    symbols['imports'].append({
                        'module': node.module or '',
                        'names': [alias.name for alias in node.names],
                        'line': node.lineno
                    })
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            symbols['variables'].append({
                                'name': target.id,
                                'line': node.lineno
                            })
        except:
            pass
        
        return symbols
    
    def _extract_js_symbols(self, content: str) -> Dict[str, List]:
        """Extract symbols from JavaScript/TypeScript code"""
        symbols = {
            'functions': [],
            'classes': [],
            'variables': [],
            'imports': []
        }
        
        # Extract imports
        import_patterns = [
            r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s*\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'const\s+(\w+)\s*=\s*require\s*\([\'"]([^\'"]+)[\'"]\)'
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                symbols['imports'].append({
                    'module': match.group(2) if len(match.groups()) > 1 else match.group(1),
                    'line': content[:match.start()].count('\n') + 1
                })
        
        # Extract functions
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
        
        # Extract classes
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            symbols['classes'].append({
                'name': match.group(1),
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
        
        # Extract imports
        import_pattern = r'import\s+([^;]+);'
        for match in re.finditer(import_pattern, content):
            symbols['imports'].append({
                'module': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Extract classes
        class_pattern = r'(?:public\s+)?class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            symbols['classes'].append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Extract methods
        method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*\('
        for match in re.finditer(method_pattern, content):
            symbols['functions'].append({
                'name': match.group(2),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return symbols
    
    def _extract_imports(self, content: str, file_path: Path) -> List[str]:
        """Extract import statements"""
        language = self._detect_language(file_path)
        
        if language == 'python':
            return self._extract_python_imports(content)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_imports(content)
        elif language == 'java':
            return self._extract_java_imports(content)
        
        return []
    
    def _extract_python_imports(self, content: str) -> List[str]:
        """Extract Python imports"""
        imports = []
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            pass
        return imports
    
    def _extract_js_imports(self, content: str) -> List[str]:
        """Extract JavaScript/TypeScript imports"""
        imports = []
        patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'const\s+.*\s*=\s*require\s*\([\'"]([^\'"]+)[\'"]\)'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                imports.append(match.group(1))
        
        return imports
    
    def _extract_java_imports(self, content: str) -> List[str]:
        """Extract Java imports"""
        imports = []
        pattern = r'import\s+([^;]+);'
        for match in re.finditer(pattern, content):
            imports.append(match.group(1))
        return imports
    
    def _extract_functions(self, content: str, file_path: Path) -> List[Dict]:
        """Extract function definitions"""
        return self._extract_symbols(content, file_path)['functions']
    
    def _extract_classes(self, content: str, file_path: Path) -> List[Dict]:
        """Extract class definitions"""
        return self._extract_symbols(content, file_path)['classes']
    
    def _extract_comments(self, content: str, file_path: Path) -> List[str]:
        """Extract comments from code"""
        language = self._detect_language(file_path)
        comments = []
        
        if language == 'python':
            # Python comments
            for line in content.split('\n'):
                if '#' in line:
                    comment = line.split('#')[1].strip()
                    if comment:
                        comments.append(comment)
        elif language in ['javascript', 'typescript', 'java', 'cpp', 'c']:
            # C-style comments
            # Single line comments
            for line in content.split('\n'):
                if '//' in line:
                    comment = line.split('//')[1].strip()
                    if comment:
                        comments.append(comment)
            
            # Multi-line comments
            pattern = r'/\*([^*]|\*(?!/))*\*/'
            for match in re.finditer(pattern, content, re.DOTALL):
                comments.append(match.group(1).strip())
        
        return comments
    
    def _analyze_dependencies(self):
        """Analyze dependencies between files"""
        for file_path, file_info in self.file_index.items():
            for import_name in file_info['imports']:
                # Find files that might be imported
                for other_file, other_info in self.file_index.items():
                    if self._is_import_match(import_name, other_file):
                        self.dependency_graph[file_path].add(other_file)
    
    def _is_import_match(self, import_name: str, file_path: str) -> bool:
        """Check if an import matches a file path"""
        # Simple heuristic - can be improved
        file_name = Path(file_path).stem
        return import_name.endswith(file_name) or file_name in import_name
    
    def _detect_coding_standards(self):
        """Detect coding standards from the codebase"""
        standards = {
            'indentation': self._detect_indentation_style(),
            'naming_conventions': self._detect_naming_conventions(),
            'line_length': self._detect_line_length(),
            'comment_style': self._detect_comment_style()
        }
        self.coding_standards = standards
    
    def _detect_indentation_style(self) -> str:
        """Detect indentation style (spaces vs tabs)"""
        space_count = 0
        tab_count = 0
        
        for file_info in self.file_index.values():
            content = file_info['content']
            for line in content.split('\n'):
                if line.startswith(' '):
                    space_count += 1
                elif line.startswith('\t'):
                    tab_count += 1
        
        return 'spaces' if space_count > tab_count else 'tabs'
    
    def _detect_naming_conventions(self) -> Dict[str, str]:
        """Detect naming conventions"""
        conventions = {}
        
        # Analyze function names
        function_names = []
        for file_info in self.file_index.values():
            function_names.extend([f['name'] for f in file_info['functions']])
        
        if function_names:
            snake_case = sum(1 for name in function_names if '_' in name)
            camel_case = sum(1 for name in function_names if name and name[0].islower() and any(c.isupper() for c in name))
            
            if snake_case > camel_case:
                conventions['functions'] = 'snake_case'
            else:
                conventions['functions'] = 'camelCase'
        
        return conventions
    
    def _detect_line_length(self) -> int:
        """Detect typical line length"""
        line_lengths = []
        for file_info in self.file_index.values():
            for line in file_info['content'].split('\n'):
                line_lengths.append(len(line))
        
        if line_lengths:
            return sorted(line_lengths)[len(line_lengths) // 2]  # Median
        return 80
    
    def _detect_comment_style(self) -> str:
        """Detect comment style"""
        # Simple heuristic based on language distribution
        languages = [info['language'] for info in self.file_index.values()]
        if 'python' in languages:
            return 'hash'
        else:
            return 'slash'
    
    async def get_relevant_context(self, query: str) -> Dict[str, Any]:
        """Get relevant context for a query using semantic search"""
        query_lower = query.lower()
        
        # Check if this is a directory or file path query
        if '/' in query or 'directory' in query_lower or 'folder' in query_lower:
            # Directory/file path query - return all files in that directory
            relevant_files = self._directory_search(query)
        else:
            # Semantic query - use semantic search
            relevant_files = self._semantic_search(query)
        
        context = {
            'relevant_files': [],
            'related_symbols': [],
            'codebase_summary': self._generate_codebase_summary(),
            'coding_standards': self.coding_standards
        }
        
        for file_path in relevant_files[:10]:  # Increased to top 10 for directory queries
            if file_path in self.file_index:
                file_info = self.file_index[file_path]
                context['relevant_files'].append({
                    'path': file_path,
                    'content': file_info['content'][:2000],  # Limit content size
                    'symbols': file_info['symbols'],
                    'language': file_info['language']
                })
        
        return context
    
    def _semantic_search(self, query: str) -> List[str]:
        """Perform semantic search on the codebase"""
        query_lower = query.lower()
        scores = []
        
        for file_path, file_info in self.file_index.items():
            score = 0
            
            # Score based on file name
            file_name = Path(file_path).name.lower()
            score += fuzz.partial_ratio(query_lower, file_name) * 0.3
            
            # Score based on content
            content_lower = file_info['content'].lower()
            score += fuzz.partial_ratio(query_lower, content_lower) * 0.4
            
            # Score based on symbols
            for symbol_type, symbols in file_info['symbols'].items():
                for symbol in symbols:
                    symbol_name = symbol.get('name', '').lower()
                    score += fuzz.partial_ratio(query_lower, symbol_name) * 0.2
            
            # Score based on comments
            for comment in file_info.get('comments', []):
                comment_lower = comment.lower()
                score += fuzz.partial_ratio(query_lower, comment_lower) * 0.1
            
            scores.append((file_path, score))
        
        # Sort by score and return file paths
        scores.sort(key=lambda x: x[1], reverse=True)
        return [file_path for file_path, score in scores if score > 30]
    
    def _directory_search(self, query: str) -> List[str]:
        """Search for files in a specific directory"""
        query_lower = query.lower()
        matching_files = []
        
        for file_path in self.file_index.keys():
            file_path_lower = file_path.lower()
            
            # Check if the query matches the directory path
            if query_lower in file_path_lower:
                matching_files.append(file_path)
        
        # Sort by path for consistent results
        matching_files.sort()
        return matching_files
    
    def _generate_codebase_summary(self) -> Dict[str, Any]:
        """Generate a summary of the codebase"""
        total_files = len(self.file_index)
        total_lines = sum(len(info['content'].split('\n')) for info in self.file_index.values())
        
        languages = {}
        for info in self.file_index.values():
            lang = info['language']
            languages[lang] = languages.get(lang, 0) + 1
        
        total_functions = sum(len(info['functions']) for info in self.file_index.values())
        total_classes = sum(len(info['classes']) for info in self.file_index.values())
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'languages': languages,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'root_path': str(self.root_path)
        }
    
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a specific file"""
        if file_path not in self.file_index:
            return {'error': 'File not found in index'}
        
        file_info = self.file_index[file_path]
        
        analysis = {
            'file_info': file_info,
            'complexity': self._calculate_complexity(file_info),
            'dependencies': list(self.dependency_graph.get(file_path, [])),
            'suggestions': await self._generate_suggestions(file_info)
        }
        
        return analysis
    
    def _calculate_complexity(self, file_info: Dict) -> Dict[str, int]:
        """Calculate code complexity metrics"""
        content = file_info['content']
        lines = content.split('\n')
        
        complexity = {
            'lines_of_code': len(lines),
            'functions': len(file_info['functions']),
            'classes': len(file_info['classes']),
            'imports': len(file_info['imports']),
            'comments': len(file_info.get('comments', []))
        }
        
        # Calculate cyclomatic complexity (simplified)
        complexity['cyclomatic'] = self._calculate_cyclomatic_complexity(content)
        
        return complexity
    
    def _calculate_cyclomatic_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_patterns = [
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
            r'\band\b', r'\bor\b', r'\bcase\b', r'\bcatch\b'
        ]
        
        for pattern in decision_patterns:
            complexity += len(re.findall(pattern, content, re.IGNORECASE))
        
        return complexity
    
    async def _generate_suggestions(self, file_info: Dict) -> List[str]:
        """Generate improvement suggestions for a file"""
        suggestions = []
        
        # Check for long functions
        for func in file_info['functions']:
            if func.get('line', 0) > 50:  # Arbitrary threshold
                suggestions.append(f"Function '{func['name']}' might be too long")
        
        # Check for missing docstrings
        if file_info['language'] == 'python':
            for func in file_info['functions']:
                if not func.get('docstring'):
                    suggestions.append(f"Function '{func['name']}' lacks docstring")
        
        # Check for unused imports
        if len(file_info['imports']) > 10:
            suggestions.append("Consider reducing the number of imports")
        
        return suggestions
    
    def get_coding_standards(self) -> Dict[str, Any]:
        """Get detected coding standards"""
        return self.coding_standards
    
    def refresh_index(self):
        """Refresh the codebase index"""
        self.file_index.clear()
        self.symbol_index.clear()
        self.dependency_graph.clear()
        self._build_index()
    
    def watch_file(self, file_path: str, callback):
        """Watch a file for changes"""
        # This would integrate with watchdog for file watching
        pass
