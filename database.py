import os
from supabase import create_client, Client

class DataManager:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        self.db: Client = create_client(url, key)
        self.reset_cache()
    
    def reset_cache(self):
        self.profile_cache = {}
        self.prompt_cache = {}
        self.message_cache = {}

    def get_profile(self, key):
        if key is None: return
        return Profile(key, self.db, self)
    
    def get_prompt(self, id):
        if id in self.prompt_cache:
            return Prompt(id, self.db, self)
        response = (
            self.db.table('Prompt')
            .select('profile')
            .eq('id', id)
            .execute()
        )
        if response.data:
            self.prompt_cache[id] = dict(response.data[0])
            return Prompt(id, self.db, self)

    def register_prompt(self, id):
        if id in self.prompt_cache: return
        response = (
            self.db.table('Prompt')
            .upsert({"id": id})
            .execute()
        )
        self.prompt_cache[id] = {'profile': response.data[0]['profile']}
    
    def log_message(self, prompt_message_id, webhook_message_id):
        response = (
            self.db.table('Message')
            .insert({'prompt_message_id': prompt_message_id, 'webhook_message_id': webhook_message_id})
            .execute()
        )
        self.message_cache[prompt_message_id] = {'webhook_message_id': webhook_message_id}
    
    def get_webhook_message_id(self, prompt_message_id):
        if prompt_message_id in self.message_cache:
            return self.message_cache[prompt_message_id]['webhook_message_id']
        response = (
            self.db.table('Message')
            .select("webhook_message_id")
            .eq("prompt_message_id", prompt_message_id)
            .execute()
        )
        if not response.data: return
        webhook_message_id = response.data[0]['webhook_message_id']
        self.message_cache[prompt_message_id] = {'webhook_message_id': webhook_message_id}
        return webhook_message_id

    def list_profiles(self):
        response = (
            self.db.table('Profile')
            .select('key')
            .execute()
        )
        items = sorted(item['key'] for item in response.data)
        return ' '.join(items)
    

class Profile:
    def __init__(self, profile_key: str, db: Client, dm: DataManager):
        self.key = profile_key.lower()
        self.db = db
        self.dm = dm
    
    def get_details(self) -> tuple[str | None, str | None]:
        if self.key in self.dm.profile_cache:
            cache = self.dm.profile_cache[self.key]
            if 'username' in cache and 'avatar' in cache:
                return cache['username'] or self.key, cache['avatar']
        response = (
            self.db.table('Profile')
            .select('username, avatar')
            .eq('key', self.key)
            .execute()
        )
        if response.data:
            username = response.data[0]['username']
            avatar = response.data[0]['avatar']
            self.dm.profile_cache[self.key] = {'username': username, 'avatar': avatar}
            return username or self.key, avatar
        else:
            self.dm.profile_cache[self.key] = {'username': None, 'avatar': None}
            return self.key, None

    def set_username(self, username):
        response = (
            self.db.table('Profile')
            .upsert({'key': self.key, 'username': username})
            .execute()
        )
        if self.key not in self.dm.profile_cache: self.dm.profile_cache[self.key] = {}
        self.dm.profile_cache[self.key]['username'] = username
    
    def set_avatar(self, avatar):
        response = (
            self.db.table('Profile')
            .upsert({'key': self.key, 'avatar': avatar})
            .execute()
        )
        if self.key not in self.dm.profile_cache: self.dm.profile_cache[self.key] = {}
        self.dm.profile_cache[self.key]['avatar'] = avatar


class Prompt:
    def __init__(self, id, db: Client, dm: DataManager):
        self.id = id
        self.db = db
        self.dm = dm
    
    def get_profile(self):
        if self.id in self.dm.prompt_cache:
            cache = self.dm.prompt_cache[self.id]
            if 'profile' in cache:
                return self.dm.get_profile(cache['profile'])
        
        response = (
            self.db.table('Prompt')
            .select('profile')
            .eq('id', self.id)
            .execute()
        )
        profile = response.data[0]['profile']
        self.dm.prompt_cache[self.id] = {'profile': profile}
        return self.dm.get_profile(profile)

    def set_profile(self, key):
        response = (
            self.db.table('Prompt')
            .update({'profile': key}).eq('id', self.id)
            .execute()
        )
        self.dm.prompt_cache[self.id] = {'profile': key}