from discord import *
client = Client(Intents=Intents(reactions=True))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_reaction_add(reaction: Reaction, user: User):
    print(reaction.emoji)
    if reaction.emoji == reaction.emoji:
        print('send')

client.run(open('clientsecret.txt').read())