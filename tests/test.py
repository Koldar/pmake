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

    def test_onWindows(self):
        model = pm.PMakeupModel()
        model.input_string = """
        echo(on_windows())
        """
        self.assertStdoutEquals("True" if os.name == "nt" else "False", lambda: model.manage_pmakefile())

    def test_onLinux(self):
        model = pm.PMakeupModel()
        model.input_string = """
        echo(on_windows())
        """
        self.assertStdoutEquals("False" if os.name == "posix" else "True", lambda : model.manage_pmakefile())

    def test_echo_01(self):
        model = pm.PMakeupModel()
        model.input_string = """
        echo("Hello world!")
        """
        self.assertStdoutEquals("Hello world!", lambda : model.manage_pmakefile())

    def test_echo_02(self):
        model = pm.PMakeupModel()
        model.input_string = """
        x = 3
        echo(f"Hello {x}!")
        """
        self.assertStdoutEquals("Hello 3!", lambda : model.manage_pmakefile())

    def test_create_empty_file(self):
        model = pm.PMakeupModel()
        model.input_string = """
        create_empty_file(f"Hello")
        """
        model.manage_pmakefile()
        self.assertTrue(os.path.exists("Hello"))
        os.unlink("Hello")

    def test_is_file_exists_01(self):
        model = pm.PMakeupModel()
        model.input_string = """
                create_empty_file(f"Hello")
                echo(is_file_exists("Hello"))
                """
        self.assertStdoutEquals("True", lambda : model.manage_pmakefile())
        os.unlink("Hello")

    def test_is_file_exists_02(self):
        model = pm.PMakeupModel()
        model.input_string = """
                echo(is_file_exists("Hellosdfgdhfg"))
                """
        self.assertStdoutEquals("False", lambda : model.manage_pmakefile())

    def test_is_file_empty(self):
        model = pm.PMakeupModel()
        model.input_string = """
            create_empty_file(f"Hello")
            echo(is_file_empty("Hello"))
            """
        self.assertStdoutEquals("True", lambda: model.manage_pmakefile())
        os.unlink("Hello")

    def test_write_file(self):
        model = pm.PMakeupModel()
        model.input_string = """
            write_file(f"Hello", "5")
            echo(read_file_content("Hello"))
            """
        self.assertStdoutEquals("5", lambda: model.manage_pmakefile())
        os.unlink("Hello")

    def test_read_lines(self):
        model = pm.PMakeupModel()
        model.input_string = """
            write_lines(f"Hello", ["5", "6", "7"])
            echo(', '.join(read_lines("Hello")))
            """
        self.assertStdoutEquals("5, 6, 7", lambda: model.manage_pmakefile())
        os.unlink("Hello")

    def test_append_string_at_end_of_file(self):
        model = pm.PMakeupModel()
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
        model = pm.PMakeupModel()
        model.input_string = """
            write_file("Hello", "test")
            copy_file("Hello", "Hello2")
            echo(read_file_content("Hello2"))
        """
        self.assertStdoutEquals("test", lambda: model.manage_pmakefile())
        os.unlink("Hello")
        os.unlink("Hello2")

    def test_download_url(self):
        model = pm.PMakeupModel()
        model.input_string = """
            download_url("https://www.google.com", "Hello.html")
            echo(is_file_non_empty("Hello.html"))
        """
        self.assertStdoutEquals("True", lambda: model.manage_pmakefile())
        os.unlink("Hello.html")

    def test_remove_tree(self):
        model = pm.PMakeupModel()
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
        model = pm.PMakeupModel()
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
        model = pm.PMakeupModel()
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
        model = pm.PMakeupModel()
        model.input_string = """
                create_empty_file("empty.txt")
                move_file("empty.txt", "foo.txt")
                echo(not is_file_exists("empty.txt"))
                echo(is_file_exists("foo.txt"))
            """
        self.assertStdoutEquals("True\nTrue", lambda: model.manage_pmakefile())
        os.unlink("foo.txt")

    def test_cd(self):
        model = pm.PMakeupModel()
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

    def test_fire_and_forget_windows(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                echo(execute_and_forget("echo hello > temp.txt"))
            """
            self.assertStdoutEquals("0", lambda: model.manage_pmakefile())

    def test_execute_run_in_background(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                s = datetime.datetime.now()
                execute_and_run_in_background("sleep 5000; echo hello > temp.txt")
                e = datetime.datetime.now()
                echo((e -s).seconds)
            """
            self.assertStdoutEquals("0", lambda: model.manage_pmakefile())

    def test_admin_fire_and_forget_windows(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                echo(execute_admin_and_forget("echo hello > temp.txt"))
            """
            self.assertStdoutEquals("0", lambda: model.manage_pmakefile())

    def test_execute_admin_and_run_in_background(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                s = datetime.datetime.now()
                execute_admin_and_run_in_background("sleep 5000; echo hello > temp.txt")
                e = datetime.datetime.now()
                echo((e -s).seconds)
            """
            self.assertStdoutEquals("0", lambda: model.manage_pmakefile())

    def test_execute_stdout_on_screen_windows(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                execute_stdout_on_screen("echo hello > temp.txt")
                echo(read_file_content("temp.txt"))
                remove_file("temp.txt")
            """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_admin_execute_stdout_on_screen_windows(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
               temp_file = get_temp_filepath()
               execute_admin_stdout_on_screen(f"echo hello > {temp_file}")
               echo(read_file_content(temp_file))
               remove_file(temp_file)
           """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_execute_return_stdout_windows(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                exit_core, v, _ = execute_return_stdout("echo hello")
                echo(v)
            """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_admin_execute_return_stdout_windows(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                exit_code, v, _ = execute_admin_return_stdout("echo hello")
                echo(v)
            """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_whoami(self):
        model = pm.PMakeupModel()
        model.input_string = """
            echo(current_user())
        """
        self.assertStdout(lambda stdout: len(stdout) > 0, lambda: model.manage_pmakefile())

    def test_copy_folder_content(self):
        model = pm.PMakeupModel()
        model.cli_variables = {"foo": "bar"}
        model.input_string = """
            create_empty_directory("temp_copy")
            old_pwd = cwd()
            cd("temp_copy")
            create_empty_file("foo.txt")
            create_empty_file("bar.txt")
            create_empty_file("baz.txt")
            cd(old_pwd)
            create_empty_directory("temp2_copy")
            
            copy_folder_content(
                folder="temp_copy",
                destination="temp2_copy",
            )
            if is_file_exists(os.path.join("temp2_copy", "bar.txt")):
                echo("Hello")
            if not is_directory_exists(os.path.join("temp2_copy", "temp_copy")):
                echo("World")
        """
        self.assertStdoutEquals("Hello\nWorld", lambda: model.manage_pmakefile())
        shutil.rmtree("temp_copy")
        shutil.rmtree("temp2_copy")

    def test_variables_01(self):
        model = pm.PMakeupModel()
        model.cli_variables = {"foo": "bar"}
        model.input_string = """
            echo(vars()['foo'])
        """
        self.assertStdoutEquals("bar", lambda: model.manage_pmakefile())

    def test_variables_02(self):
        model = pm.PMakeupModel()
        model.cli_variables = {"foo": "bar"}
        model.input_string = """
            echo(variables.foo)
        """
        self.assertStdoutEquals("bar", lambda: model.manage_pmakefile())

    def test_variables_03(self):
        model = pm.PMakeupModel()
        model.cli_variables = {"foo": "bar"}
        model.input_string = """
            echo(vars().foo)
        """
        self.assertStdoutEquals("bar", lambda: model.manage_pmakefile())

    def test_include(self):
        model = pm.PMakeupModel()
        model.input_string = """
            write_file("test-temp.py", "echo(\\"Hello\\")")
            include_file("test-temp.py")
            remove_file("test-temp.py")
        """
        self.assertStdoutEquals("Hello", lambda: model.manage_pmakefile())

    def test_commands(self):
        model = pm.PMakeupModel()
        model.input_string = """
            commands.echo("Hello world")
        """
        self.assertStdoutEquals("Hello world", lambda: model.manage_pmakefile())

    def test_execute_and_forget(self):
        model = pm.PMakeupModel()
        model.input_string = """
            echo(execute_and_forget("echo hello"))
        """
        self.assertStdoutEquals("0", lambda: model.manage_pmakefile())

    def test_execute_stdout_on_screen(self):
        if os.name == "posix":
            model = pm.PMakeupModel()
            model.input_string = """
                execute_stdout_on_screen(["echo hello > temp.txt"], cwd=cwd())
                echo(read_file_content("/tmp/temp.txt"))
                remove_file("/tmp/temp.txt")
            """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_execute_return_stdout(self):
        model = pm.PMakeupModel()
        model.input_string = """
            echo(execute_return_stdout("echo hello")[1])
        """
        self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_admin_execute_and_forget(self):
        if os.name == "posix":
            model = pm.PMakeupModel()
            model.input_string = """
                password = read_file_content("../PASSWORD")
                echo(execute_admin_with_password_fire_and_forget(["echo hello"], password))
            """
            self.assertStdoutEquals("0", lambda: model.manage_pmakefile())

    def test_admin_execute_stdout_on_screen(self):
        if os.name == "posix":
            model = pm.PMakeupModel()
            model.input_string = """
                password = read_file_content("../PASSWORD")
                execute_admin_with_password_stdout_on_screen(commands=["echo hello > /tmp/temp.txt"], password=password)
                echo(read_file_content("/tmp/temp.txt"))
                remove_file("/tmp/temp.txt")
            """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_execute_admin_with_password_return_stdout(self):
        if os.name == "posix":
            model = pm.PMakeupModel()
            model.input_string = """
                password = read_file_content("../PASSWORD")
                echo(execute_admin_with_password_return_stdout(["echo hello"], password)[1])
            """
            self.assertStdoutEquals("hello", lambda: model.manage_pmakefile())

    def test_has_processes(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                echo(is_process_running("winlogon.exe"))
                echo(is_process_running("asdrubalini.exe"))
            """
            self.assertStdoutEquals("True\nFalse", lambda: model.manage_pmakefile())
        elif os.name == "posix":
            model = pm.PMakeupModel()
            model.input_string = """
                echo(is_process_running("winlogon.exe"))
                echo(is_process_running("asdrubalini.exe"))
            """
            self.assertStdoutEquals("True\nFalse", lambda: model.manage_pmakefile())

    def kill_process(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                echo(is_process_running("iexplorer.exe"))
                echo(execute_and_forget("iexplorer.exe"))
                echo(is_process_running("iexplorer.exe"))
                echo(kill_process_by_name("iexplorer.exe"))
            """
            self.assertStdoutEquals("False\nTrue", lambda: model.manage_pmakefile())

    def test_cache_usage(self):
        model = pm.PMakeupModel()
        model.input_string = """
            if has_variable_in_cache("foo"):
                echo(get_variable_in_cache("foo"))
            else:
                set_variable_in_cache("foo", "bar")
                echo("not found")
        """
        self.assertStdoutEquals("not found", lambda: model.manage_pmakefile())
        self.assertStdoutEquals("bar", lambda: model.manage_pmakefile())

        os.unlink("pmakeup-cache.json")

    def test_get_absolute_file_till_root_01(self):
        model = pm.PMakeupModel()
        model.input_string = """
                    make_directories("temp1/temp2/temp3/temp4")
                    create_empty_file("temp1/awesome")
                    result = get_absolute_file_till_root("awesome", "temp1/temp2/temp3/temp4") 
                    echo("awesome" in result)
                    remove_tree("temp1")
                """
        self.assertStdoutEquals("True", lambda: model.manage_pmakefile())

    def test_get_absolute_file_till_root_02(self):
        model = pm.PMakeupModel()
        model.input_string = """
                    make_directories("temp1/temp2/temp3/temp4")
                    try: 
                        result = get_absolute_file_till_root("awesome", "temp1/temp2/temp3/temp4")
                        echo("awesome" in result)
                    except ValueError:
                        pass
                    finally:
                        remove_tree("temp1")
                """
        self.assertStdoutEquals("", lambda: model.manage_pmakefile())

    def test_get_absolute_file_till_root_03(self):
        model = pm.PMakeupModel()
        model.input_string = """
                    make_directories("temp1/temp2/awesome/temp4") 
                    try: 
                        result = get_absolute_file_till_root("awesome", "temp1/temp2/temp3/temp4")
                        echo("awesome" in result)
                    except ValueError:
                        pass
                    finally:
                        remove_tree("temp1")
                """
        self.assertStdoutEquals("", lambda: model.manage_pmakefile())

    def test_get_latest_version_in_folder_01(self):
        model = pm.PMakeupModel()
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
        model = pm.PMakeupModel()
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

    def test_is_program_installed_linux(self):
        if os.name == "posix":
            model = pm.PMakeupModel()
            model.input_string = """
                echo(is_program_installed("echo"))
                echo(is_program_installed("opasdfhiovsefuhawzxcvsdvbjkfawfhsd"))
            """
            self.assertStdoutEquals("True\nFalse", lambda: model.manage_pmakefile())

    def test_is_program_installed_windows(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                echo(is_program_installed("cmd.exe"))
                echo(is_program_installed("opasdfhiovsefuhawzxcvsdvbjkfawfhsd"))
            """
            self.assertStdoutEquals("True\nFalse", lambda: model.manage_pmakefile())

    def test_get_program_path(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                echo("C:\\Windows" in get_program_path())
                echo(len(get_program_path()) > 5)
            """
            self.assertStdoutEquals("True\nTrue", lambda: model.manage_pmakefile())
        elif os.name == "posix":
            model = pm.PMakeupModel()
            model.input_string = """
                            echo("/usr/local/bin" in get_program_path())
                            echo(len(get_program_path()) > 5)
                        """
            self.assertStdoutEquals("True\nTrue", lambda: model.manage_pmakefile())

    def test_find_executable_in_program_directories(self):
        if os.name == "nt":
            model = pm.PMakeupModel()
            model.input_string = """
                echo(find_executable_in_program_directories("hsdghsdklghdf"))
                echo(find_executable_in_program_directories("iexplore.exe"))
            """
            self.assertStdoutEquals("None\nC:\\Program Files\\Internet Explorer\\iexplore.exe", lambda: model.manage_pmakefile())

    def test_replace_regex_in_string(self):
        model = pm.PMakeupModel()
        model.input_string = r"""
            echo(replace_regex_in_string(
                string="3435spring9437",
                regex=r"(?P<word>[a-z]+)",
                replacement=r"\1aa",
            ))
        """
        self.assertStdoutEquals("3435springaa9437", lambda: model.manage_pmakefile())

    def replace_substring_in_string(self):
        model = pm.PMakeupModel()
        model.input_string = """
            echo(replace_substring_in_string(
                string="3435spring9437",
                substring="ring",
                replacement="aringa",
            ))
        """
        self.assertStdoutEquals("3435sparinga9437", lambda: model.manage_pmakefile())

    def test_convert_table_01(self):
        model = pm.PMakeupModel()

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
        model = pm.PMakeupModel()

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
        model = pm.PMakeupModel()

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
        model = pm.PMakeupModel()

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

    def test_read_registry_key(self):
        if os.name == 'nt':
            model = pm.PMakeupModel()
            model.input_string = """
                        echo(read_registry_local_machine_value(
                            key=r"SOFTWARE\\Microsoft\\Clipboard",
                            item="IsClipboardSignalProducingFeatureAvailable"
                        ))
                    """
            self.assertStdoutEquals("1", lambda: model.manage_pmakefile())

    def test_read_registry_keys(self):
        if os.name == 'nt':
            model = pm.PMakeupModel()
            model.input_string = """
                        echo(len(list(get_registry_local_machine_values(
                            key=r"SOFTWARE\\Microsoft\\Clipboard",
                        ))))
                    """
            self.assertStdoutEquals("2", lambda: model.manage_pmakefile())

    def test_set_registry_keys(self):
        if os.name == 'nt':
            model = pm.PMakeupModel()
            model.input_string = """
                        echo(set_registry_in_current_user_as_int(
                            key_relative_to_root=r"SOFTWARE\\Microsoft\\Clipboard",
                            key="hello",
                            value=3
                        ))
                    """
            self.assertStdoutEquals("True", lambda: model.manage_pmakefile())

    def test_has_registry_value_present(self):
        if os.name == 'nt':
            model = pm.PMakeupModel()
            model.input_string = """
                        echo(has_registry_local_machine_value(
                            key=r"SOFTWARE\\Microsoft\\FilePicker",
                            item="UseMinPickerControllerUI"
                        ))
                    """
            self.assertStdoutEquals("True", lambda: model.manage_pmakefile())

    def test_has_registry_value_absent(self):
        if os.name == 'nt':
            model = pm.PMakeupModel()
            model.input_string = """
                        echo(has_registry_local_machine_value(
                            key=r"SOFTWARE\\Microsoft\\FilePicker",
                            item="Seedsdjkf"
                        ))
                    """
            self.assertStdoutEquals("False", lambda: model.manage_pmakefile())

    def test_default_has_registry_local_machine_value(self):
        if os.name == 'nt':
            model = pm.PMakeupModel()
            model.input_string = """
                echo(has_registry_local_machine_value(
                    key=r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\IEXPLORE.EXE",
                    item=""
                ))
            """
            self.assertStdoutEquals("True", lambda: model.manage_pmakefile())

    def test_default_internet_explorer(self):
        if os.name == 'nt':
            model = pm.PMakeupModel()
            model.input_string = """
                echo(get_latest_path_with_architecture("internet-explorer", 64))
            """
            self.assertStdoutEquals(os.path.join("C:\\", "Program Files", "Internet Explorer", "iexplore.exe"), lambda: model.manage_pmakefile())

    def test_is_git_repo_clean(self):
        from git import Repo

        repo = Repo(os.path.pardir)
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
