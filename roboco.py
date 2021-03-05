import asyncio
import json
from typing import Set

import discord
from discord import message

from util import *

client = discord.Client(intents=discord.Intents.all())
kalm_moments = None

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
    global kalm_moments
    print("We have logged in as", client.user)
    kalm_moments = client.get_channel(796900918901080085)


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
    global kalm_moments
    print(reaction.emoji)
    if reaction.emoji == "📌":
        if await any_reaction_pinners(reaction):
            if not any((x.embeds[0].author.url if len(x.embeds) > 0 else None) == reaction.message.jump_url for x in await kalm_moments.history().flatten()):
                send_embed = discord.Embed(timestamp=reaction.message.created_at)
                if not reaction.message.reference:
                    send_embed.set_author(
                        name=reaction.message.author.display_name,
                        url=reaction.message.jump_url,
                        icon_url=reaction.message.author.avatar_url,
                    )
                    send_embed.add_field(
                        name=f"#{reaction.message.channel.name}",
                        value=f"[{reaction.message.content}]({reaction.message.jump_url})",
                        inline=False,
                    )
                else:
                    send_embed.set_author(
                        name="multiple people",
                        url=reaction.message.jump_url,
                    )
                    send_embed.add_field(
                        name=f"#{reaction.message.channel.name}",
                        value="multiple messages",
                        inline=False,
                    )
                    await add_replies_to_embed(send_embed, reaction.message, 1, reaction.message.channel)
                for x in reversed(reaction.message.attachments):
                    if x.filename.lower().endswith(
                        (".jpg", ".jpeg", ".png", ".gif", ".gifv")
                    ):
                        send_embed.set_image(url=x.url)
                await kalm_moments.send(embed=send_embed)
                messageEmbed = discord.Embed()
                messageEmbed.set_author(
                    name=client.user.name,
                    icon_url=client.user.avatar_url,
                )
                messageEmbed.add_field(
                    name="📌",
                    value=f"{(await first_pinner(reaction)).display_name} has pinned a [message]({reaction.message.jump_url}) to #{kalm_moments.name}.",
                    inline=False,
                )
                await reaction.message.channel.send(embed=messageEmbed)
        else:
            await reaction.message.channel.send(
                "You don't have the proper role to pin that message"
            )

async def add_replies_to_embed(embed: discord.Embed, message: discord.Message, depth: int, channel: discord.TextChannel):
    if not message or depth > 24:
        return
    if message.reference:
        await add_replies_to_embed(embed, await channel.fetch_message(message.reference.message_id), depth+1, channel)
    embed.add_field(
        name=message.author.display_name,
        value=f"[{message.content}]({message.jump_url})",
        inline=False,
    )

async def any_reaction_pinners(reaction: discord.Reaction) -> bool:
    return any((user_has_pin(x)) for x in (await reaction.users().flatten()))

async def first_pinner(reaction: discord.Reaction) -> discord.Member:
    return next((x for x in (await reaction.users().flatten()) if user_has_pin(x)))

def user_has_pin(user: discord.Member) -> bool:
    return any(y.id in pin_roles for y in user.roles)


with open("clientsecret.txt", "r") as fin:
    client.run(fin.read())
