class WritingAgent:
    def __init__(self, plan):
        self.plan = plan

    def write(self):
        # ...existing code...
        article = ""
        article += self.plan['introduction'] + "\n\n"
        for section in self.plan['sections']:
            article += section['title'] + "\n"
            article += section['content'] + "\n\n"
        article += self.plan['conclusion']
        return article
