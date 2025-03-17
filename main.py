"""Main script for running the article generation system with military terminology support"""
from config import get_config
from agents import create_agents
from article_generator import generate_article_section
from outline_generator import generate_outline
from terminology_handler import TerminologyManager
import os

def main():
    # Get configuration
    agent_config = get_config()
    
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
    agents = create_agents(agent_config)
    
    # Generate the outline
    print("\nGenerating article outline...")
    outline = generate_outline(agents, topic, target_audience, tone, word_count)
    
    # Create output directory if it doesn't exist
    os.makedirs("article_output", exist_ok=True)
    
    # Save outline
    with open("article_output/outline.txt", "w", encoding="utf-8") as f:
        f.write(outline)
    print("Outline saved to article_output/outline.txt")
    
    # Generate introduction
    print("\nGenerating introduction...")
    intro = generate_article_section(agents, "Introduction", 0, outline)
    
    # Keep track of generated sections for context
    generated_sections = [intro]
    
    # Extract section titles from outline and generate each section
    sections = []
    for line in outline.split("\n"):
        if line.strip().startswith("Section") or line.strip().startswith("##"):
            sections.append(line.strip())
    
    # Generate each section
    for i, section_title in enumerate(sections, 1):
        print(f"\nGenerating section {i}: {section_title}...")
        section_content = generate_article_section(
            agents, 
            section_title, 
            i, 
            outline, 
            generated_sections
        )
        generated_sections.append(section_content)
    
    # Generate conclusion
    print("\nGenerating conclusion...")
    conclusion = generate_article_section(
        agents,
        "Conclusion",
        -1,
        outline,
        generated_sections
    )
    
    # Combine into complete article
    print("\nAssembling complete article...")
    complete_article = intro + "\n\n"
    for i, content in enumerate(generated_sections[1:], 1):
        complete_article += f"## {sections[i-1]}\n\n{content}\n\n"
    complete_article += f"## Conclusion\n\n{conclusion}"
    
    # Final terminology check
    print("\nPerforming final terminology verification...")
    final_article, suggestions = term_manager.check_content(complete_article, language)
    if suggestions:
        print(f"Made {len(suggestions)} terminology adjustments in the final document")
    
    # Save complete article
    with open("article_output/complete_article.txt", "w", encoding="utf-8") as f:
        f.write(final_article)
    
    print("\nArticle generation complete! Output saved to article_output/complete_article.txt")

if __name__ == "__main__":
    main()