import asyncio
from asyncio.tasks import sleep
import json
import re
from tts import tts
import pytchat as pyt
import ytthings
import os
from filter import parseTranslation
from mchad import *
from typing import Dict, Set, Tuple, Union, List

import discord
import discord_slash

from util import *

client = discord.Client(intents=discord.Intents.all(), activity=discord.Game(name='Send all complaints to yoyoyonono#5582'))
timestamp_match = re.compile(r'\d\d:\d\d:\d\d|\d\d:\d\d')
slash = discord_slash.SlashCommand(client, sync_commands=True)
kalm_moments: discord.TextChannel
clip_request: discord.TextChannel
nice_channel: discord.TextChannel
slash_command_guilds = [780938154437640232, 331172263800078339]
onii_chan: str
help_file: str
FAQ: List[Tuple[str, str]] = [
    ('How does LiveTL Work?', 'LiveTL is, at its core, a chat filter for YouTube streams. It helps foreign viewers better catch translations that other viewers are providing in the live chat. LiveTL does not automatically translate streams – instead, it picks up translations found in the chat.'),
    ('I opened my stream with LiveTL but it isn’t loading.', 'The stream chat may be temporarily unavailable. LiveTL will only load if the stream has a valid live chat or chat replay.'),
    ("I don't see any translations in the translations panel.", 'If there are no translators in chat, LiveTL is unable to provide translations. Any messages properly taggedwith a language (ex. [en], ESP:, etc.) will appear when they are available.'),
    ("A translator is using their own style of language tags.", "You can manually select additional users to filter in the settings."),
    ("The YouTube video isn’t loading in Firefox.", "Allowing video and audio autoplay in Firefox’s website preferences usually fixes this problem."),
    ("I'm having an issue not mentioned here.", "A reinstall of the extension fixes most issues. After that, ask in #tech-support and someone will help you."),
    ("Where is the best place to report a bug or suggest a feature?", "The best place to report bugs/suggest Features for LiveTL is our GitHub. You can find a list of all out platforms at https://github.com/LiveTL. Simply choose a platform, click on the issues tab, and fill out the form.")
]


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


async def wait_delete(message: discord.Message, time: float = 1):
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
async def on_slash_queryc(ctx: discord_slash.SlashContext):
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
async def on_slash_query(ctx: discord_slash.SlashContext):
    await ctx.send(
        "Roles who can pin: " + str([ctx.guild.get_role(x).name for x in pin_roles])
    )

@register_command("help")
async def on_help(message: discord.Message, message_content: str):
    await message.channel.send(f"{help_file}")

@slash.slash(name="help",
             description="Take your best guess.",
             guild_ids=slash_command_guilds)
async def on_slash_help(ctx: discord_slash.SlashContext):
    await ctx.send(f"{help_file}")

@register_command("forcopy")
async def on_forcopy(message: discord.Message, message_content: str):
    await message.channel.send(f"ids: {' '.join(map(str, pin_roles))}")

@slash.slash(name="forcopy",
             description="Get role ids that are able to ping, for copying into a set.",
             guild_ids=slash_command_guilds)
async def on_slash_forcopy(ctx: discord_slash.SlashContext):
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
               discord_slash.utils.manage_commands.create_option(
                 name="role",
                 description="The role that you want to add to the approved role list.",
                 option_type=8,
                   required=True
               )
             ], guild_ids=slash_command_guilds)
async def on_slash_pingset(ctx: discord_slash.SlashContext, role: discord.Role):
    if await is_contributor(ctx.author):
        add_pin_roles(role.id)
        await ctx.send("Pin permission granted.")
    else:
        await ctx.send("This action requires elevated privileges. Nice try tho.")

@slash.slash(name="pinremove",
            description="Revokes a role's permission to pin messages. Requires the @Contributor role.",
            options=[
               discord_slash.utils.manage_commands.create_option(
                 name="role",
                 description="The role that you want to remove from the approved role list.",
                 option_type=8,
                   required=True
               )
             ], guild_ids=slash_command_guilds)
async def on_slash_pingremove(ctx: discord_slash.SlashContext, role: discord.Role):
    if await is_contributor(ctx.author):
        remove_pin_roles(role.id)
        await ctx.send("Pin permission removed.")
    else:
        await ctx.send("This action requires elevated privileges. Nice try tho.")


@register_command("pinsetid")
@needs_contributor
async def on_set(message: discord.Message, message_content: str):
    save_pin_roles({int(x) for x in message_content[4:].split(" ")})


