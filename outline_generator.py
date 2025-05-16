"""Generate outlines for military articles with terminology support"""
import os
import autogen
from typing import Dict, List
import re

class OutlineGenerator:
    def __init__(self, agents: Dict[str, autogen.ConversableAgent], agent_config: Dict):
        self.agents = agents
        self.agent_config = agent_config

    def generate_outline(self, topic: str, target_audience: str, tone: str, word_count: int, language: str = "arabic") -> str:
        """Generate an article outline based on topic and parameters"""
        print("\nGenerating outline...")
        
        outline_creator = self.agents["outline_creator"]
        editor = self.agents["editor"]
        terminology_checker = self.agents["terminology_checker"]
        user_proxy = self.agents["user_proxy"]
        
        # Create group chat for outline creation
        outline_group_chat = autogen.GroupChat(
            agents=[user_proxy, outline_creator, editor, terminology_checker],
            messages=[],
            max_round=10 # Increased rounds for potentially better refinement
        )
        
        # Get the LLM config from one of the agents
        llm_config = outline_creator.llm_config
        
        # Initialize manager with llm_config
        manager = autogen.GroupChatManager(
            groupchat=outline_group_chat,
            llm_config=llm_config
        )
        
        # Calculate section distribution based on word count
        try:
            total_words = int(word_count)
            intro_words = min(150, max(75, total_words * 0.10)) # Adjusted intro/conclusion words
            conclusion_words = min(150, max(75, total_words * 0.10))
            remaining_words = total_words - (intro_words + conclusion_words)
            num_main_sections = 3 # Default to 3 main sections, can be made configurable
            section_words = remaining_words / num_main_sections if num_main_sections > 0 else remaining_words
        except ValueError:
            intro_words, section_words, conclusion_words = 100, 300, 100 # Fallback
        
        # Generate outline prompt with military terminology focus
        prompt = f"""
        Create a detailed outline for a military article on "{topic}".
        
        Parameters:
        - Target audience: {target_audience}
        - Tone: {tone}
        - Total word count: {word_count} words
        
        Output a well-structured Markdown outline.
        Use '##' for main section titles (Introduction, Main Section X, Conclusion).
        Use '###' or '####' for sub-points or details within each main section.
        Include estimated word counts for each main section in parentheses, e.g., (approx. {int(intro_words)} words).

        Example Structure:
        ## 1. Introduction (approx. {int(intro_words)} words)
           - Context and importance of the topic
           - Key military concepts to be covered
           - Article objectives
        
        ## 2. Main Section 1: [Descriptive Title] (approx. {int(section_words)} words)
           - Each section should focus on specific military aspects
           - List key sub-topics or bullet points for content.
           - Ensure logical progression between sections
        
        (Add 2-4 more main sections as appropriate for the topic, each with a descriptive title and estimated word count of approx. {int(section_words)} words)

        ## X. Conclusion (approx. {int(conclusion_words)} words)
           - Summary of key military concepts covered
           - Strategic implications
           - Final insights
        
        Requirements:
        - The outline must be written entirely in {language.upper()}.
        - Ensure technical accuracy and use precise military terminology where appropriate within the outline points.
        - The structure should be logical and easy for other agents to follow to write the full article.
        """
        
        try:
            # Generate outline
            user_proxy.initiate_chat(manager, message=prompt)
            
            # Extract the final outline from the conversation
            chat_history = outline_group_chat.messages
            final_outline = chat_history[-1]["content"]
            # Basic cleanup: remove any "OUTLINE:" or "END OF OUTLINE" markers if present
            final_outline = re.sub(r"^\s*OUTLINE:\s*", "", final_outline, flags=re.IGNORECASE | re.MULTILINE)
            final_outline = re.sub(r"\s*END OF OUTLINE\s*$", "", final_outline, flags=re.IGNORECASE | re.MULTILINE)
            print("\nGenerated Outline:\n", final_outline)
            return final_outline
            
        except Exception as e:
            print(f"Error generating outline: {str(e)}")
            return ""

def generate_outline(agents, topic, target_audience, tone, word_count, language="arabic"):
    """Wrapper function to create an OutlineGenerator and call generate_outline"""
    # Get the agent config from one of the agents rather than using an index
    agent_config = next(iter(agents.values())).llm_config
    generator = OutlineGenerator(agents, agent_config)
    return generator.generate_outline(topic, target_audience, tone, word_count, language)
