"""
Configuration Management - Settings and configuration handling
Manages user preferences, API keys, and system settings.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv


class Config:
    """Configuration management for Terminal Claude"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path"""
        config_dir = Path.home() / '.terminal_claude'
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / 'config.json')
    
    def _load_config(self):
        """Load configuration from file and environment"""
        # Load from .env file if it exists
        load_dotenv()
        
        # Default configuration
        self.config = {
            'MODEL_PROVIDER': 'mlx',
            'MLX_MODEL': 'mlx-community/Mistral-7B-Instruct-v0.3-4bit',
            'VSCODE_PATH': '/usr/local/bin/code',
            'MAX_TOKENS': 4000,
            'TEMPERATURE': 0.7,
            'ENABLE_STREAMING': True,
            'AUTO_SAVE': True,
            'BACKUP_CHANGES': True,
            'THEME': 'monokai',
            'LANGUAGE': 'en',
            'LOG_LEVEL': 'INFO'
        }
        
        # Load from config file if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Override with environment variables
        for key in self.config.keys():
            env_value = os.getenv(key)
            if env_value is not None:
                self.config[key] = env_value
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self.config.update(updates)
    
    def reset(self):
        """Reset configuration to defaults"""
        self._load_config()
    
    def export(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return self.config.copy()
    
    def import_config(self, config_dict: Dict[str, Any]):
        """Import configuration from dictionary"""
        self.config.update(config_dict)
    
    def validate(self) -> Dict[str, str]:
        """Validate configuration and return errors"""
        errors = {}
        
        # Check if MLX is available
        try:
            import mlx
            import mlx_lm
        except ImportError:
            errors['MLX_MODEL'] = 'MLX is not installed. Run: pip install mlx mlx-lm'
        
        # Validate numeric values
        try:
            max_tokens = int(self.config.get('MAX_TOKENS', 4000))
            if max_tokens <= 0:
                errors['MAX_TOKENS'] = 'MAX_TOKENS must be positive'
        except ValueError:
            errors['MAX_TOKENS'] = 'MAX_TOKENS must be a number'
        
        try:
            temperature = float(self.config.get('TEMPERATURE', 0.7))
            if not 0 <= temperature <= 2:
                errors['TEMPERATURE'] = 'TEMPERATURE must be between 0 and 2'
        except ValueError:
            errors['TEMPERATURE'] = 'TEMPERATURE must be a number'
        
        return errors
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model-specific configuration"""
        provider = self.config.get('MODEL_PROVIDER', 'ollama')
        
        model_config = {
            'provider': provider,
            'max_tokens': int(self.config.get('MAX_TOKENS', 4000)),
            'temperature': float(self.config.get('TEMPERATURE', 0.7)),
            'streaming': self.config.get('ENABLE_STREAMING', True)
        }
        
        if provider == 'ollama':
            model_config.update({
                'model_name': self.config.get('MODEL_NAME', 'codellama:7b'),
                'base_url': self.config.get('OLLAMA_BASE_URL', 'http://localhost:11434')
            })
        elif provider == 'openai':
            model_config.update({
                'api_key': self.config.get('OPENAI_API_KEY'),
                'model': self.config.get('MODEL_NAME', 'gpt-4')
            })
        elif provider == 'anthropic':
            model_config.update({
                'api_key': self.config.get('ANTHROPIC_API_KEY'),
                'model': self.config.get('MODEL_NAME', 'claude-3-sonnet-20240229')
            })
        
        return model_config
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI-specific configuration"""
        return {
            'theme': self.config.get('THEME', 'monokai'),
            'language': self.config.get('LANGUAGE', 'en'),
            'auto_save': self.config.get('AUTO_SAVE', True),
            'backup_changes': self.config.get('BACKUP_CHANGES', True)
        }
    
    def get_integration_config(self) -> Dict[str, Any]:
        """Get integration-specific configuration"""
        return {
            'vscode_path': self.config.get('VSCODE_PATH', '/usr/local/bin/code'),
            'git_enabled': self.config.get('GIT_ENABLED', True),
            'file_watching': self.config.get('FILE_WATCHING', True)
        }
    
    def create_backup(self) -> str:
        """Create a backup of the current configuration"""
        backup_file = f"{self.config_file}.backup"
        try:
            with open(backup_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return backup_file
        except Exception as e:
            print(f"Error creating backup: {e}")
            return ""
    
    def restore_backup(self, backup_file: str) -> bool:
        """Restore configuration from backup"""
        try:
            with open(backup_file, 'r') as f:
                backup_config = json.load(f)
            self.config = backup_config
            self.save()
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def list_backups(self) -> List[str]:
        """List available backup files"""
        config_dir = Path(self.config_file).parent
        backup_files = list(config_dir.glob('config.json.backup*'))
        return [str(f) for f in backup_files]
    
    def get_sensitive_keys(self) -> List[str]:
        """Get list of configuration keys that contain sensitive information"""
        return [
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'GITHUB_TOKEN',
            'GITLAB_TOKEN'
        ]
    
    def mask_sensitive_values(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive values in configuration for display"""
        masked_config = config_dict.copy()
        sensitive_keys = self.get_sensitive_keys()
        
        for key in sensitive_keys:
            if key in masked_config and masked_config[key]:
                masked_config[key] = '*' * 8
        
        return masked_config
    
    def print_config(self, mask_sensitive: bool = True):
        """Print current configuration"""
        config_to_print = self.mask_sensitive_values(self.config) if mask_sensitive else self.config
        
        print("Current Configuration:")
        for key, value in config_to_print.items():
            print(f"  {key}: {value}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            'provider': self.config.get('MODEL_PROVIDER', 'ollama'),
            'model': self.config.get('MODEL_NAME', 'codellama:7b'),
            'max_tokens': self.config.get('MAX_TOKENS', 4000),
            'temperature': self.config.get('TEMPERATURE', 0.7),
            'streaming': self.config.get('ENABLE_STREAMING', True),
            'auto_save': self.config.get('AUTO_SAVE', True),
            'backup_changes': self.config.get('BACKUP_CHANGES', True),
            'theme': self.config.get('THEME', 'monokai')
        }
