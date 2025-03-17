"""Generate outlines for military articles with terminology support"""
import os
import autogen
from typing import Dict, List
import re

class OutlineGenerator:
    def __init__(self, agents: Dict[str, autogen.ConversableAgent], agent_config: Dict):
        self.agents = agents
        self.agent_config = agent_config

    def generate_outline(self, topic: str, target_audience: str, tone: str, word_count: int) -> str:
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
            max_round=5
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
            intro_words = min(250, total_words * 0.15)
            conclusion_words = min(250, total_words * 0.15)
            remaining_words = total_words - (intro_words + conclusion_words)
            section_words = remaining_words / 3  # Default to 3 main sections
        except ValueError:
            intro_words = 250
            section_words = 500
            conclusion_words = 250
        
        # Generate outline prompt with military terminology focus
        prompt = f"""
        Create a detailed outline for a military article on "{topic}".
        
        Parameters:
        - Target audience: {target_audience}
        - Tone: {tone}
        - Total word count: {word_count} words
        
        Structure:
        1. Introduction ({int(intro_words)} words)
           - Context and importance of the topic
           - Key military concepts to be covered
           - Article objectives
        
        2. Main Sections (3-5 sections, ~{int(section_words)} words each)
           - Each section should focus on specific military aspects
           - Include relevant military terminology and definitions
           - Ensure logical progression between sections
        
        3. Conclusion ({int(conclusion_words)} words)
           - Summary of key military concepts covered
           - Strategic implications
           - Final insights
        
        Requirements:
        - Use precise military terminology
        - Maintain technical accuracy
        - Follow military writing conventions
        - Include clear section headings
        - List key military terms to be defined in each section
        
        Format the outline with clear section titles and bullet points for key content.
        """
        
        try:
            # Generate outline
            user_proxy.initiate_chat(manager, message=prompt)
            
            # Extract the final outline from the conversation
            chat_history = outline_group_chat.messages
            final_outline = chat_history[-1]["content"]
            
            # Save outline to file
            os.makedirs("article_output", exist_ok=True)
            with open("article_output/outline.txt", "w", encoding="utf-8") as f:
                f.write(final_outline)
                
            return final_outline
            
        except Exception as e:
            print(f"Error generating outline: {str(e)}")
            return ""

    def _get_sender(self, msg: Dict) -> str:
        """Helper to get sender from message regardless of format"""
        return msg.get("sender") or msg.get("name", "")

    def _extract_outline_content(self, messages: List[Dict]) -> str:
        """Extract outline content from messages with better error handling"""
        print("Searching for outline content in messages...")
        
        # Look for content between "OUTLINE:" and "END OF OUTLINE"
        for msg in reversed(messages):
            content = msg.get("content", "")
            if "OUTLINE:" in content:
                # Extract content between OUTLINE: and END OF OUTLINE
                start_idx = content.find("OUTLINE:")
                end_idx = content.find("END OF OUTLINE")
                
                if (start_idx != -1):
                    if (end_idx != -1):
                        return content[start_idx:end_idx].strip()
                    else:
                        # If no END OF OUTLINE marker, take everything after OUTLINE:
                        return content[start_idx:].strip()
                        
        # Fallback: look for content with chapter markers
        for msg in reversed(messages):
            content = msg.get("content", "")
            if "Chapter 1:" in content or "**Chapter 1:**" in content:
                return content

        return ""

    def _process_outline_results(self, messages: List[Dict], num_chapters: int) -> List[Dict]:
        """Extract and process the outline with strict format requirements"""
        outline_content = self._extract_outline_content(messages)
        
        if not outline_content:
            print("No structured outline found, attempting emergency processing...")
            return self._emergency_outline_processing(messages, num_chapters)

        chapters = []
        chapter_sections = re.split(r'Chapter \d+:', outline_content)
        
        for i, section in enumerate(chapter_sections[1:], 1):  # Skip first empty section
            try:
                    # Extract required components
                title_match = re.search(r'\*?\*?Title:\*?\*?\s*(.+?)(?=\n|$)', section, re.IGNORECASE)
                events_match = re.search(r'\*?\*?Key Events:\*?\*?\s*(.*?)(?=\*?\*?Character Developments:|$)', section, re.DOTALL | re.IGNORECASE)
                character_match = re.search(r'\*?\*?Character Developments:\*?\*?\s*(.*?)(?=\*?\*?Setting:|$)', section, re.DOTALL | re.IGNORECASE)
                setting_match = re.search(r'\*?\*?Setting:\*?\*?\s*(.*?)(?=\*?\*?Tone:|$)', section, re.DOTALL | re.IGNORECASE)
                tone_match = re.search(r'\*?\*?Tone:\*?\*?\s*(.*?)(?=\*?\*?Chapter \d+:|$)', section, re.DOTALL | re.IGNORECASE)

                # If no explicit title match, try to get it from the chapter header
                if not title_match:
                    title_match = re.search(r'\*?\*?Chapter \d+:\s*(.+?)(?=\n|$)', section)

                # Verify all components exist
                if not all([title_match, events_match, character_match, setting_match, tone_match]):
                    print(f"Missing required components in Chapter {i}")
                    missing = []
                    if not title_match: missing.append("Title")
                    if not events_match: missing.append("Key Events")
                    if not character_match: missing.append("Character Developments")
                    if not setting_match: missing.append("Setting")
                    if not tone_match: missing.append("Tone")
                    print(f"  Missing: {', '.join(missing)}")
                    continue

                # Format chapter content
                chapter_info = {
                    "chapter_number": i,
                    "title": title_match.group(1).strip(),
                    "prompt": "\n".join([
                        f"- Key Events: {events_match.group(1).strip()}",
                        f"- Character Developments: {character_match.group(1).strip()}",
                        f"- Setting: {setting_match.group(1).strip()}",
                        f"- Tone: {tone_match.group(1).strip()}"
                    ])
                }
                
                # Verify events (at least 3)
                events = re.findall(r'-\s*(.+?)(?=\n|$)', events_match.group(1))
                if len(events) < 3:
                    print(f"Chapter {i} has fewer than 3 events")
                    continue

                chapters.append(chapter_info)

            except Exception as e:
                print(f"Error processing Chapter {i}: {str(e)}")
                continue

        # If we don't have enough valid chapters, raise error to trigger retry
        if len(chapters) < num_chapters:
            raise ValueError(f"Only processed {len(chapters)} valid chapters out of {num_chapters} required")

        return chapters

    def _verify_chapter_sequence(self, chapters: List[Dict], num_chapters: int) -> List[Dict]:
        """Verify and fix chapter numbering"""
        # Sort chapters by their current number
        chapters.sort(key=lambda x: x['chapter_number'])
        
        # Renumber chapters sequentially starting from 1
        for i, chapter in enumerate(chapters, 1):
            chapter['chapter_number'] = i
        
        # Add placeholder chapters if needed
        while len(chapters) < num_chapters:
            next_num = len(chapters) + 1
            chapters.append({
                'chapter_number': next_num,
                'title': f'Chapter {next_num}',
                'prompt': '- Key events: [To be determined]\n- Character developments: [To be determined]\n- Setting: [To be determined]\n- Tone: [To be determined]'
            })
        
        # Trim excess chapters if needed
        chapters = chapters[:num_chapters]
        
        return chapters

    def _emergency_outline_processing(self, messages: List[Dict], num_chapters: int) -> List[Dict]:
        """Emergency processing when normal outline extraction fails"""
        print("Attempting emergency outline processing...")
        
        chapters = []
        current_chapter = None
        
        # Look through all messages for any chapter content
        for msg in messages:
            content = msg.get("content", "")
            lines = content.split('\n')
            
            for line in lines:
                # Look for chapter markers
                chapter_match = re.search(r'Chapter (\d+)', line)
                if chapter_match and "Key events:" in content:
                    if current_chapter:
                        chapters.append(current_chapter)
                    
                    current_chapter = {
                        'chapter_number': int(chapter_match.group(1)),
                        'title': line.split(':')[-1].strip() if ':' in line else f"Chapter {chapter_match.group(1)}",
                        'prompt': []
                    }
                
                # Collect bullet points
                if current_chapter and line.strip().startswith('-'):
                    current_chapter['prompt'].append(line.strip())
            
            # Add the last chapter if it exists
            if current_chapter and current_chapter.get('prompt'):
                current_chapter['prompt'] = '\n'.join(current_chapter['prompt'])
                chapters.append(current_chapter)
                current_chapter = None
        
        if not chapters:
            print("Emergency processing failed to find any chapters")
            # Create a basic outline structure
            chapters = [
                {
                    'chapter_number': i,
                    'title': f'Chapter {i}',
                    'prompt': '- Key events: [To be determined]\n- Character developments: [To be determined]\n- Setting: [To be determined]\n- Tone: [To be determined]'
                }
                for i in range(1, num_chapters + 1)
            ]
        
        # Ensure proper sequence and number of chapters
        return self._verify_chapter_sequence(chapters, num_chapters)

def generate_outline(agents, topic, target_audience, tone, word_count):
    """Wrapper function to create an OutlineGenerator and call generate_outline"""
    # Get the agent config from one of the agents rather than using an index
    agent_config = next(iter(agents.values())).llm_config
    generator = OutlineGenerator(agents, agent_config)
    return generator.generate_outline(topic, target_audience, tone, word_count)