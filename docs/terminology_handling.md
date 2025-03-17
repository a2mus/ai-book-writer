# Military Terminology Handling

This document explains how the AI Article Writer manages and enforces military terminology consistency in the generated content.

## Overview

The system incorporates specialized terminology from a military glossary (`glossaire_2022_sample.csv`), ensuring accurate and consistent use of military terms in the generated articles. This is accomplished through a dedicated Terminology Checker agent and supporting infrastructure.

## Glossary Structure

The military terminology glossary uses the following format:

| Column | Description | Example |
|--------|-------------|---------|
| Num | Unique identifier | 1 |
| Old_Num | Legacy identifier | 1 |
| MOTS_AR | Term in Arabic | الإبرار البحري الاستعراضي |
| MOTS_fr | Term in French | Débarquement naval démonstratif |
| DESIGNATION | Definition in Arabic | إبرار تمثيلي مشابه للإبرار الحقيقي... |
| DESIGNATION_fr | Definition in French | Débarquement similaire au débarquement réel... |
| chairdappartenance | Category | قوات بحرية |
| Sous_Chapitre | Subcategory | 20 |

## Implementation

### Terminology Agent

The `TerminologyAgent` class in `terminology_agent.py` provides the core functionality:

```python
class TerminologyAgent:
    def __init__(self, glossary_file):
        self.glossary = self.load_glossary(glossary_file)
        self.arabic_terms = {}
        self.french_terms = {}
        self.categorized_terms = {}
        self.process_glossary()
```

Main features include:
- Loading and parsing the CSV glossary file
- Indexing terms by language and category
- Checking content for proper term usage
- Suggesting relevant terms for a given topic
- Providing definitions for used terms

### Integration Process

1. **During Planning**: The system suggests relevant terminology for the article topic
2. **During Writing**: Writers are provided term guidelines from the glossary
3. **During Editing**: Content is checked against the glossary for terminology accuracy
4. **Final Check**: Completed article undergoes a comprehensive terminology review

### Key Functions

#### Term Recognition

```python
def check_terminology_usage(self, chapter, language='arabic'):
    """Check if terminology is used correctly in the chapter"""
    terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
    results = {
        'used_terms': [],
        'missing_terms': [],
        'suggestions': []
    }
    
    # Check which terms are used
    for term, entry in terms_dict.items():
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, chapter, re.UNICODE):
            results['used_terms'].append(entry)
```

#### Term Suggestions

```python
def suggest_terms_for_topic(self, topic, language='arabic'):
    """Suggest terms related to a specific topic"""
    suggestions = []
    terms = self.arabic_terms if language == 'arabic' else self.french_terms
    
    for term, entry in terms.items():
        if topic.lower() in term.lower() or topic.lower() in entry['category'].lower():
            suggestions.append(entry)
```

## Usage Example

When generating an article on military tactics:

1. The system identifies relevant terms like "الاتجاه الرئيسي" (Direction principale)
2. These terms are provided to the writer agent as suggested terminology
3. During content generation, the terminology checker verifies proper usage
4. Misused or inconsistent terms are flagged for correction
5. Final document includes terminology with proper context and definitions

## Benefits

- **Accuracy**: Technical military content uses precise, domain-specific terminology
- **Consistency**: Terms maintain consistent definitions throughout the article
- **Educational**: Readers benefit from proper use of specialized military vocabulary
- **Credibility**: Proper terminology enhances the article's professional quality

## Future Enhancements

- Embedding-based semantic matching for better term suggestions
- Term frequency analysis to ensure natural distribution of terminology
- Automated glossary generation for the final document
- Cross-language term consistency checking