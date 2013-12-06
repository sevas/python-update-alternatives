#!/usr/bin/env python
"""
What is this?
-------------

This program detects all the python executables installed on a unix system,
and creates a shell script with shell functions to switch between them.

Every generated function will follow this pattern:

.. code:: shell

    select_macpython_271()
    {
        echo "Setting environment for Python 2.7.1 -- MacPython"
        export PATH="/Library/Frameworks/Python.framework/Versions/2.7/bin:${PRISTINE_INIT_PATH}"
        export PROMPT_PYTHON_VERSION="MacPython 2.7.1"
    }


That's it. It just monkeypatches the PATH variable. Additionally, you can use
the content of PROMPT_PYTHON_VERSION in your PS1 variable.

By default, these selector functions will be saved to $HOME/.python_switchers.sh.

You will need to add the following lines to your shell initialization file.
On MacOS X systems, use $HOME/.bash_profile for bash, and $HOME/.zshrc for zsh.

.. code:: shell

    source $HOME/.python_switchers.sh

    # Setup the default python. update_python_switchers.py must have been
    # called at least once, and this function must have been defined in
    # the generated .python_switchers.sh file.
    select_macpython_271

This thing was not tested with any other shell. I intend to make it work with
the fish shell though.


What are these python variants?
-------------------------------

I identified the following python distributions:

- System python : the python installed with the OS.
- MacPython: Obviously only for Mac OS X. A python installed from
  python.org.
- EPD: The Enthought Python Distribution. A python distribution dedicated to
  scientific computing with a lot of pre-built packages. See
  https://www.enthought.com/products/epd/
- Anaconda: A python distribution dedicated to scientific computing with a lot
  of pre-built packages. See https://store.continuum.io/cshop/anaconda/


It is possible that other flavours exist.

This program will ignore all the pythons that seem to be part of a virtualenv.
Use the --excluded-patterns flag if you with to blacklist even more pythons.


Is there more?
--------------

Not much. Just try and run this program with --help.


License
-------

This program is licensed under the WTFPL license. See LICENSE.txt for details.

"""
__version__ = '1.0'

import os
import subprocess
import re
import string

SYSTEM_ROOT = "/System/Library/Frameworks/Python.framework"
MACPYTHON_ROOT = "/Library/Frameworks/Python.framework"


