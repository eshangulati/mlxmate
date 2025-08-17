"""
Terminal UI - Rich terminal interface for the AI assistant
Provides beautiful, responsive terminal interface with interactive features.
"""

import asyncio
import sys
from typing import Dict, List, Optional, Any
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
import difflib

from .prompts import PromptTemplates


class TerminalUI:
    """Rich terminal interface for the AI assistant"""
    
    def __init__(self):
        self.console = Console()
        self.session = PromptSession()
        self.prompts = PromptTemplates()
        self.style = Style.from_dict({
            'prompt': 'ansicyan bold',
            'input': 'ansigreen',
            'output': 'ansiyellow',
            'error': 'ansired',
            'success': 'ansigreen',
            'info': 'ansiblue'
        })
        
        # Command completions
        self.commands = [
            'help', 'analyze', 'generate', 'review', 'refactor', 'explain',
            'search', 'clear', 'history', 'exit', 'quit', 'save', 'load'
        ]
        self.completer = WordCompleter(self.commands)
    
    async def start_interactive_session(self, agent, codebase):
        """Start interactive chat session"""
        self.console.print(Panel.fit(
            "[bold blue]Terminal Claude[/bold blue]\n"
            "[dim]AI Coding Assistant - Type 'help' for commands[/dim]",
            border_style="blue"
        ))
        
        while True:
            try:
                # Get user input
                user_input = await self.session.prompt_async(
                    HTML('<prompt>🤖 Claude:</prompt> '),
                    completer=self.completer,
                    style=self.style
                )
                
                if not user_input.strip():
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    await self._handle_command(user_input[1:], agent, codebase)
                else:
                    # Regular chat
                    await self._handle_chat(user_input, agent, codebase)
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    async def _handle_command(self, command: str, agent, codebase):
        """Handle special commands"""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == 'help':
            self._show_help()
        elif cmd == 'analyze':
            if args:
                await self._analyze_file(args[0], agent, codebase)
            else:
                self.console.print("[red]Please specify a file to analyze[/red]")
        elif cmd == 'generate':
            if args:
                prompt = ' '.join(args)
                await self._generate_code(prompt, agent, codebase)
            else:
                self.console.print("[red]Please provide a generation prompt[/red]")
        elif cmd == 'review':
            if args:
                await self._review_file(args[0], agent, codebase)
            else:
                self.console.print("[red]Please specify a file to review[/red]")
        elif cmd == 'refactor':
            if len(args) >= 2:
                file_path = args[0]
                instructions = ' '.join(args[1:])
                await self._refactor_file(file_path, instructions, agent, codebase)
            else:
                self.console.print("[red]Please specify file and refactoring instructions[/red]")
        elif cmd == 'explain':
            if args:
                await self._explain_code(args[0], agent, codebase)
            else:
                self.console.print("[red]Please specify a file to explain[/red]")
        elif cmd == 'search':
            if args:
                query = ' '.join(args)
                await self._search_codebase(query, codebase)
            else:
                self.console.print("[red]Please provide a search query[/red]")
        elif cmd == 'clear':
            self.console.clear()
        elif cmd == 'history':
            self._show_history(agent)
        elif cmd in ['exit', 'quit']:
            self.console.print("[green]Goodbye! 👋[/green]")
            sys.exit(0)
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
    
    async def _handle_chat(self, message: str, agent, codebase):
        """Handle regular chat messages"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Thinking...", total=None)
            
            try:
                # Get relevant context
                context = await codebase.get_relevant_context(message)
                
                # Get AI response
                response = await agent.chat(message, context)
                
                progress.update(task, completed=True)
                
                # Display response
                self._display_response(response)
                
            except Exception as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]Error: {e}[/red]")
    
    def _display_response(self, response: str):
        """Display AI response with formatting"""
        # Check if response contains code
        if '```' in response:
            # Split response into text and code parts
            parts = response.split('```')
            
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Text part
                    if part.strip():
                        self.console.print(Panel(part.strip(), border_style="blue"))
                else:  # Code part
                    if part.strip():
                        # Try to detect language
                        lines = part.split('\n')
                        if lines and ':' in lines[0]:
                            lang = lines[0].split(':')[0]
                            code = '\n'.join(lines[1:])
                        else:
                            lang = 'text'
                            code = part
                        
                        syntax = Syntax(code, lang, theme="monokai")
                        self.console.print(Panel(syntax, border_style="green"))
        else:
            # Regular text response
            self.console.print(Panel(response, border_style="blue"))
    
    def _show_help(self):
        """Show help information"""
        help_text = """
