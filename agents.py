"""Define specialized agents for military article generation"""
from typing import Dict, List
import autogen
from utils.web_search import perform_web_search

def create_agents(agent_config: Dict) -> Dict:
    """Create the specialized agents for article generation"""
    
    # Writer agent - generates primary content
    writer = autogen.AssistantAgent(
        name="Writer",
        system_message="""You are an expert military writer who creates clear, technically accurate content.
Your primary goal is to generate the body content for a given section title and outline details.
Do NOT repeat the main section title in your output. Use sub-headings (e.g., H3, H4) within your content as appropriate.
Focus on using precise military terminology, maintaining a formal tone, and adhering strictly to the provided outline segment for structure and content focus.
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
- Logical flow between sections
- Ensuring the generated section strictly follows the requested structure (e.g., heading levels, paragraph/bullet point mix) and word count guidelines from the outline.
- Removing redundancies and improving conciseness. Ensure the main section title is NOT repeated in the content.""",
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
    
    # Web Searcher agent - fetches updated data from the internet
    web_searcher_llm_config = agent_config.copy()
    web_searcher_llm_config["tools"] = [
        {
            "type": "function",
            "function": {
                "name": "perform_web_search",
                "description": "Searches the web for a given query to find up-to-date information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find information about.",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "The desired number of search results.",
                            "default": 3,
                        },
                    },
                    "required": ["query"],
                },
            },
        }
    ]
    web_searcher = autogen.AssistantAgent(
        name="WebSearcher",
        system_message="You are a Web Search Specialist. When you need to find information from the internet, use the 'perform_web_search' tool.",
        llm_config=web_searcher_llm_config,
    )
    
    # User proxy for interaction
    user_proxy = autogen.UserProxyAgent(
        name="ArticleRequester",
        human_input_mode="TERMINATE",
        system_message="You are requesting a military article with specific terminology requirements.",
        code_execution_config=agent_config.get("code_execution_config", {"use_docker": False, "work_dir": "article_output"}),
    )
    user_proxy.register_function(
        function_map={
            "perform_web_search": perform_web_search
        }
    )
    
    return {
        "writer": writer,
        "editor": editor,
        "researcher": researcher,
        "outline_creator": outline_creator,
        "formatter": formatter,
        "terminology_checker": terminology_checker,
        "web_searcher": web_searcher,
        "user_proxy": user_proxy
    }
