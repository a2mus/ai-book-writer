# System Patterns

## Architecture Overview
The system utilizes a multi-agent architecture based on AutoGen, where specialized agents collaborate to perform different tasks in the article generation pipeline.

## Key Technical Decisions
- **Multi-Agent Framework:** Using AutoGen for agent definition and collaboration.
- **Terminology Handling:** Dedicated Terminology Checker agent and a centralized Terminology Manager class for consistency.
- **Configuration:** Centralized configuration system for agents and article structure.
- **Modularity:** Designed for easy addition of new agents, languages, and features.

## Design Patterns
- **Agent-Based System:** Each agent has a specific role and responsibility.
- **Pipeline Architecture:** Article generation follows a defined sequence of steps (Outline -> Section Generation -> Assembly).
- **Centralized Configuration:** Configuration settings are managed in a single location.

## Component Relationships
- **User Proxy Agent:** Interfaces with the user.
- **Outline Creator & Editor:** Collaborate on article structure.
- **Writer, Researcher, Terminology Checker, Editor:** Collaborate on section content generation within GroupChats.
- **Formatter:** Handles final article formatting.
- **Terminology Manager:** Used by the Terminology Checker to access the glossary.

## Directory Structure
- `/article_output/`: Stores generated articles.
- `/docs/`: System documentation.
- `config.py`: Agent configuration.
- `agents.py`: Agent definitions.
- `article_generator.py`: Main generation logic.
- `outline_generator.py`: Outline creation.
- `terminology_handler.py`: Terminology processing.
- `main.py`: Entry point.
- `glossaire_2022_sample.csv`: Terminology data.
