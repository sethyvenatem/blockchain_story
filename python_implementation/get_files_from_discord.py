import discord

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
guild = discord.Guild
with open('discord_token.txt') as file:
    token = file.read()
signed_chapters_id = 1133791244858966096
validates_stories_id = 1133791437637558332

@client.event
async def on_ready():
    channel = client.get_channel(signed_chapters_id)
    messages = channel.history(limit=1000)#.flatten()
    async for mes in messages:
        for file in mes.attachments:
            if file.filename.endswith('.json'):
                await file.save('test_'+file.filename)
                
    channel = client.get_channel(validates_stories_id)
    messages = channel.history(limit=1000)#.flatten()
    async for mes in messages:
        for file in mes.attachments:
            if file.filename.endswith('.json'):
                await file.save('test_'+file.filename)
                
    await client.close()

client.run(token)