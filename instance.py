import discord
from database import Database, Prompt, Profile
from help import HELP_MESSAGE

class Instance:
    def __init__(self, message: discord.Message, prompt: Prompt, webhook: discord.Webhook, db: Database):
        self.message = message
        self.prompt = prompt
        self.thread = message.channel
        self.webhook = webhook
        self.db = db
    
    async def handle_message(self):
        if self.message.content.startswith(';'):
            await self.handle_command()
        elif self.message.content.startswith('>'):
            await self.handle_profile_command()
        else:
            if self.prompt.get_profile():
                await self.webhook_send(self.message.content)
                await self.message.add_reaction('✅')
            else:
                await self.thread.send('Switch to a profile using `>[profile]` before sending messages')

    async def handle_command(self):
        command = self.message.content[1:]
        if ' ' in command:
            command, argument = command.split(' ', 1)
        else:
            argument = None
        command = command.lower()

        if command == 'help':
            await self.thread.send(HELP_MESSAGE)

        elif command == 'profiles':
            await self.command_profiles()

        elif command == 'avatar':
            if self.message.attachments and self.message.attachments[0].content_type.startswith('image/'):
                await self.command_avatar(self.message.attachments[0].url)
            elif argument:
                await self.command_avatar(argument)
            else:
                await self.command_avatar(None)

        elif command == 'username':
            await self.command_username(argument)

        elif command == 'preview':
            await self.command_preview(argument)

        else:
            await self.thread.send('Unknown command. Use ;help for instructions')
        

    async def handle_profile_command(self):
        command = self.message.content[1:]
        if len(command) == 0:
            await self.thread.send('Unknown command. Use ;help for instructions')
            return
        
        if ' ' in command:
            profile_key, message = command.split(' ', 1)
            profile_key = profile_key.lower()
            await self.command_temp_profile(profile_key, message)
        else:
            await self.command_profile(command)


    async def command_avatar(self, url):
        profile = self.prompt.get_profile()
        if profile is None:
            await self.thread.send('Switch to a profile using `>[profile]` before setting avatar')
            return
        profile.set_avatar(url)
        await self.webhook_preview('Changed avatar')

    async def command_username(self, username):
        profile = self.prompt.get_profile()
        if profile is None:
            await self.thread.send('Switch to a profile using `>[profile]` before setting username')
            return
        profile.set_username(username)
        await self.webhook_preview(f'Changed username to {username}')

    async def command_preview(self, message):
        await self.webhook_preview(message if message else f'Profile: {self.prompt.get_profile().key}')
    
    async def command_profile(self, profile_key: str):
        profile_key = profile_key.lower()
        self.prompt.set_profile(profile_key)
        await self.webhook_preview(f'Changed profile to {profile_key}')

    async def command_temp_profile(self, profile_key, message):
        await self.webhook_send(message, alias = self.db.get_profile(profile_key))
        await self.message.add_reaction('✅')

    async def command_profiles(self):
        await self.thread.send(f'Profiles: {self.db.list_profiles()}')

    async def webhook_send(self, message: str, alias: Profile = None):
        profile = self.prompt.get_profile() if alias is None else alias
        if profile:
            username, avatar_url = profile.get_details()
        else:
            username, avatar_url = 'Rz Fake', None
        if avatar_url is None: avatar_url = 'https://discord.com/assets/18e336a74a159cfd.png'
        msg = await self.webhook.send(
            message,
            username = username,
            avatar_url = avatar_url,
            wait = True
            )
        self.db.log_message(self.message.id, msg.id)
    
    async def webhook_preview(self, message):
        profile = self.prompt.get_profile()
        if profile:
            username, avatar_url = profile.get_details()
        else:
            username, avatar_url = 'Rz Fake', None
        if avatar_url is None: avatar_url = 'https://discord.com/assets/18e336a74a159cfd.png'

        await self.webhook.send(
            message,
            username = username,
            avatar_url = avatar_url,
            thread = self.thread
            )