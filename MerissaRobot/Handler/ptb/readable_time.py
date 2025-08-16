def get_readable_time(seconds: int) -> str:
    """
    Converts seconds to a human-readable format: days, hours, minutes, seconds.
    Example:
        93784 -> "1d, 2h:3m:4s"
    """
    seconds = int(seconds)
    time_list = []

    # Calculate days
    days, seconds = divmod(seconds, 86400)
    if days:
        time_list.append(f"{days}d")

    # Calculate hours
    hours, seconds = divmod(seconds, 3600)
    if hours:
        time_list.append(f"{hours}h")

    # Calculate minutes
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        time_list.append(f"{minutes}m")

    # Remaining seconds
    time_list.append(f"{seconds}s")

    # Join with ':' for hours/minutes/seconds and ', ' for days
    if "d" in time_list[0]:
        return time_list[0] + ", " + ":".join(time_list[1:])
    return ":".join(time_list)
