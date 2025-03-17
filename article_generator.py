"""Generate articles based on outlines"""
import os
from typing import Dict, List
import autogen
from terminology_handler import TerminologyManager

def generate_article_section(agents: Dict, section_title: str, section_number: int, outline_content: str, previous_sections: List[str] = None):
    """Generate content for a specific article section"""
    
    writer = agents["writer"]
    editor = agents["editor"]
    researcher = agents["researcher"]
    terminology_checker = agents["terminology_checker"]
    user_proxy = agents["user_proxy"]
    
    # Create group chat for this section
    section_group_chat = autogen.GroupChat(
        agents=[user_proxy, writer, editor, researcher, terminology_checker],
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
    
    # Prompt for section generation
    section_prompt = f"""
    Write section {section_number}: "{section_title}" for our article.
    
    Article outline:
    {outline_content}
    
    {previous_context}
    
    TERMINOLOGY GUIDELINES:
    Use appropriate military terminology. Examples:
    {term_list}
    
    Focus on creating informative, well-structured content that flows logically from the previous sections.
    Keep the writing clear, concise, and engaging.
    The section should be approximately 300-500 words.
    """
    
    try:
        # Generate section content
        user_proxy.initiate_chat(manager, message=section_prompt)
        
        # Extract the final content from the conversation
        chat_history = section_group_chat.messages
        final_content = chat_history[-1]["content"]
        
        # Final terminology check
        final_content, suggestions = terminology_manager.check_content(final_content)
        
        # If we have suggestions, log them
        if suggestions:
            print(f"Found {len(suggestions)} terminology suggestions in section {section_number}")
        
    except Exception as e:
        print(f"Error generating section {section_title}: {str(e)}")
        # Fallback content
        final_content = f"# {section_title}\n\nThis section will cover important aspects of electronic warfare in countering drones."
    
    # Write section to file
    if section_number == 0:
        filename = "introduction.txt"
    elif section_number == -1:
        filename = "conclusion.txt"
    else:
        filename = f"section_{section_number}.txt"
    
    os.makedirs("article_output/sections", exist_ok=True)
    with open(f"article_output/sections/{filename}", "w", encoding="utf-8") as f:
        f.write(final_content)
        
    return final_content
