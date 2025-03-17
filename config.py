"""Configuration for the article generation system"""
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
        "cache_seed": None,
        "article_structure": {
            "max_sections": 5,
            "section_word_limit": 500,
            "intro_word_limit": 250,
            "conclusion_word_limit": 250
        }
    }
    
    return agent_config