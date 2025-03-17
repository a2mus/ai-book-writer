import csv
import re

class TerminologyAgent:
    def __init__(self, glossary_file):
        self.glossary = self.load_glossary(glossary_file)
        self.arabic_terms = {}
        self.french_terms = {}
        self.categorized_terms = {}
        self.process_glossary()

    def load_glossary(self, glossary_file):
        glossary = []
        with open(glossary_file, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter=';')
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 7:
                    glossary.append({
                        'id': row[0],
                        'arabic_term': row[2],
                        'french_term': row[3],
                        'arabic_def': row[4],
                        'french_def': row[5],
                        'category': row[6]
                    })
        return glossary

    def process_glossary(self):
        """Process glossary into usable dictionaries"""
        for entry in self.glossary:
            # Index by Arabic term
            self.arabic_terms[entry['arabic_term']] = entry
            
            # Index by French term
            self.french_terms[entry['french_term']] = entry
            
            # Group by category
            category = entry['category']
            if category not in self.categorized_terms:
                self.categorized_terms[category] = []
            self.categorized_terms[category].append(entry)

    def check_terminology_usage(self, chapter, language='arabic'):
        """Check if terminology is used correctly in the chapter"""
        terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
        results = {
            'used_terms': [],
            'missing_terms': [],
            'suggestions': []
        }
        
        # Check which terms are used
        for term, entry in terms_dict.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, chapter, re.UNICODE):
                results['used_terms'].append(entry)
            
        # Suggest terms based on chapter content
        # This is a simplified approach - could be enhanced with more advanced NLP
        for category, entries in self.categorized_terms.items():
            category_used = False
            for entry in entries:
                if entry in results['used_terms']:
                    category_used = True
                    break
            
            if category_used:
                # Suggest other terms from the same category
                for entry in entries:
                    if entry not in results['used_terms']:
                        results['missing_terms'].append(entry)
        
        return results

    def generate_definitions(self, terms, language='arabic'):
        """Generate definitions for a list of terms"""
        definitions = {}
        terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
        
        for term in terms:
            if term in terms_dict:
                entry = terms_dict[term]
                definition = entry['arabic_def'] if language == 'arabic' else entry['french_def']
                definitions[term] = definition
                
        return definitions

    def suggest_terms_for_topic(self, topic, language='arabic'):
        """Suggest terms related to a specific topic"""
        # This is a simple implementation - could be enhanced with embeddings/NLP
        suggestions = []
        terms = self.arabic_terms if language == 'arabic' else self.french_terms
        
        for term, entry in terms.items():
            if topic.lower() in term.lower() or topic.lower() in entry['category'].lower():
                suggestions.append(entry)
                
        return suggestions
