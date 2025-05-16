"""Main script for running the article generation system with military terminology support"""
from config import get_config
from agents import create_agents
from article_generator import generate_article_section
from outline_generator import generate_outline
from terminology_handler import TerminologyManager
import re
import os

def main():
    # Get configuration
    config = get_config()

    # Separate llm_config from other configurations
    llm_config = {
        "seed": config.get("seed"),
        "temperature": config.get("temperature"),
        "config_list": config.get("config_list"),
        "timeout": config.get("timeout"),
        "cache_seed": config.get("cache_seed"),
    }

    # Extract other configuration sections
    code_execution_config = config.get("code_execution_config")
    article_structure_config = config.get("article_structure")
    terminology_config = config.get("terminology")
    output_config = config.get("output")

    # Default article parameters
    default_topic = "دور وأهمية الحرب الالكترونية في التصدي للطائرات بدون طيار"
    default_audience = "military personel"
    default_tone = "formal"
    default_word_count = "500"
    default_language = "arabic"
    
    # Get article parameters with defaults
    print("\n=== Military Article Generation System ===\n")
    topic = input(f"Enter article topic [{default_topic}]: ") or default_topic
    target_audience = input(f"Enter target audience [{default_audience}]: ") or default_audience
    tone = input(f"Enter desired tone (formal, technical, etc.) [{default_tone}]: ") or default_tone

    word_count = input(f"Enter target word count [{default_word_count}]: ") or default_word_count
    language = input(f"Enter language (arabic/french) [{default_language}]: ").lower() or default_language
    
    # Initialize terminology manager with military glossary
    glossary_path = "glossaire_2022_sample.csv"
    term_manager = TerminologyManager(glossary_path)
    print(f"\nLoaded {len(term_manager.terminology)} military terms from glossary")
    
    # Get relevant terminology suggestions for the topic
    relevant_terms = term_manager.suggest_terms_for_topic(topic, language)
    if relevant_terms:
        print("\nRelevant military terms for your topic:")
        for term in relevant_terms[:5]:  # Show top 5 relevant terms
            if language == "arabic":
                print(f"- {term['arabic_term']}: {term['arabic_def']}")
            else:
                print(f"- {term['french_term']}: {term['french_def']}")
    
    # Create agents
    print("\nInitializing specialized agents...")
    agents = create_agents(llm_config)

    # Generate the outline
    print("\nGenerating article outline...")
    outline_content = generate_outline(agents, topic, target_audience, tone, word_count, language) # Pass language

    # Create output directory if it doesn't exist
    os.makedirs("article_output", exist_ok=True)

    # Save outline
    with open("article_output/outline.txt", "w", encoding="utf-8") as f:
        f.write(outline_content)
    print("Outline saved to article_output/outline.txt")

    # Parse the outline into sections (title and details)
    parsed_outline_sections = []
    current_section_title = None
    current_section_details = []

    for line in outline_content.split('\n'):
        # Regex to find markdown headings (##, ###, etc.)
        # This should match the style produced by OutlineCreator
        match = re.match(r"^(#+)\s*(.+)", line.strip()) # Simpler regex for any # heading
        if match:
            if current_section_title is not None: # Save previous section
                parsed_outline_sections.append({
                    "title": current_section_title,
                    "details": "\n".join(current_section_details).strip()
                })
            current_section_title = line.strip() # Keep the full heading line as title
            current_section_details = [] # Reset details for the new section
        elif current_section_title is not None: # Only append details if we are inside a section
            current_section_details.append(line)

    if current_section_title is not None: # Save the last section
        parsed_outline_sections.append({
            "title": current_section_title,
            "details": "\n".join(current_section_details).strip()
        })

    if not parsed_outline_sections:
        print("Warning: Could not parse any sections from the outline. Article generation might be incomplete.")
        # Fallback: treat the whole outline as a single section to generate if needed
        # This part can be enhanced based on how critical structured sections are.

    complete_article_parts = []
    previous_content_for_context = []

    # Generate each section based on the parsed outline
    for i, section_data in enumerate(parsed_outline_sections):
        section_title_from_outline = section_data["title"]
        section_details_from_outline = section_data["details"]

        print(f"\nGenerating content for section: {section_title_from_outline}...")

        # Determine section_number for article_generator (0 for intro, -1 for conclusion, 1+ for body)
        # This is a heuristic and might need refinement based on outline conventions
        num = i
        title_lower = section_title_from_outline.lower()
        if "introduction" in title_lower or "مقدمة" in title_lower:
            num = 0
        elif "conclusion" in title_lower or "خاتمة" in title_lower or "الخاتمة" in title_lower :
            num = -1
        else:
            num = i + 1 # Assuming 0 is intro, so body sections start from 1

        section_body_content = generate_article_section(
            agents,
            section_title_from_outline, # This is the key title to generate content FOR
            num,
            section_details_from_outline, # Pass only the details for this section
            previous_content_for_context,
            target_language=language
        )
        # Assemble the section with its title
        full_section_text = f"{section_title_from_outline}\n\n{section_body_content}"
        complete_article_parts.append(full_section_text)
        previous_content_for_context.append(full_section_text) # Add full section for context

    # Combine into complete article
    print("\nAssembling complete article...")
    complete_article = "\n\n".join(complete_article_parts)

    # Final terminology check
    print("\nPerforming final terminology verification...")
    # Using check_and_replace_content for consistency, assuming an empty map if no global replacements
    final_article, suggestions = term_manager.check_and_replace_content(complete_article, language=language, replacement_map={})
    if suggestions:
        print(f"Made {len(suggestions)} terminology adjustments in the final document")

    # Save complete article
    with open("article_output/complete_article.txt", "w", encoding="utf-8") as f:
        f.write(final_article)
    
    print("\nArticle generation complete! Output saved to article_output/complete_article.txt")

if __name__ == "__main__":
    main()
