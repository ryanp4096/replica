import os
from typing import override
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
        if message.type != discord.MessageType.default: return
        if message.channel.type != discord.ChannelType.private_thread:
            if message.content == ';help':
                await message.channel.send(HELP_MESSAGE)
            return
        if not self.db.check_thread(message.channel.id) and not (message.content.startswith(';') or message.content.startswith('>')): return
        
        user = self.db.get_user(message.author.id)
        webhook = await self.get_bot_webhook(message.channel.parent)
        instance = Instance(message, user, webhook, self.db)
        await instance.handle_message()


    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        id = self.db.get_webhook_message_id(payload.message_id)
        if id is None: return
        channel = self.get_channel(payload.channel_id).parent
        webhook = await self.get_bot_webhook(channel)
        # message = channel.get_partial_message(id)
        # await message.edit(content = payload.message.content)
        content = payload.message.content
        if content.startswith('>'): content = content.split(' ', 1)[1]
        await webhook.edit_message(id, content = content)

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        id = self.db.get_webhook_message_id(payload.message_id)
        if id is None: return
        channel = self.get_channel(payload.channel_id).parent
        webhook = await self.get_bot_webhook(channel)
        # message = channel.get_partial_message(id)
        # await message.delete()
        await webhook.delete_message(id)

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