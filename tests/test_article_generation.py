"""Integration tests for the article generation pipeline"""
import unittest
import os
from main import main
from terminology_handler import TerminologyManager
from config import get_config
from agents import create_agents
from article_generator import generate_article_section
from outline_generator import generate_outline

class TestArticleGeneration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.config = get_config()
        self.agents = create_agents(self.config)
        self.term_manager = TerminologyManager("../glossaire_2022_sample.csv")
        
        # Test article parameters
        self.test_params = {
            "topic": "الإستراتيجية العسكرية",
            "target_audience": "military professionals",
            "tone": "formal technical",
            "word_count": "1500",
            "language": "arabic"
        }

    def test_outline_generation(self):
        """Test outline generation"""
        outline = generate_outline(
            self.agents,
            self.test_params["topic"],
            self.test_params["target_audience"],
            self.test_params["tone"],
            self.test_params["word_count"]
        )
        
        self.assertIsNotNone(outline)
        self.assertGreater(len(outline), 0)
        self.assertIn("Introduction", outline)
        self.assertIn("Conclusion", outline)

    def test_section_generation(self):
        """Test section generation"""
        # Generate a test section
        section = generate_article_section(
            self.agents,
            "Introduction",
            0,
            "Test outline content"
        )
        
        self.assertIsNotNone(section)
        self.assertGreater(len(section), 0)

    def test_terminology_integration(self):
        """Test terminology integration in content"""
        # Generate some test content
        content = "الإستراتيجية العسكرية هي علم وفن تخطيط"
        
        # Check terminology
        modified, suggestions = self.term_manager.check_content(
            content,
            self.test_params["language"]
        )
        
        self.assertIsNotNone(modified)
        self.assertIsInstance(suggestions, list)

    def test_output_structure(self):
        """Test output directory structure"""
        required_dirs = [
            "article_output",
            "article_output/sections",
            "article_output/glossary"
        ]
        
        for dir_path in required_dirs:
            self.assertTrue(os.path.exists(dir_path))

if __name__ == '__main__':
    unittest.main()