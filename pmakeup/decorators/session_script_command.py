import logging


def add_command():
    def decorator(func):
        def decorator_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        name = func.__name__
        logging.debug("adding function \"{name}\"")
        if name in add_command.call_dictionary:
            raise ValueError(f"The key \"{name}\" is already present as a sessions script command! Rename the entry")
        if name not in add_command.call_dictionary:
            add_command.call_dictionary[name] = []
        add_command.call_dictionary[name].append(func)

        return decorator_wrapper

    if not hasattr(add_command, "call_dictionary"):
        add_command.call_dictionary = {}
    return decorator
