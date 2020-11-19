import argparse
import logging
import os
import sys
import textwrap

from pmake import version
from pmake.PMakeModel import PMakeModel
from pmake.commands import SessionScript
from pmake.constants import STANDARD_MODULES, STANDARD_VARIABLES


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
        So you can write loops, checks all the python juicy stuff in it withtout worries.
        I have developed this utility for writing batch without worrying about the underlying operating system, 
        hence several utilities are immeidately provided to you in order to perform basic stuff.
        
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
    parser.add_argument("-l", "--log_level", type=str, required=False, default="CRITICAL", help="""
    Log level of the application. Allowed values are "INFO", "DEBUG", "CRITICAL"
    """)
    parser.add_argument("-m", "--python_module", nargs=2, action="append", default=None, help="""
    A python module that the script will load. The first argument represents the name that you will use in the PMakefile
    while the second parameter is the python module to import. For instance --python_module "numpy" "np"
    """)
    parser.add_argument("-v", "--variable", nargs=2, action="append", default=[], help="""
    Allows to input external variables in this file. For instance:
    
    --value "VariableName" "variableValue"
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

    model = PMakeModel()
    model.input_file = os.path.abspath(options.input_file)
    model.input_encoding = options.input_encoding
    model.log_level = options.log_level
    model.input_string = options.input_string
    model.variable = options.variable
    model.targets = options.targets

    logging.basicConfig(level=getattr(logging, model.log_level))
    model.manage_pmakefile()


if __name__ == "__main__":
    main(sys.argv[1:])