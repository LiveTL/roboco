from typing import Optional


commands = {
    "queryc": [],
    "query": [],
    "forcopy": [],
    "pingset": [],
    "set": [],
    "channelm": [],
    "channel": [],
    "clip": [],
    "onii-chan": [],
    "bean": [],
    "help": [],
    None: [],
}

clip_requester_roles = [
    "contributor",
    "clipper",
    "regular",
    "server booster",
    "donator",
    "sponsor",
]

def command_starts_with(command: str) -> Optional[str]:
    for possible in commands:
        if command.startswith(possible):
            return possible


def register_command(command: Optional[str]):
    def wrapper(func):
        async def inner(**kwargs):
            try:
                return await func(**kwargs)
            except TypeError:
                return func(**kwargs)

        commands[command].append(inner)
        return inner

    return wrapper


def needs_contributor(func):
    async def inner(*args, **kwargs):
        if await is_contributor(kwargs["message"].author):
            return await func(*args, **kwargs)
        else:
            await kwargs["message"].channel.send("nice try")

    return inner

def needs_clip_requester(func):
    async def inner(*args, **kwargs):
        if await is_clip_requester(kwargs["message"].author):
            return await func(*args, **kwargs)
        else:
            await kwargs["message"].channel.send("Sorry, you can't request a clip")
    return inner

async def is_clip_requester(user):
    return any(x.name.lower() in clip_requester_roles for x in user.roles)

async def is_contributor(user):
    return any(x.name.lower() == "contributor" for x in user.roles)