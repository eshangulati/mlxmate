"""
Prompt Templates - Predefined prompts for different AI interactions
Provides structured prompts for code generation, review, refactoring, etc.
"""

from typing import Dict, List, Optional, Any


class PromptTemplates:
    """Collection of prompt templates for different AI interactions"""
    
    def build_chat_prompt(self, message: str, context: Optional[Dict] = None, history: List[Dict] = None) -> str:
        """Build a chat prompt with context"""
        prompt = self._get_system_prompt()
        
        # Add conversation history
        if history:
            prompt += "\n\nConversation History:\n"
            for msg in history[-6:]:  # Last 6 messages
                role = "User" if msg['role'] == 'user' else "Assistant"
                prompt += f"{role}: {msg['content']}\n"
        
        # Add codebase context
        if context and context.get('relevant_files'):
            prompt += "\n\nRelevant Codebase Context:\n"
            for file_info in context['relevant_files'][:3]:  # Top 3 files
                prompt += f"\nFile: {file_info['path']}\n"
                prompt += f"Language: {file_info['language']}\n"
                prompt += f"Content:\n{file_info['content'][:1000]}...\n"
        
        # Add coding standards
        if context and context.get('coding_standards'):
            standards = context['coding_standards']
            prompt += f"\n\nCoding Standards:\n"
            prompt += f"- Indentation: {standards.get('indentation', 'spaces')}\n"
            prompt += f"- Line length: {standards.get('line_length', 80)} characters\n"
            if 'naming_conventions' in standards:
                for conv_type, conv_style in standards['naming_conventions'].items():
                    prompt += f"- {conv_type}: {conv_style}\n"
        
        prompt += f"\n\nUser: {message}\nAssistant:"
        
        return prompt
    
    def build_code_generation_prompt(self, prompt: str, context: Optional[Dict] = None, coding_standards: Optional[Dict] = None) -> str:
        """Build a code generation prompt"""
        system_prompt = """You are an expert software developer. Generate high-quality, production-ready code that follows best practices and the project's coding standards.

Guidelines:
- Write clean, readable, and maintainable code
- Include appropriate comments and documentation
- Follow the project's coding conventions
- Consider error handling and edge cases
- Use modern language features when appropriate
- Ensure the code is efficient and performant

Respond with only the generated code, wrapped in appropriate code blocks with language specification."""
        
        full_prompt = system_prompt
        
        # Add codebase context
        if context and context.get('relevant_files'):
            full_prompt += "\n\nRelevant Codebase Context:\n"
            for file_info in context['relevant_files'][:2]:
                full_prompt += f"\nFile: {file_info['path']}\n"
                full_prompt += f"Language: {file_info['language']}\n"
                full_prompt += f"Content:\n{file_info['content'][:800]}...\n"
        
        # Add coding standards
        if coding_standards:
            full_prompt += f"\n\nCoding Standards:\n"
            full_prompt += f"- Indentation: {coding_standards.get('indentation', 'spaces')}\n"
            full_prompt += f"- Line length: {coding_standards.get('line_length', 80)} characters\n"
            if 'naming_conventions' in coding_standards:
                for conv_type, conv_style in coding_standards['naming_conventions'].items():
                    full_prompt += f"- {conv_type}: {conv_style}\n"
        
        full_prompt += f"\n\nGeneration Request: {prompt}\n\nGenerated Code:"
        
        return full_prompt
    
    def build_code_review_prompt(self, code: str, context: Optional[Dict] = None, coding_standards: Optional[Dict] = None) -> str:
        """Build a code review prompt"""
        system_prompt = """You are an expert code reviewer. Analyze the provided code and provide a comprehensive review.

Review the code for:
- Code quality and readability
- Potential bugs and issues
- Performance considerations
- Security vulnerabilities
- Adherence to coding standards
- Best practices
- Maintainability

Provide your review in the following JSON format:
{
    "summary": "Brief summary of the code",
    "issues": ["List of issues found"],
    "suggestions": ["List of improvement suggestions"],
    "score": 85
}"""
        
        full_prompt = system_prompt
        
        # Add coding standards
        if coding_standards:
            full_prompt += f"\n\nCoding Standards:\n"
            full_prompt += f"- Indentation: {coding_standards.get('indentation', 'spaces')}\n"
            full_prompt += f"- Line length: {coding_standards.get('line_length', 80)} characters\n"
            if 'naming_conventions' in coding_standards:
                for conv_type, conv_style in coding_standards['naming_conventions'].items():
                    full_prompt += f"- {conv_type}: {conv_style}\n"
        
        full_prompt += f"\n\nCode to Review:\n```\n{code}\n```\n\nReview:"
        
        return full_prompt
    
    def build_refactoring_prompt(self, code: str, instructions: str, context: Optional[Dict] = None, coding_standards: Optional[Dict] = None) -> str:
        """Build a refactoring prompt"""
        system_prompt = """You are an expert software developer. Refactor the provided code according to the given instructions while maintaining functionality and improving code quality.

Guidelines:
- Preserve the original functionality
- Improve code readability and maintainability
- Follow the project's coding standards
- Use modern language features when appropriate
- Maintain or improve performance
- Add appropriate comments if needed

Respond with only the refactored code, wrapped in appropriate code blocks with language specification."""
        
        full_prompt = system_prompt
        
        # Add coding standards
        if coding_standards:
            full_prompt += f"\n\nCoding Standards:\n"
            full_prompt += f"- Indentation: {coding_standards.get('indentation', 'spaces')}\n"
            full_prompt += f"- Line length: {coding_standards.get('line_length', 80)} characters\n"
            if 'naming_conventions' in coding_standards:
                for conv_type, conv_style in coding_standards['naming_conventions'].items():
                    full_prompt += f"- {conv_type}: {conv_style}\n"
        
        full_prompt += f"\n\nOriginal Code:\n```\n{code}\n```\n\nRefactoring Instructions: {instructions}\n\nRefactored Code:"
        
        return full_prompt
    
    def build_explanation_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Build a code explanation prompt"""
        system_prompt = """You are an expert software developer and educator. Explain the provided code in a clear, comprehensive manner.

