"""Utility to help convert existing book content to military articles"""
import os
import re
from typing import List, Dict
from terminology_handler import TerminologyManager

class ContentConverter:
    def __init__(self, glossary_path: str):
        self.term_manager = TerminologyManager(glossary_path)
        
    def convert_chapter_to_article(self, chapter_path: str, language: str = 'arabic') -> Dict:
        """Convert a book chapter to an article format with terminology checks"""
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract main sections
        sections = self._extract_sections(content)
        
        # Check terminology in each section
        processed_sections = {}
        for section_name, section_content in sections.items():
            modified_content, suggestions = self.term_manager.check_content(
                section_content,
                language
            )
            processed_sections[section_name] = {
                'content': modified_content,
                'terminology_suggestions': suggestions
            }
            
        return processed_sections
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract main sections from chapter content"""
        sections = {}
        
        # Try to find common section markers
        section_pattern = r'#{1,3}\s*(.*?)\n(.*?)(?=#{1,3}|\Z)'
        matches = re.finditer(section_pattern, content, re.DOTALL)
        
        for match in matches:
            section_title = match.group(1).strip()
            section_content = match.group(2).strip()
            sections[section_title] = section_content
            
        # If no sections found, treat whole content as one section
        if not sections:
            sections['Main Content'] = content
            
        return sections
    
    def generate_article_structure(self, sections: Dict) -> str:
        """Generate properly formatted article from sections"""
        article = []
        
        # Start with Introduction if it exists
        if 'Introduction' in sections:
            article.append(f"# Introduction\n\n{sections['Introduction']['content']}\n")
            
        # Add other sections
        for name, content in sections.items():
            if name not in ['Introduction', 'Conclusion']:
                article.append(f"# {name}\n\n{content['content']}\n")
                
        # End with Conclusion if it exists
        if 'Conclusion' in sections:
            article.append(f"# Conclusion\n\n{sections['Conclusion']['content']}\n")
            
        return '\n'.join(article)
    
    def create_terminology_glossary(self, sections: Dict) -> str:
        """Create a glossary of military terms used in the article"""
        used_terms = set()
        
        # Collect all used terms
        for section in sections.values():
            for suggestion in section['terminology_suggestions']:
                used_terms.add((
                    suggestion['term'],
                    suggestion['definition'],
                    suggestion['category']
                ))
        
        # Generate glossary content
        glossary = ["# Military Terminology Glossary\n"]
        
        # Group terms by category
        terms_by_category = {}
        for term, definition, category in used_terms:
            if category not in terms_by_category:
                terms_by_category[category] = []
            terms_by_category[category].append((term, definition))
        
        # Format glossary with categories
        for category, terms in terms_by_category.items():
            glossary.append(f"\n## {category}\n")
            for term, definition in sorted(terms):
                glossary.append(f"\n### {term}\n{definition}\n")
        
        return '\n'.join(glossary)

def main():
    """Main function to convert book chapters to articles"""
    print("Book to Article Converter\n")
    
    # Get input parameters
    book_dir = input("Enter path to book chapters directory: ")
    language = input("Enter content language (arabic/french) [default: arabic]: ").lower() or 'arabic'
    glossary_path = input("Enter path to glossary file [default: glossaire_2022_sample.csv]: ") or 'glossaire_2022_sample.csv'
    
    converter = ContentConverter(glossary_path)
    
    # Process each chapter file
    for filename in os.listdir(book_dir):
        if filename.endswith('.txt') or filename.endswith('.md'):
            print(f"\nProcessing {filename}...")
            
            # Convert chapter to article
            chapter_path = os.path.join(book_dir, filename)
            sections = converter.convert_chapter_to_article(chapter_path, language)
            
            # Generate article and glossary
            article_content = converter.generate_article_structure(sections)
            glossary_content = converter.create_terminology_glossary(sections)
            
            # Save outputs
            output_dir = f"article_output/converted_{os.path.splitext(filename)[0]}"
            os.makedirs(output_dir, exist_ok=True)
            
            with open(f"{output_dir}/article.md", 'w', encoding='utf-8') as f:
                f.write(article_content)
            
            with open(f"{output_dir}/glossary.md", 'w', encoding='utf-8') as f:
                f.write(glossary_content)
            
            print(f"Created article and glossary in {output_dir}")
    
    print("\nConversion complete!")

if __name__ == '__main__':
    main()