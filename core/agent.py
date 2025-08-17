"""
AI Agent - Main AI interaction module
Handles all AI model interactions and code generation.
"""

import asyncio
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from .models import ModelProvider, MLXProvider
from .codebase import CodebaseAnalyzer
from ui.prompts import PromptTemplates


class AIAgent:
    def __init__(self, config):
        self.config = config
        self.model_provider = self._initialize_model_provider()
        self.prompts = PromptTemplates()
        self.conversation_history = []
        
    def _initialize_model_provider(self) -> ModelProvider:
        """Initialize the MLX model provider"""
        model_path = self.config.get('MLX_MODEL', 'mlx-community/Mistral-7B-Instruct-v0.3-4bit')
        return MLXProvider(model_path=model_path)
    
    async def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """Send a message to the AI and get a response"""
        # Build the full prompt with context
        full_prompt = self.prompts.build_chat_prompt(
            message=message,
            context=context,
            history=self.conversation_history
        )
        
        # Get response from model
        response = await self.model_provider.generate(full_prompt)
        
        # Update conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': message
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return response
    
    async def generate_code(self, prompt: str, codebase: CodebaseAnalyzer) -> str:
        """Generate code based on a prompt and codebase context"""
        # Analyze codebase for context
        context = await codebase.get_relevant_context(prompt)
        
        # Build code generation prompt
        full_prompt = self.prompts.build_code_generation_prompt(
            prompt=prompt,
            context=context,
            coding_standards=codebase.get_coding_standards()
        )
        
        # Generate code
        response = await self.model_provider.generate(full_prompt)
        
        # Extract code from response
        code = self._extract_code_from_response(response)
        
        return code
    
    async def review_code(self, file_path: str, codebase: CodebaseAnalyzer) -> Dict[str, Any]:
        """Review code and provide feedback"""
        with open(file_path, 'r') as f:
            code_content = f.read()
        
        # Get file context
        file_context = await codebase.analyze_file(file_path)
        
        # Build review prompt
        review_prompt = self.prompts.build_code_review_prompt(
            code=code_content,
            context=file_context,
            coding_standards=codebase.get_coding_standards()
        )
        
        # Get review
        review_response = await self.model_provider.generate(review_prompt)
        
        # Parse review into structured format
        review = self._parse_review_response(review_response)
        
        return review
    
    async def refactor_code(self, file_path: str, instructions: str, codebase: CodebaseAnalyzer) -> str:
        """Refactor code based on instructions"""
        with open(file_path, 'r') as f:
            original_code = f.read()
        
        # Get file context
        file_context = await codebase.analyze_file(file_path)
        
        # Build refactoring prompt
        refactor_prompt = self.prompts.build_refactoring_prompt(
            code=original_code,
            instructions=instructions,
            context=file_context,
            coding_standards=codebase.get_coding_standards()
        )
        
        # Generate refactored code
        response = await self.model_provider.generate(refactor_prompt)
        
        # Extract refactored code
        refactored_code = self._extract_code_from_response(response)
        
        return refactored_code
    
    async def explain_code(self, code: str, context: Optional[Dict] = None) -> str:
        """Explain code functionality"""
        explain_prompt = self.prompts.build_explanation_prompt(code, context)
        response = await self.model_provider.generate(explain_prompt)
        return response
    
    async def suggest_improvements(self, code: str, context: Optional[Dict] = None) -> List[str]:
        """Suggest improvements for code"""
        improve_prompt = self.prompts.build_improvement_prompt(code, context)
        response = await self.model_provider.generate(improve_prompt)
        
        # Parse improvements into list
        improvements = self._parse_improvements_response(response)
        return improvements
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract code blocks from AI response"""
        # Look for code blocks marked with ```
        if '```' in response:
            # Find all code blocks
            import re
            code_blocks = re.findall(r'```(?:[\w-]+)?\n(.*?)```', response, re.DOTALL)
            if code_blocks:
                return '\n\n'.join(code_blocks)
        
        # If no code blocks, return the whole response
        return response.strip()
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse review response into structured format"""
        try:
            # Try to parse as JSON first
            return json.loads(response)
        except json.JSONDecodeError:
            # Fall back to simple parsing
            return {
                'summary': response[:200] + '...' if len(response) > 200 else response,
                'issues': [],
                'suggestions': [],
                'score': 0
            }
    
    def _parse_improvements_response(self, response: str) -> List[str]:
        """Parse improvements response into list"""
        # Split by common list markers
        lines = response.split('\n')
        improvements = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
                improvements.append(line[1:].strip())
            elif line and line[0].isdigit() and '. ' in line:
                improvements.append(line.split('. ', 1)[1])
        
        return improvements if improvements else [response]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.copy()
