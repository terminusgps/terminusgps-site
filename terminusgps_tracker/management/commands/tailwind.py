import argparse
import json
import os
import subprocess

from django.core.management.base import BaseCommand, CommandError


def get_node_dependencies() -> list[str]:
    """
    Retrives a list of application dependencies from ``package.json``.

    Returns an empty list if ``package.json`` does not exist.

    :returns: A list of application dependencies as strings.
    :rtype: :py:obj:`list`

    """
    if not os.path.isfile("package.json"):
        return []

    with open("package.json", "r") as file:
        return json.load(file).get("devDependencies", {}).keys()


def node_package_installed(name: str) -> bool:
    """
    Checks whether or not a node package is installed.

    :param name: A npm package name.
    :type name: :py:obj:`str`
    :returns: Whether or not node package ``name`` is installed.
    :rtype: :py:obj:`bool`

    """
    return name in get_node_dependencies()


class Command(BaseCommand):
    help = "Builds and compiles tailwind classes in the project"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Adds subcommand arguments to the ``tailwind`` command.

        +-------------+-------------------------------------------------------------------+
        | Subcommand  | Action                                                            |
        +=============+===================================================================+
        | ``build``   | Builds the tailwind output file for production.                   |
        +-------------+-------------------------------------------------------------------+
        | ``install`` | Installs the tailwind compiler for the project.                   |
        +-------------+-------------------------------------------------------------------+
        | ``start``   | Starts the tailwind compiler. Must be canceled with ``<CTRL>-c``. |
        +-------------+-------------------------------------------------------------------+

        :param parser: An argument parser.
        :type parser: :py:obj:`argparse.ArgumentParser`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        subparsers = parser.add_subparsers(dest="subcommand")
        subparsers.add_parser("build", help="Build tailwind for production")
        subparsers.add_parser("install", help="Install tailwind")
        subparsers.add_parser("start", help="Start the tailwind compiler")

    def handle(self, *args, **options):
        """
        Handles command execution based on the provided subcommand.

        :raises CommandError: If the subcommand is invalid.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        try:
            command = self.generate_command(options["subcommand"])
            subprocess.run(command, check=True)
        except ValueError as e:
            raise CommandError(e)

    def generate_command(self, subcommand: str | None) -> list[str]:
        """
        Generates a tailwind command based on the provided subcommand.

        :returns: A command to be executed by :py:func:`subprocess.run`.
        :rtype: :py:obj:`list`

        """
        input, output = self.get_input_filepath(), self.get_output_filepath()
        base_command = ["npx", "@tailwindcss/cli", "-i", input, "-o", output]

        match subcommand:
            case "start":
                style = self.style.NOTICE
                message = "Starting tailwind compiler..."
                command = base_command + ["--watch"]
            case "build":
                style = self.style.NOTICE
                message = "Building tailwind for production..."
                command = base_command + ["--minify"]
            case "install":
                if not node_package_installed("tailwindcss"):
                    style = self.style.NOTICE
                    message = "Installing tailwind..."
                    command = [
                        "npm",
                        "install",
                        "-D",
                        "tailwindcss",
                        "@tailwindcss/cli",
                    ]
                else:
                    style = self.style.WARNING
                    message = "Tailwind is already installed, building for production instead..."
                    command = base_command + ["--minify"]
            case _:
                raise ValueError(f"Invalid subcommand '{subcommand}'.")
        self.stdout.write(style(message))
        return command

    def get_input_filepath(self) -> str:
        """Returns an input filepath for the tailwind compiler."""
        return "./src/static/terminusgps/css/input.css"

    def get_output_filepath(self) -> str:
        """Returns an output filepath for the tailwind compiler."""
        return "./src/static/terminusgps/css/output.css"
