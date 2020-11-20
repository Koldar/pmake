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

    def test_execute_and_forget(self):
        model = PMakeModel()
        model.input_string = """
            echo(execute_and_forget("echo hello"))
        """
        self.assertStdoutEquals("0", lambda: model.manage_pmakefile())

    def test_execute_stdout_on_screen(self):
        model = PMakeModel()
        model.input_string = """
            execute_stdout_on_screen(["echo hello > temp.txt"])
            echo(read_file_content("temp.txt"))
            remove_file("temp.txt")
        """
        self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_execute_return_stdout(self):
        model = PMakeModel()
        model.input_string = """
            echo(execute_return_stdout("echo hello")[1])
        """
        self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_admin_execute_and_forget(self):
        if os.name == "posix":
            model = PMakeModel()
            model.input_string = """
                password = read_file_content("PASSWORD")
                echo(execute_admin_with_password_fire_and_forget(["echo hello"], password))
            """
            self.assertStdoutEquals("0", lambda: model.manage_pmakefile())

    def test_admin_execute_stdout_on_screen(self):
        if os.name == "posix":
            model = PMakeModel()
            model.input_string = """
                password = read_file_content("PASSWORD")
                execute_admin_with_password_stdout_on_screen(["echo hello > temp.txt"], password)
                echo(read_file_content("temp.txt"))
                remove_file("temp.txt")
            """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_execute_admin_with_password_return_stdout(self):
        if os.name == "posix":
            model = PMakeModel()
            model.input_string = """
                password = read_file_content("PASSWORD")
                echo(execute_admin_with_password_return_stdout(["echo hello"], password)[1])
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

    def test_get_latest_version_in_folder_01(self):
        model = PMakeModel()
        model.input_string = """
            make_directories("temp")
            oldcwd = cd("temp")
            create_empty_file("awesome-1.0.0")
            create_empty_file("awesome-1.0.1")
            create_empty_file("awesome-1.10.0")
            create_empty_file("awesome-2.0.1")
            create_empty_file("awesome-1.8.1")
            latest_version, file_list = get_latest_version_in_folder() 
            echo(latest_version)
            echo(len(file_list))
            echo(os.path.basename(file_list[0]))
            cd(oldcwd)
        """
        self.assertStdoutEquals("2.0.1\n1\nawesome-2.0.1", lambda: model.manage_pmakefile())

    def test_get_latest_version_in_folder_02(self):
        model = PMakeModel()
        model.input_string = """
            make_directories("temp")
            oldcwd = cd("temp")
            create_empty_file("awesome-1.0.0")
            create_empty_file("awesome-1.0.1")
            create_empty_file("awesome-1.10.0")
            create_empty_file("awesome-2.0.1")
            create_empty_file("awesome-1.8.1")
            create_empty_file("awesome2-2.0.1")
            latest_version, file_list = get_latest_version_in_folder(version_fetcher=semantic_version_2_only_core)
            file_list = sorted(file_list) 
            echo(latest_version)
            echo(len(file_list))
            echo(os.path.basename(file_list[0]))
            echo(os.path.basename(file_list[1]))
            cd(oldcwd)
        """
        self.assertStdoutEquals("2.0.1\n2\nawesome-2.0.1\nawesome2-2.0.1", lambda: model.manage_pmakefile())

    def test_is_program_installed(self):
        model = PMakeModel()
        model.input_string = """
            echo(is_program_installed("echo"))
            echo(is_program_installed("opasdfhiovsefuhawzxcvsdvbjkfawfhsd"))
        """
        self.assertStdoutEquals("True\nFalse", lambda: model.manage_pmakefile())

    def test_convert_table_01(self):
        model = PMakeModel()

        table = "" \
            + "NAME    SURNAME" + "\\n" \
            + "Mario   Rossi" + "\\n" \
            + "Paolo   Bianchi" + "\\n" \
            + "Carlo   Verdi" + "\\n"

        model.input_string = f"""
            table = convert_table("{table}")
            echo(table[0][0])
            echo(table[0][1])
            echo(table[1][0])
            echo(table[1][1])
            echo(table[2][0])
            echo(table[2][1])
            echo(table[3][0])
            echo(table[3][1])
        """
        self.assertStdoutEquals("NAME\nSURNAME\nMario\nRossi\nPaolo\nBianchi\nCarlo\nVerdi", lambda: model.manage_pmakefile())

    def test_convert_table_02(self):
        model = PMakeModel()

        table = "" \
            + "NAME    SURNAME" + "\\n" \
            + "Ma io   Rossi" + "\\n" \
            + "Paolo   Bian hi" + "\\n" \
            + "C rlo   Verdi" + "\\n"

        model.input_string = f"""
            table = convert_table("{table}")
            echo(table[0][0])
            echo(table[0][1])
            echo(table[1][0])
            echo(table[1][1])
            echo(table[2][0])
            echo(table[2][1])
            echo(table[3][0])
            echo(table[3][1])
        """
        self.assertStdoutEquals("NAME\nSURNAME\nMa io\nRossi\nPaolo\nBian hi\nC rlo\nVerdi", lambda: model.manage_pmakefile())

    def test_convert_table_03(self):
        model = PMakeModel()

        table = "" \
            + "NAME    SURNAME" + "\\n" \
            + "Ma ioli Rossi" + "\\n" \
            + "Paolo   Bian hi" + "\\n" \
            + "C rlo   Verdi" + "\\n"

        model.input_string = f"""
            table = convert_table("{table}")
            echo(table[0][0])
            echo(table[0][1])
            echo(table[1][0])
            echo(table[1][1])
            echo(table[2][0])
            echo(table[2][1])
            echo(table[3][0])
            echo(table[3][1])
        """
        self.assertStdoutEquals("NAME\nSURNAME\nMa ioli\nRossi\nPaolo\nBian hi\nC rlo\nVerdi", lambda: model.manage_pmakefile())

    def test_convert_table_04(self):
        model = PMakeModel()

        table = "" \
            + 'Port         Type              Board Name  FQBN            Core       ' + "\\n" \
            + '/dev/ttyACM0 Serial Port (USB) Arduino Uno arduino:avr:uno arduino:avr' + "\\n"

        model.input_string = f"""
            table = convert_table("{table}")
            echo(table[0][0])
            echo(table[0][1])
            echo(table[0][2])
            echo(table[0][3])
            echo(table[0][4])
            echo(table[1][0])
            echo(table[1][1])
            echo(table[1][2])
            echo(table[1][3])
            echo(table[1][4])
        """
        self.assertStdoutEquals("Port\nType\nBoard Name\nFQBN\nCore\n/dev/ttyACM0\nSerial Port (USB)\nArduino Uno\narduino:avr:uno\narduino:avr",
                                lambda: model.manage_pmakefile())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