@slash.slash(name="pinsetid",
             description="Gives a role permission to pin messages. Uses the role's ID. Requires the @Contributor role.",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                     name="roleid",
                     description="The ID of role that you want to add to the approved role list.",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_set(ctx: discord_slash.SlashContext, roleid: str):
    if await is_contributor(ctx.author):
        add_pin_roles(int(roleid))
        await ctx.send("Pin permission granted.")
    else:
        await ctx.send("This action requires elevated privileges. Nice try tho.")

@slash.slash(name="pinremoveid",
             description="Removes a role's permission to pin messages. Uses the role's ID. Requires the @Contributor role.",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                     name="roleid",
                     description="The ID of role that you want to remove from the approved role list.",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_remove(ctx: discord_slash.SlashContext, roleid: str):
    if await is_contributor(ctx.author):
        remove_pin_roles(int(roleid))
        await ctx.send("Pin permission removed.")
    else:
        await ctx.send("This action requires elevated privileges. Nice try tho.")


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
                 discord_slash.utils.manage_commands.create_option(
                     name="channel",
                     description="The channel you want to block.",
                     option_type=7,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_channelm(ctx: discord_slash.SlashContext, channel: discord.TextChannel):
    if await is_contributor(ctx.author):
        add_invisible_channels(channel.id)
        await ctx.send("Added channel to the block list.")
    else:
        await ctx.send("This action requires elevated privileges. Nice try tho.")

@slash.slash(name="channelunblock",
             description="Makes an invisible channel visible again to the bot. Requires the @Contributor role.",
             options=[
                 discord_slash.utils.manage_commands.create_option(
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
        await ctx.send("This action requires elevated privileges. Nice try tho.")


@slash.slash(name="channelidblock",
             description="Makes a channel invisible to the bot. Uses the channel's ID. Requires the @Contributor role.",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                     name="channelid",
                     description="The ID of the channel you want to block.",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_rm_channel(ctx: discord_slash.SlashContext, channelid: str):
    if await is_contributor(ctx.author):
        add_invisible_channels(int(channelid))
        await ctx.send("Added channel to the block list.")
    else:
        await ctx.send("This action requires elevated privileges. Nice try tho.")

@slash.slash(name="channelidunblock",
             description="Makes an invisible channel visible again to the bot, uses ID. Requires the @Contributor role.",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                     name="channelid",
                     description="The id of the channel you want to unblock.",
                     option_type=7,
                     required=True
                 )
             ], guild_ids=slash_command_guilds)
async def on_slash_id_rm_channel(ctx: discord_slash.SlashContext, channelid: str):
    if await is_contributor(ctx.author):
        remove_invisible_channels(int(channelid))
        await ctx.send("Removed channel from the block list.")
    else:
        await ctx.send("This action requires elevated privileges. Nice try tho.")


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
                 discord_slash.utils.manage_commands.create_option(
                     name="video",
                     description="A link to the original stream.",
                     option_type=3,
                     required=True
                 ),
                 discord_slash.utils.manage_commands.create_option(
                     name="clipreason",
                     description="A reason for clipping and additional comments.",
                     option_type=3,
                     required=True
                 ),
                 discord_slash.utils.manage_commands.create_option(
                     name="timestamp",
                     description="A timestamp where the clip begins.",
                     option_type=3,
                     required=False
                 )
             ],
             guild_ids=slash_command_guilds)
async def on_slash_clip(ctx: discord_slash.SlashContext, video: str, timestamp="none", clipreason=None):
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
async def on_slash_oniichan(ctx: discord_slash.SlashContext):
    if ctx.channel.is_nsfw():
        await ctx.send(onii_chan)
    else:
        await ctx.send("oi what you tryna do")
    if ctx.guild.voice_client.channel == ctx.author.voice.channel:
        with open(tts(onii_chan)) as f:
            ctx.guild.voice_client.play(discord.FFmpegPCMAudio(f, pipe=True))
        while (ctx.guild.voice_client is not None) and ctx.guild.voice_client.is_playing():
            await asyncio.sleep(1)
        os.remove(f.name)

@register_command("bean")
async def on_bean(message: discord.Message, message_content: str):
    await message.channel.send(f"{message_content[5:]} has been beaned")

@slash.slash(name="bean",
             description="Beans a user.",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                     name="user",
                     description="The user you wish to bean.",
                     option_type=6,
                     required=True
                 )
             ],
             guild_ids=slash_command_guilds)
async def on_slash_bean(ctx: discord_slash.SlashContext, user: discord.User):
    await ctx.send(f"{user.mention} has been beaned.")


@slash.slash(name="faq", description="Puts the FAQ in the chat.",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                     name="faq_number",
                     description="The number of a spesfic question you want to send.",
                     option_type=4,
                     required=False
                 )
             ],
             guild_ids=slash_command_guilds)
async def on_slash_faq(ctx: discord_slash.SlashContext, faq_number: Optional[int] = None):
    faq_number = int(faq_number) if faq_number is not None else None
    embed = discord.Embed(title="Frequently Asked Questions")
    if not faq_number or faq_number < 1 or faq_number > len(FAQ):
        await ctx.send("That's not a valid FAQ number! I'll go on and send them all anyway.")
        for x in FAQ:
            embed.add_field(name=x[0], value=x[1])
    else:
        embed.add_field(name=FAQ[faq_number - 1][0], value=FAQ[faq_number - 1][1])    
    await ctx.send(embed=embed)

