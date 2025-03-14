from googletrans import Translator

class TranslationAgent:
    def __init__(self, resources, target_language):
        self.resources = resources
        self.target_language = target_language
        self.translator = Translator()

    def translate(self):
        # ...existing code...
        translated_resources = []
        for resource in self.resources:
            translated = self.translator.translate(resource, dest=self.target_language)
            translated_resources.append(translated.text)
        return translated_resources
