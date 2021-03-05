import json
from pathlib import Path
from typing import Set

import discord

client = discord.Client(intents=discord.Intents.all())

with open("roles.txt", "r") as fin:
    pin_roles: Set[int] = set(json.load(fin))

with open("channels.txt", "r") as fin:
    invisible_channels: Set[int] = set(json.load(fin))


def save_pin_roles():
    with open("roles.txt", "w+") as fout:
        json.dump(pin_roles, fout)


def save_invisible_channels():
    with open("channels.txt", "w") as fout:
        json.dump(invisible_channels, fout)


@client.event
async def on_ready():
    print("We have logged in as", client.user)


@client.event
async def on_message(message: discord.Message):
    global pin_roles, invisible_channels
    if message.author == client.user:
        return
    if message.channel.id not in invisible_channels:
        message_content = message.content
        if message_content.startswith(".rbc"):
            message_content = message_content[5:]
            print(message_content)
            if message_content.startswith("queryc"):
                await message.channel.send(
                    "Channels the bot can't see: "
                    + str(
                        [
                            message.guild.get_channel(x).name
                            for x in invisible_channels
                        ]
                    )
                )
            elif message_content.startswith("query"):
                await message.channel.send(
                    "Roles who can pin: "
                    + str([message.guild.get_role(x).name for x in pin_roles])
                )
            elif message_content.startswith("forcopy"):
                await message.channel.send(f"ids: {' '.join(map(str, pin_roles))}")
            elif message_content.startswith("pingset"):
                if await is_contributor(message.author):
                    pin_roles = {
                        int("".join(filter(str.isdigit, x)))
                        for x in message_content[9:].split(" ")
                    }
                    save_pin_roles()
                else:
                    await message.channel.send("nice try")
            elif message_content.startswith("set"):
                if await is_contributor(message.author):
                    pin_roles = {int(x) for x in message_content[5:].split(" ")}
                    save_pin_roles()
                else:
                    await message.channel.send("nice try")
            elif message_content.startswith("channelm"):
                if await is_contributor(message.author):
                    invisible_channels = {
                        int("".join(y for y in x if y.isdigit()))
                        for x in message_content[10:].split(" ")
                    }
                    save_invisible_channels()
            elif message_content.startswith("channel"):
                if await is_contributor(message.author):
                    invisible_channels = set(
                        map(int, message_content[8:].split(" "))
                    )
                    save_invisible_channels()
                else:
                    await message.channel.send("nice try")
            else:
                await message.channel.send("syntax error")


@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    print(reaction.emoji)
    if reaction.emoji == "📌":
        if await user_has_pin(reaction):
            sendEmbed = discord.Embed(timestamp=reaction.message.created_at)
            sendEmbed.set_author(
                name=reaction.message.author.display_name,
                url=reaction.message.jump_url,
                icon_url=reaction.message.author.avatar_url,
            )
            sendEmbed.add_field(
                name=f"#{reaction.message.channel.name}",
                value=reaction.message.content,
                inline=False,
            )
            for x in reversed(reaction.message.attachments):
                if x.filename.lower().endswith(
                    (".jpg", ".jpeg", ".png", ".gif", ".gifv")
                ):
                    sendEmbed.set_image(url=x.url)
            await client.get_channel(796900918901080085).send(embed=sendEmbed)
        else:
            await reaction.message.channel.send(
                "You don't have the proper role to pin that message"
            )


async def is_contributor(user: discord.Member):
    return any(x.name.lower() == "contributor" for x in user.roles)


async def user_has_pin(reaction: discord.Reaction):
    return any(
        y.id in pin_roles for x in await reaction.users().flatten() for y in x.roles
    )


with open("clientsecret.txt", "r") as fin:
    client.run(fin.read())