@slash.slash(name="join", description="Joins the voice channel.",
             guild_ids=slash_command_guilds)
async def on_slash_join(ctx: discord_slash.SlashContext):
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel.")
    else:
        await ctx.author.voice.channel.connect()
        await ctx.send("Joined the voice channel.")

@slash.slash(name="leave", description="Leaves the voice channel.",
             guild_ids=slash_command_guilds)
async def on_slash_leave(ctx: discord_slash.SlashContext):
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel.")
    elif ctx.guild.voice_client is None:
        await ctx.send("I'm not in a voice channel.")
    elif ctx.guild.voice_client.channel == ctx.author.voice.channel:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I'm not in that voice channel.")

@slash.slash(name="say", description="Says something in the voice chat.",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                        name="message",
                        description="The message you want to say.",
                        option_type=3,
                        required=True
                 ),
                ],
                guild_ids=slash_command_guilds
            )
async def on_slash_say(ctx: discord_slash.SlashContext, message: str):
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel.")
    elif ctx.guild.voice_client is None:
        await ctx.send("I'm not in a voice channel.")
    elif ctx.guild.voice_client.channel == ctx.author.voice.channel:
        with open(tts(message)) as f:
            ctx.guild.voice_client.play(discord.FFmpegPCMAudio(f, pipe=True))
        await ctx.send(f'said {message}')
        while (ctx.guild.voice_client is not None) and ctx.guild.voice_client.is_playing():
            await asyncio.sleep(1)
        os.remove(f.name)

@slash.slash(name="mchadvoice", description="Mchad live text in the voice channel.",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                        name="link",
                        description="Youtube link for the stream",
                        option_type=3,
                        required=True
                 )
             ],
             guild_ids=slash_command_guilds
        )
async def on_slash_mchadvoice(ctx: discord_slash.SlashContext, link: str):
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel.")
    elif ctx.guild.voice_client is None:
        await ctx.send("I'm not in a voice channel.")
    elif ctx.guild.voice_client.channel == ctx.author.voice.channel:
        await ctx.send("Starting mchad live")
        try:
            room = roomGeneratorbyID(video_id(link))
        except:
            await ctx.send("Mchad room not found")
            return
        for x in room:
            if ctx.guild.voice_client is None:
                return
            with open(tts(x)) as f:
                ctx.guild.voice_client.play(discord.FFmpegPCMAudio(f, pipe=True))
            while ctx.guild.voice_client is not None and ctx.guild.voice_client.is_playing():
                await asyncio.sleep(1)
            os.remove(f.name)

@slash.slash(name="livetlstream", description="LiveTL-style filtered chat",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                        name="link",
                        description="Youtube link for the stream",
                        option_type=3,
                        required=True
                 ),
                 discord_slash.utils.manage_commands.create_option(
                        name="filterlang",
                        description="Language you want to filter",
                        option_type=3,
                        required=False
                 )],
                 guild_ids=slash_command_guilds
        )
async def on_slash_livetlstream(ctx: discord_slash.SlashContext, link: str, filterlang: str = None):
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel.")
    elif ctx.guild.voice_client is None:
        await ctx.send("I'm not in a voice channel.")
    elif ctx.guild.voice_client.channel == ctx.author.voice.channel:
        id_index = -1
        if 'youtube.com' in link:
            id_index = link.find('v=') + 2
        elif 'youtu.be' in link:
            id_index = link.find('/') + 1
        if id_index == -1:
            await ctx.send("Invalid link")
            return
        await ctx.send("Starting livetl stream")
        try:
            room = pyt.create(video_id=link[id_index:id_index+11])
        except:
            await ctx.send("Not Live")
            return
        while room.is_alive():
            for x in room.get().sync_items():
                if ctx.guild.voice_client.channel is None:
                    return
                if (the_real_message := parseTranslation(x)) is not None:
                    if filterlang is None or filterlang.lower() in the_real_message[0].lower():
                        with open(tts(the_real_message[1])) as f:
                            ctx.guild.voice_client.play(discord.FFmpegPCMAudio(f, pipe=True))
                        while ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
                            await asyncio.sleep(1)
                        os.remove(f.name)
        return

@register_command(None)
async def on_default(message: discord.Message):
    await message.channel.send("syntax error")


@client.event
async def on_message(message: discord.Message):
    if (message.channel.id == nice_channel.id):
        if message.content.lower() not in ['', 'nice']:
            await wait_delete(message)
        return    
    if len(yt_links := ytthings.get_youtube_links_from_list(ytthings.get_links_from_string(message.content))) > 0:
        yt_links = ytthings.convert_youtube_links_to_format(yt_links)
        if any(ytthings.get_channel_link_from_link(link) == 'https://www.youtube.com/c/OtakMoriTranslationsVTubers' for link in yt_links):
            await message.reply('otakmore is an arse just don\'t')
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
