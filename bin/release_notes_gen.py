#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import distutils.dir_util as dir_util
import textwrap
import timeit
import json
from collections import OrderedDict

parser = argparse.ArgumentParser(description='For Essentials release', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-q', '--quit', action='store_true', help='Print only commit description.')
parser.add_argument('target', metavar='TARGET', help='Please specify a git tag name.')

tag = parser.parse_args().target

if parser.parse_args().quit:
    git_command = 'git --no-pager log --color="always" --pretty=format:"- %s" HEAD...' + tag
else:
    git_command = 'git --no-pager log --color="always" --pretty=format:"%h %C(blue) %<|(25) %an %C(red) %<|(40) %ar  %C(auto) %s" HEAD...' + tag

git_check_tag_cmd = 'git tag | grep ' + tag + ' > /dev/null'

SCRIPT_PATH=os.path.realpath(__file__)
TOOLCHAINS_DIR_PATH=os.path.dirname(os.path.dirname(SCRIPT_PATH))
TOOLCHAINS_DIR_NAME=os.path.basename(TOOLCHAINS_DIR_PATH)
PROJECT_DIR_PATH=os.path.join(TOOLCHAINS_DIR_PATH, "..")
APP_DIR_PATH=os.path.join(PROJECT_DIR_PATH, "App")
PLUGIN_DIR_PATH=os.path.join(PROJECT_DIR_PATH, "Plugins")
TESTS_DIR_PATH=os.path.join(PROJECT_DIR_PATH, "Tests")


def run_cmd(cmd, ignore_error=False):
    ret = subprocess.call(cmd, shell=True)
    if not ignore_error and ret != 0:
        sys.exit(ret)

def print_info(path):
    os.chdir(path)
    ret = subprocess.call(git_check_tag_cmd, shell=True)
    if(ret == 1):
        print("these is no tag named: " + tag)
    else:
        run_cmd(git_command)
        print("")
    print("")


print("======================= App commits log =======================")
print("")

print_info(APP_DIR_PATH)
        

print("======================= Plugins commits log =======================")
print("")

plugins_dirs = os.listdir(PLUGIN_DIR_PATH)
for dir in plugins_dirs:
    plugin_dir = os.path.join(PLUGIN_DIR_PATH, dir)
    if os.path.isdir(plugin_dir):
        print("----------------------- Plugin: " + dir + " -----------------------")
        print_info(plugin_dir)

print("======================= Tests commits log =======================")
print("")

print_info(TESTS_DIR_PATH)
