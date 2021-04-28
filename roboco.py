import asyncio
from asyncio.tasks import sleep
import json
import re
from typing import Dict, Set, Union, List

import discord
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

from util import *

client = discord.Client(intents=discord.Intents.all())
timestamp_match = re.compile(r'\d\d:\d\d:\d\d|\d\d:\d\d')
slash = SlashCommand(client, sync_commands=True)
kalm_moments: discord.TextChannel
clip_request: discord.TextChannel
nice_channel: discord.TextChannel
slash_command_guilds = [808452876920946728]
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

def add_pin_roles(new_pin_roles):
    global pin_roles
    pin_roles.add(new_pin_roles)
    with open("roles.txt", "w") as fout:
        json.dump(list(pin_roles), fout)

def remove_pin_roles(new_pin_roles):
    global pin_roles
    pin_roles.remove(new_pin_roles)
    with open("roles.txt", "w") as fout:
        json.dump(list(pin_roles), fout)


def save_invisible_channels(new_invisible):
    global invisible_channels
    invisible_channels = new_invisible
    with open("channels.txt", "w") as fout:
        json.dump(list(invisible_channels), fout)

def add_invisible_channels(new_invisible):
    global invisible_channels
    invisible_channels.add(new_invisible)
    with open("channels.txt", "w") as fout:
        json.dump(list(invisible_channels), fout)

def remove_invisible_channels(new_invisible):
    global invisible_channels
    invisible_channels.remove(new_invisible)
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

@slash.slash(name="queryc",
             description="See list of channels invilible to the bot.",
             guild_ids=slash_command_guilds)
async def on_slash_queryc(ctx):
    await ctx.send(
        "Channels the bot can't see: "
        + str([ctx.guild.get_channel(x).name for x in invisible_channels])
    )


@register_command("query")
async def on_query(message: discord.Message, message_content: str):
    await message.channel.send(
        "Roles who can pin: " + str([message.guild.get_role(x).name for x in pin_roles])
    )

@slash.slash(name="query",
             description="See list of roles that are able to pin messages.",
             guild_ids=slash_command_guilds)
async def on_slash_query(ctx):
    await ctx.send(
        "Roles who can pin: " + str([ctx.message.guild.get_role(x).name for x in pin_roles])
    )

@register_command("help")
async def on_help(message: discord.Message, message_content: str):
    await message.channel.send(f"{help_file}")

@slash.slash(name="help",
             description="Take your best guess.",
             guild_ids=slash_command_guilds)
async def on_slash_help(ctx):
    await ctx.send(f"{help_file}")

@register_command("forcopy")
async def on_forcopy(message: discord.Message, message_content: str):
    await message.channel.send(f"ids: {' '.join(map(str, pin_roles))}")

@slash.slash(name="forcopy",
             description="Get role ids that are able to ping, for copying into a set.",
             guild_ids=slash_command_guilds)
async def on_slash_forcopy(ctx):
    await ctx.send(f"ids: {' '.join(map(str, pin_roles))}")

@register_command("pinset")
@needs_contributor
async def on_pingset(message: discord.Message, message_content: str):
    save_pin_roles(
        {int("".join(filter(str.isdigit, x))) for x in message_content[9:].split(" ")}
    )

@slash.slash(name="pinset",
            description="Gives a role permission to pin messages. Requires the @Contributor role.",
            options=[
               create_option(
                 name="role",
                 description="The role that you want to add to the approved role list.",
                 option_type=8,
                   required=True
               )
             ], guild_ids=slash_command_guilds)
async def on_slash_pingset(ctx, role):
    if await is_contributor(ctx.author):
        add_pin_roles(role.id)
        await ctx.send("Pin permission granted.")
    else:
        await ctx.send("This action required elevated privigales. Nice try tho.")

@slash.slash(name="pinremove",
            description="Revokes a role's permission to pin messages. Requires the @Contributor role.",
            options=[
               create_option(
                 name="role",
                 description="The role that you want to remove from the approved role list.",
                 option_type=8,
                   required=True
               )
             ], guild_ids=slash_command_guilds)
async def on_slash_pingremove(ctx, role):
    if await is_contributor(ctx.author):
        remove_pin_roles(role.id)
        await ctx.send("Pin permission removed.")
    else:
        await ctx.send("This action required elevated privigales. Nice try tho.")


@register_command("pinsetid")
@needs_contributor
async def on_set(message: discord.Message, message_content: str):
    save_pin_roles({int(x) for x in message_content[4:].split(" ")})


