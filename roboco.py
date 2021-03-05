import discord
from pathlib import Path
from typing import List

client = discord.Client(intents=discord.Intents.all())
pinRoles: List[int] = eval(Path('roles.txt').read_text())
visibleChannels: List[int] = eval(Path('channels.txt').read_text())

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message: discord.Message):
    global pinRoles, visibleChannels
    if message.author != client.user:
        messageContent = message.content
        if messageContent.startswith('.rbc'):
            messageContent = messageContent[5:]
            print(messageContent)
            if messageContent.startswith('query'):
                await message.channel.send('Roles who can pin: ' + str([message.guild.get_role(x).name for x in pinRoles]))
            elif messageContent.startswith('forcopy'):
                await message.channel.send('ids: ' + ' '.join(str(x) for x in pinRoles))
            elif messageContent.startswith('pingset'):
                if isContributor(message.author):
                    pinRoles = [''.join(y for y in x if y.isdigit()) for x in messageContent[9:].split(' ')]
                    roleFile = open('roles.txt', 'w')
                    roleFile.write(str(pinRoles))
                    roleFile.close()
                else:
                    await message.channel.send('nice try')
            elif messageContent.startswith('set'):
                if isContributor(message.author):
                    pinRoles = [int(x) for x in messageContent[5:].split(' ')]
                    roleFile = open('roles.txt', 'w')
                    roleFile.write(str(pinRoles))
                    roleFile.close()
                else:
                    await message.channel.send('nice try')
            elif messageContent.startswith('channel'):
                if isContributor(message.author):
                    visibleChannels = [int(x) for x in messageContent[8:].split(' ')]
                    channelFile = open('channels.txt', 'w')
                    channelFile.write(str(visibleChannels))
                    channelFile.close()
            else:
                await message.channel.send('syntax error')

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
            await client.get_channel(796900918901080085).send(embed=sendEmbed)
        else:
            await reaction.message.channel.send("You don't have the proper role to pin that message")

async def isContributor(user: discord.Member):
    return any(x.name.lower() == 'contributor' for x in user.roles)

async def userHasPin(reaction: discord.Reaction):
    return any(y.id in pinRoles for x in await reaction.users().flatten() for y in x.roles)

client.run(open('clientsecret.txt').read())