Your explanation should include:
- What the code does (purpose and functionality)
- How it works (step-by-step breakdown)
- Key concepts and patterns used
- Important variables, functions, and their roles
- Any notable algorithms or data structures
- Potential use cases or applications

Make the explanation accessible to developers of different skill levels."""
        
        full_prompt = system_prompt
        
        # Add context if available
        if context and context.get('relevant_files'):
            full_prompt += "\n\nCodebase Context:\n"
            for file_info in context['relevant_files'][:1]:
                full_prompt += f"This code is part of: {file_info['path']}\n"
        
        full_prompt += f"\n\nCode to Explain:\n```\n{code}\n```\n\nExplanation:"
        
        return full_prompt
    
    def build_improvement_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Build a code improvement prompt"""
        system_prompt = """You are an expert software developer. Analyze the provided code and suggest specific improvements to enhance its quality, performance, and maintainability.

Focus on:
- Code structure and organization
- Performance optimizations
- Error handling and robustness
- Code readability and maintainability
- Security considerations
- Best practices
- Modern language features that could be used

Provide specific, actionable suggestions with brief explanations."""
        
        full_prompt = system_prompt
        
        # Add coding standards if available
        if context and context.get('coding_standards'):
            standards = context['coding_standards']
            full_prompt += f"\n\nCoding Standards:\n"
            full_prompt += f"- Indentation: {standards.get('indentation', 'spaces')}\n"
            full_prompt += f"- Line length: {standards.get('line_length', 80)} characters\n"
        
        full_prompt += f"\n\nCode to Improve:\n```\n{code}\n```\n\nImprovement Suggestions:"
        
        return full_prompt
    
    def build_search_prompt(self, query: str, context: Optional[Dict] = None) -> str:
        """Build a semantic search prompt"""
        system_prompt = """You are an expert code analyst. Help find relevant code in the codebase based on the user's query.

Analyze the query and identify:
- Key concepts and functionality being searched
- Relevant file types and languages
- Specific patterns or structures to look for
- Related functions, classes, or modules

Provide guidance on what to search for and where to look."""
        
        full_prompt = system_prompt
        
        # Add codebase context
        if context and context.get('codebase_summary'):
            summary = context['codebase_summary']
            full_prompt += f"\n\nCodebase Overview:\n"
            full_prompt += f"- Total files: {summary.get('total_files', 0)}\n"
            full_prompt += f"- Languages: {', '.join(summary.get('languages', {}).keys())}\n"
            full_prompt += f"- Total functions: {summary.get('total_functions', 0)}\n"
            full_prompt += f"- Total classes: {summary.get('total_classes', 0)}\n"
        
        full_prompt += f"\n\nSearch Query: {query}\n\nSearch Guidance:"
        
        return full_prompt
    
    def _get_system_prompt(self) -> str:
        """Get the base system prompt"""
        return """You are Terminal Claude, an expert AI coding assistant that lives in the terminal. You help developers write, review, refactor, and understand code.

Your capabilities:
- Code generation and completion
- Code review and analysis
- Refactoring and optimization
- Code explanation and documentation
- Bug detection and fixing
- Best practices guidance
- Multi-language support

You have access to the entire codebase context and understand the project structure, coding standards, and patterns. You provide helpful, accurate, and actionable responses.

Guidelines:
- Be concise but thorough
- Provide practical, implementable solutions
- Follow the project's coding standards
- Consider performance and maintainability
- Explain complex concepts clearly
- Suggest improvements when appropriate
- Always prioritize code quality and best practices"""
    
    def get_language_specific_prompt(self, language: str) -> str:
        """Get language-specific prompt additions"""
        language_prompts = {
            'python': """
Python-specific guidelines:
- Follow PEP 8 style guide
- Use type hints when appropriate
- Prefer list comprehensions and generator expressions
- Use context managers for resource management
- Follow the principle of least surprise
- Use virtual environments for dependency management""",
            
            'javascript': """
JavaScript-specific guidelines:
- Use ES6+ features when possible
- Follow consistent naming conventions
- Use const and let instead of var
- Prefer arrow functions for callbacks
- Use template literals for string interpolation
- Consider using TypeScript for type safety""",
            
            'typescript': """
TypeScript-specific guidelines:
- Use strict type checking
- Define interfaces for complex objects
- Use enums for constants
- Prefer readonly properties when possible
- Use utility types effectively
- Follow naming conventions for types""",
            
            'java': """
Java-specific guidelines:
- Follow Java naming conventions
- Use appropriate access modifiers
- Prefer composition over inheritance
- Use streams for data processing
- Implement proper exception handling
- Use builder pattern for complex objects""",
            
            'cpp': """
C++-specific guidelines:
- Use RAII for resource management
- Prefer const correctness
- Use smart pointers instead of raw pointers
- Follow the rule of three/five/zero
- Use std:: algorithms when possible
- Consider move semantics for performance"""
        }
        
        return language_prompts.get(language.lower(), "")
    
    def build_context_aware_prompt(self, base_prompt: str, context: Dict) -> str:
        """Build a context-aware prompt with relevant information"""
        prompt = base_prompt
        
        # Add file context
        if context.get('current_file'):
            file_info = context['current_file']
            prompt += f"\n\nCurrent File: {file_info['path']}\n"
            prompt += f"Language: {file_info['language']}\n"
            if file_info.get('symbols'):
                prompt += f"Functions: {len(file_info['symbols'].get('functions', []))}\n"
                prompt += f"Classes: {len(file_info['symbols'].get('classes', []))}\n"
        
        # Add project context
        if context.get('project_info'):
            project = context['project_info']
            prompt += f"\n\nProject: {project.get('name', 'Unknown')}\n"
            prompt += f"Type: {project.get('type', 'Unknown')}\n"
        
        # Add recent changes
        if context.get('recent_changes'):
            changes = context['recent_changes']
            prompt += f"\n\nRecent Changes:\n"
            for change in changes[:3]:
                prompt += f"- {change}\n"
        
        return prompt
