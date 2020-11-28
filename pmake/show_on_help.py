def add_command(name: str):
    def decorator(func):
        def decorator_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        if name not in add_command.call_dictionary:
            add_command.call_dictionary[name] = []
        add_command.call_dictionary[name].append(func)

        return decorator_wrapper

    if not hasattr(add_command, "call_dictionary"):
        add_command.call_dictionary = {}
    return decorator
