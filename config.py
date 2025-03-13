"""Configuration for the book generation system"""
import os
from typing import Dict, List

def get_config(local_url: str = "http://localhost:11434/v1") -> Dict:
    """Get the configuration for the agents"""
    
    # Ollama config with command-r7b-arabic model
    config_list = [{
        'model': 'command-r7b-arabic:7b-02-2025-q8_0',
        'base_url': local_url,
        'api_key': "ollama"  # Ollama typically doesn't need a real key
    }]

    # Common configuration for all agents
    agent_config = {
        "seed": 42,
        "temperature": 0.7,
        "config_list": config_list,
        "timeout": 600,
        "cache_seed": None
    }
    
    return agent_config