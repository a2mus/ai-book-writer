"""Generate articles based on outlines"""
import os
from typing import Dict, List, Optional
import autogen
from terminology_handler import TerminologyManager
import re

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
DetectorFactory.seed = 0

def detect_language_distribution(text, target_lang, technical_terms=None):
    """Detects the proportion of text in the target language vs. other languages."""
    import re

    # Split into sentences (simple split, can be improved)
    sentences = re.split(r'(?<=[.!?؟])\s+', text)
    total = 0
    wrong_lang = 0
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        # Skip if sentence is just a technical term (heuristic: contains many Latin chars or is short)
        if technical_terms:
            if any(term in sent for term in technical_terms):
                continue
        try:
            lang = detect(sent)
        except LangDetectException:
            continue
        total += 1
        if lang != target_lang:
            wrong_lang += 1
    if total == 0:
        return 0.0
    return wrong_lang / total

def generate_article_section(
    agents: Dict,
    section_title: str, # This is the full title from the outline, e.g., "## My Section Title"
    section_number: int,
    section_outline_details: str, # This is the content/bullet points for this specific section from the outline
    previous_sections: Optional[List[str]] = None,
    target_language: str = "ar"):
    """Generate content for a specific article section"""
    
    writer = agents["writer"]
    editor = agents["editor"]
    researcher = agents["researcher"]
    terminology_checker = agents["terminology_checker"]
    web_searcher = agents["web_searcher"] # Get the new agent
    user_proxy = agents["user_proxy"]
    
    # Create group chat for this section
    section_group_chat = autogen.GroupChat(
        agents=[user_proxy, writer, editor, researcher, terminology_checker, web_searcher], # Add web_searcher
        messages=[],
        max_round=10
    )
    
    # Get the agent config from one of the agents
    llm_config = writer.llm_config
    
    # Initialize manager with llm_config
    manager = autogen.GroupChatManager(
        groupchat=section_group_chat, 
        llm_config=llm_config
    )
    
    # Context from previous sections
    previous_context = ""
    if previous_sections and len(previous_sections) > 0:
        previous_context = "Previous sections content:\n" + "\n".join(previous_sections)
    
    # Get terminology data for the checker agent
    # Use the glossary path
    glossary_path = "glossaire_2022_sample.csv"
    terminology_manager = TerminologyManager(glossary_path)
    
    # Create a term list for guidelines (limit to a few examples to keep prompt size manageable)
    term_examples = list(terminology_manager.arabic_terms.keys())[:5]
    term_list = "\n".join([f"- {term}: {terminology_manager.arabic_terms[term]['arabic_def'][:100]}..." for term in term_examples])
    
    # Prompt for section generation.
    # section_title is the main title for this section (e.g., "## Title").
    # section_outline_details contains the bullet points/notes for this section from the outline.
    section_prompt = f"""
    You are generating the body content for a section of a military article.
    The main title for this section is: "{section_title}"
    Your task is to write the detailed content that should appear *under* this title.
    Do NOT repeat the main section title ("{section_title}") in your output.
    You can and should use sub-headings (e.g., starting with ### or ####) within your content if appropriate for structure.

    The specific points to cover in this section, based on the article outline, are:
    {section_outline_details}

    {previous_context}

    TERMINOLOGY GUIDELINES:
    Use appropriate military terminology. Examples:
    {term_list}
    - Write the entire response in {target_language.upper()}, except for technical or military terms, which may be in English or French if there is no direct translation. Do NOT write full sentences or paragraphs in any language other than {target_language.upper()}. If you do, your answer will be rejected.

    FORMATTING GUIDELINES:
    - If "{section_title}" contains "Introduction", "Conclusion", "المقدمة", or "الخاتمة", use only paragraphs (no bullet points).
    - For all other sections, use a mix of paragraphs and bullet points. Start with a short introductory paragraph, then present key information as bullet points, and use short paragraphs for explanations or transitions as needed.
    - Avoid using only bullet points for the entire section.

    Focus on creating informative, well-structured content that flows logically. Keep the writing clear, concise, and engaging.
    The section should be approximately 300-500 words.
    Ensure your response is ONLY the body content for this section.
    """
    
    try:
        # Generate section content
        user_proxy.initiate_chat(manager, message=section_prompt)
        
        # Extract the final content from the conversation
        chat_history = section_group_chat.messages
        final_content = chat_history[-1]["content"]
        
        # Automatic terminology replacement step
        # Example replacement map: {incorrect_term: correct_term}
        # In production, this should be expanded or loaded from config
        replacement_map = {
            # Example: "غير صحيح": "صحيح",  # Replace with real mappings as needed
            # "variant_term": "official_glossary_term"
        }
        final_content, suggestions = terminology_manager.check_and_replace_content(final_content, language="arabic", replacement_map=replacement_map)

        # If we have suggestions or corrections, log them
        if suggestions:
            print(f"Terminology replacements/suggestions in section {section_number}: {suggestions}")
        
        # Language enforcement check
        # Map language code to langdetect code
        lang_map = {"arabic": "ar", "french": "fr", "english": "en"}
        target_lang_code = lang_map.get(target_language.lower(), "ar") # Use passed target_language
        # Use technical terms as exceptions
        technical_terms = term_examples
        wrong_lang_ratio = detect_language_distribution(final_content, target_lang_code, technical_terms)
        if wrong_lang_ratio > 0.2:
            print(f"WARNING: More than 20% of the generated section is not in the target language ({target_language}). Please review or regenerate this section.")
        
    except Exception as e:
        print(f"Error generating section {section_title}: {str(e)}")
        # Fallback content
        final_content = f"# {section_title}\n\nThis section will cover important aspects of electronic warfare in countering drones."
    
    # Write section to file
    # The filename logic might need adjustment based on how section_number is now determined in main.py
    if section_number == 0:
        filename = "introduction.txt"
    elif section_number == -1:
        filename = "conclusion.txt"
    else:
        # Sanitize section_title for filename
        safe_title_part = re.sub(r'[^\w\s-]', '', section_title.splitlines()[0])[:50].strip().replace(' ', '_')
        filename = f"section_{section_number}_{safe_title_part}.txt" if safe_title_part else f"section_{section_number}.txt"
    os.makedirs("article_output/sections", exist_ok=True)
    with open(f"article_output/sections/{filename}", "w", encoding="utf-8") as f:
        f.write(final_content)
        
    return final_content
