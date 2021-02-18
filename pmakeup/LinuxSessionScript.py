from pmakeup import PMakeupModel
from pmakeup.SessionScript import SessionScript


class LinuxSessionScript(SessionScript):

    def test_linux(self, string: str):
        """
        Test if linux commands is loaded
        :param string: the string to echo'ed
        """
        self.echo(string)
