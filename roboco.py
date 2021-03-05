from typing import List
import discord

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    print(reaction.emoji)
    if reaction.emoji == '📌':
        if await userHasPin(reaction):
            sendEmbed = discord.Embed(timestamp=reaction.message.created_at)
            sendEmbed.set_author(name=reaction.message.author.display_name, url=reaction.message.jump_url, icon_url=reaction.message.author.avatar_url)
            sendEmbed.add_field(name='#' + reaction.message.channel.name, value=reaction.message.content, inline=False)
            for x in reaction.message.attachments[::-1]:
                if x.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv')):
                    sendEmbed.set_image(url=x.url)
            await client.get_channel(709079297813512205).send(embed=sendEmbed)
        else:
            await reaction.message.channel.send("You don't have the proper role to pin that message")

async def userHasPin(reaction: discord.Reaction):
    for x in await reaction.users().flatten():
        for y in reaction.message.guild.get_member(x.id).roles:
            if y.name.lower() == 'pin':
                return True
    return False            

client.run(open('clientsecret.txt').read())