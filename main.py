import os
import discord
from dotenv import load_dotenv
from database import DataManager
from instance import Instance
from help import HELP_MESSAGE
from util import convert_attachments

load_dotenv()
ADMIN_ID = int(os.getenv('ADMIN_ID')) if os.getenv('ADMIN_ID') else None

class MyClient(discord.Client):
    def start_bot(self, dev_mode=False):
        self.dev_mode = dev_mode
        self.paused = False
        self.run(os.getenv('DISCORD_TOKEN'))

    async def on_ready(self):
        self.dm = DataManager()
        self.bot_webhook_cache = {}
        print(f'logged in as {self.user}')

    async def on_message(self, message: discord.Message):
        if message.author.id == ADMIN_ID and message.type == discord.MessageType.default:
            if message.content == ';pause':
                self.paused = True
                print('paused')
                await message.channel.send('paused')
                return
            elif message.content == ';resume':
                self.paused = False
                print('resumed')
                await message.channel.send('resumed')
                return
        
        if self.paused: return
        if message.author.bot: return
        if message.author.id == self.user.id: return
        if message.type not in (discord.MessageType.default, discord.MessageType.reply, discord.MessageType.thread_starter_message): return
        
        if message.channel.type != discord.ChannelType.private_thread:
            if message.content == ';help':
                await message.channel.send(HELP_MESSAGE)
            elif message.content == ';thread' and message.channel.type == discord.ChannelType.text:
                thread = await message.channel.create_thread(name = 'Rz Fake')
                self.dm.register_prompt(thread.id)
                await thread.send(f'<@{message.author.id}>\n' + HELP_MESSAGE)
            return
        
        prompt = self.dm.get_prompt(message.channel.id)
        if prompt is None:
            self.dm.register_prompt(message.channel.id)
            prompt = self.dm.get_prompt(message.channel.id)
            await message.channel.send(HELP_MESSAGE)
            return

        webhook = await self.get_bot_webhook(message.channel.parent)
        instance = Instance(message, prompt, webhook, self.dm)
        await instance.handle_message()


    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        if self.paused: return
        id = self.dm.get_webhook_message_id(payload.message_id)
        if id is None: return

        channel = self.get_channel(payload.channel_id).parent
        webhook = await self.get_bot_webhook(channel)

        content = payload.message.content
        if content.startswith('>'): content = content.split(' ', 1)[1]
        content += convert_attachments(payload.message.attachments)

        await webhook.edit_message(id, content = content)


    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if self.paused: return
        id = self.dm.get_webhook_message_id(payload.message_id)
        if id is None: return

        channel = self.get_channel(payload.channel_id).parent
        webhook = await self.get_bot_webhook(channel)
        await webhook.delete_message(id)    


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


def create_client():
    return MyClient(intents=discord.Intents(
        guilds=True, webhooks=True, messages=True, message_content=True
    ))

# def start_bot():
#     client = MyClient(intents=discord.Intents(
#         guilds=True, webhooks=True, messages=True, message_content=True
#     ))
#     client.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    create_client().start_bot(dev_mode=True)