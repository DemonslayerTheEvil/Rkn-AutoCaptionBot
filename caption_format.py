def add_prefix_suffix(file_name, prefix=None, suffix=None):
    """
    Adds a prefix and/or suffix to the file name for caption formatting.

    :param file_name: The name of the file (media).
    :param prefix: (Optional) A prefix to add before the file name.
    :param suffix: (Optional) A suffix to add after the file name.
    :return: Formatted caption with prefix and suffix.
    """
    # Ensure file_name is a string and strip extra spaces
    file_name = str(file_name).strip()

    # Add prefix if provided, with a space if it's not empty
    if prefix:
        file_name = f"{prefix} {file_name}".strip()

    # Add suffix if provided, with a space before it
    if suffix:
        file_name += f" {suffix}".strip()

    return file_name
