from rich import print


class Logger:
    """A class to log messages to the console."""

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
        text = f"{message} [{default}]" if default else message
        return input(text).strip() or default

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
        print(f"[red]{message}[/red]")
        exit(1)

    def success(self, message: str):
        """Print a success message.

        Parameters
        ----------
        message : str
            The message to print.
        """
        print(f"[green]{message}[/green]")

    def warning(self, message: str):
        """Print a warning message.

        Parameters
        ----------
        message : str
            The message to print.
        """
        print(f"[yellow]{message}[/yellow]")
