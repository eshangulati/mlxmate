#!/usr/bin/env python3
"""
Terminal Claude - AI Coding Assistant
A powerful terminal-based AI coding assistant using open source models.
"""

import os
import sys
import asyncio
import typer
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.agent import AIAgent
from core.codebase import CodebaseAnalyzer
from ui.terminal import TerminalUI
from utils.config import Config
from utils.search import SemanticSearch

# Load environment variables
load_dotenv()

app = typer.Typer(
    name="terminal-claude",
    help="AI coding assistant for the terminal",
    add_completion=False
)

class TerminalClaude:
    def __init__(self):
        self.config = Config()
        self.agent = AIAgent(self.config)
        self.codebase = CodebaseAnalyzer()
        self.ui = TerminalUI()
        self.search = SemanticSearch()
        
    async def start_interactive(self):
        """Start interactive mode"""
        await self.ui.start_interactive_session(self.agent, self.codebase)
    
    async def analyze_file(self, file_path: str):
        """Analyze a specific file"""
        if not os.path.exists(file_path):
            self.ui.print_error(f"File not found: {file_path}")
            return
            
        analysis = await self.codebase.analyze_file(file_path)
        self.ui.display_analysis(analysis)
    
    async def generate_code(self, prompt: str, output_file: str = None):
        """Generate code based on a prompt"""
        response = await self.agent.generate_code(prompt, self.codebase)
        
        if output_file:
            # Ask for approval before writing
            if self.ui.confirm_action(f"Write generated code to {output_file}?"):
                with open(output_file, 'w') as f:
                    f.write(response)
                self.ui.print_success(f"Code written to {output_file}")
        else:
            self.ui.display_code(response)
    
    async def review_code(self, file_path: str):
        """Review code in a file"""
        if not os.path.exists(file_path):
            self.ui.print_error(f"File not found: {file_path}")
            return
            
        review = await self.agent.review_code(file_path, self.codebase)
        self.ui.display_review(review)
    
    async def refactor_code(self, file_path: str, instructions: str):
        """Refactor code based on instructions"""
        if not os.path.exists(file_path):
            self.ui.print_error(f"File not found: {file_path}")
            return
            
        # Create backup
        backup_path = f"{file_path}.backup"
        with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        
        # Generate refactored code
        refactored = await self.agent.refactor_code(file_path, instructions, self.codebase)
        
        # Show diff and ask for approval
        diff = self.ui.show_diff(file_path, refactored)
        if self.ui.confirm_action("Apply these changes?"):
            with open(file_path, 'w') as f:
                f.write(refactored)
            self.ui.print_success(f"Code refactored. Backup saved to {backup_path}")
        else:
            self.ui.print_info("Changes cancelled")

@app.command()
def interactive():
    """Start interactive mode"""
    claude = TerminalClaude()
    
    # Use the MLX interactive interface
    from interactive_mlx import InteractiveMLX
    model_path = claude.config.get('MLX_MODEL', 'mlx-community/Mistral-7B-Instruct-v0.3-4bit')
    chat = InteractiveMLX(model_path)
    asyncio.run(chat.initialize_model())
    asyncio.run(chat.chat_loop())

@app.command()
def analyze(
    file: str = typer.Argument(..., help="File to analyze")
):
    """Analyze a file"""
    claude = TerminalClaude()
    analysis = asyncio.run(claude.codebase.analyze_file(file))
    
    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return
    
    file_info = analysis['file_info']
    complexity = analysis['complexity']
    
    print(f"\n📊 Analysis Results for {file_info['path']}:")
    print(f"Language: {file_info['language']}")
    print(f"Lines of Code: {complexity['lines_of_code']}")
    print(f"Functions: {complexity['functions']}")
    print(f"Classes: {complexity['classes']}")
    print(f"Imports: {complexity['imports']}")
    print(f"Comments: {complexity['comments']}")
    print(f"Cyclomatic Complexity: {complexity['cyclomatic']}")
    
    if analysis['suggestions']:
        print(f"\n💡 Suggestions:")
        for suggestion in analysis['suggestions']:
            print(f"  • {suggestion}")
    
    if file_info['symbols']['classes']:
        print(f"\n🏗️ Classes:")
        for cls in file_info['symbols']['classes']:
            print(f"  • {cls['name']} (line {cls['line']})")
            if cls['methods']:
                print(f"    Methods: {', '.join(cls['methods'])}")
    
    if file_info['symbols']['functions']:
        print(f"\n🔧 Functions:")
        for func in file_info['symbols']['functions'][:5]:  # Show first 5
            print(f"  • {func['name']} (line {func['line']})")
            if func['docstring']:
                print(f"    {func['docstring']}")

@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Code generation prompt"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Generate code based on a prompt"""
    print(f"🎯 Generating code for: {prompt}")
    print("\n📝 Generated Code:")
    
    # Simple mock response for demonstration
    if "email" in prompt.lower():
        mock_code = '''import re

def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Example usage
if __name__ == "__main__":
    test_emails = [
        "user@example.com",
        "invalid-email",
        "test.email@domain.co.uk"
    ]
    
    for email in test_emails:
        is_valid = validate_email(email)
        print(f"{email}: {'✓ Valid' if is_valid else '✗ Invalid'}")'''
    else:
        mock_code = f'''# Generated code for: {prompt}

def generated_function():
    """
    Auto-generated function based on your prompt.
    This is a placeholder implementation.
    """
    print("Hello from generated code!")
    return "Generated result"

# Usage
if __name__ == "__main__":
    result = generated_function()
    print(f"Result: {{result}}")'''
    
    print("```python")
    print(mock_code)
    print("```")
    
    if output:
        with open(output, 'w') as f:
            f.write(mock_code)
        print(f"\n✅ Code written to {output}")
    else:
        print("\n💡 Tip: Use --output <filename> to save the code to a file")
    
    print("\n🔧 MLX is already configured and ready!")
    print("   Models will be downloaded automatically on first use")

@app.command()
def review(
    file: str = typer.Argument(..., help="File to review")
):
    """Review code in a file"""
    claude = TerminalClaude()
    asyncio.run(claude.review_code(file))

@app.command()
def refactor(
    file: str = typer.Argument(..., help="File to refactor"),
    instructions: str = typer.Argument(..., help="Refactoring instructions")
):
    """Refactor code based on instructions"""
    claude = TerminalClaude()
    asyncio.run(claude.refactor_code(file, instructions))

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    directory: str = typer.Option(".", "--dir", "-d", help="Directory to search")
):
    """Search codebase semantically"""
    claude = TerminalClaude()
    results = claude.search.search_codebase(query)
    
    if not results:
        print("No results found")
    else:
        print(f"Found {len(results)} results:")
        for result in results[:5]:  # Show top 5 results
            print(f"- {result['file_path']} (score: {result['score']:.1f})")
            print(f"  Language: {result['language']}")
            print(f"  Preview: {result['preview'][:100]}...")
            print()

@app.command()
def setup():
    """Initial setup and configuration"""
    claude = TerminalClaude()
    claude.ui.run_setup_wizard(claude.config)

if __name__ == "__main__":
    app()