[bold]Available Commands:[/bold]

[cyan]/help[/cyan] - Show this help message
[cyan]/analyze <file>[/cyan] - Analyze a specific file
[cyan]/generate <prompt>[/cyan] - Generate code based on prompt
[cyan]/review <file>[/cyan] - Review code in a file
[cyan]/refactor <file> <instructions>[/cyan] - Refactor code
[cyan]/explain <file>[/cyan] - Explain code functionality
[cyan]/search <query>[/cyan] - Search the codebase
[cyan]/clear[/cyan] - Clear the terminal
[cyan]/history[/cyan] - Show conversation history
[cyan]/exit[/cyan] - Exit the application

[bold]Regular Chat:[/bold]
Just type your message without '/' to chat with the AI assistant.
The assistant will automatically understand your codebase context.
        """
        
        self.console.print(Panel(help_text, title="Help", border_style="cyan"))
    
    async def _analyze_file(self, file_path: str, agent, codebase):
        """Analyze a file"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing file...", total=None)
            
            try:
                analysis = await codebase.analyze_file(file_path)
                progress.update(task, completed=True)
                self._display_analysis(analysis)
            except Exception as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]Error analyzing file: {e}[/red]")
    
    def _display_analysis(self, analysis: Dict[str, Any]):
        """Display file analysis results"""
        if 'error' in analysis:
            self.console.print(f"[red]Error: {analysis['error']}[/red]")
            return
        
        file_info = analysis['file_info']
        
        # Create analysis table
        table = Table(title=f"Analysis: {file_info['path']}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        complexity = analysis['complexity']
        table.add_row("Language", file_info['language'])
        table.add_row("Lines of Code", str(complexity['lines_of_code']))
        table.add_row("Functions", str(complexity['functions']))
        table.add_row("Classes", str(complexity['classes']))
        table.add_row("Imports", str(complexity['imports']))
        table.add_row("Cyclomatic Complexity", str(complexity['cyclomatic']))
        
        self.console.print(table)
        
        # Show suggestions
        if analysis['suggestions']:
            self.console.print("\n[bold yellow]Suggestions:[/bold yellow]")
            for suggestion in analysis['suggestions']:
                self.console.print(f"• {suggestion}")
    
    async def _generate_code(self, prompt: str, agent, codebase):
        """Generate code"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Generating code...", total=None)
            
            try:
                code = await agent.generate_code(prompt, codebase)
                progress.update(task, completed=True)
                
                self.console.print("[bold green]Generated Code:[/bold green]")
                syntax = Syntax(code, "python", theme="monokai")
                self.console.print(Panel(syntax, border_style="green"))
                
            except Exception as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]Error generating code: {e}[/red]")
    
    async def _review_file(self, file_path: str, agent, codebase):
        """Review a file"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Reviewing code...", total=None)
            
            try:
                review = await agent.review_code(file_path, codebase)
                progress.update(task, completed=True)
                self._display_review(review)
            except Exception as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]Error reviewing file: {e}[/red]")
    
    def _display_review(self, review: Dict[str, Any]):
        """Display code review results"""
        self.console.print("[bold yellow]Code Review:[/bold yellow]")
        
        if 'summary' in review:
            self.console.print(Panel(review['summary'], title="Summary", border_style="yellow"))
        
        if 'issues' in review and review['issues']:
            self.console.print("\n[bold red]Issues:[/bold red]")
            for issue in review['issues']:
                self.console.print(f"• {issue}")
        
        if 'suggestions' in review and review['suggestions']:
            self.console.print("\n[bold green]Suggestions:[/bold green]")
            for suggestion in review['suggestions']:
                self.console.print(f"• {suggestion}")
    
    async def _refactor_file(self, file_path: str, instructions: str, agent, codebase):
        """Refactor a file"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Refactoring code...", total=None)
            
            try:
                refactored_code = await agent.refactor_code(file_path, instructions, codebase)
                progress.update(task, completed=True)
                
                # Show diff
                with open(file_path, 'r') as f:
                    original_code = f.read()
                
                self._show_diff(original_code, refactored_code)
                
                # Ask for approval
                if Confirm.ask("Apply these changes?"):
                    with open(file_path, 'w') as f:
                        f.write(refactored_code)
                    self.console.print("[green]Changes applied successfully![/green]")
                else:
                    self.console.print("[yellow]Changes cancelled[/yellow]")
                    
            except Exception as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]Error refactoring file: {e}[/red]")
    
    def _show_diff(self, original: str, modified: str):
        """Show diff between original and modified code"""
        self.console.print("[bold]Changes Preview:[/bold]")
        
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile='original',
            tofile='modified'
        )
        
        diff_text = ''.join(diff)
        if diff_text:
            syntax = Syntax(diff_text, "diff", theme="monokai")
            self.console.print(Panel(syntax, border_style="yellow"))
        else:
            self.console.print("[yellow]No changes detected[/yellow]")
    
    async def _explain_code(self, file_path: str, agent, codebase):
        """Explain code functionality"""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Analyzing code...", total=None)
                
                explanation = await agent.explain_code(code)
                progress.update(task, completed=True)
                
                self.console.print("[bold blue]Code Explanation:[/bold blue]")
                self.console.print(Panel(explanation, border_style="blue"))
                
        except Exception as e:
            self.console.print(f"[red]Error explaining code: {e}[/red]")
    
    async def _search_codebase(self, query: str, codebase):
        """Search the codebase"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Searching codebase...", total=None)
            
            try:
                results = codebase._semantic_search(query)
                progress.update(task, completed=True)
                
                self._display_search_results(results)
                
            except Exception as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]Error searching codebase: {e}[/red]")
    
    def _display_search_results(self, results: List[str]):
        """Display search results"""
        if not results:
            self.console.print("[yellow]No results found[/yellow]")
            return
        
        self.console.print(f"[bold green]Found {len(results)} results:[/bold green]")
        
        table = Table()
        table.add_column("File", style="cyan")
        table.add_column("Language", style="green")
        
        for file_path in results[:10]:  # Show top 10 results
            file_info = codebase.file_index.get(file_path, {})
            language = file_info.get('language', 'unknown')
            table.add_row(file_path, language)
        
        self.console.print(table)
    
    def _show_history(self, agent):
        """Show conversation history"""
        history = agent.get_history()
        
        if not history:
            self.console.print("[yellow]No conversation history[/yellow]")
            return
        
        self.console.print("[bold blue]Conversation History:[/bold blue]")
        
        for i, message in enumerate(history[-10:], 1):  # Show last 10 messages
            role = message['role']
            content = message['content'][:100] + "..." if len(message['content']) > 100 else message['content']
            
            if role == 'user':
                self.console.print(f"[cyan]{i}. User:[/cyan] {content}")
            else:
                self.console.print(f"[green]{i}. Assistant:[/green] {content}")
    
    def print_success(self, message: str):
        """Print success message"""
        self.console.print(f"[green]✅ {message}[/green]")
    
    def print_error(self, message: str):
        """Print error message"""
        self.console.print(f"[red]❌ {message}[/red]")
    
    def print_info(self, message: str):
        """Print info message"""
        self.console.print(f"[blue]ℹ️ {message}[/blue]")
    
    def confirm_action(self, message: str) -> bool:
        """Ask for user confirmation"""
        return Confirm.ask(message)
    
    def run_setup_wizard(self, config):
        """Run initial setup wizard"""
        self.console.print(Panel.fit(
            "[bold blue]Terminal Claude Setup Wizard[/bold blue]\n"
            "Let's configure your AI coding assistant!",
            border_style="blue"
        ))
        
        # Model provider selection (MLX only)
        provider = "mlx"
        self.console.print("[blue]Using MLX (Apple Silicon optimized)[/blue]")
        
        config.set('MODEL_PROVIDER', provider)
        
        # MLX model selection
        model_path = Prompt.ask(
            "Enter MLX model path",
            default="mlx-community/Mistral-7B-Instruct-v0.3-4bit"
        )
        config.set('MLX_MODEL', model_path)
        
        # VS Code integration
        if Confirm.ask("Enable VS Code integration?"):
            vscode_path = Prompt.ask(
                "Enter VS Code executable path",
                default="/usr/local/bin/code"
            )
            config.set('VSCODE_PATH', vscode_path)
        
        config.save()
        self.console.print("[green]✅ Setup complete![/green]")
