# AI Article Writer System Architecture

This document provides an overview of the AI Article Writer's system architecture, explaining how the different agents collaborate to generate coherent, terminology-consistent articles.

## System Overview

The AI Article Writer uses AutoGen's multi-agent framework to create a collaborative system where specialized agents handle different aspects of article generation. This approach allows for high-quality output through the division of responsibilities and agent cooperation.

```
                         ┌─────────────┐
                         │    User     │
                         │   Prompt    │
                         └──────┬──────┘
                                │
                                ▼
┌─────────────────────────────────────────────────┐
│               Main Coordination                 │
└─────────┬────────────┬─────────────┬────────────┘
          │            │             │
          ▼            ▼             ▼
┌──────────────┐ ┌──────────┐ ┌─────────────┐
│    Outline   │ │ Article  │ │ Terminology │
│  Generation  │ │Generation│ │  Handling   │
└──────┬───────┘ └────┬─────┘ └──────┬──────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  Final Article  │
             └─────────────────┘
```

## Agent Definitions and Responsibilities

### 1. User Proxy Agent

Acts as the interface between the user and the system, collecting input parameters and presenting results.

```python
user_proxy = UserProxyAgent(
    name="ArticleRequester",
    human_input_mode="TERMINATE",
    system_message="You are requesting an article on a specific topic.",
    code_execution_config={"work_dir": "article_output"},
)
```

### 2. Writer Agent

Responsible for generating the primary content for each section of the article.

```python
writer = AssistantAgent(
    name="Writer",
    system_message="You are an expert article writer who creates clear, engaging content. Focus on informative writing with logical flow.",
    llm_config=agent_config,
)
```

### 3. Editor Agent 

Reviews and improves content for clarity, coherence, and accuracy.

```python
editor = AssistantAgent(
    name="Editor",
    system_message="You are an expert editor who reviews article content for clarity, grammar, factual accuracy, and cohesion between sections.",
    llm_config=agent_config,
)
```

### 4. Researcher Agent

Provides relevant information, data, and context for article sections.

```python
researcher = AssistantAgent(
    name="Researcher",
    system_message="You are a research specialist who provides relevant information, data, and context for article sections.",
    llm_config=agent_config,
)
```

### 5. Outline Creator Agent

Structures the article with a logical progression of sections.

```python
outline_creator = AssistantAgent(
    name="OutlineCreator",
    system_message="You create logical article outlines with clear section progression and coherent structure.",
    llm_config=agent_config,
)
```

### 6. Formatter Agent

Ensures consistent formatting and professional appearance.

```python
formatter = AssistantAgent(
    name="Formatter",
    system_message="You ensure consistent formatting, citation style, and overall professional appearance for articles.",
    llm_config=agent_config,
)
```

### 7. Terminology Checker Agent

Verifies terminology against a military glossary database.

```python
terminology_checker = AssistantAgent(
    name="TerminologyChecker",
    system_message="You ensure consistent terminology usage throughout the article. You check content against a provided terminology database (CSV) and suggest replacements for non-standard terms.",
    llm_config=agent_config,
)
```

## Collaboration Workflow

The system uses GroupChat and GroupChatManager for agent collaboration:

```python
# Create group chat for this section
section_group_chat = autogen.GroupChat(
    agents=[user_proxy, writer, editor, researcher, terminology_checker],
    messages=[],
    max_round=10
)

manager = autogen.GroupChatManager(groupchat=section_group_chat)
```

### Process Flow

1. **Initialization**: User provides article topic, audience, tone, and word count
2. **Outline Generation**:
   - Outline Creator and Editor collaborate to create article structure
   - Outline is saved to `article_output/outline.txt`

3. **Section Generation** (for each section including introduction and conclusion):
   - Writer creates initial content
   - Researcher provides relevant information
   - Terminology Checker verifies proper term usage
   - Editor refines and improves content
   - Final section content is saved to respective files

4. **Article Assembly**:
   - All sections are combined
   - Final terminology check is performed
   - Complete article is saved to `article_output/complete_article.txt`

## Configuration System

The system uses a centralized configuration:

```python
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
        "article_structure": {
            "max_sections": 5,
            "section_word_limit": 500,
            "intro_word_limit": 250,
            "conclusion_word_limit": 250
        }
    }
    
    return agent_config
```

## Terminology Handling

The Terminology Manager maintains consistency:

```python
class TerminologyManager:
    """Manage terminology consistency throughout article generation"""
    
    def __init__(self, csv_path: str = "terminology.csv"):
        """Initialize with path to terminology CSV file"""
        self.csv_path = csv_path
        self.terminology = self._load_terminology()
        
    def check_content(self, content: str) -> Tuple[str, List[Dict]]:
        """Check content against terminology database and return suggestions"""
        suggestions = []
        modified_content = content
        
        for term, preferred in self.terminology.items():
            if term.lower() in content.lower() and term.lower() != preferred.lower():
                suggestions.append({
                    'original': term,
                    'preferred': preferred,
                    'context': self._get_context(content, term)
                })
                # Replace instances of the term with preferred terminology
                modified_content = modified_content.replace(term, preferred)
        
        return modified_content, suggestions
```

## Directory Structure

```
/ai-article-writer/
    /article_output/         # Generated article files
    /docs/                   # System documentation
    config.py                # Agent configuration settings
    agents.py                # Agent definitions and roles
    article_generator.py     # Article generation logic
    outline_generator.py     # Outline creation functionality
    terminology_handler.py   # Military terminology processing
    main.py                  # Main execution script
    glossaire_2022_sample.csv # Military terminology reference data
```

## Extending the Architecture

The system is designed to be modular and extensible:

1. **Additional Agents**: New specialized agents can be added by defining them in `agents.py` and incorporating them into the appropriate GroupChats
2. **Language Support**: The system can be extended to support additional languages by modifying the terminology handling
3. **Advanced Features**: The architecture allows for the addition of features like citation management, image generation, or fact-checking