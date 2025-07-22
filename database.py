import os
from supabase import create_client, Client

class Database:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        self.db: Client = create_client(url, key)

        self.usernames = {}
        self.avatars = {}
        # self.message_log = {}
        # self.prompts = {}
    
    def get_profile(self, key):
        if key is None: return
        return Profile(key, self)
    
    def get_prompt(self, id):
        response = (
            self.db.table('Prompt')
            .select('id')
            .eq('id', id)
            .execute()
        )
        if response.data:
            return Prompt(id, self.db, self)

    def register_prompt(self, id):
        response = (
            self.db.table('Prompt')
            .upsert({"id": id})
            .execute()
        )
        # self.prompts[id] = self.prompts.get(id)
        # sets to current value if already added, or None if not already added
    
    def log_message(self, prompt_message_id, webhook_message_id):
        self.db.table('Message').insert({'prompt_message_id': prompt_message_id, 'webhook_message_id': webhook_message_id}).execute()
        # self.message_log[prompt_message_id] = webhook_message_id
    
    def get_webhook_message_id(self, prompt_message_id):
        response = (
            self.db.table('Message')
            .select("webhook_message_id")
            .eq("prompt_message_id", prompt_message_id)
            .execute()
        )
        return response.data[0]['webhook_message_id'] if response.data else None
        # return self.message_log.get(prompt_message_id)

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
    def __init__(self, id, db: Client, database: Database):
        self.id = id
        self.db = db
        self.database = database
    
    def get_profile(self):
        response = (
            self.db.table('Prompt')
            .select('profile')
            .eq('id', self.id)
            .execute()
        )
        return self.database.get_profile(response.data[0]['profile'])

    def set_profile(self, key):
        response = (
            self.db.table('Prompt')
            .update({'profile': key}).eq('id', self.id)
            .execute()
        )

    # @property
    # def profile_key(self):
    #     return self.database.prompts.get(self.id)

    # @profile_key.setter
    # def profile_key(self, value: str):
    #     self.database.prompts[self.id] = value.lower() if value else None

    # @property
    # def profile(self):
    #     return self.database.get_profile(self.profile_key)
    
    # @profile.setter
    # def profile(self, profile: Profile):
    #     self.profile_key = profile.key if profile else None