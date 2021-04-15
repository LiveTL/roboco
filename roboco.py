import asyncio
from asyncio.tasks import sleep
import json
import re
from typing import Dict, Set, Union, List

import discord

from util import *

client = discord.Client(intents=discord.Intents.all())
timestamp_match = re.compile(r'\d\d:\d\d:\d\d|\d\d:\d\d')
kalm_moments: discord.TextChannel
clip_request: discord.TextChannel
nice_channel: discord.TextChannel
onii_chan: str
help_file: str

with open("README.md", "r") as fin:
    help_file_list = fin.read().splitlines()
    for i, v in enumerate(help_file_list):
        if v == "## Commmands":
            help_file_list = help_file_list[i:]
            break
    help_file = "\n".join(x for x in help_file_list)

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


async def wait_delete(message: discord.Message, time = 1):
    await sleep(time)
    await message.delete()


@client.event
async def on_ready():
    global kalm_moments, clip_request, nice_channel
    print("We have logged in as", client.user)
    kalm_moments = client.get_channel(796900918901080085)
    clip_request = client.get_channel(820547559319273473)
    nice_channel = client.get_channel(829385883735556108)


@register_command("queryc")
async def on_queryc(message: discord.Message, message_content: str):
    await message.channel.send(
        "Channels the bot can't see: "
        + str([message.guild.get_channel(x).name for x in invisible_channels])
    )


@register_command("query")
async def on_query(message: discord.Message, message_content: str):
    await message.channel.send(
        "Roles who can pin: " + str([message.guild.get_role(x).name for x in pin_roles])
    )

@register_command("help")
async def on_help(message: discord.Message, message_content: str):
    await message.channel.send(f"{help_file}")

@register_command("forcopy")
async def on_forcopy(message: discord.Message, message_content: str):
    await message.channel.send(f"ids: {' '.join(map(str, pin_roles))}")


@register_command("pingset")
@needs_contributor
async def on_pingset(message: discord.Message, message_content: str):
    save_pin_roles(
        {int("".join(filter(str.isdigit, x))) for x in message_content[9:].split(" ")}
    )


@register_command("set")
@needs_contributor
async def on_set(message: discord.Message, message_content: str):
    save_pin_roles({int(x) for x in message_content[4:].split(" ")})


@register_command("channelm")
@needs_contributor
async def on_channelm(message: discord.Message, message_content: str):
    save_invisible_channels(
        {
            int("".join(y for y in x if y.isdigit()))
            for x in message_content[10:].split(" ")
        }
    )


@register_command("channel")
@needs_contributor
async def on_channel(message: discord.Message, message_content: str):
    save_invisible_channels(set(map(int, message_content[8:].split(" "))))


@register_command("clip")
@needs_clip_requester
async def on_clip(message: discord.Message, message_content: str):
    things = message_content[5:].split(' ')
    send_message_content = f"Request from {message.author} to clip {things[0]}"
    things.pop(0)
    if len(things) > 0:
        if timestamp_match.match(things[0]):
            send_message_content += f"at timestamp {things[0]} "
            things.pop(0)
        if len(things) > 0:
            send_message_content += "\nbecause " + ' '.join(x for x in things)
    await clip_request.send(send_message_content)

@register_command("onii-chan")
async def on_oniichan(message: discord.Message, message_content: str):
    if message.channel.is_nsfw():
        await message.channel.send(onii_chan)
    else:
        await message.channel.send("oi what you tryna do")

@register_command("bean")
async def on_bean(message: discord.Message, message_content: str):
    await message.channel.send(f"{message_content[5:]} has been beaned")

@register_command(None)
async def on_default(message: discord.Message):
    await message.channel.send("syntax error")


