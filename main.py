import os
import discord
from dotenv import load_dotenv

load_dotenv()

class MyClient(discord.Client):
    async def on_ready(self):
        self.bot_webhook_cache = {}
        self.saved_threads = set()
        self.user_profiles = {}
        self.profile_usernames = {}
        self.profile_avatars = {}
        print(f'logged in as {self.user}')

    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        if message.author.id == self.user.id: return
        if message.channel.type != discord.ChannelType.private_thread: return
        if message.channel.id not in self.saved_threads:
            self.saved_threads.add(message.channel.id)
            return
        
        profile = self.user_profiles.get(message.author.id, '')
        webhook = await self.get_bot_webhook(message.channel.parent)

        if message.content.startswith(';'):
            if message.content.startswith(';help'):
                await message.channel.send('Hello World!')

            elif message.content.startswith(';avatar'):
                if message.attachments:
                    avatar = message.attachments[0].url
                self.profile_avatars[profile] = avatar
                await message.channel.send('Changed avatar')
            
            elif message.content.startswith(';username'):
                username = message.content[10:]
                self.profile_usernames[profile] = username
                await message.channel.send(f'Changed username to {username}')
            
            elif message.content.startswith(';preview'):
                await webhook.send('Preview',
                             username = self.profile_usernames.get(profile, profile),
                             avatar_url = self.profile_avatars.get(profile),
                             thread = message.channel
                             )
            
            else:
                await message.channel.send('Unknown Command')

            return
        
        if message.content.startswith('>'):
            profile = message.content[1:]
            self.user_profiles[message.author.id] = profile
            await message.channel.send(f'Changed profile to {profile}')
            return
            
            
        await webhook.send(message.content,
                        username = self.profile_usernames.get(profile, profile),
                        avatar_url = self.profile_avatars.get(profile)
                        )


    async def on_thread_join(self, thread: discord.Thread):
        if thread.type != discord.ChannelType.private_thread: return
        await thread.send("Hello World!")
    
    async def get_bot_webhook(self, channel: discord.TextChannel):
        if channel.id in self.bot_webhook_cache:
            return self.bot_webhook_cache[channel.id]
        
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.user.id == self.user.id:
                break
        else:
            webhook = await channel.create_webhook(name = 'Rz Fake')
        
        self.bot_webhook_cache[channel.id] = webhook
        return webhook


client = MyClient(intents=discord.Intents(
    guilds=True, webhooks=True, messages=True, message_content=True
))
client.run(os.getenv('TOKEN'))