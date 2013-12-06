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
#    Parse parameters
#    Auto reboot on crash

import subprocess
import sys
import os
import argparse
import locale

encoding = locale.getdefaultlocale()[1]
if encoding is None: encoding = "utf-8"

def run_command(command):
    p = subprocess.Popen(command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

def interact_command(command):
    for output_line in run_command(command):
        sys.stdout.write(str(output_line))

def sum_lines_command(command, pattern = None):
    if pattern is None:
        return sum(1 for output_line in run_command(command))
    else:
        return sum(1 for output_line in run_command(command) 
            if any(s in output_line.decode(encoding) for s in pattern))

script_name = os.path.basename(__file__)
max_worlds = 2
max_ram = int(400 / max_worlds) # Give 400M RAM total to worlds this script calls
jars = ["minecraft_server.jar", "craftbukkit.jar"]
jars_index = 0
save = False
save_over = False
save_to = None
extract_from = None
port = None
world = None
args_to_forward = None

parser = argparse.ArgumentParser(description="Process arguments")
parser.add_argument("world")
args = parser.parse_args()
print(args.world) # Debug code

# Bash code: # Extract world directory from parameter, else assume it is the directory
# Bash code: # containing this script
# Bash code: if [ $1 ]; then
# Bash code:    mcDir="$HOME/minecraft"
# Bash code:    worldDir="$mcDir/$1"
# Bash code:    world="$1"
# Bash code: else
# Bash code:    worldDir="$(dirname "$0" 2> /dev/null)"
# Bash code:    if [ "$worldDir" == "/" ]; then
# Bash code:       printf '%s\n' "$scriptName: Please run from a subfolder" >&2
# Bash code:       exit 1
# Bash code:    fi
# Bash code:    mcDir="${worldDir%/*}"
# Bash code:    world="${worldDir##*/}"
# Bash code: fi
# Bash code: saveDir="$mcDir/saves"
# Bash code: 
# Bash code: if [ ! -d "$worldDir" ]; then
# Bash code:    printf '%s\n' "$scriptName: World directory does not exist" >&2
# Bash code:    exit 1
# Bash code: fi
# Bash code: cd "$worldDir" || exit 1
# Bash code: 
# Bash code: # Set tmux window title to "mc-$world"
# Bash code: oldWName="$(tmux display-message -p "#W" 2> /dev/null)"
# Bash code: [ "$TMUX" ] && printf '\033k%s\033\\' "mc-$world"

worlds_running = sum_lines_command("ps x", jars)
#print("instances of minecraft server running: {0}".format(worlds_running)) # Debug code
#print("current working directory: {0}".format(os.getcwd())) # Debug code

if worlds_running >= max_worlds:
    sys.stderr.write("{0}: Too many worlds running\n".format(script_name))
    sys.exit(1)

# To do: remove nogui option for craftbukkit.jar invocation
to_run = "java -Xincgc -Xms50M -Xmx{0}M -jar {1} nogui".format(max_ram, jars[jars_index])
print("to_run: {0}".format(to_run)) # Debug code

print("Running...") # Debug code
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
