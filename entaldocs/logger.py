from datetime import datetime

from rich import print


class Logger:
    """A class to log messages to the console."""

    def __init__(self, name: str, with_time: bool = True):
        """Initialize the Logger.

        Parameters
        ----------
        name : str
            The name of the logger.
        with_time : bool, optional
            Whether to include the time in the log messages, by default True.
        """
        self.name = name
        self.with_time = with_time

    def now(self):
        """Get the current time.

        Returns:
        --------
        str
            The current time.
        """
        return datetime.now().strftime("%H:%M:%S")

    @property
    def prefix(self):
        """Get the prefix for the log messages.

        The prefix includes the name of the logger and the current time.

        Returns:
        --------
        str
            The prefix.
        """
        prefix = ""
        if self.name:
            prefix += f"{self.name}"
            if self.with_time:
                prefix += f" | {self.now()}"
        else:
            prefix += self.now()
        if prefix:
            return f"[grey50 bold]\[{prefix}][/grey50 bold] "
        return prefix

    def prompt(self, message: str, default: str = None) -> str:
        """Prompt the user for a value.

        Parameters
        ----------
        message : str
            The message to prompt the user with.
        default : str, optional
            The default value, by default None.

        Returns:
        --------
        str
            The value entered by the user.
        """
        text = (
            f"{self.prefix}{message} [{default}]"
            if default
            else f"{self.prefix}{message}"
        )
        print(text, end="")
        return input(": ").strip() or default

    def confirm(self, message: str) -> bool:
        """Confirm a message with the user.

        Parameters
        ----------
        message : str
            The message to confirm.

        Returns:
        --------
        bool
            Whether the user confirmed the message.
        """
        return self.prompt(f"{message} (y/N)", "N").lower() == "y"

    def abort(self, message: str):
        """Abort the program with a message.

        Parameters
        ----------
        message : str
            The message to print before aborting.
        """
        print(f"{self.prefix}[red]{message}[/red]")
        exit(1)

    def success(self, message: str):
        """Print a success message.

        Parameters
        ----------
        message : str
            The message to print.
        """
        print(f"{self.prefix}[green]{message}[/green]")

    def warning(self, message: str):
        """Print a warning message.

        Parameters
        ----------
        message : str
            The message to print.
        """
        print(f"{self.prefix}[yellow]{message}[/yellow]")

    def info(self, message: str):
        """Print an info message.

        Parameters
        ----------
        message : str
            The message to print.
        """
        print(f"{self.prefix}[blue]{message}[/blue]")

    def clear_line(self):
        """Clear the current line."""
        import shutil

        cols = shutil.get_terminal_size().columns
        print(" " * cols, end="\r")
