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
# Technical Context

## Technologies Used
- **AutoGen:** Multi-agent conversation framework.
- **Python:** Primary programming language.
- **CSV:** Format for the military terminology glossary.
- **Markdown:** Format for documentation and potentially article output.

## Development Setup
- The project is structured with directories for agents, documentation, tests, and utilities.
- Configuration is managed in `config.py`.
- The military glossary is expected as a CSV file (`glossaire_2022_sample.csv`).

## Technical Constraints
- Reliance on the AutoGen framework for agent interaction.
- The quality of terminology handling is dependent on the accuracy and completeness of the provided CSV glossary.
- Current implementation uses a specific Ollama model (`command-r7b-arabic:7b-02-2025-q8_0`) which may impact performance and output quality depending on the environment.
- Bilingual support is currently limited to Arabic and French based on the provided glossary.

## Dependencies
- AutoGen library.
- Standard Python libraries (e.g., `csv`, `re`).
- An accessible language model compatible with AutoGen (currently configured for Ollama).