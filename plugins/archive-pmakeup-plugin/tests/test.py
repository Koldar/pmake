import unittest

from typing import Callable

from io import StringIO
from unittest.mock import patch

import pmakeup as pm
from pmakeup.main import configure_logging


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

    def test_archive(self):
        model = pm.PMakeupModel()
        model.log_level = "INFO"
        configure_logging(model.log_level)
        model.input_string = """
            make_directories("temp/foo/bar")
            make_directories("temp/foo2/bar")
            make_directories("temp/foo2/baz")
            create_empty_file("temp/foo/bar/empty.txt")
            create_empty_file("temp/foo2/bar/empty1.dat")
            create_empty_file("temp/foo2/bar/empty2.txt")
            zip_files(
                files=["temp/foo/bar/empty.txt", "temp/foo2/bar/empty1.dat", "temp/foo2/bar/empty2.txt"],
                base_dir="temp/",
                zip_name="text.zip",
                zip_format="zip",
                create_folder_in_zip_file=False,
            )

            echo(is_file_exists("text.zip"))
            echo(is_file_non_empty("text.zip"))

            remove_tree("temp")
            remove_file("text.zip")
        """
        self.assertStdoutEquals("True\nTrue", lambda: model.manage_pmakefile())

    def test_archive_02(self):
        model = pm.PMakeupModel()
        model.input_string = """
            make_directories("temp/foo/bar")
            make_directories("temp/foo2/bar")
            make_directories("temp/foo2/baz")
            create_empty_file("temp/foo/bar/empty.txt")
            create_empty_file("temp/foo2/bar/empty1.dat")
            create_empty_file("temp/foo2/bar/empty2.txt")
            zip_files(
                files=["temp/foo/bar/empty.txt", "temp/foo2/bar/empty1.dat", "temp/foo2/bar/empty2.txt"],
                zip_name="text.zip",
                zip_format="zip",
                create_folder_in_zip_file=True,
                folder_name_in_zip_file="qwerty",
            )

            echo(is_file_exists("text.zip"))
            echo(is_file_non_empty("text.zip"))

            remove_tree("temp")
            remove_file("text.zip")
        """
        self.assertStdoutEquals("True\nTrue", lambda: model.manage_pmakefile())

    def test_archive_01_autoregister(self):
        model = pm.PMakeupModel()

        model.input_string = """
            make_directories("temp/foo/bar")
            make_directories("temp/foo2/bar")
            make_directories("temp/foo2/baz")
            create_empty_file("temp/foo/bar/empty.txt")
            create_empty_file("temp/foo2/bar/empty1.dat")
            create_empty_file("temp/foo2/bar/empty2.txt")
            zip_files(
                files=["temp/foo/bar/empty.txt", "temp/foo2/bar/empty1.dat", "temp/foo2/bar/empty2.txt"],
                base_dir="temp/",
                zip_name="text.zip",
                zip_format="zip",
                create_folder_in_zip_file=False,
            )

            echo(is_file_exists("text.zip"))
            echo(is_file_non_empty("text.zip"))

            remove_tree("temp")
            remove_file("text.zip")
        """
        self.assertStdoutEquals("True\nTrue", lambda: model.manage_pmakefile())


if __name__ == '__main__':
    unittest.main()
