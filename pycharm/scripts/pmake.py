#!python
# see https://docs.python.org/3.4/distutils/setupscript.html#installing-scripts
import sys
from pmake import main

if __name__ == "__main__":
    main.main(sys.argv[1:])
