
[![Build Status](https://travis-ci.org/sevas/update_python_alternatives.png)](https://travis-ci.org/sevas/update_python_alternatives)


# What is this?


This program is a helper to switch between several python installations.
It first tries to locate all the installed binaries on a Unix system. Then, it
generate a shell function for each of them, and stores them in a file.

Every shell function basically looks like this:

    select_macpython_271()
    {
        echo "Setting environment for Python 2.7.1 -- MacPython"
        export PATH="/Library/Frameworks/Python.framework/Versions/2.7/bin:${OLD_PATH}"
        export PROMPT_PYTHON_VERSION="MacPython 2.7.1"
    }




By default, it excludes folders known to contain python binaries that are not
root installations. Things like python living inside a virtualenv are ignored.


# Motivation

I work with several python distributions: [Enthought's EPD](https://www.enthought.com/products/epd/), [Continuum Analytics' Anaconda](https://store.continuum.io/cshop/anaconda/), MacPython 2.x and 3.x.
I like to be able to control which one I'm using at any given time.


# How to use it?


## Generate switching functions
There is nothing to install. Run the `update_python_switchers.py` script, and it
will generate files in your home. These file are intended to be sourced by a
common shell program.


## Shell integration

This program currently generates two files:

- *~/.python_switchers.sh*: for bash and bash-compatible shells, such as zsh
- *~/.python_switchers.fish*: for the [fish shell](http://fishshell.com/)


Here is how to enable the python switcher functions if you are using zsh.
Edit your *~/.zshrc* file to make it look like this:


    # ~/.zshrc
    ...
    source $HOME/.python_switchers.sh
    # Set the default version to use
    select_anaconda_161_x86_64
    # EOF


It is required that you put these lines at the end of your init script, so that
all your other `$PATH` modifications will be taken into account.


## Pimp your prompt

Once a python version is selected, a shell variable, called
`$PROMPT_PYTHON_VERSION`, is defined. Use it at will in your `$PS1` or `$PROMPT` variable.
Have a look [here](https://github.com/sevas/oh-my-zsh/blob/master/themes/prose.zsh-theme#L29-L39) for an example


## Repeat

Run `update_python_switchers.py` again everytime you install or remove a python
distribution from your system.

Be aware that it uses the `locate` command to detect the installed python.
Don't forget to keep the locate database to be up to date with `updatedb`.

This program was tested on Mac OS X and Ubuntu 12.04.



# License

This important piece of software is licensed under the "DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE."
Please consult LICENSE.txt in case you have any doubt about what it means.
