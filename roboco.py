import asyncio
import json
from typing import Set

import discord

from util import *

client = discord.Client(intents=discord.Intents.all())

with open("roles.txt", "r") as fin:
    pin_roles: Set[int] = set(json.load(fin))

with open("channels.txt", "r") as fin:
    invisible_channels: Set[int] = set(json.load(fin))


def save_pin_roles(new_pin_roles):
    global pin_roles
    pin_roles = new_pin_roles
    with open("roles.txt", "w") as fout:
        json.dump(list(pin_roles), fout)


def save_invisible_channels(new_invisible):
    global invisible_channels
    invisible_channels = new_invisible
    with open("channels.txt", "w") as fout:
        json.dump(list(invisible_channels), fout)


@client.event
async def on_ready():
    print("We have logged in as", client.user)


@register_command("queryc")
async def on_queryc(message, message_content):
    await message.channel.send(
        "Channels the bot can't see: "
        + str([message.guild.get_channel(x).name for x in invisible_channels])
    )


@register_command("query")
async def on_query(message, message_content):
    await message.channel.send(
        "Roles who can pin: " + str([message.guild.get_role(x).name for x in pin_roles])
    )


@register_command("forcopy")
async def on_forcopy(message, message_content):
    await message.channel.send(f"ids: {' '.join(map(str, pin_roles))}")


@register_command("pingset")
@needs_contributor
async def on_pingset(message, message_content):
    save_pin_roles(
        {int("".join(filter(str.isdigit, x))) for x in message_content[9:].split(" ")}
    )


@register_command("set")
@needs_contributor
async def on_set(message, message_content):
    save_pin_roles({int(x) for x in message_content[4:].split(" ")})


@register_command("channelm")
@needs_contributor
async def on_channelm(message, message_content):
    save_invisible_channels(
        {
            int("".join(y for y in x if y.isdigit()))
            for x in message_content[10:].split(" ")
        }
    )


@register_command("channel")
@needs_contributor
async def on_channel(message, message_content):
    save_invisible_channels(set(map(int, message_content[8:].split(" "))))


@register_command(None)
async def on_default(message):
    await message.channel.send("syntax error")


@client.event
async def on_message(message: discord.Message):
    if (
        message.author == client.user
        or message.channel.id in invisible_channels
        or not message.content.startswith(".rbc")
    ):
        return
    message_content = message.content[5:]
    print(message_content)
    command = command_starts_with(message_content)
    await asyncio.gather(
        *(
            callback(message=message, message_content=message_content)
            for callback in commands[command]
        )
    )


@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    print(reaction.emoji)
    if reaction.emoji == "📌":
        if await user_has_pin(reaction):
            if not any((x.embeds[0].author.url if len(x.embeds) > 0 else None) == reaction.message.jump_url for x in await client.get_channel(796900918901080085).history().flatten()):
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


async def user_has_pin(reaction: discord.Reaction):
    return any(
        y.id in pin_roles for x in await reaction.users().flatten() for y in x.roles
    )


with open("clientsecret.txt", "r") as fin:
    client.run(fin.read())
