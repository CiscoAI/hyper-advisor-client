""" main module to control all the commands"""
import argparse
import importlib
import inspect

from pkgutil import iter_modules

import sys

from advisorclient.commands.AdvisorCommand import AdvisorCommand


def walk_modules(path):
    """ function to find all the modules recursively under a path """

    mods = []
    mod = importlib.import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = importlib.import_module(fullpath)
                mods.append(submod)
    return mods


def iter_command_classes(module_name):
    """ the generator to fetch all the subclass of the AdvisorCommand class """

    mods = walk_modules(module_name)
    for mod in mods:
        for obj in vars(mod).values():
            if inspect.isclass(obj) \
                    and issubclass(obj, AdvisorCommand) \
                    and obj.__module__ == mod.__name__ \
                    and not obj == AdvisorCommand:
                yield obj


def get_commands_from_module(mod):
    """ create a dictionary for commands """

    cmd_dict = {}
    for cmd in iter_command_classes(mod):
        cmdname = cmd.__module__.split('.')[-1]
        cmd_dict[cmdname] = cmd()
    return cmd_dict


def get_command_from_argument(argv):
    """ extract command from the command line arguments """

    for arg in argv[1:]:
        if not arg.startswith('-'):
            return arg
    return None


def print_usage():
    """ print usage of this cli tool """

    print("Usage:")
    print("advisor-client <command> [options] [args]")
    print("Available commands:")
    cmds = get_commands_from_module('advisorclient.commands')
    for cmdname, cmdclass in sorted(cmds.items()):
        print("%-20s %s" % (cmdname, cmdclass.show_desc()))
    print()
    print("Use 'advisor-client <command> -h' to see more info about a command")


def print_unknown_command(cmdname):
    """ print the error of unknown commands"""

    print("Unknown command: %s" % cmdname)
    print("Use 'advisor-client' to see available commands")


def execute(argv=None):
    """ main entry of this module"""

    if argv is None:
        argv = sys.argv

    cmds = get_commands_from_module('advisorclient.commands')
    cmdname = get_command_from_argument(argv)
    if not cmdname:
        print_usage()
        sys.exit(0)
    elif cmdname not in cmds:
        print_unknown_command(cmdname)
        sys.exit(1)

    parser = argparse.ArgumentParser()
    cmd = cmds[cmdname]
    cmd.add_options(parser)
    args = parser.parse_args()

    cmd.process_args(args)
    cmd.run()


if __name__ == "__main__":
    execute()