@client.event
async def on_message(message: discord.Message):
    if (message.channel.id == nice_channel.id):
        if message.content.lower() not in ['', 'nice']:
            await wait_delete(message)
        return
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
    global kalm_moments
    print(reaction.emoji)
    if reaction.emoji == "📌":
        if not reaction.message.channel.is_nsfw():
            if await any_reaction_pinners(reaction):
                if not any((x.embeds[0].author.url if len(x.embeds) > 0 else None) == reaction.message.jump_url for x in await kalm_moments.history().flatten()):
                    send_embed = discord.Embed(timestamp=reaction.message.created_at)
                    if not reaction.message.reference:
                        send_embed.set_author(
                            reaction.message.author.display_name,
                            reaction.message.jump_url,
                            reaction.message.author.avatar_url,
                        )
                        send_embed.add_field(
                            f"#{reaction.message.channel.name}",
                            f"[{reaction.message.content}]({reaction.message.jump_url})",
                            False,
                        )
                    else:
                        send_embed.set_author(
                            "multiple people",
                            reaction.message.jump_url,
                        )
                        send_embed.add_field(
                            f"#{reaction.message.channel.name}",
                            "multiple messages",
                            False,
                        )
                        await add_replies_to_embed(send_embed, reaction.message, 1, reaction.message.channel)
                    for x in reversed(reaction.message.attachments):
                        if x.filename.lower().endswith(
                            (".jpg", ".jpeg", ".png", ".gif", ".gifv")
                        ):
                            send_embed.set_image(x.url)
                    await kalm_moments.send(embed=send_embed)
                    message_embed = discord.Embed()
                    message_embed.set_author(
                        client.user.name,
                        icon_url = client.user.avatar_url,
                    )
                    message_embed.add_field(
                        "📌",
                        f"{(await first_pinner(reaction)).display_name} has pinned a [message]({reaction.message.jump_url}) to #{kalm_moments.name}.",
                        False,
                    )
                    await reaction.message.channel.send(embed=message_embed)
            else:
                await reaction.message.channel.send(
                    "You don't have the proper role to pin that message"
                )
        else:
            await reaction.message.channel.send("no pinning in nsfw channels. bad")
    elif reaction.emoji == "📍":
        if not reaction.message.channel.is_nsfw():
            if await any_reaction_pinners(reaction):
                if not any((x.embeds[0].author.url if len(x.embeds) > 0 else None) == reaction.message.jump_url for x in await kalm_moments.history().flatten()):
                    send_embed = discord.Embed(timestamp=reaction.message.created_at)
                    send_embed.set_author(
                        reaction.message.author.display_name,
                        reaction.message.jump_url,
                        reaction.message.author.avatar_url,
                    )
                    send_embed.add_field(
                        f"#{reaction.message.channel.name}",
                        f"[{reaction.message.content}]({reaction.message.jump_url})",
                        False,
                    )
                    for x in reversed(reaction.message.attachments):
                        if x.filename.lower().endswith(
                            (".jpg", ".jpeg", ".png", ".gif", ".gifv")
                        ):
                            send_embed.set_image(x.url)
                    await kalm_moments.send(embed=send_embed)
                    message_embed = discord.Embed()
                    message_embed.set_author(
                        client.user.name,
                        icon_url=client.user.avatar_url,
                    )
                    message_embed.add_field(
                        "📍",
                        f"{(await first_pinner(reaction)).display_name} has pinned a [message]({reaction.message.jump_url}) to #{kalm_moments.name}.",
                        False,
                    )
                    await reaction.message.channel.send(embed=message_embed)
            else:
                await reaction.message.channel.send(
                    "You don't have the proper role to pin that message"
                )
        else:
            await reaction.message.channel.send("no pinning in nsfw channels. bad")

async def add_replies_to_embed(embed: discord.Embed, message: discord.Message, depth: int, channel: discord.TextChannel):
    if not message or depth > 24:
        return
    if message.reference:
        await add_replies_to_embed(embed, await channel.fetch_message(message.reference.message_id), depth+1, channel)
    embed.add_field(
        message.author.display_name,
        f"[{message.content}]({message.jump_url})",
        False,
    )

async def any_reaction_pinners(reaction: discord.Reaction) -> bool:
    return any((user_has_pin(x)) for x in (await reaction.users().flatten()))

async def first_pinner(reaction: discord.Reaction) -> discord.Member:
    return next((x for x in (await reaction.users().flatten()) if user_has_pin(x)))

def user_has_pin(user: discord.Member) -> bool:
    return any(y.id in pin_roles for y in user.roles)


if __name__ == "__main__":
    with open("roles.txt", "r") as fin:
        pin_roles: Set[int] = set(json.load(fin))

    with open("channels.txt", "r") as fin:
        invisible_channels: Set[int] = set(json.load(fin))

    with open("oniichan.txt", "r", encoding="utf-8") as fin:
        onii_chan = fin.read()

    with open("clientsecret.txt", "r") as fin:
        client.run(fin.read())
