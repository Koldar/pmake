import logging
import os
import shutil
import unittest
from typing import Callable

from pmake.PMakeModel import PMakeModel
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

    def test_onWindows(self):
        model = PMakeModel()
        model.input_string = """
        echo(on_windows())
        """
        self.assertStdoutEquals("True" if os.name == "nt" else "False", lambda : model.manage_pmakefile())

    def test_onLinux(self):
        model = PMakeModel()
        model.input_string = """
        echo(on_windows())
        """
        self.assertStdoutEquals("False" if os.name == "posix" else "True", lambda : model.manage_pmakefile())

    def test_echo_01(self):
        model = PMakeModel()
        model.input_string = """
        echo("Hello world!")
        """
        self.assertStdoutEquals("Hello world!", lambda : model.manage_pmakefile())

    def test_echo_02(self):
        model = PMakeModel()
        model.input_string = """
        x = 3
        echo(f"Hello {x}!")
        """
        self.assertStdoutEquals("Hello 3!", lambda : model.manage_pmakefile())

    def test_create_empty_file(self):
        model = PMakeModel()
        model.input_string = """
        create_empty_file(f"Hello")
        """
        model.manage_pmakefile()
        self.assertTrue(os.path.exists("Hello"))
        os.unlink("Hello")

    def test_is_file_exists_01(self):
        model = PMakeModel()
        model.input_string = """
                create_empty_file(f"Hello")
                echo(is_file_exists("Hello"))
                """
        self.assertStdoutEquals("True", lambda : model.manage_pmakefile())
        os.unlink("Hello")

    def test_is_file_exists_02(self):
        model = PMakeModel()
        model.input_string = """
                echo(is_file_exists("Hellosdfgdhfg"))
                """
        self.assertStdoutEquals("False", lambda : model.manage_pmakefile())

    def test_is_file_empty(self):
        model = PMakeModel()
        model.input_string = """
            create_empty_file(f"Hello")
            echo(is_file_empty("Hello"))
            """
        self.assertStdoutEquals("True", lambda: model.manage_pmakefile())
        os.unlink("Hello")

    def test_write_file(self):
        model = PMakeModel()
        model.input_string = """
            write_file(f"Hello", "5")
            echo(read_file_content("Hello"))
            """
        self.assertStdoutEquals("5", lambda: model.manage_pmakefile())
        os.unlink("Hello")

    def test_read_lines(self):
        model = PMakeModel()
        model.input_string = """
            write_lines(f"Hello", ["5", "6", "7"])
            echo(', '.join(read_lines("Hello")))
            """
        self.assertStdoutEquals("5, 6, 7", lambda: model.manage_pmakefile())
        os.unlink("Hello")

    def test_append_string_at_end_of_file(self):
        model = PMakeModel()
        model.input_string = """
            remove_file("Hello")
            append_string_at_end_of_file("Hello", 5)
            append_string_at_end_of_file("Hello", 6)
            append_string_at_end_of_file("Hello", 7)
            echo(', '.join(read_lines("Hello")))
            """
        self.assertStdoutEquals("5, 6, 7", lambda: model.manage_pmakefile())
        os.unlink("Hello")

    def test_copy_file(self):
        model = PMakeModel()
        model.input_string = """
            write_file("Hello", "test")
            copy_file("Hello", "Hello2")
            echo(read_file_content("Hello2"))
        """
        self.assertStdoutEquals("test", lambda: model.manage_pmakefile())
        os.unlink("Hello")
        os.unlink("Hello2")

    def test_download_url(self):
        model = PMakeModel()
        model.input_string = """
            download_url("https://www.google.com", "Hello.html")
            echo(is_file_non_empty("Hello.html"))
        """
        self.assertStdoutEquals("True", lambda: model.manage_pmakefile())
        os.unlink("Hello.html")

    def test_remove_tree(self):
        model = PMakeModel()
        model.input_string = """
            make_directories("temp/foo/bar")
            make_directories("temp/foo2/bar")
            make_directories("temp/foo2/baz")
            create_empty_file("temp/foo/bar/empty")
            create_empty_file("temp/foo2/bar/empty1")
            create_empty_file("temp/foo2/bar/empty2")
            remove_tree("temp")
            echo(is_directory_exists("temp"))
        """
        self.assertStdoutEquals("False", lambda: model.manage_pmakefile())

    def test_remove_files_that_basename(self):
        model = PMakeModel()
        model.input_string = """
            make_directories("temp/foo/bar")
            make_directories("temp/foo2/bar")
            make_directories("temp/foo2/baz")
            create_empty_file("temp/foo/bar/empty.txt")
            create_empty_file("temp/foo2/bar/empty1.dat")
            create_empty_file("temp/foo2/bar/empty2.txt")
            remove_files_that_basename("temp", r".txt$")
            echo(is_file_exists("temp/foo2/bar/empty1.dat"))
        """
        self.assertStdoutEquals("True", lambda: model.manage_pmakefile())
        shutil.rmtree("temp", ignore_errors=True)

    def test_copy_files_that_basename(self):
        model = PMakeModel()
        model.input_string = """
            make_directories("temp/foo/bar")
            make_directories("temp/foo2/bar")
            make_directories("temp/foo2/baz")
            create_empty_file("temp/foo/bar/empty.txt")
            create_empty_file("temp/foo2/bar/empty1.dat")
            create_empty_file("temp/foo2/bar/empty2.txt")
            copy_files_that_basename("temp", "temp2", r".txt$")
            echo(is_file_exists("temp2/foo2/bar/empty2.txt"))
            echo(not is_file_exists("temp2/foo2/bar/empty1.dat"))
        """
        self.assertStdoutEquals("True\nTrue", lambda: model.manage_pmakefile())
        shutil.rmtree("temp", ignore_errors=True)
        shutil.rmtree("temp2", ignore_errors=True)

    def test_move_file(self):
        model = PMakeModel()
        model.input_string = """
                create_empty_file("empty.txt")
                move_file("empty.txt", "foo.txt")
                echo(not is_file_exists("empty.txt"))
                echo(is_file_exists("foo.txt"))
            """
        self.assertStdoutEquals("True\nTrue", lambda: model.manage_pmakefile())
        os.unlink("foo.txt")

    def test_cd(self):
        model = PMakeModel()
        model.input_string = """
            create_empty_directory("temp")
            old_pwd = cwd()
            cd("temp")
            create_empty_file("empty.txt")
            cd(old_pwd)
            echo(is_file_exists("temp/empty.txt"))
        """
        self.assertStdoutEquals("True", lambda: model.manage_pmakefile())
        shutil.rmtree("temp")

    def test_admin_windows(self):
        if os.name == "nt":
            model = PMakeModel()
            model.input_string = """
                echo(exec_admin_stdout("echo hello"))
            """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_whoami(self):
        model = PMakeModel()
        model.input_string = """
            echo(current_user())
        """
        self.assertStdout(lambda stdout: len(stdout) > 0, lambda: model.manage_pmakefile())

    def test_copy_folder_content(self):
        model = PMakeModel()
        model.variable = [("foo", "bar")]
        model.input_string = """
            create_empty_directory("temp")
            old_pwd = cwd()
            cd("temp")
            create_empty_file("foo.txt")
            create_empty_file("bar.txt")
            create_empty_file("baz.txt")
            cd(old_pwd)
            create_empty_directory("temp2")
            
            copy_folder_content(
                folder="temp",
                destination="temp2",
            )
            if is_file_exists(os.path.join("temp2", "bar.txt")):
                echo("Hello")
            if not is_directory_exists(os.path.join("temp2", "temp")):
                echo("World")
        """
        self.assertStdoutEquals("Hello\nWorld", lambda: model.manage_pmakefile())
        shutil.rmtree("temp")
        shutil.rmtree("temp2")

    def test_variables_01(self):
        model = PMakeModel()
        model.variable = [("foo", "bar")]
        model.input_string = """
            echo(variables['foo'])
        """
        self.assertStdoutEquals("bar", lambda: model.manage_pmakefile())

    def test_variables_02(self):
        model = PMakeModel()
        model.variable = [("foo", "bar")]
        model.input_string = """
            echo(variables.foo)
        """
        self.assertStdoutEquals("bar", lambda: model.manage_pmakefile())

    def test_include(self):
        model = PMakeModel()
        model.input_string = """
            write_file("test-temp.py", "echo(\\"Hello\\")")
            include_file("test-temp.py")
            remove_file("test-temp.py")
        """
        self.assertStdoutEquals("Hello", lambda: model.manage_pmakefile())

    def test_commands(self):
        model = PMakeModel()
        model.input_string = """
            commands.echo("Hello world")
        """
        self.assertStdoutEquals("Hello world", lambda: model.manage_pmakefile())

    def test_execute_admin_with_password(self):
        if os.name == "posix":
            model = PMakeModel()
            model.input_string = """
                password = read_file_content("PASSWORD", trim_newlines=True)
                echo(execute_admin_with_password("echo hello", password))
            """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_cache_usage(self):
        model = PMakeModel()
        model.input_string = """
            if has_variable_in_cache("foo"):
                echo(get_variable_in_cache("foo"))
            else:
                set_variable_in_cache("foo", "bar")
                echo("not found")
        """
        self.assertStdoutEquals("not found", lambda: model.manage_pmakefile())
        self.assertStdoutEquals("bar", lambda: model.manage_pmakefile())

        os.unlink("pmake-cache.json")

    def test_is_program_installed(self):
        model = PMakeModel()
        model.input_string = """
            echo(is_program_installed("echo"))
            echo(is_program_installed("opasdfhiovsefuhawzxcvsdvbjkfawfhsd"))
        """
        self.assertStdoutEquals("True\nFalse", lambda: model.manage_pmakefile())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
