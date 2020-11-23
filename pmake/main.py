import argparse
import logging
import os
import sys
import textwrap
import trace
import traceback

from pmake import version
from pmake.PMakeModel import PMakeModel
from pmake.commands import SessionScript
from pmake.constants import STANDARD_MODULES, STANDARD_VARIABLES
from pmake.exceptions.PMakeException import AssertionPMakeException, InvalidScenarioPMakeException, PMakeException


def parse_options(args):
    core_functions = f'\n'.join(map(lambda x: f' {x[0] + 1}. {x[1][1].__name__};', enumerate(STANDARD_MODULES)))
    core_functions = textwrap.dedent(core_functions)
    core_constants = f'\n'.join(map(lambda x: f' {x[0] + 1}. {x[1][0]}: {x[1][2]};', enumerate(STANDARD_VARIABLES)))
    core_constants = textwrap.dedent(core_constants)

    convenience_commands = '\n'.join(map(lambda x: f' * {x[1][0]}\n{x[1][1]}\n', enumerate(SessionScript._list_all_commands())))
    convenience_commands = textwrap.dedent(convenience_commands)

    parser = argparse.ArgumentParser(
        prog="pmake",
        description=f"""
        A program like make, but platform independent. Requires python3
        
        The file is basically written in python. within the input_fle, you can write python code in 
        order to perform some tasks.
        So you can write loops, checks all the python juicy stuff in it without worries.
        I have developed this utility for writing batch without worrying about the underlying operating system, 
        hence several utilities are immediately provided to you in order to perform basic stuff.
        
        Aside from the core functions, you can access these modules:
        
{core_functions}

        You can add more modules using --python_module argument.
        In order to facilitate writing scripts, you can use the additional convenience functions:

{convenience_commands}

        Alongside such functions, there are some important readonly variables always available:

{core_constants}

        You can access the variables passed to "--variable" by calling their name. For instance if you have 
        
        "--variable "foo" "bar"
        
        From pamke script, you can access foo variable via "variables.foo". Aside from variable you
        can access:
         - the set of all the commands via "commands.X", where "X" is the name of the command (e.g., "echo");
         - "model" to gain access to the whole application shared context;
         - the interesting paths by using "interesting_path";
         - the latest interesting paths by using "latest_interesting_path";
         - the ordered list fo target the user has specified via "targets";

        Return Status
        =============

         - 0: no error detected
         - 1: an assertion failed
         - 2: a variable allowing to discern between mutually exclusive scenarios is invalid
         - 254: a generic error that is explicitly thrown by pmake
         - 255: a serious error while executing pmake.
        
        """,
        epilog=f"Massimo Bono 2020, Version {version.VERSION}",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-f", "--input_file", type=str, required=False, default="PMakefile.py", help="""
    The file in input. If not present it will be "PMakefile" on the CWD
    """)
    parser.add_argument("-s", "--input_string", type=str, required=False, default=None, help="""
    A string containing the file in input. Useful when the input_file would be very tiny. If present, it will overwrite
    any input_file provided
    """)
    parser.add_argument("-e", "--input_encoding", type=str, required=False, default="utf-8", help="""
    Encoding of the input file
    """)
    parser.add_argument("-l", "--log_level", type=str, required=False, default="INFO", help="""
    Log level of the application. Allowed values are "INFO", "DEBUG", "INFO"
    """)
    parser.add_argument("-m", "--python_module", nargs=2, action="append", default=None, help="""
    A python module that the script will load. The first argument represents the name that you will use in the PMakefile
    while the second parameter is the python module to import. For instance --python_module "numpy" "np"
    """)
    parser.add_argument("-v", "--variable", nargs=2, action="append", default=[], help="""
    Allows to input external variables in this file. For instance:
    
    --value "VariableName" "variableValue"
    """)
    parser.add_argument("-V", "--version", action="store_true", help="""
    Show the version of th software and exits
    """)
    parser.add_argument('targets', metavar="TARGET", nargs="*", type=str, help="""
    An ordered list of pmake targets the user wants to build. For example, target names may be "all", 
    "clean", "install", "uninstall".
    
    Targets are available via `targets` variable. You can check if a target has been requested by the user 
    by calling `specifies_target`
    """)

    options = parser.parse_args(args)

    return options


def main(args):
    options = parse_options(args)

    if options.version:
        print(version.VERSION)
        sys.exit(0)

    log_level = options.log_level
    logging.basicConfig(
        level="INFO",
        datefmt="%Y-%m-%dT%H:%M:%S",
        format='%(asctime)s %(funcName)20s@%(lineno)4d[%(levelname)8s] - %(message)s',
    )
    logging.debug(f"Logging set to {log_level} (DEBUG={logging.DEBUG}, INFO={logging.INFO}, WARNING={logging.WARN}, ERROR={logging.ERROR}, CRITICAL={logging.CRITICAL})")

    model = PMakeModel()
    model.input_file = os.path.abspath(options.input_file)
    model.input_encoding = options.input_encoding
    model.log_level = options.log_level
    model.input_string = options.input_string
    logging.critical(options.variable)
    model.variable = {x[0]: x[1] for x in options.variable}
    model.targets = options.targets
    model.manage_pmakefile()


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except AssertionPMakeException as e:
        sys.exit(1)
    except InvalidScenarioPMakeException as e:
        sys.exit(2)
    except PMakeException as e:
        sys.exit(254)
    except Exception as e:
        raise e
