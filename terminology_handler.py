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
        print(f"INFO: [TerminologyManager] Attempting to load terminology from: {self.csv_path}")
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
                    # i+2 because list_reader starts after header, and lines are 1-indexed, i is 0-indexed.
                    for i, row_data in enumerate(list_reader): 
                        if len(row_data) >= len(header): # Check against actual header length
                            row = dict(zip(header, row_data)) # Create a dict from header and row_data
                            self._process_term_entry(row, row_number=i+2) 
                        else:
                            print(f"WARNING: [TerminologyManager] Skipping row {i+2} in '{self.csv_path}' due to unexpected number of columns. Expected {len(header)}, got {len(row_data)}. Data: {row_data}")
                else:
                    # The header was recognized correctly, process normally
                    # i+2 because reader starts after header, and lines are 1-indexed, i is 0-indexed.
                    for i, row in enumerate(reader):
                        self._process_term_entry(row, row_number=i+2)
            
            # After attempting to load, check if any terms were actually loaded.
            if not self.terminology:
                # This condition implies the file might have been empty, had only headers, 
                # or all rows were skippable due to missing essential fields or column count issues.
                # Differentiate based on whether reader.fieldnames was populated.
                if not reader.fieldnames: # This implies the file was empty or header couldn't be read
                     print(f"WARNING: [TerminologyManager] No terminology loaded. File '{self.csv_path}' might be empty or its header row is malformed (expected 'Num', ... with ';' delimiter).")
                else: # Headers were read, but no valid data rows followed or all were skipped.
                     print(f"WARNING: [TerminologyManager] No terminology loaded. File '{self.csv_path}' contains headers but no valid data rows, or all rows were skipped.")
            else:
                print(f"INFO: [TerminologyManager] Successfully loaded {len(self.terminology)} military terms from '{self.csv_path}'.")

        except FileNotFoundError:
            print(f"ERROR: [TerminologyManager] Terminology file not found at path: {self.csv_path}")
            raise
        except PermissionError:
            print(f"ERROR: [TerminologyManager] Permission denied when trying to read terminology file: {self.csv_path}")
            raise
        except csv.Error as e:
            # csv.Error is the base class for exceptions raised by the csv module.
            # This can include issues with the delimiter, quoting, or other CSV format violations.
            # The error 'iterator should return strings, not bytes' can occur if file not opened in text mode ('r' vs 'rb').
            # Our 'utf-8' encoding and mode='r' should prevent that, but good to be aware.
            print(f"ERROR: [TerminologyManager] CSV parsing error in file '{self.csv_path}'. Details: {e}. Please ensure the file is a valid semicolon-delimited CSV with UTF-8 encoding.")
            raise
        except StopIteration: # Raised by next() if the file is completely empty (no header, no data)
            print(f"ERROR: [TerminologyManager] Terminology file '{self.csv_path}' is completely empty (no header row found).")
            # Following the hard-fail policy.
            raise RuntimeError(f"Terminology file '{self.csv_path}' is completely empty.")
        except Exception as e:
            # Catch-all for any other unexpected exceptions
            print(f"ERROR: [TerminologyManager] An unexpected error occurred while loading terminology from '{self.csv_path}': {e}")
            raise
    
    def _process_term_entry(self, row, row_number=None):
        """Process a single row of terminology data. Added row_number for logging."""
        # Use .get() to avoid KeyError and provide defaults or skip if essential data is missing
        num = row.get('Num')
        mots_ar = row.get('MOTS_AR')
        mots_fr = row.get('MOTS_fr')

        # Basic validation: Num, MOTS_AR, and MOTS_fr are essential
        if not all([num, mots_ar, mots_fr]):
            error_msg = f"Skipping row"
            if row_number:
                error_msg += f" at approx line {row_number}"
            error_msg += f" due to missing essential fields (Num, MOTS_AR, MOTS_fr). Row data: {row}"
            print(f"WARNING: [TerminologyManager] {error_msg}")
            return # Skip this entry

        term_entry = {
            'id': num,
            'arabic_term': mots_ar,
            'french_term': mots_fr,
            'arabic_def': row.get('DESIGNATION', ''), 
            'french_def': row.get('DESIGNATION_fr', ''), 
            'category': row.get('chairdappartenance', 'Uncategorized'),
            'subcategory': row.get('Sous_Chapitre', '')
        }
        
        # Index by both Arabic and French terms
        if mots_ar: # Ensure key is not empty
            self.arabic_terms[mots_ar] = term_entry
        if mots_fr: # Ensure key is not empty
            self.french_terms[mots_fr] = term_entry
        
        # Group by category
        category = term_entry['category']
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(term_entry)
        
        # Store in main terminology dict
        if num: # Ensure key is not empty
            self.terminology[num] = term_entry

    def check_content(self, content: str, language: str = 'arabic') -> Tuple[str, List[Dict]]:
        """Check content against terminology database and return suggestions"""
        print(f"INFO: [TerminologyManager] Checking content for language: {language}. Content length: {len(content)}")
        terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
        suggestions = []
        modified_content = content

        for term, entry in terms_dict.items():
            # Create pattern that handles Arabic text direction and variations
            # print(f"DEBUG: [TerminologyManager] Checking for term: {term}") # Can be very verbose
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.finditer(pattern, content, re.UNICODE | re.MULTILINE)

            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(content), match.end() + 50)
                context = content[context_start:context_end]
                print(f"DEBUG: [TerminologyManager] Found term '{term}' in content.")

                suggestions.append({
                    'term': term,
                    'definition': entry['arabic_def' if language == 'arabic' else 'french_def'],
                    'category': entry['category'],
                    'context': context
                })

        print(f"INFO: [TerminologyManager] Found {len(suggestions)} potential terminology suggestions.")
        return modified_content, suggestions

    def check_and_replace_content(self, content: str, language: str = 'arabic', replacement_map: Optional[Dict[str, str]] = None) -> Tuple[str, List[Dict]]:
        """
        Check content against terminology and perform replacements.
        replacement_map: A dictionary where keys are terms to find (potentially incorrect)
                         and values are the correct glossary terms to replace them with.
        Returns modified content and a list of corrections made (or glossary suggestions if no replacements).
        """
        print(f"INFO: [TerminologyManager] Checking and replacing content. Language: {language}. Replacement map provided: {bool(replacement_map)}")
        modified_content = content
        corrections_made = []

        # 1. Perform replacements if a map is provided
        if replacement_map:
            for term_to_find, correct_term in replacement_map.items():
                pattern = r'\b' + re.escape(term_to_find) + r'\b'
                occurrences = len(re.findall(pattern, modified_content, re.UNICODE | re.MULTILINE))
                if occurrences > 0:
                    modified_content = re.sub(pattern, correct_term, modified_content, flags=re.UNICODE | re.MULTILINE)
                    print(f"DEBUG: [TerminologyManager] Replaced '{term_to_find}' with '{correct_term}' ({occurrences} occurrences).")
                    corrections_made.append({
                        "found": term_to_find,
                        "replaced_with": correct_term,
                        "count": occurrences
                    })

        # 2. Identify glossary terms present in the (potentially modified) content
        terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
        suggestions_found = []
        for term, entry in terms_dict.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.finditer(pattern, modified_content, re.UNICODE | re.MULTILINE)
            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(modified_content), match.end() + 50)
                context = modified_content[context_start:context_end]
                # print(f"DEBUG: [TerminologyManager] Identified glossary term '{term}' in content post-replacement.") # Can be verbose
                suggestions_found.append({
                    'term': term,
                    'definition': entry['arabic_def' if language == 'arabic' else 'french_def'],
                    'category': entry['category'],
                    'context': context,
                    'status': 'identified_in_text'
                })

        final_suggestions = corrections_made if corrections_made else suggestions_found
        if corrections_made:
            print(f"INFO: [TerminologyManager] Made {len(corrections_made)} types of replacements.")
        print(f"INFO: [TerminologyManager] Returning {len(final_suggestions)} suggestions/corrections.")

        return modified_content, final_suggestions

    def suggest_terms_for_topic(self, topic: str, language: str = 'arabic') -> List[Dict]:
        print(f"INFO: [TerminologyManager] Suggesting terms for topic: '{topic}', language: {language}")
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
                # print(f"DEBUG: [TerminologyManager] Suggested term '{entry['arabic_term' if language == 'arabic' else 'french_term']}' for topic '{topic}'.")
        
        print(f"INFO: [TerminologyManager] Found {len(suggestions)} relevant terms for topic '{topic}'.")
        return suggestions

    def get_category_terms(self, category: str) -> List[Dict]:
        """Get all terms in a specific category"""
        print(f"INFO: [TerminologyManager] Getting terms for category: {category}")
        return self.categories.get(category, [])

    def get_term_definition(self, term: str, language: str = 'arabic') -> Optional[str]:
        """Get the definition of a specific term"""
        print(f"INFO: [TerminologyManager] Getting definition for term: '{term}', language: {language}")
        terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
        if term in terms_dict:
            return terms_dict[term]['arabic_def' if language == 'arabic' else 'french_def']
        return None

    def get_related_terms(self, term: str, language: str = 'arabic') -> List[Dict]:
        print(f"INFO: [TerminologyManager] Getting related terms for: '{term}', language: {language}")
        terms_dict = self.arabic_terms if language == 'arabic' else self.french_terms
        if term not in terms_dict:
            return []
            
        category = terms_dict[term]['category']
        return [t for t in self.categories[category] if t['arabic_term' if language == 'arabic' else 'french_term'] != term]
