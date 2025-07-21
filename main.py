import os
import discord
from dotenv import load_dotenv
from database import Database
from instance import Instance
from help import HELP_MESSAGE

load_dotenv()

class MyClient(discord.Client):
    async def on_ready(self):
        self.db = Database()
        self.bot_webhook_cache = {}
        print(f'logged in as {self.user}')

    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        if message.author.id == self.user.id: return
        if message.channel.type != discord.ChannelType.private_thread:
            if message.content == ';help':
                await message.channel.send(HELP_MESSAGE)
            return
        if not self.db.check_thread(message.channel.id) and not (message.content.startswith(';') or message.content.startswith('>')): return
        
        user = self.db.get_user(message.author.id)
        webhook = await self.get_bot_webhook(message.channel.parent)
        instance = Instance(message, user, webhook)
        await instance.handle_message()


        # if message.content.startswith(';'):
        #     if message.content.startswith(';help'):
        #         await message.channel.send('Hello World!')

        #     elif message.content.startswith(';avatar'):
        #         if message.attachments:
        #             avatar = message.attachments[0].url
        #         profile.avatar = avatar
        #         await message.channel.send('Changed avatar')
            
        #     elif message.content.startswith(';username'):
        #         username = message.content[10:]
        #         profile.username = username
        #         await message.channel.send(f'Changed username to {username}')
            
        #     elif message.content.startswith(';preview'):
        #         await webhook.send('Preview',
        #                      username = profile.username,
        #                      avatar_url = profile.avatar,
        #                      thread = message.channel
        #                      )
            
        #     else:
        #         await message.channel.send('Unknown Command')

        #     return
        
        # if message.content.startswith('>'):
        #     new_profile = message.content[1:]
        #     user.set_profile(new_profile)
        #     await message.channel.send(f'Changed profile to {profile}')
        #     return
            
            
        # await webhook.send(message.content,
        #                 username = profile.username,
        #                 avatar_url = profile.avatar
        #                 )


    async def on_thread_join(self, thread: discord.Thread):
        if thread.type != discord.ChannelType.private_thread: return
        await thread.send(HELP_MESSAGE)
    
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