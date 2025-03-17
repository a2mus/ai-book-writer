"""Handle military terminology processing and validation"""
import csv
import re
from typing import Dict, List, Tuple, Optional

class TerminologyManager:
    def __init__(self, csv_path: str):
        """Initialize with path to military terminology CSV file"""
        self.csv_path = csv_path
        self.terminology = {}
        self.arabic_terms = {}
        self.french_terms = {}
        self.categories = {}
        self.load_terminology()
    
    def load_terminology(self) -> None:
        """Load and process the military terminology CSV file"""
        try:
            with open(self.csv_path, mode='r', encoding='utf-8') as file:
                # Use the DictReader with explicit delimiter for the semicolon-separated file
                reader = csv.DictReader(file, delimiter=';')
                
                # Check if the expected columns exist in the CSV file
                if not reader.fieldnames or 'Num' not in reader.fieldnames:
                    # The header row might not be recognized correctly - try to fix
                    file.seek(0)  # Go back to the beginning of the file
                    header = next(file).strip().split(';')
                    
                    # Create a custom reader with the manually extracted headers
                    file.seek(0)
                    next(file)  # Skip the header line
                    
                    # Use a list reader and convert to dict manually
                    list_reader = csv.reader(file, delimiter=';')
                    for row_data in list_reader:
                        if len(row_data) >= 7:  # Make sure the row has enough columns
                            row = {
                                'Num': row_data[0],
                                'Old_Num': row_data[1],
                                'MOTS_AR': row_data[2],
                                'MOTS_fr': row_data[3],
                                'DESIGNATION': row_data[4],
                                'DESIGNATION_fr': row_data[5],
                                'chairdappartenance': row_data[6],
                                'Sous_Chapitre': row_data[7] if len(row_data) > 7 else ''
                            }
                            self._process_term_entry(row)
                else:
                    # The header was recognized correctly, process normally
                    for row in reader:
                        self._process_term_entry(row)
                        
            print(f"Successfully loaded {len(self.terminology)} military terms")
        except Exception as e:
            print(f"Error loading terminology file: {e}")
            raise
    
    def _process_term_entry(self, row):
        """Process a single row of terminology data"""
        term_entry = {
            'id': row['Num'],
            'arabic_term': row['MOTS_AR'],
            'french_term': row['MOTS_fr'],
            'arabic_def': row['DESIGNATION'],
            'french_def': row['DESIGNATION_fr'],
            'category': row['chairdappartenance'],
            'subcategory': row['Sous_Chapitre']
        }
        
        # Index by both Arabic and French terms
        self.arabic_terms[row['MOTS_AR']] = term_entry
        self.french_terms[row['MOTS_fr']] = term_entry
        
        # Group by category
        category = row['chairdappartenance']
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(term_entry)
        
        # Store in main terminology dict
        self.terminology[row['Num']] = term_entry

    def check_content(self, content: str, language: str = 'arabic') -> Tuple[str, List[Dict]]:
        """Check content against terminology database and return suggestions"""
        terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
        suggestions = []
        modified_content = content
        
        for term, entry in terms_dict.items():
            # Create pattern that handles Arabic text direction and variations
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.finditer(pattern, content, re.UNICODE | re.MULTILINE)
            
            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(content), match.end() + 50)
                context = content[context_start:context_end]
                
                suggestions.append({
                    'term': term,
                    'definition': entry['arabic_def' if language == 'arabic' else 'french_def'],
                    'category': entry['category'],
                    'context': context
                })
        
        return modified_content, suggestions

    def suggest_terms_for_topic(self, topic: str, language: str = 'arabic') -> List[Dict]:
        """Suggest relevant military terms for a given topic"""
        suggestions = []
        terms = self.arabic_terms if language == 'arabic' else self.french_terms
        
        # Convert topic to lowercase for matching
        topic_lower = topic.lower()
        
        for term, entry in terms.items():
            # Check if topic appears in term, definition, or category
            term_matches = topic_lower in term.lower()
            def_field = 'arabic_def' if language == 'arabic' else 'french_def'
            def_matches = topic_lower in entry[def_field].lower()
            category_matches = topic_lower in entry['category'].lower()
            
            if term_matches or def_matches or category_matches:
                suggestions.append(entry)
        
        return suggestions

    def get_category_terms(self, category: str) -> List[Dict]:
        """Get all terms in a specific category"""
        return self.categories.get(category, [])

    def get_term_definition(self, term: str, language: str = 'arabic') -> Optional[str]:
        """Get the definition of a specific term"""
        terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
        if term in terms_dict:
            return terms_dict[term]['arabic_def' if language == 'arabic' else 'french_def']
        return None

    def get_related_terms(self, term: str, language: str = 'arabic') -> List[Dict]:
        """Get terms related to a given term (same category)"""
        terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
        if term not in terms_dict:
            return []
            
        category = terms_dict[term]['category']
        return [t for t in self.categories[category] if t['arabic_term' if language == 'arabic' else 'french_term'] != term]