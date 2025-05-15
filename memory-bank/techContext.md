# Technical Context

## Core Technologies
- Python 3.8+
- AutoGen (multi-agent framework)
- Pandas (for terminology handling)

## Development Environment
- Local machine setup
- VSCode as the primary IDE

## Dependencies
- Listed in `requirements.txt`
- Managed via pip

## Configuration
- Centralized configuration in `config.py`
- Uses Ollama for language models
- Configurable parameters for agents and article structure

## Terminology Handling Implementation
- `TerminologyManager` class in `terminology_handler.py`
- Loads terminology from a CSV file (`glossaire_2022_sample.csv`)
- Checks content and suggests replacements
