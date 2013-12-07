#!/usr/bin/env python3
# -- coding: utf-8 --

# mcrun.py - Python Minecraft server wrapper script
# Copyright Daniel Cranston 2013.
#
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this file. If not, see <http://www.gnu.org/licenses/>.

###############################################################################

# To do:
#    Port from bash
#    Implement options
#    Allow script to be called from world directory without WORLD argument
#    Allow forwarding of args

import subprocess
import sys
import os
import argparse
import locale

script_name = os.path.basename(__file__)
encoding = locale.getdefaultlocale()[1]
if encoding is None: encoding = "utf-8"


class IntRange(object):
    def __init__(self, start, stop=None):
        if stop is None:
            start, stop = 0, start
        self.start, self.stop = start, stop
    def __call__(self, value):
        value = int(value)
        if value < self.start or value >= self.stop:
            raise argparse.ArgumentTypeError('value outside of range')
        return value


def run_command(command):
    p = subprocess.Popen(command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

def interact_command(command):
    for output_line in run_command(command):
        sys.stdout.write(str(output_line))

def sum_lines_command(command, pattern=None):
    if pattern is None:
        return sum(1 for output_line in run_command(command))
    else:
        return sum(1 for output_line in run_command(command) 
                if any(s in output_line.decode(encoding) for s in pattern))

max_worlds = 2
max_ram = int(400 / max_worlds)  # Allocate 400M RAM total
jars = ["minecraft_server.jar", "craftbukkit.jar"]
jar_args = ["nogui", "-o true"]
parent_dir = "{0}/minecraft".format(os.getenv("HOME"))

parser = argparse.ArgumentParser()
parser.add_argument("world",
        help="world directory",
        metavar="WORLD",
        type=str)
parser.add_argument("-v", "--verbose",
        help="increase output verbosity",
        action="store_true",
        default=False)
parser.add_argument("-b", "--bukkit",
        help="run as bukkit server",
        dest="jar",
        action="store_const",
        const=1,
        default=0)
parser.add_argument("-k", "--keepalive",
        help="auto reboot on crash",
        action="store_true",
        default=False)
parser.add_argument("-s", "--save",
        help="save world on close",
        action="store_true",
        default=False)
parser.add_argument("-o", "--saveover",
        help="overwrite save (else appends number). implies -s",
        action="store_true",
        default=False)
parser.add_argument("-d", "--savedir",
        help="save to SAVEDIR (else to saves/WORLD). implies -s",
        type=str)
parser.add_argument("-x", "--extract",
        help="extract from TARBALL then run. overwrites WORLD",
        metavar="TARBALL",
        type=str)
parser.add_argument("-e", "--level",
        help="level within WORLD to run",
        type=str)
parser.add_argument("-p", "--port",
        help="listening port (valid range: 1-65535)",
        type=IntRange(1, 65536))
args = parser.parse_args()

if args.saveover or args.savedir: args.save = True
if args.savedir is None:
    args.savedir = "{0}/saves/{1}".format(parent_dir, args.world)
world_dir = "{0}/{1}".format(parent_dir, args.world)

if args.extract:
    pass # tar -xvzf args.extract world_dir
elif not os.path.isdir(world_dir):
    pass # printf '%s\n' "$scriptName: World directory does not exist" >&2
    # exit 1

# Bash code: cd "$worldDir" || exit 1

worlds_running = sum_lines_command("ps x", jars)

if worlds_running >= max_worlds:
    sys.exit("{0}: Too many worlds running ({1})\n".format(script_name,
            worlds_running))

to_run = "java -Xincgc -Xms50M -Xmx{0}M -jar {1} {2}".format(max_ram,
        jars[args.jar], jar_args[args.jar])

if args.verbose:
    print("instances of minecraft server running: {0}".format(worlds_running))
    print("current working directory: {0}".format(os.getcwd()))
    print("parent dir: {0}".format(parent_dir))
    print("world: {0}".format(args.world))
    print("keep alive: {0}".format(args.keepalive))
    print("save: {0}".format(args.save))
    print("save over: {0}".format(args.saveover))
    print("save dir: {0}".format(args.savedir))
    if args.level is None:
        print("level: (read from server.properties)")
    else:
        print("level: {0}".format(args.level))
    if args.port is None:
        print("port: (read from server.properties)")
    else:
        print("port: {0}".format(args.port))
    print("to_run: {0}".format(to_run))  # Debug code

# Bash code: # Set tmux window title to "mc-$world"
# Bash code: oldWName="$(tmux display-message -p "#W" 2> /dev/null)"
# Bash code: [ "$TMUX" ] && printf '\033k%s\033\\' "mc-$world"

print("Running...")  # Debug code
#interact_command(to_run)

# Bash code: exitStatus=$?
# Bash code: 
# Bash code: [ "$TMUX" ] && printf '\033k%s\033\\' "$oldWName"
# Bash code: 
# Bash code: # Backup level to a tarball in "$saveDir/$world"
# Bash code: [ -d "$saveDir" ] || mkdir "$saveDir"
# Bash code: [ -d "$saveDir/$world" ] || mkdir "$saveDir/$world"
# Bash code: cd .. || exit 1
# Bash code: saveFile="$saveDir/$world/$world-$(date +%Y-%m-%d)-"
# Bash code: 
# Bash code: i=0
# Bash code: while true; do
# Bash code:    if [ ! -e $saveFile$i.tgz ]; then
# Bash code:       printf '%s\n' "Backing up: $saveFile$i.tgz"
# Bash code:       tar -czf "$saveFile$i.tgz" "$world/"
# Bash code:       let exitStatus+=$?
# Bash code:       break
# Bash code:    fi
# Bash code:    let i+=1
# Bash code: done
# Bash code: 
# Bash code: exit $exitStatus
