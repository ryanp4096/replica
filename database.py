class Database:
    def __init__(self):
        self.profiles = {}
        self.usernames = {}
        self.avatars = {}
        self.prompt_threads = {}
    
    def get_profile(self, key):
        return Profile(key, self)
    
    def get_user(self, id):
        return User(id, self)
    
    def check_thread(self, thread_id):
        if thread_id in self.prompt_threads:
            return True
        else:
            self.prompt_threads[thread_id] = 1
            return False
    
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

class User:
    def __init__(self, id, database: Database):
        self.id = id
        self.database = database
    
    @property
    def profile(self):
        profile_key = self.database.profiles.get(self.id)
        if profile_key is None: return
        return self.database.get_profile(profile_key)
    
    @profile.setter
    def profile(self, profile: Profile):
        self.database.profiles[self.id] = profile.key
    
    def set_profile(self, profile_key: str):
        self.database.profiles[self.id] = profile_key.lower()