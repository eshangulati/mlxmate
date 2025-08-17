"""
Model Providers - AI model backend implementations
Supports MLX (local Apple Silicon) models only.
"""

import asyncio
import json
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load, generate


class ModelProvider(ABC):
    """Abstract base class for model providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs):
        """Generate text stream from prompt"""
        pass


class MLXProvider(ModelProvider):
    """MLX provider for local models on Apple Silicon"""
    
    def __init__(self, model_path: str = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load the MLX model and tokenizer"""
        try:
            self.model, self.tokenizer = load(self.model_path)
        except Exception as e:
            raise Exception(f"Failed to load MLX model: {str(e)}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using MLX"""
        try:
            # Set default parameters
            max_tokens = kwargs.get('max_tokens', 512)
            temperature = kwargs.get('temperature', 0.7)
            top_p = kwargs.get('top_p', 0.9)
            
            # Prepare the prompt for the model using chat template
            messages = [{"role": "user", "content": prompt}]
            formatted_prompt = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True)
            
            # Generate response
            response = await asyncio.to_thread(
                generate,
                self.model,
                self.tokenizer,
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                verbose=False
            )
            return response
        except Exception as e:
            raise Exception(f"MLX generation failed: {str(e)}")
    
    async def generate_stream(self, prompt: str, **kwargs):
        """Generate streaming text using MLX"""
        try:
            # For streaming, we'll generate in chunks
            max_tokens = kwargs.get('max_tokens', 512)
            temperature = kwargs.get('temperature', 0.7)
            top_p = kwargs.get('top_p', 0.9)
            
            # Generate the full response first, then yield chunks
            response = await asyncio.to_thread(
                generate,
                self.model,
                self.tokenizer,
                prompt,
                max_tokens=max_tokens
            )
            
            # Yield response in chunks for streaming effect
            chunk_size = 20
            for i in range(0, len(response), chunk_size):
                yield response[i:i + chunk_size]
                await asyncio.sleep(0.01)  # Small delay for streaming effect
                
        except Exception as e:
            raise Exception(f"MLX streaming failed: {str(e)}")
    
    async def list_models(self) -> List[str]:
        """List available MLX models"""
        # Common MLX models (Mistral first)
        return [
            "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
            "mlx-community/Mistral-7B-Instruct-v0.3-8bit",
            "mlx-community/Phi-3-mini-4k-instruct-4bit",
            "mlx-community/Phi-3-mini-4k-instruct-8bit",
            "mlx-community/Phi-3-medium-4k-instruct-4bit",
            "mlx-community/Phi-3-medium-4k-instruct-8bit",
            "mlx-community/Llama-2-7b-chat-4bit",
            "mlx-community/CodeLlama-7b-Instruct-4bit"
        ]
    
    async def check_health(self) -> bool:
        """Check if MLX model is loaded and ready"""
        try:
            return self.model is not None and self.tokenizer is not None
        except:
            return False





class ModelManager:
    """Manager for multiple model providers"""
    
    def __init__(self):
        self.providers: Dict[str, ModelProvider] = {}
        self.default_provider = None
    
    def add_provider(self, name: str, provider: ModelProvider):
        """Add a model provider"""
        self.providers[name] = provider
        if not self.default_provider:
            self.default_provider = name
    
    def set_default_provider(self, name: str):
        """Set the default provider"""
        if name in self.providers:
            self.default_provider = name
        else:
            raise ValueError(f"Provider '{name}' not found")
    
    def get_provider(self, name: str = None) -> ModelProvider:
        """Get a provider by name or default"""
        provider_name = name or self.default_provider
        if not provider_name:
            raise ValueError("No default provider set")
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        return self.providers[provider_name]
    
    async def generate(self, prompt: str, provider: str = None, **kwargs) -> str:
        """Generate text using specified or default provider"""
        provider_instance = self.get_provider(provider)
        return await provider_instance.generate(prompt, **kwargs)
    
    async def generate_stream(self, prompt: str, provider: str = None, **kwargs):
        """Generate streaming text using specified or default provider"""
        provider_instance = self.get_provider(provider)
        async for chunk in provider_instance.generate_stream(prompt, **kwargs):
            yield chunk
    
    def list_providers(self) -> List[str]:
        """List available providers"""
        return list(self.providers.keys())
    
    async def check_health(self, provider: str = None) -> Dict[str, bool]:
        """Check health of providers"""
        results = {}
        
        if provider:
            providers_to_check = [provider]
        else:
            providers_to_check = self.providers.keys()
        
        for name in providers_to_check:
            if name in self.providers:
                try:
                    if hasattr(self.providers[name], 'check_health'):
                        results[name] = await self.providers[name].check_health()
                    else:
                        results[name] = True  # Assume healthy if no health check method
                except:
                    results[name] = False
        
        return results
