import shelve


def setGuildId(guildID: int):
    with shelve.open("guilddata") as db:
        db["ID"] = guildID


def getGuildId() -> int | None:
    with shelve.open("guilddata") as db:
        if not db["ID"]:
            return None
        else:
            guild_id = db["ID"]
            return guild_id
