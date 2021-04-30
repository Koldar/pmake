import logging
import os
import shutil
import unittest
from typing import Callable

import pmakeup as pm

from io import StringIO
from unittest.mock import patch


class MyTestCase(unittest.TestCase):

    def assertStdout(self, expected: Callable[[str], bool], do: Callable[[], None]):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            do()
            self.assertTrue(expected(fake_out.getvalue().strip()))

    def assertStdoutEquals(self, expected, do: Callable[[], None]):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            do()
            self.assertEqual(fake_out.getvalue().strip(), expected)

    def assertStdoutContains(self, expected, do: Callable[[], None]):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            do()
            self.assertTrue(fake_out.getvalue().strip() in expected)

    def assertStderrEquals(self, expected, do: Callable[[], None]):
        with patch("sys.stderr", new=StringIO()) as fake_err:
            do()
            self.assertEqual(fake_err.getvalue().strip(), expected)

    def test_is_git_repo_clean(self):
        from git import Repo

        repo = Repo(os.path.curdir, search_parent_directories=True)
        expected = not repo.is_dirty()
        model = pm.PMakeupModel()
        model.input_string = """
            echo(is_git_repo_clean())
        """
        self.assertStdoutEquals(f"{expected}", lambda: model.manage_pmakefile())

    def skipped_test_git_log(self):
        expected = """hash=e2dd71820a12d6a708a0b732379bc53b027c21d1, author=Massimo Bono, mail=massimobono1@gmail.com, date=2021-02-24 14:28:33+01:00, title=work started on git log, description=start on developing the test
now it is a good time to write a description

ok?
 * hash=3fb9879058bf8e93340d5f47e5d6693a3cf5fc08, author=Massimo Bono, mail=massimobono1@gmail.com, date=2021-02-24 14:05:39+01:00, title=git repo clean, description= * hash=318fe18ee70dfa90af2ba35d06a0bc319b02301b, author=Massimo Bono, mail=massimobono1@gmail.com, date=2021-02-24 13:52:30+01:00, title=test, description="""

        model = pm.PMakeupModel()
        model.input_string = """
            log = list(git_log(cwd(), "e2dd71820a12d6a708a0b732379bc53b027c21d1~~~", "e2dd71820a12d6a708a0b732379bc53b027c21d1"))
            echo(len(log))
            echo(' * '.join(map(str, log)))
        """
        self.assertStdoutEquals(f"3\n{expected}", lambda: model.manage_pmakefile())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
