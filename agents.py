"""Define specialized agents for military article generation"""
from typing import Dict, List
import autogen

def create_agents(agent_config: Dict) -> Dict:
    """Create the specialized agents for article generation"""
    
    # Writer agent - generates primary content
    writer = autogen.AssistantAgent(
        name="Writer",
        system_message="""You are an expert military writer who creates clear, technically accurate content.
Focus on using precise military terminology and maintaining formal tone.
Always verify technical accuracy and use established military writing conventions.""",
        llm_config=agent_config,
    )
    
    # Editor agent - reviews and improves content
    editor = autogen.AssistantAgent(
        name="Editor",
        system_message="""You are an expert military editor who reviews content for:
- Proper use of military terminology
- Technical accuracy
- Clarity and coherence
- Formal military writing style
- Logical flow between sections""",
        llm_config=agent_config,
    )
    
    # Researcher agent - provides military context
    researcher = autogen.AssistantAgent(
        name="Researcher",
        system_message="""You are a military research specialist who:
- Provides accurate military context and information
- Verifies technical details and terminology
- Ensures factual accuracy of military concepts
- Suggests relevant military examples and references""",
        llm_config=agent_config,
    )
    
    # Outline creator - structures the article
    outline_creator = autogen.AssistantAgent(
        name="OutlineCreator",
        system_message="""You create logical article outlines that:
- Follow military writing conventions
- Include clear section progression
- Incorporate key military concepts
- Maintain focus on technical accuracy
- Structure content for optimal comprehension""",
        llm_config=agent_config,
    )
    
    # Formatter agent - ensures consistent style
    formatter = autogen.AssistantAgent(
        name="Formatter",
        system_message="""You ensure professional military document formatting:
- Follow military writing style guides
- Maintain consistent terminology usage
- Apply proper citation formats
- Structure content clearly
- Format technical terms appropriately""",
        llm_config=agent_config,
    )
    
    # Terminology checker - verifies military terms
    terminology_checker = autogen.AssistantAgent(
        name="TerminologyChecker",
        system_message="""You ensure consistent and accurate military terminology:
- Verify terms against the official glossary
- Suggest correct terminology usage
- Check for consistency in both Arabic and French
- Provide term definitions when needed
- Ensure technical accuracy of term usage""",
        llm_config=agent_config,
    )
    
    # User proxy for interaction
    user_proxy = autogen.UserProxyAgent(
        name="ArticleRequester",
        human_input_mode="TERMINATE",
        system_message="You are requesting a military article with specific terminology requirements.",
        code_execution_config=agent_config.get("code_execution_config", {"use_docker": False, "work_dir": "article_output"}),
    )
    
    return {
        "writer": writer,
        "editor": editor,
        "researcher": researcher,
        "outline_creator": outline_creator,
        "formatter": formatter,
        "terminology_checker": terminology_checker,
        "user_proxy": user_proxy
    }