from typing import Optional


commands = {
    "queryc": [],
    "query": [],
    "forcopy": [],
    "pingset": [],
    "set": [],
    "channelm": [],
    "channel": [],
    None: [],
}


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