def get_python_version(python_filepath):
    "Gets the version string of an installed python, using the -V flag"
    process = subprocess.Popen([python_filepath, '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = process.communicate()
    return stderr.strip()


def generate_bash_select_func(python_filepath, version_string, prompt_string, bash_function_name):
    """Generates a shell function to monkeypatch the PATH variable and put
       a particular python as the default one.
    """
    values = {
        'path':            os.path.dirname(python_filepath),
        'version_string':  version_string,
        'prompt_string':   prompt_string,
        'bash_func_name':  bash_func_name
    }

    return """\
select_{bash_func_name}()
{{
    echo \"Setting environment for {version_string}\"
    export PATH=\"{path}:${{PRISTINE_INIT_PATH}}\"
    export PROMPT_PYTHON_VERSION="{prompt_string}"
}}

""".format(**values)


def generate_fish_select_function(python_filepath, version_string, prompt_string, bash_function_name):
    """Generates a shell function to monkeypatch the PATH variable and put
       a particular python as the default one
    """
    values = {
        'path':            os.path.dirname(python_filepath),
        'version_string':  version_string,
        'prompt_string':   prompt_string,
        'bash_func_name':  bash_func_name
    }

    return """\
function select_{bash_func_name}
    printf \"Setting environment for {version_string}\"
    set -gx PATH {path} $PRISTINE_INIT_PATH
    set -gx PROMPT_PYTHON_VERSION "{prompt_string}"
end

""".format(**values)



def is_python_filepath(filepath):
    """Checks if a filepath corresponds to a python binary.

    >>> is_python_filepath("/usr/bin/python")
    True

    >>> is_python_filepath("/usr/bin/python3")
    True

    >>> is_python_filepath("/home/aneiko/python_projects/macx")
    False
    """
    return filepath.endswith("bin/python") or filepath.endswith("bin/python3")


def is_python_executable(filepath, excluded_patterns, file_exists=os.path.exists):
    """Checks that a filepath is a python executable and that it does not match
       a list of patterns.

    Parameters
    ----------
    filepath: str
    excluded_patterns: list of strings
        List of regexps for paths to ignore


    Examples
    --------
    >>> is_python_executable("/usr/bin/python", [], file_exists=lambda x: True)
    True

    >>> is_python_executable("/usr/bin/python", ["/usr/.*"], file_exists=lambda x: True)
    False

    >>> is_python_executable("/home/aneiko/.virtualenvs/django_sandbox/bin/python", [], file_exists=lambda x: True)
    True

    >>> is_python_executable("/home/aneiko/.virtualenvs/django_sandbox/bin/python", [".*virtualenv.*"], file_exists=lambda x: True)
    False
    """

    if not is_python_filepath(filepath) or not file_exists(filepath):
        return False

    for pattern in excluded_patterns:
        if re.match(pattern, filepath):
            return False
    return True


def detect_all_python_installs(excluded_patterns):
    """Detects all the python installed on a Unix system. Filters out those who match given patterns"""
    p = subprocess.Popen(['locate', 'bin/python'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    results = stdout.split("\n")

    return [each for each in results if is_python_executable(each, excluded_patterns)]


def make_bash_func_string(s):
    """Transforms a string into something suitable for a shell function. Removes or replace forbidden characters"""
    bash_func_name = string.translate(s, None, ':.()[]{}').lower()

    for forbidden_char in ' -':
        bash_func_name = bash_func_name.replace(forbidden_char, "_")

    return bash_func_name


def make_short_strings(version_string):
    """

    >>> make_short_strings('Python 2.7.2 -- EPD 7.2-2 (64-bit)')
    ('EPD 7.2-2 (64-bit)', 'epd_72_2_64_bit')

    >>> make_short_strings('Python 2.7.1 -- MacPython')
    ('MacPython 2.7.1', 'macpython_271')

    >>> make_short_strings('Python 2.7.5 :: Anaconda 1.6.1 (x86_64)')
    ('Anaconda 1.6.1 (x86_64)', 'anaconda_161_x86_64')
    """

    if "-- EPD" in version_string:
        epd_version = version_string.split('--')[1].strip()
        return epd_version, make_bash_func_string(epd_version)

    if "Anaconda" in version_string:
        anaconda_version = version_string.split('::')[1].strip()
        return anaconda_version, make_bash_func_string(anaconda_version)

    if "MacPython" in version_string:
        python_version =  version_string.split("--")[0].split("Python")[1].strip()
        macpython_version = "MacPython " + python_version
        return macpython_version, make_bash_func_string(macpython_version)

    if "System" in version_string:
        return version_string, make_bash_func_string(version_string)

    return version_string, make_bash_func_string(version_string)


def make_version_strings(python_filepath):
    version_string = get_python_version(p)

    if python_filepath.startswith(MACPYTHON_ROOT):
        version_string += " -- MacPython"
        short_version_string, bash_func_name =  make_short_strings(version_string)
        return version_string, short_version_string, bash_func_name

    elif python_filepath.startswith(SYSTEM_ROOT) or python_filepath.startswith('/usr'):
        version_string = "System " + version_string
        short_version_string, bash_func_name = make_short_strings(version_string)
        return version_string, short_version_string, bash_func_name

    else:
        short_version_string, bash_func_name = make_short_strings(version_string)
        return version_string, short_version_string, bash_func_name


EXCLUDED_PATTERNS = [".*virtualenv.*", ".*pkgs.*", ".*anaconda/envs.*"]
DEFAULT_OUTFILE_BASENAME = os.path.expandvars("$HOME/.python_switchers")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Detects all python installations and creates bash functions to switch between them')
    parser.add_argument('-e', '--excluded-patterns', action='append', default=EXCLUDED_PATTERNS, help="Add a pattern (regex) to exclude when looking for python installations. Use as many as needed. (default: {0})".format(EXCLUDED_PATTERNS))
    parser.add_argument('-o', '--outfile-basename', action='store', default=DEFAULT_OUTFILE_BASENAME, help="Output file basename, without extension, for the generated shell functions (default: {0})".format("$HOME/.python_switchers.{sh,fish}"))
    parser.add_argument('-d', '--dry-run', action='store_true', default=False, help="Only show the detected installations, don't write the shell files.")
    args = parser.parse_args()

    print("--- Searching all installed pythons, except those that match the following patterns: {0}".format(args.excluded_patterns))

    installed_pythons = detect_all_python_installs(args.excluded_patterns)

    print("--- Found {0} results.".format(len(installed_pythons)))


    if args.dry_run:
        for p in installed_pythons:
            full_version, prompt, _ = make_version_strings(p)
            print "--- {:<50} (path: {0})".format(full_version, p)
    else:
        filenames = [args.outfile_basename+ext for ext in (".sh", ".fish")]
        shell_filename, fish_filename = filenames
        print("--- Saving selectors to {0}".format(filenames))

        with open(shell_filename, 'w') as shell_file, open(fish_filename, 'w') as fish_file:

            shell_file.write("export PRISTINE_INIT_PATH=$PATH\n")
            fish_file.write("set -gx PRISTINE_INIT_PATH $PATH\n")

            for p in installed_pythons:
                full_version, prompt, bash_func_name = make_version_strings(p)
                print("--- Adding shell function to switch to {0:<50} shell function: {1:<50} (path: {2}".format(full_version, "select_"+bash_func_name+"()", p))
                bash_func = generate_bash_select_func(p, full_version, prompt, bash_func_name)
                shell_file.write(bash_func)

                fish_func = generate_fish_select_function(p, full_version, prompt, bash_func_name)
                fish_file.write(fish_func)


        print("--- Selectors saved. Don't forget to source the adequate generated file to your .bashrc, .zshrc or fish.config file".format(filenames))
