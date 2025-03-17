# AI Article Writer

AI Article Writer is a multi-agent system designed to automatically create well-structured articles and specialized documents with consistent terminology using AutoGen's collaborative agent framework.

## Overview

This project employs multiple specialized agents working together to:

1. Generate detailed article outlines with introduction, sections, and conclusion
2. Create coherent content following the outline structure
3. Ensure consistent terminology using a military glossary reference
4. Maintain quality through multi-agent collaboration and review
5. Produce professionally formatted articles with consistent style

## Agents

- **Writer Agent**: Generates primary content for each article section
- **Editor Agent**: Reviews and improves content for clarity and accuracy
- **Researcher Agent**: Provides relevant information and context for sections
- **Outline Creator**: Structures the article with logical section progression
- **Formatter Agent**: Ensures consistent formatting and professional appearance
- **Terminology Checker**: Verifies terminology against a military glossary database

## Key Features

- **Military Terminology Consistency**: Integration with a military glossary (glossaire_2022_sample.csv)
- **Modular Design**: Independent agents handle specific aspects of article creation
- **Collaborative Generation**: Agents work together to refine content and ensure quality
- **Structured Output**: Articles follow a consistent introduction-body-conclusion format
- **Customizable Parameters**: Configure article length, tone, target audience, and more

## Usage

```python
python main.py
```

Follow the prompts to specify:
- Article topic
- Target audience
- Desired tone (formal, conversational, etc.)
- Target word count
- Path to terminology glossary CSV file

## Requirements

- Python 3.8+
- AutoGen
- Pandas
- Other dependencies in requirements.txt

## Installation

```bash
git clone https://github.com/yourusername/ai-article-writer.git
cd ai-article-writer
pip install -r requirements.txt
```

## Project Structure

```
/ai-article-writer/
    /article_output/         # Generated article files
        outline.txt
        introduction.txt
        section_1.txt
        section_2.txt
        conclusion.txt
        complete_article.txt
    config.py                # Agent configuration settings
    agents.py                # Agent definitions and roles
    article_generator.py     # Article generation logic
    outline_generator.py     # Outline creation functionality
    terminology_handler.py   # Military terminology processing
    main.py                  # Main execution script
    glossaire_2022_sample.csv # Military terminology reference data
```

## License

MIT License