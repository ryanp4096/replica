class Database:
    def __init__(self):
        self.usernames = {}
        self.avatars = {}
        self.message_log = {}
        self.prompts = {}
    
    def get_profile(self, key):
        if key is None: return
        return Profile(key, self)
    
    def get_prompt(self, id):
        if id not in self.prompts: return
        return Prompt(id, self)

    def register_prompt(self, id):
        self.prompts[id] = self.prompts.get(id)
        # sets to current value if already added, or None if not already added
    
    def log_message(self, prompt_message_id, webhook_message_id):
        self.message_log[prompt_message_id] = webhook_message_id
    
    def get_webhook_message_id(self, prompt_message_id):
        return self.message_log.get(prompt_message_id)

    def list_profiles(self):
        items = sorted(set(self.usernames) | set(self.avatars))
        return ' '.join(items)
    
class Profile:
    def __init__(self, profile_key: str, database: Database):
        self.key = profile_key.lower()
        self.database = database
    
    @property
    def username(self):
        return self.database.usernames.get(self.key, self.key)
    
    @username.setter
    def username(self, value):
        self.database.usernames[self.key] = value
    
    @property
    def avatar(self):
        return self.database.avatars.get(self.key)
    
    @avatar.setter
    def avatar(self, value):
        self.database.avatars[self.key] = value

class Prompt:
    def __init__(self, id, database: Database):
        self.id = id
        self.database = database
    
    @property
    def profile_key(self):
        return self.database.prompts.get(self.id)

    @profile_key.setter
    def profile_key(self, value: str):
        self.database.prompts[self.id] = value.lower() if value else None

    @property
    def profile(self):
        return self.database.get_profile(self.profile_key)
    
    @profile.setter
    def profile(self, profile: Profile):
        self.profile_key = profile.key if profile else None