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
    
    manager = autogen.GroupChatManager(groupchat=section_group_chat)
    
    # Context from previous sections
    previous_context = ""
    if previous_sections and len(previous_sections) > 0:
        previous_context = "Previous sections content:\n" + "\n".join(previous_sections)
    
    # Get terminology data for the checker agent
    terminology_manager = TerminologyManager()
    term_list = "\n".join([f"- Use '{preferred}' instead of '{term}'" for term, preferred in terminology_manager.terminology.items()])
    
    # Prompt for section generation
    section_prompt = f"""
    Write section {section_number}: "{section_title}" for our article.
    
    Article outline:
    {outline_content}
    
    {previous_context}
    
    TERMINOLOGY GUIDELINES:
    {term_list}
    
    Focus on creating informative, well-structured content that flows logically from the previous sections.
    Keep the writing clear, concise, and engaging.
    The section should be approximately 300-500 words.
    Make sure to follow the terminology guidelines exactly.
    """
    
    # Generate section content
    user_proxy.initiate_chat(manager, message=section_prompt)
    
    # Extract the final content from the conversation
    chat_history = section_group_chat.messages
    final_content = chat_history[-1]["content"]
    
    # Final terminology check
    final_content, suggestions = terminology_manager.check_content(final_content)
    
    # If we have suggestions, log them
    if suggestions:
        suggestion_log = "\n".join([f"- Changed '{s['original']}' to '{s['preferred']}'" for s in suggestions])
        print(f"Terminology adjustments made in section {section_number}:\n{suggestion_log}")
    
    # Write section to file
    if section_number == 0:
        filename = "introduction.txt"
    elif section_number == -1:
        filename = "conclusion.txt"
    else:
        filename = f"section_{section_number}.txt"
    
    os.makedirs("article_output", exist_ok=True)
    with open(f"article_output/{filename}", "w", encoding="utf-8") as f:
        f.write(final_content)
        
    return final_content
