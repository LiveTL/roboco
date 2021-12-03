from typing import Tuple, Union


langTokens = [['[', ']'], ['{', '}'], ['(', ')'], ['|', '|'], ['<', '>'], ['【', '】'], ['「', '」'], ['『', '』'], ['〚', '〛'], ['（', '）'], ['〈', '〉'], ['⁽', '₎']]
startLangTokens = [x[0] for x in langTokens]
tokenMap = {x[0]:x[1] for x in langTokens}

def parseTranslation(c) -> Union[Tuple[str, str], None]:
    message = c.message
    trimmed = message.strip()
    if len(trimmed) > 0:
        leftToken = trimmed[0] 
        if trimmed[0] in startLangTokens:
            rightToken = tokenMap[leftToken]
            rightTokenIndex = trimmed.find(rightToken)
            if rightTokenIndex != -1:
                lang = trimmed[1:rightTokenIndex]
                msg = trimmed[rightTokenIndex:].strip()
                if (msg[0] == '-' or msg[0] == ':'):
                    msg = msg[1:]
                return (lang, msg)
    return None