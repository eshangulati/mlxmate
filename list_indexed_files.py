#!/usr/bin/env python3
"""
Simple script to show what files are being indexed by MLXMate
"""

import os
from pathlib import Path

def get_code_files(root_path="."):
    """Get all code files that would be indexed"""
    code_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
        '.scala', '.clj', '.hs', '.ml', '.fs', '.dart', '.r', '.m', '.mm'
    }
    
    files = []
    root_path = Path(root_path).resolve()
    
    for root, dirs, filenames in os.walk(root_path):
        # Skip common directories to ignore
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
            'node_modules', '__pycache__', '.git', 'build', 'dist', 'target',
            'venv', 'env', '.venv', '.env', 'bin', 'obj'
        }]
        
        for filename in filenames:
            if Path(filename).suffix in code_extensions:
                file_path = Path(root) / filename
                relative_path = file_path.relative_to(root_path)
                files.append(str(relative_path))
    
    return files

if __name__ == "__main__":
    print("🔍 Files that would be indexed by MLXMate:")
    print("=" * 50)
    
    # Use current working directory
    import os
    current_dir = os.getcwd()
    print(f"📁 Analyzing directory: {current_dir}")
    print()
    
    indexed_files = get_code_files(current_dir)
    
    if not indexed_files:
        print("No code files found in current directory!")
    else:
        for i, file_path in enumerate(sorted(indexed_files), 1):
            print(f"{i:2d}. {file_path}")
        
        print(f"\n📊 Total: {len(indexed_files)} files")
        
        # Show file types breakdown
        extensions = {}
        for file_path in indexed_files:
            ext = Path(file_path).suffix
            extensions[ext] = extensions.get(ext, 0) + 1
        
        print("\n📈 File types breakdown:")
        for ext, count in sorted(extensions.items()):
            print(f"   {ext}: {count} files")
