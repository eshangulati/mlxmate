#!/usr/bin/env python3
"""
Test MLX Integration
Simple test to verify MLX is working correctly
"""

import asyncio
from rich.console import Console
from core.models import MLXProvider

async def test_mlx():
    console = Console()
    
    console.print("[blue]🧪 Testing MLX Integration...[/blue]")
    
    try:
        # Test model loading
        console.print("[yellow]📥 Loading model...[/yellow]")
        provider = MLXProvider("mlx-community/Mistral-7B-Instruct-v0.3-4bit")
        console.print("[green]✅ Model loaded successfully![/green]")
        
        # Test simple generation
        console.print("[yellow]🤖 Testing generation...[/yellow]")
        response = await provider.generate("Say hello!")
        console.print(f"[green]✅ Response: {response[:100]}...[/green]")
        
        console.print("[green]🎉 MLX integration test passed![/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")
        return False

if __name__ == "__main__":
    asyncio.run(test_mlx())
