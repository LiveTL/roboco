# roboco

my pinbot brings all the boys to the yard

and they're like, it's better than yours

damn right, it's better than yours

## Usage

put a `[]` in `channels.txt` and `roles.txt`

put your bot's client secret in `clientsecret.txt`

put your pin channel id in `kalm_moments` in `on_ready`

run `roboco.py`

## Nice Channel

set nice channel in the nice_channel variable
the bot will delete any message that isn't either empty or 'nice'

## Pinning

whoever has the role that is able to pin is able to pin

react with the pin emoji (📌)

## Commmands

default prefix: `.rbc`

`channel`(contributor): set blacklisted channels with ids seperated by spaces

`channelm`(contributor): set blacklisted channels with mentions

`clip`(regular, clipper, contributor, donator, booster, sponsor): send request to clip video

`bean`: bean a user

`forcopy`: get role ids that are able to ping, for copying into set

`help`: get help

`pingset`(contributor): same as set but with role mentions instead of role ids

`query`: see list of roles that are able to ping

`queryc`: see list of blacklisted channels

`set`(contributor): set roles that are able to ping, with ids, seperated by spaces
