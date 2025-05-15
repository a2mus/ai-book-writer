# System Patterns

## Architecture
- Multi-agent system based on AutoGen framework
- Centralized main coordination module
- Specialized agents for distinct tasks

## Agent Collaboration
- GroupChat for agent communication and task execution
- User Proxy Agent for user interaction
- Iterative refinement of content through agent feedback

## File Organization
- Dedicated `article_output` directory for generated files
- `docs` directory for system documentation
- `memory-bank` directory for project context and progress

## Data Flow
- User input -> Main Coordination -> Outline Generation -> Section Generation (iterative) -> Article Assembly -> Final Output
- Terminology handling integrated into Section Generation and Article Assembly

## Key Components
- Agents (Writer, Editor, Researcher, etc.)
- Configuration system
- Terminology Manager
- Outline Generator
- Article Generator
