import discord
from database import Database, User
from help import HELP_MESSAGE

class Instance:
    def __init__(self, message: discord.Message, user: User, webhook: discord.Webhook, db: Database):
        self.message = message
        self.user = user
        self.thread = message.channel
        self.webhook = webhook
        self.db = db
    
    async def handle_message(self):
        if self.message.content.startswith(';'):
            await self.handle_command()
        elif self.message.content.startswith('>'):
            await self.handle_profile_command()
        else:
            await self.webhook_send(self.message.content)

    async def handle_command(self):
        command = self.message.content[1:]

        if command.lower() == 'help':
            await self.command_help()

        elif command.lower() == 'profiles':
            await self.thread.send('Coming soon') #TODO

        elif command.lower() == 'avatar':
            if self.message.attachments and self.message.attachments[0].content_type.startswith('image/'):
                await self.command_avatar(self.message.attachments[0].url)
            else:
                await self.thread.send('Could not find attached image')

        elif command.lower().startswith('avatar '):
            await self.command_avatar(command[7:])

        elif command.lower().startswith('username '):
            await self.command_username(command[9:])

        elif command.lower() == 'preview':
            await self.command_preview()

        else:
            await self.thread.send('Unknown command. Use ;help for instructions')
        

    async def handle_profile_command(self):
        command = self.message.content[1:]
        if len(command) == 0:
            await self.thread.send('Unknown command. Use ;help for instructions')
            return
        
        if ' ' in command:
            profile_key, message = command.split(' ', 1)
            old_profile = self.user.profile
            self.user.set_profile(profile_key)
            await self.webhook_send(message)
            self.user.profile = old_profile
        else:
            await self.command_profile(command)


    async def command_help(self):
        await self.thread.send(HELP_MESSAGE)
    
    async def command_avatar(self, url):
        if self.user.profile is None:
            await self.thread.send('Switch to a profile using `>[profile name]` before setting avatar')
            return
        self.user.profile.avatar = url
        await self.webhook_preview('Changed avatar')

    async def command_username(self, username):
        if self.user.profile is None:
            await self.thread.send('Switch to a profile using `>[profile name]` before setting username')
            return
        self.user.profile.username = username
        await self.webhook_preview(f'Changed username to {username}')

    async def command_preview(self):
        await self.webhook_preview('Preview')
    
    async def command_profile(self, profile_key):
        self.user.set_profile(profile_key)
        await self.webhook_preview(f'Changed profile to {self.user.profile.key}')

    async def webhook_send(self, message):
        if self.user.profile is None:
            msg = await self.webhook.send(message, username = 'Rz Fake', wait = True)
        else:
            msg = await self.webhook.send(
                message,
                username = self.user.profile.username,
                avatar_url = self.user.profile.avatar,
                wait = True
                )
        self.db.log_message(self.message.id, msg.id)
    
    async def webhook_preview(self, message):
        if self.user.profile is None:
            await self.webhook.send(message, username = 'Rz Fake', thread = self.thread)
            return

        await self.webhook.send(
            message,
            username = self.user.profile.username,
            avatar_url = self.user.profile.avatar,
            thread = self.thread
            )