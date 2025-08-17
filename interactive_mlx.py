#!/usr/bin/env python3
"""
Interactive MLX Terminal Interface
Simple terminal-based chat interface using MLX models with codebase context
"""

import asyncio
import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from core.models import MLXProvider
from core.codebase import CodebaseAnalyzer

class InteractiveMLX:
    def __init__(self, model_path="mlx-community/Mistral-7B-Instruct-v0.3-4bit"):
        self.console = Console()
        self.model_path = model_path
        self.model_provider = None
        self.codebase_analyzer = None
        
    async def initialize_model(self):
        """Initialize the MLX model and codebase analyzer"""
        self.console.print("[yellow]🤖 Loading MLX model...[/yellow]")
        try:
            self.model_provider = MLXProvider(self.model_path)
            self.console.print("[green]✅ Model loaded successfully![/green]")
            
            # Initialize codebase analyzer with current working directory
            self.console.print("[yellow]🔍 Building codebase index...[/yellow]")
            import os
            current_dir = os.getcwd()
            self.codebase_analyzer = CodebaseAnalyzer(current_dir)
            self.console.print("[green]✅ Codebase indexed successfully![/green]")
            
            return True
        except Exception as e:
            self.console.print(f"[red]❌ Failed to load model: {e}[/red]")
            return False
    
    async def chat_loop(self):
        """Main chat loop"""
        self.console.print(Panel.fit(
            "[bold blue]MLX Interactive Chat[/bold blue]\n"
            f"Model: {self.model_path}\n"
            "Type 'quit' or 'exit' to end the session",
            border_style="blue"
        ))
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[cyan]You[/cyan]")
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                
                if not user_input.strip():
                    continue
                
                # Generate response with codebase context
                self.console.print("[yellow]🤖 Thinking...[/yellow]")
                
                # Check if this is a codebase-related question
                codebase_keywords = ['codebase', 'project', 'files', 'code', 'analyze', 'review', 'improve', 'structure']
                is_codebase_question = any(keyword in user_input.lower() for keyword in codebase_keywords)
                
                if is_codebase_question and self.codebase_analyzer:
                    # Get relevant codebase context
                    context_data = await self.codebase_analyzer.get_relevant_context(user_input)
                    
                    # Build context from relevant files
                    context = "Based on the current codebase:\n\n"
                    
                    # Add codebase summary
                    summary = context_data['codebase_summary']
                    context += f"Codebase Summary:\n"
                    context += f"- Total files: {summary['total_files']}\n"
                    context += f"- Total lines: {summary['total_lines']}\n"
                    context += f"- Languages: {', '.join(summary['languages'].keys())}\n"
                    context += f"- Functions: {summary['total_functions']}\n"
                    context += f"- Classes: {summary['total_classes']}\n\n"
                    
                    # Add relevant files
                    if context_data['relevant_files']:
                        context += f"Found {len(context_data['relevant_files'])} relevant files:\n\n"
                        for file_info in context_data['relevant_files']:
                            context += f"File: {file_info['path']}\n"
                            context += f"Language: {file_info['language']}\n"
                            context += f"Content preview: {file_info['content'][:300]}...\n\n"
                    else:
                        context += "No specific files found, but here's the general project structure.\n\n"
                    
                    # Add complete file list for directory queries
                    if 'problems' in user_input.lower() or 'directory' in user_input.lower():
                        context += "Complete file list:\n"
                        for file_path in sorted(self.codebase_analyzer.file_index.keys()):
                            if 'problems' in file_path.lower():
                                context += f"- {file_path}\n"
                        context += "\n"
                    
                    # Add specific instructions for code-related queries
                    if any(keyword in user_input.lower() for keyword in ['code', 'implementation', 'class', 'function', 'method']):
                        context += "IMPORTANT: When analyzing code, provide specific details from the actual file contents shown above. Reference specific classes, functions, and code patterns you see in the files.\n\n"
                    
                    # Create enhanced prompt
                    enhanced_prompt = f"{context}\n\nUser Question: {user_input}\n\nPlease provide a detailed analysis based on the codebase context above. If the user is asking about specific files or code, provide concrete details from the actual file contents shown above. Be specific and reference the actual code when possible."
                    response = await self.model_provider.generate(enhanced_prompt)
                else:
                    # Regular response without codebase context
                    response = await self.model_provider.generate(user_input)
                
                # Display response
                self.console.print(Panel(
                    Text(response, style="green"),
                    title="[bold green]MLX Assistant[/bold green]",
                    border_style="green"
                ))
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]❌ Error: {e}[/red]")

async def main():
    """Main function"""
    console = Console()
    
    # Check command line arguments for model path
    model_path = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    
    console.print(f"[blue]🚀 Starting MLX Interactive Chat with model: {model_path}[/blue]")
    
    # Create and run interactive session
    chat = InteractiveMLX(model_path)
    
    if await chat.initialize_model():
        await chat.chat_loop()
    else:
        console.print("[red]Failed to initialize model. Exiting.[/red]")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
