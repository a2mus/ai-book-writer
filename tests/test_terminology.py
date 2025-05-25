"""Test cases for military terminology handling"""
import unittest
from unittest.mock import patch, mock_open
import os
import csv
import tempfile
import shutil # For rmtree
from terminology_handler import TerminologyManager

# Define a sample header that matches the expected structure
SAMPLE_HEADER = ['Num', 'Old_Num', 'MOTS_AR', 'MOTS_fr', 'DESIGNATION', 'DESIGNATION_fr', 'chairdappartenance', 'Sous_Chapitre']
SAMPLE_DATA_ROWS = [
    ["1", "O1", "الاستخبارات", "Intelligence", "جمع وتحليل المعلومات", "Collection and analysis of information", "Operations", "CI"],
    ["2", "O2", "الإستراتيجية العسكرية", "Stratégie militaire", "تخطيط وإدارة الحملات", "Planning and execution of campaigns", "Strategy", "General"],
    ["3", "O3", "تكتيك", "Tactique", "فن استخدام القوات في المعركة", "Art of using forces in battle", "Operations", "Maneuver"],
    ["4", "O4", "دفاع", "Défense", "إجراءات الحماية", "Protective measures", "Strategy", "Security"]
]

class TestTerminologyHandler(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir) # Ensure temp dir is cleaned up

        # Create a default glossary for most tests to use
        self.default_glossary_filename = "default_glossary.csv"
        # Construct path relative to this test file
        current_dir = os.path.dirname(__file__)
        # Path to the main glossary file (assuming it's in the parent directory of 'tests')
        # For real sample file, adjust if needed, or use a dedicated test sample.
        # For now, we rely on _create_temp_csv for a controlled default glossary.
        self.glossary_path = self._create_temp_csv(
            self.default_glossary_filename,
            header=SAMPLE_HEADER,
            data_rows=SAMPLE_DATA_ROWS
        )
        self.term_manager = TerminologyManager(self.glossary_path)

    def _create_temp_csv(self, filename, data_rows, header=None, delimiter=';', base_dir=None):
        """Helper to create a temporary CSV file for testing."""
        if base_dir is None:
            base_dir = self.temp_dir # Default to the class's temp_dir
        filepath = os.path.join(base_dir, filename)
        
        # Ensure the directory exists (it should, if base_dir is self.temp_dir)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=delimiter)
            if header:
                writer.writerow(header)
            if data_rows: # Make sure data_rows is not None before iterating
                for row in data_rows:
                    writer.writerow(row)
        return filepath
    
    def test_load_terminology(self):
        """Test if terminology is loaded correctly from the default test glossary."""
        self.assertGreater(len(self.term_manager.terminology), 0, "Terminology should be loaded.")
        self.assertEqual(len(self.term_manager.terminology), len(SAMPLE_DATA_ROWS))
        self.assertGreater(len(self.term_manager.arabic_terms), 0, "Arabic terms should be loaded.")
        self.assertGreater(len(self.term_manager.french_terms), 0, "French terms should be loaded.")

    # --- Start of Error Handling Tests for load_terminology ---
    def test_load_non_existent_csv(self):
        """Test loading a non-existent CSV file."""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.csv")
        with self.assertRaises(FileNotFoundError):
            TerminologyManager(non_existent_path)

    def test_load_empty_csv(self):
        """Test loading a completely empty CSV file (no header, no data)."""
        empty_csv_path = self._create_temp_csv("empty.csv", data_rows=None, header=None)
        # Expecting RuntimeError due to "StopIteration" when trying to read header from an empty file
        with self.assertRaisesRegex(RuntimeError, f"Terminology file '{empty_csv_path}' is completely empty"):
            TerminologyManager(empty_csv_path)

    @patch('builtins.print')
    def test_load_csv_header_only(self, mock_print):
        """Test loading a CSV file with only a header row."""
        header_only_path = self._create_temp_csv("header_only.csv", data_rows=None, header=SAMPLE_HEADER)
        manager = TerminologyManager(header_only_path)
        self.assertEqual(len(manager.terminology), 0, "No terms should be loaded from a header-only CSV.")
        expected_warning = f"WARNING: [TerminologyManager] No terminology loaded. File '{header_only_path}' contains headers but no valid data rows, or all rows were skipped."
        self.assertTrue(any(expected_warning in call_args[0][0] for call_args in mock_print.call_args_list),
                        f"Expected warning '{expected_warning}' not found in print calls: {mock_print.call_args_list}")

    @patch('builtins.print')
    def test_load_malformed_csv_columns_skipped(self, mock_print):
        """Test loading a CSV with some rows having incorrect column counts."""
        malformed_data = [
            SAMPLE_DATA_ROWS[0], # Valid
            ["11", "O11", "صف معطوب"], # Malformed - too few columns for SAMPLE_HEADER
            SAMPLE_DATA_ROWS[1]  # Valid
        ]
        malformed_path = self._create_temp_csv("malformed_cols.csv", malformed_data, header=SAMPLE_HEADER)
        manager = TerminologyManager(malformed_path)
        # The manager should skip the malformed row and load the valid ones.
        self.assertEqual(len(manager.terminology), 2, "Should load 2 valid terms and skip 1 malformed.")
        
        # Check for the warning from _process_term_entry (row number is 1-indexed file line, header is line 1)
        # The malformed row is the 2nd data row, so it's line 3 in the CSV file.
        # _process_term_entry logs "Skipping row at approx line X due to missing essential fields"
        expected_warning_fragment = "Skipping row at approx line 3 due to missing essential fields"
        # Or, if the issue was caught by the len(row_data) >= len(header) check in load_terminology (manual path)
        alt_expected_warning_fragment = f"Skipping row 3 in '{malformed_path}' due to unexpected number of columns"

        found = any(expected_warning_fragment in call[0][0] or alt_expected_warning_fragment in call[0][0] for call in mock_print.call_args_list)
        self.assertTrue(found, f"Expected warning for skipping malformed row not logged. Calls: {mock_print.call_args_list}")

    @patch('builtins.print')
    def test_load_malformed_csv_delimiter(self, mock_print):
        """Test loading a CSV with a wrong delimiter (e.g., comma instead of semicolon)."""
        # Create a CSV file using commas for its internal structure
        wrong_delimiter_path = self._create_temp_csv(
            "wrong_delimiter.csv",
            # Header and data written as single fields because the writer uses ';' but content has ','
            header=["Num,Old_Num,MOTS_AR,MOTS_fr,DESIGNATION,DESIGNATION_fr,chairdappartenance,Sous_Chapitre"], 
            data_rows=[["1,O1,الاستخبارات,Intelligence,جمع وتحليل المعلومات,Collection and analysis of information,Operations,CI"]],
            delimiter=';' # The file is written correctly with ; but its *content* is comma-separated strings
        )
        # TerminologyManager expects ';' to separate values.
        # It will read the header "Num,Old_Num,..." as a single field. 'Num' won't be found.
        # Manual header parsing will split by ';'. If the header has no ';', it's one field.
        # Rows will also be read as single fields. _process_term_entry will skip them.
        manager = TerminologyManager(wrong_delimiter_path)
        self.assertEqual(len(manager.terminology), 0, "No terms should be loaded due to delimiter mismatch.")
        
        # Expect a warning that the header is malformed or the file is empty.
        expected_warning_fragment = f"File '{wrong_delimiter_path}' might be empty or its header row is malformed"
        self.assertTrue(any(expected_warning_fragment in call[0][0] for call in mock_print.call_args_list),
                        f"Expected warning for malformed header not found. Calls: {mock_print.call_args_list}")
    # --- End of Error Handling Tests ---
    
    def test_suggest_terms(self):
        """Test term suggestions for a topic using the default test glossary."""
        # Test Arabic suggestions
        suggestions_ar = self.term_manager.suggest_terms_for_topic("الاستخبارات", "arabic") # Exact match from sample
        self.assertTrue(any(s['arabic_term'] == "الاستخبارات" for s in suggestions_ar))
        
        # Test French suggestions
        suggestions_fr = self.term_manager.suggest_terms_for_topic("Intelligence", "french") # Exact match from sample
        self.assertTrue(any(s['french_term'] == "Intelligence" for s in suggestions_fr))
    
    def test_check_content(self):
        """Test content checking for terminology using the default test glossary."""
        # Test Arabic content
        content_ar = "الاستخبارات العسكرية هي علم وفن" # Contains "الاستخبارات"
        modified_ar, suggestions_ar = self.term_manager.check_content(content_ar, "arabic")
        self.assertTrue(any(s['term'] == "الاستخبارات" for s in suggestions_ar))
        
        # Test French content
        content_fr = "La Intelligence militaire est une science" # Contains "Intelligence"
        modified_fr, suggestions_fr = self.term_manager.check_content(content_fr, "french")
        self.assertTrue(any(s['term'] == "Intelligence" for s in suggestions_fr))
    
    def test_get_related_terms(self):
        """Test finding related terms using the default test glossary."""
        # "الاستخبارات" and "تكتيك" are both in "Operations" category in SAMPLE_DATA_ROWS
        related_ar = self.term_manager.get_related_terms("الاستخبارات", "arabic")
        self.assertTrue(any(t['arabic_term'] == "تكتيك" for t in related_ar),
                        f"Related terms for الاستخبارات: {[t['arabic_term'] for t in related_ar if 'arabic_term' in t]}")
        
        related_fr = self.term_manager.get_related_terms("Intelligence", "french")
        self.assertTrue(any(t['french_term'] == "Tactique" for t in related_fr),
                        f"Related terms for Intelligence: {[t['french_term'] for t in related_fr if 'french_term' in t]}")

    # --- Start of get_term_definition and get_category_terms Tests ---
    def test_get_term_definition(self):
        """Test getting term definitions."""
        definition_ar = self.term_manager.get_term_definition("الاستخبارات", "arabic")
        self.assertEqual(definition_ar, "جمع وتحليل المعلومات")
        
        definition_fr = self.term_manager.get_term_definition("Intelligence", "french")
        self.assertEqual(definition_fr, "Collection and analysis of information")
        
        non_existent_def = self.term_manager.get_term_definition("مصطلح_غير_موجود", "arabic")
        self.assertIsNone(non_existent_def)

    def test_get_category_terms(self):
        """Test getting terms by category."""
        # "Operations" category has "الاستخبارات" and "تكتيك"
        category_terms_ops = self.term_manager.get_category_terms("Operations")
        self.assertEqual(len(category_terms_ops), 2)
        self.assertTrue(all(term['category'] == "Operations" for term in category_terms_ops))
        
        # "Strategy" category has "الإستراتيجية العسكرية" and "دفاع"
        category_terms_strat = self.term_manager.get_category_terms("Strategy")
        self.assertEqual(len(category_terms_strat), 2)
        self.assertTrue(all(term['category'] == "Strategy" for term in category_terms_strat))
        
        non_existent_category_terms = self.term_manager.get_category_terms("فئة_غير_موجودة")
        self.assertEqual(len(non_existent_category_terms), 0)
    # --- End of get_term_definition and get_category_terms Tests ---

    # --- Start of check_and_replace_content Tests ---
    def test_check_and_replace_content(self):
        """Test check_and_replace_content functionality."""
        # 1. Without replacement_map (should behave like check_content finding existing terms)
        content_ar_orig = "هذا الاستخبارات جيد." # "الاستخبارات" is in SAMPLE_DATA_ROWS
        modified_content, suggestions = self.term_manager.check_and_replace_content(content_ar_orig, "arabic")
        self.assertEqual(modified_content, content_ar_orig, "Content should not change if no map.")
        self.assertTrue(any(s['term'] == "الاستخبارات" for s in suggestions), "Should find existing terms.")
        self.assertTrue(all('status' in s and s['status'] == 'identified_in_text' for s in suggestions), "Suggestions should be marked as identified.")

        # 2. With replacement_map (Arabic)
        replacement_map_ar = {"مصطلح خاطئ": "الاستخبارات"} # Replace with a known term
        content_ar = "هذا مصطلح خاطئ يجب استبداله. وهذا الاستخبارات جيد."
        expected_ar = "هذا الاستخبارات يجب استبداله. وهذا الاستخبارات جيد."
        
        modified_content_ar, corrections_ar = self.term_manager.check_and_replace_content(content_ar, "arabic", replacement_map_ar)
        self.assertEqual(modified_content_ar, expected_ar, "Arabic content not replaced as expected.")
        self.assertEqual(len(corrections_ar), 1, "Should be one correction made.")
        self.assertEqual(corrections_ar[0]['found'], "مصطلح خاطئ")
        self.assertEqual(corrections_ar[0]['replaced_with'], "الاستخبارات")
        self.assertEqual(corrections_ar[0]['count'], 1, "Incorrect count for Arabic replacement.")

        # 3. With replacement_map (French)
        replacement_map_fr = {"le faux terme": "Intelligence"} # Replace with a known term
        content_fr = "Ceci est le faux terme. Et cela Intelligence est bon."
        expected_fr = "Ceci est Intelligence. Et cela Intelligence est bon."
        
        modified_content_fr, corrections_fr = self.term_manager.check_and_replace_content(content_fr, "french", replacement_map_fr)
        self.assertEqual(modified_content_fr, expected_fr, "French content not replaced as expected.")
        self.assertEqual(len(corrections_fr), 1, "Should be one correction made for French.")
        self.assertEqual(corrections_fr[0]['found'], "le faux terme")
        self.assertEqual(corrections_fr[0]['replaced_with'], "Intelligence")

        # 4. Term in map not found in content (should return suggestions for existing terms if any)
        content_fr_no_match_needed = "Un texte sans le terme à remplacer, mais avec Intelligence."
        # replacement_map_fr has "le faux terme", which is not in content_fr_no_match_needed
        modified_content_no_match, suggestions_no_match = self.term_manager.check_and_replace_content(
            content_fr_no_match_needed, "french", replacement_map_fr 
        )
        self.assertEqual(modified_content_no_match, content_fr_no_match_needed, "Content should be unchanged if map term not found.")
        # It should provide suggestions for "Intelligence" which is in the content
        self.assertTrue(any(s['term'] == "Intelligence" and s['status'] == 'identified_in_text' for s in suggestions_no_match),
                        "Should still find suggestions for other terms if replacement term not found.")

        # 5. Interaction with glossary identification:
        #    Ensure that after replacements, other glossary terms are still identifiable.
        #    The current check_and_replace_content returns 'corrections_made' if replacements happened.
        #    To check for other identified terms, we need to call check_content on the modified output.
        replacement_map_ar_interaction = {"كلمة سيئة": "دفاع"} # "دفاع" is a valid term from SAMPLE_DATA_ROWS
        content_ar_interaction = "هذه كلمة سيئة يجب استبدالها. وهذا تكتيك جيد." # "تكتيك" is also a valid term
        
        modified_content_interaction, corrections_interaction = self.term_manager.check_and_replace_content(
            content_ar_interaction, "arabic", replacement_map_ar_interaction
        )
        self.assertIn("دفاع", modified_content_interaction, "Replacement did not occur.")
        self.assertIn("تكتيك", modified_content_interaction, "Original term 'تكتيك' was lost.")
        self.assertTrue(any(c['found'] == "كلمة سيئة" and c['replaced_with'] == "دفاع" for c in corrections_interaction),
                        "Corrections list is incorrect.")
        
        # Now, check the modified content for all glossary terms
        _, suggestions_after_replace = self.term_manager.check_content(modified_content_interaction, "arabic")
        self.assertTrue(any(s['term'] == "دفاع" for s in suggestions_after_replace), 
                        "Replaced term 'دفاع' not identified in subsequent check.")
        self.assertTrue(any(s['term'] == "تكتيك" for s in suggestions_after_replace), 
                        "Other term 'تكتيك' not identified in subsequent check.")
    # --- End of check_and_replace_content Tests ---

    # --- Start of Edge Case Term Matching Tests ---
    def test_term_matching_edge_cases(self):
        """Test term matching with punctuation and at string boundaries."""
        # 1. Term with punctuation (Arabic) - "الاستخبارات" is a sample term
        content_ar_punct = "هذا هو الاستخبارات."
        _, suggestions_ar = self.term_manager.check_content(content_ar_punct, "arabic")
        self.assertTrue(any(s['term'] == "الاستخبارات" for s in suggestions_ar), 
                        f"Arabic term with period not found. Suggestions: {suggestions_ar}")

        # 2. Term with punctuation (French) - "Intelligence" is a sample term
        content_fr_punct = "Ceci est Intelligence!"
        _, suggestions_fr = self.term_manager.check_content(content_fr_punct, "french")
        self.assertTrue(any(s['term'] == "Intelligence" for s in suggestions_fr),
                        f"French term with exclamation not found. Suggestions: {suggestions_fr}")

        # 3. Term at beginning of string (Arabic)
        content_ar_begin = "الاستخبارات في البداية."
        _, suggestions_ar_begin = self.term_manager.check_content(content_ar_begin, "arabic")
        self.assertTrue(any(s['term'] == "الاستخبارات" for s in suggestions_ar_begin),
                        "Arabic term at beginning not found.")

        # 4. Term at end of string (French)
        content_fr_end = "A la fin, c'est Intelligence"
        _, suggestions_fr_end = self.term_manager.check_content(content_fr_end, "french")
        self.assertTrue(any(s['term'] == "Intelligence" for s in suggestions_fr_end),
                        "French term at end not found.")

        # 5. Term that is a substring of another word (should not match if using \b word boundaries)
        # "الاستخبارات" is the term. "استخباراتي" contains it but is not the whole word.
        content_ar_substring_false_positive = "هذا استخباراتي وليس الاستخبارات المقصودة." 
        _, suggestions_ar_substring = self.term_manager.check_content(content_ar_substring_false_positive, "arabic")
        
        found_exact_term = False
        found_substring_context_for_exact_term = False

        for s in suggestions_ar_substring:
            if s['term'] == "الاستخبارات": # Exact term from glossary
                found_exact_term = True
                # Check context to ensure it's not matching "استخباراتي"
                if "استخباراتي" in s['context'] and "الاستخبارات المقصودة" not in s['context']:
                    found_substring_context_for_exact_term = True 
                # print(f"DEBUG: Found term '{s['term']}' in context '{s['context']}'")

        self.assertTrue(found_exact_term, "The exact term 'الاستخبارات' should be found in '...وليس الاستخبارات المقصودة'.")
        self.assertFalse(found_substring_context_for_exact_term, 
                         "The exact term 'الاستخبارات' should not be matched within 'استخباراتي'. Its context should be from '...الاستخبارات المقصودة'.")

        # 6. Content with term that could be a prefix of another glossary term (ensure whole word matching)
        # Add "استخبارات" (shorter) to a temporary glossary if "الاستخبارات" (longer) is already there.
        # This is to ensure that searching for "استخبارات" doesn't wrongly flag "الاستخبارات".
        # Our current SAMPLE_DATA_ROWS only has "الاستخبارات".
        # Let's assume "دفاع" (Defence) is a term. Test against "دفاعي" (defensive).
        content_ar_prefix = "هذا عمل دفاعي وليس دفاع مباشر." # "دفاع" is a term
        _, suggestions_ar_prefix = self.term_manager.check_content(content_ar_prefix, "arabic")
        
        found_exact_term_prefix_case = False
        found_substring_context_for_exact_term_prefix_case = False
        for s in suggestions_ar_prefix:
            if s['term'] == "دفاع":
                found_exact_term_prefix_case = True
                if "دفاعي" in s['context'] and "دفاع مباشر" not in s['context']:
                     found_substring_context_for_exact_term_prefix_case = True
        
        self.assertTrue(found_exact_term_prefix_case, "The exact term 'دفاع' should be found in '...وليس دفاع مباشر'.")
        self.assertFalse(found_substring_context_for_exact_term_prefix_case,
                         "The exact term 'دفاع' should not be matched within 'دفاعي'.")
    # --- End of Edge Case Term Matching Tests ---

if __name__ == '__main__':
    # This allows running the tests from the command line
    # Ensure terminology_handler.py can be found if it's in the parent directory:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    # from terminology_handler import TerminologyManager # Already imported globally

    unittest.main()