import csv

class TerminologyAgent:
    def __init__(self, glossary_file):
        self.glossary = self.load_glossary(glossary_file)

    def load_glossary(self, glossary_file):
        glossary = {}
        with open(glossary_file, mode='r') as infile:
            reader = csv.reader(infile)
            for rows in reader:
                glossary[rows[0]] = rows[1]
        return glossary

    def check_terminology(self, chapter):
        # ...existing code...
        for term in self.glossary:
            if term not in chapter:
                return False
        return True
