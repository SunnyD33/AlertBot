import shelve


# Set the Guild ID
def setGuildId(guildID: int):
    with shelve.open("guilddata") as db:
        db["ID"] = guildID


# Get the Guild ID
def getGuildId() -> int | None:
    with shelve.open("guilddata") as db:
        return db.get("ID", None)


def removeGuildID(guildID: int):
    with shelve.open("guilddata") as db:
        if "ID" in db:
            db["ID"] = None
            print("Guild ID has been removed.")
        else:
            print("No Guild ID found to remove.")


# Opt in to notifications
def opt_in(user_id: int):
    """
    Opt a user in for notifications. Ensures the operation occurs in a DM context.

    Args:
        user_id (int): The ID of the user opting in.
    """

    with shelve.open("guilddata") as db:
        if "user_notifications" not in db:
            db["user_notifications"] = {}
        notifications = db["user_notifications"]
        notifications[user_id] = True
        db["user_notifications"] = notifications
        print(f"User {user_id} has successfully opted in for notifications.")


# Opt out of notifications
def opt_out(user_id: int):
    """
    Opt a user out of notifications. Ensures the operation occurs in a DM context.

    Args:
        user_id (int): The ID of the user opting out.
    """

    with shelve.open("guilddata") as db:
        if "user_notifications" not in db:
            db["user_notifications"] = {}
        notifications = db["user_notifications"]
        notifications[user_id] = False
        db["user_notifications"] = notifications
        print(f"User {user_id} has successfully opted out of notifications.")


# Check user notification preference
def is_opted_in(user_id: int) -> bool:
    with shelve.open("guilddata") as db:
        notifications = db.get("user_notifications", {})
        return notifications.get(user_id, False)
