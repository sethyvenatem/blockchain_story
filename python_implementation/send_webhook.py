# -----------------------------------------------------------
# Sends webhook to the discord server through.
#
# 15/08/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------

from discord_webhook import DiscordWebhook, DiscordEmbed

# Thanks! https://www.reddit.com/r/Discord_Bots/comments/iirmzy/how_to_send_files_using_discord_webhooks_python/

file_name = 'welcome-and-how-it-works_webhook_link.txt'
with open(file_name, 'r') as f:
    webhook_url = f.read()

file_name = '../discord_text.md'
with open(file_name, 'r') as f:
    text = f.read()
text = text.split('#split')

webhook = DiscordWebhook(url=webhook_url)
webhook.content = text[0]
webhook.username = 'sethyvenatem'
webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
webhook.content = text[1]
webhook.username = 'sethyvenatem'

embed = DiscordEmbed()
#embed.set_author('sethyvenatem')
#Set the title and description of the embed
embed.set_title(text[2])
embed.set_description(text[3])
#Add the embed to the webhook
webhook.add_embed(embed)

embed = DiscordEmbed()
#embed.set_author('sethyvenatem')
#Set the title and description of the embed
embed.set_title(text[4])
embed.set_description(text[5])
#Add the embed to the webhook
webhook.add_embed(embed)

embed = DiscordEmbed()
#embed.set_author('sethyvenatem')
#Set the title and description of the embed
embed.set_title(text[6])
embed.set_description(text[7])
#Add the embed to the webhook
webhook.add_embed(embed)
webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
webhook.content = text[8]
webhook.username = 'sethyvenatem'

embed = DiscordEmbed()
#embed.set_author('sethyvenatem')
#Set the title and description of the embed
embed.set_title(text[9])
embed.set_description(text[10])
#Add the embed to the webhook
webhook.add_embed(embed)
webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
webhook.content = text[11]
webhook.username = 'sethyvenatem'

embed = DiscordEmbed()
#embed.set_author('sethyvenatem')
#Set the title and description of the embed
embed.set_title(text[12])
embed.set_description(text[13])
#Add the embed to the webhook
webhook.add_embed(embed)
webhook.execute()

webhook = DiscordWebhook(url=webhook_url)
webhook.content = text[14]
webhook.username = 'sethyvenatem'

embed = DiscordEmbed()
#embed.set_author('sethyvenatem')
#Set the title and description of the embed
embed.set_title(text[15])
embed.set_description(text[16])
#Add the embed to the webhook
webhook.add_embed(embed)

embed = DiscordEmbed()
#embed.set_author('sethyvenatem')
#Set the title and description of the embed
embed.set_title(text[17])
embed.set_description(text[18])
#Add the embed to the webhook
webhook.add_embed(embed)

webhook.execute()