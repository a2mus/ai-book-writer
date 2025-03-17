"""Test cases for military terminology handling"""
import unittest
import os
from terminology_handler import TerminologyManager

class TestTerminologyHandler(unittest.TestCase):
    def setUp(self):
        self.glossary_path = "../glossaire_2022_sample.csv"
        self.term_manager = TerminologyManager(self.glossary_path)
    
    def test_load_terminology(self):
        """Test if terminology is loaded correctly"""
        self.assertGreater(len(self.term_manager.terminology), 0)
        self.assertGreater(len(self.term_manager.arabic_terms), 0)
        self.assertGreater(len(self.term_manager.french_terms), 0)
    
    def test_suggest_terms(self):
        """Test term suggestions for a topic"""
        # Test Arabic suggestions
        suggestions_ar = self.term_manager.suggest_terms_for_topic("استراتيجية", "arabic")
        self.assertGreater(len(suggestions_ar), 0)
        
        # Test French suggestions
        suggestions_fr = self.term_manager.suggest_terms_for_topic("stratégie", "french")
        self.assertGreater(len(suggestions_fr), 0)
    
    def test_check_content(self):
        """Test content checking for terminology"""
        # Test Arabic content
        content_ar = "الإستراتيجية العسكرية هي علم وفن"
        modified_ar, suggestions_ar = self.term_manager.check_content(content_ar, "arabic")
        self.assertIsInstance(suggestions_ar, list)
        
        # Test French content
        content_fr = "La stratégie militaire est une science"
        modified_fr, suggestions_fr = self.term_manager.check_content(content_fr, "french")
        self.assertIsInstance(suggestions_fr, list)
    
    def test_get_related_terms(self):
        """Test finding related terms"""
        # Test Arabic related terms
        related_ar = self.term_manager.get_related_terms("الإستراتيجية العسكرية", "arabic")
        self.assertIsInstance(related_ar, list)
        
        # Test French related terms
        related_fr = self.term_manager.get_related_terms("Stratégie militaire", "french")
        self.assertIsInstance(related_fr, list)

if __name__ == '__main__':
    unittest.main()