@slash.slash(name="pinsetid",
             description="Gives a role permission to pin messages. Uses the role's ID. Requires the @Contributor role.",
             options=[
                 create_option(
                     name="roleId",
                     description="The ID of role that you want to add to the approved role list.",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_set(ctx, roleid):
    if await is_contributor(ctx.author):
        add_pin_roles(int(roleid))
        await ctx.send("Pin permission granted.")
    else:
        await ctx.send("This action required elevated privigales. Nice try tho.")

@slash.slash(name="pinremoveid",
             description="Removes a role's permission to pin messages. Uses the role's ID. Requires the @Contributor role.",
             options=[
                 create_option(
                     name="roleId",
                     description="The ID of role that you want to remove from the approved role list.",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_remove(ctx, roleid):
    if await is_contributor(ctx.author):
        remove_pin_roles(int(roleid))
        await ctx.send("Pin permission removed.")
    else:
        await ctx.send("This action required elevated privigales. Nice try tho.")


@register_command("channelblock")
@needs_contributor
async def on_channelm(message: discord.Message, message_content: str):
    save_invisible_channels(
        {
            int("".join(y for y in x if y.isdigit()))
            for x in message_content[10:].split(" ")
        }
    )

@slash.slash(name="channelblock",
             description="Makes a channel invisible to the bot. Requires the @Contributor role.",
             options=[
                 create_option(
                     name="channel",
                     description="The channel you want to block.",
                     option_type=7,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_channelm(ctx, channel):
    if await is_contributor(ctx.author):
        add_invisible_channels(channel.id)
        await ctx.send("Added channel to the block list.")
    else:
        await ctx.send("This action required elevated privigales. Nice try tho.")

@slash.slash(name="channelunblock",
             description="Makes an invisible channel vilible again to the bot. Requires the @Contributor role.",
             options=[
                 create_option(
                     name="channel",
                     description="The channel you want to unblock.",
                     option_type=7,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_rm_channelm(ctx, channel):
    if await is_contributor(ctx.author):
        remove_invisible_channels(channel.id)
        await ctx.send("Removed channel from the block list.")
    else:
        await ctx.send("This action required elevated privigales. Nice try tho.")


@slash.slash(name="channelidblock",
             description="Makes a channel invisible to the bot. Uses the channel's ID. Requires the @Contributor role.",
             options=[
                 create_option(
                     name="channelid",
                     description="The ID of the channel you want to block.",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_rm_channel(ctx, channelid):
    if await is_contributor(ctx.author):
        add_invisible_channels(int(channelid))
        await ctx.send("Added channel to the block list.")
    else:
        await ctx.send("This action required elevated privigales. Nice try tho.")

@slash.slash(name="channelidunblock",
             description="Makes an invisible channel vilible again to the bot, uses ID. Requires the @Contributor role.",
             options=[
                 create_option(
                     name="channel",
                     description="The id of the channel you want to unblock.",
                     option_type=7,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_rm_channel(ctx, channel):
    if await is_contributor(ctx.author):
        remove_invisible_channels(int(channelid))
        await ctx.send("Removed channel from the block list.")
    else:
        await ctx.send("This action required elevated privigales. Nice try tho.")


@register_command("channelidblock")
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

@slash.slash(name="clip",
             description="Sends a clip request to the LiveTL clipping team.",
             options=[
                 create_option(
                     name="video",
                     description="A link to the original stream.",
                     option_type=3,
                     required=True
                 ),
                 create_option(
                     name="clipreason",
                     description="A reason for clipping and additional comments.",
                     option_type=3,
                     required=True
                 ),
                 create_option(
                     name="timestamp",
                     description="A timestamp where the clip begins.",
                     option_type=3,
                     required=False
                 )
             ],
             guild_ids=slash_command_guilds)
async def on_slash_clip(ctx, video, timestamp, clipreason):
    send_message_content = f"Request from {ctx.author.mention} to clip {video} "
    if timestamp_match.match(timestamp):
        send_message_content += f"at timestamp {timestamp} "
    send_message_content += f"\nbecause {clipreason}"
    await clip_request.send(send_message_content)
    await ctx.send("Consider it done.")

@register_command("onii-chan")
async def on_oniichan(message: discord.Message, message_content: str):
    if message.channel.is_nsfw():
        await message.channel.send(onii_chan)
    else:
        await message.channel.send("oi what you tryna do")

@slash.slash(name="onii-chan",
             description="O-onii-chan...",
             guild_ids=slash_command_guilds)
async def on_slash_oniichan(ctx):
    if ctx.channel.is_nsfw():
        await ctx.send(onii_chan)
    else:
        await ctx.send("oi what you tryna do")

@register_command("bean")
async def on_bean(message: discord.Message, message_content: str):
    await message.channel.send(f"{message_content[5:]} has been beaned")

@slash.slash(name="bean",
             description="Beans a user.",
             options=[
                 create_option(
                     name="user",
                     description="The user you wish to bean.",
                     option_type=6,
                     required=True
                 )
             ],
             guild_ids=slash_command_guilds)
async def on_slash_bean(ctx, user):
    await ctx.send(f"{user.mention} has been beaned.")


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
                    message_embed = discord.Embed()
                    message_embed.set_author(
                        name=client.user.name,
                        icon_url=client.user.avatar_url,
                    )
                    message_embed.add_field(
                        name="📌",
                        value=f"{(await first_pinner(reaction)).display_name} has pinned a [message]({reaction.message.jump_url}) to #{kalm_moments.name}.",
                        inline=False,
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
                        name=reaction.message.author.display_name,
                        url=reaction.message.jump_url,
                        icon_url=reaction.message.author.avatar_url,
                    )
                    send_embed.add_field(
                        name=f"#{reaction.message.channel.name}",
                        value=f"[{reaction.message.content}]({reaction.message.jump_url})",
                        inline=False,
                    )
                    for x in reversed(reaction.message.attachments):
                        if x.filename.lower().endswith(
                            (".jpg", ".jpeg", ".png", ".gif", ".gifv")
                        ):
                            send_embed.set_image(url=x.url)
                    await kalm_moments.send(embed=send_embed)
                    message_embed = discord.Embed()
                    message_embed.set_author(
                        name=client.user.name,
                        icon_url=client.user.avatar_url,
                    )
                    message_embed.add_field(
                        name="📍",
                        value=f"{(await first_pinner(reaction)).display_name} has pinned a [message]({reaction.message.jump_url}) to #{kalm_moments.name}.",
                        inline=False,
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


if __name__ == "__main__":
    with open("roles.txt", "r") as fin:
        pin_roles: Set[int] = set(json.load(fin))

    with open("channels.txt", "r") as fin:
        invisible_channels: Set[int] = set(json.load(fin))

    with open("oniichan.txt", "r", encoding="utf-8") as fin:
        onii_chan = fin.read()

    with open("clientsecret.txt", "r") as fin:
        client.run(fin.read())
