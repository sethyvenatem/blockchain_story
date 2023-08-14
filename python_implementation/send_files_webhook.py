# -----------------------------------------------------------
# Sends file to the discord server through a webhook. Use the 'SPOILER_' tag to hide the code and avoid distracting the users.
#
# 14/08/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------

from discord_webhook import DiscordWebhook, DiscordEmbed

# Thanks! https://www.reddit.com/r/Discord_Bots/comments/iirmzy/how_to_send_files_using_discord_webhooks_python/

file_name = 'welcome-and-how-it-works_webhook_link.txt'
with open(file_name, 'r') as f:
    webhook_url = f.read()

webhook = DiscordWebhook(url=webhook_url)
file_name = 'chapter_signature.py'
embed = DiscordEmbed()
#Set the title and description of the embed
embed.set_title('Script to digitally sign chapter: '+file_name)
#embed.set_description(file_name)
#Add the embed to the webhook
webhook.add_embed(embed)
response = webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
#Add the file or files to the embed
with open(file_name, 'rb') as f: 
    file_data = f.read()
webhook.add_file(file_data, 'SPOILER_'+file_name)
response = webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
file_name = 'mining.py'
embed = DiscordEmbed()
embed.set_title('Script to mine new chapters: '+file_name)
#embed.set_description(file_name)
webhook.add_embed(embed)
response = webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
with open(file_name, 'rb') as f:
    file_data = f.read() 
webhook.add_file(file_data, 'SPOILER_'+file_name)
response = webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
file_name = 'checks.py'
embed = DiscordEmbed()
embed.set_title('Script to check story parts and generate readable *.txt file: '+file_name)
#embed.set_description(file_name)
webhook.add_embed(embed)
response = webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
with open(file_name, 'rb') as f: 
    file_data = f.read() 
webhook.add_file(file_data, 'SPOILER_'+file_name)
response = webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
file_name = 'genesis_block.json'
embed = DiscordEmbed()
embed.set_title('Example of block 0: '+file_name)
#embed.set_description(file_name)
webhook.add_embed(embed)
response = webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
with open(file_name, 'rb') as f: 
    file_data = f.read() 
webhook.add_file(file_data, 'SPOILER_'+file_name)
response = webhook.execute()