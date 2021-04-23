import logging
from typing import Iterable

import colorama

import pmakeup as pm


class LoggingPMakeupPlugin(pm.AbstractPmakeupPlugin):

    def __init__(self, model: "pm.PMakeupModel"):
        super().__init__(model)
        """
        Model referencing this object
        """
        self._foreground_mapping = {
            "RED": colorama.Fore.RED,
            "GREEN": colorama.Fore.GREEN,
            "YELLOW": colorama.Fore.YELLOW,
            "BLUE": colorama.Fore.BLUE,
            "MAGENTA": colorama.Fore.MAGENTA,
            "CYAN": colorama.Fore.CYAN,
            "WHITE": colorama.Fore.WHITE,
        }
        """
        If you need to color stdout, the foreground mapping
        """
        self._background_mapping = {
            "RED": colorama.Back.RED,
            "GREEN": colorama.Back.GREEN,
            "YELLOW": colorama.Back.YELLOW,
            "BLUE": colorama.Back.BLUE,
            "MAGENTA": colorama.Back.MAGENTA,
            "CYAN": colorama.Back.CYAN,
            "WHITE": colorama.Back.WHITE,
        }
        """
        If you need to color stdout, the background mapping
        """

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    def _color_str(self, message: str, foreground: str = None, background: str = None) -> str:
        """
        Color a string

        :param message: string involved
        :param foreground: foreground color of the string. Accepted values: RED, GREEN, YELLOW, BLUE, MAGENT, CYAN, WHITE
        :param background: background color of the string. Accepted values: RED, GREEN, YELLOW, BLUE, MAGENT, CYAN, WHITE
        :return: colored string
        """
        result = ""
        should_reset = False
        if foreground is not None:
            result += str(self._foreground_mapping[foreground.upper()])
            should_reset = True
        if background is not None:
            result += str(self._background_mapping[background.upper()])
            should_reset = True
        result += str(message)
        if should_reset:
            result += colorama.Style.RESET_ALL

        return result

    @pm.register_command.add("logging")
    def info(self, message: str):
        """
        Log a message using 'INFO' level

        :param message: the message to log
        """
        logging.info(message)

    @pm.register_command.add("logging")
    def critical(self, message: str):
        """
        Log a message using 'CRITICAL' level

        :param message: the message to log
        """
        logging.critical(message)

    @pm.register_command.add("logging")
    def debug(self, message: str):
        """
        Log a message using 'DEBUG' level

        :param message: the message to log
        """
        logging.debug(message)

    @pm.register_command.add("logging")
    def echo(self, message: str, foreground: str = None, background: str = None):
        """
        Print a message on the screen

        :param message: the message to print out
        :param foreground: foreground color of the string. Accepted values: RED, GREEN, YELLOW, BLUE, MAGENT, CYAN, WHITE
        :param background: background color of the string. Accepted values: RED, GREEN, YELLOW, BLUE, MAGENT, CYAN, WHITE
        """

        self._log_command(f"""echo \"{message}\"""")
        print(self._color_str(message, foreground, background))

    @pm.register_command.add("logging")
    def echo_variables(self, foreground: str = None, background: str = None):
        """
        Echo all the variables defined in "variables"

        :param foreground: the foregruodn color
        :param background: the background color
        """
        for k, v in self.get_shared_variables().items():
            self.echo(f"{k} = {v}", foreground=foreground, background=background)

    @pm.register_command.add("logging")
    def print_blue(self, message: str):
        """
        Print a blue message

        :param message: message to print
        """
        self.echo(message, foreground="BLUE")

    @pm.register_command.add("logging")
    def print_red(self, message: str):
        """
        Print a red message

        :param message: message to print
        """
        self.echo(message, foreground="RED")

    @pm.register_command.add("logging")
    def print_yellow(self, message: str):
        """
        Print a blue message

        :param message: message to print
        """
        self.echo(message, foreground="YELLOW")

    @pm.register_command.add("logging")
    def print_cyan(self, message: str):
        """
        Print a blue message

        :param message: message to print
        """
        self.echo(message, foreground="CYAN")


LoggingPMakeupPlugin.autoregister()
