class VerificationAgent:
    def __init__(self, topic, plan, resources):
        self.topic = topic
        self.plan = plan
        self.resources = resources

    def verify(self):
        # ...existing code...
        for section in self.plan['sections']:
            if not any(resource for resource in self.resources if section['title'].lower() in resource.lower()):
                return False
        return True
