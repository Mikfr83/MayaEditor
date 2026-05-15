"""Jedi-based code model for Python source files."""

from jedi import Script


class PythonCodeMode:
    """Wraps a jedi.Script to provide code-intelligence data for a Python file."""

    def __init__(self, filename: str) -> None:
        """Analyse the given file with jedi.

        Parameters
        ----------
        filename : str
            Path to the Python source file.
        """
        self.filename = filename
        with open(filename) as source:
            self.source = source.read()
        self.script = Script(self.source, path=filename)
        self.defs = self.script.goto_definitions()
        self.sigs = self.script.call_signatures()
        self.names = self.script.get_names()

    def set_script(self, fname: str) -> None:
        """Placeholder for re-loading the script on a different file."""
        pass
