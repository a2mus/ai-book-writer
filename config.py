"""Configuration for the article generation system with military terminology support"""
import os
from typing import Dict, List

def get_config(local_url: str = "http://localhost:11434/v1") -> Dict:
    """Get the configuration for the agents"""
    
    # Ollama config with command-r7b-arabic model
    config_list = [{
        'model': 'command-r7b-arabic:7b-02-2025-q8_0',
        'base_url': local_url,
        'api_key': "ollama"
    }]

    # Common configuration for all agents
    agent_config = {
        "seed": 42,
        "temperature": 0.7,
        "config_list": config_list,
        "timeout": 600,
        "cache_seed": None,
        
        # Code execution configuration - disable Docker
        "code_execution_config": {
            "use_docker": False,  # Set to False to disable Docker
            "timeout": 60,
            "last_n_messages": 3,
        },
        
        # Article structure configuration
        "article_structure": {
            "max_sections": 5,
            "section_word_limit": 500,
            "intro_word_limit": 250,
            "conclusion_word_limit": 250
        },
        
        # Military terminology settings
        "terminology": {
            "glossary_path": "glossaire_2022_sample.csv",
            "languages": ["arabic", "french"],
            "default_language": "arabic",
            "min_terms_per_section": 3,  # Minimum military terms to include per section
            "max_related_terms": 5       # Maximum related terms to suggest
        },
        
        # Output settings
        "output": {
            "dir": "article_output",
            "formats": ["txt", "md"],
            "create_glossary": True      # Generate terminology glossary for the article
        }
    }
    
    return agent_config