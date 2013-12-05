#!/usr/bin/env python

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

import subprocess
import sys
import os

script_name = "mcrun.py"
max_worlds = 2
max_ram = 400 / max_worlds
jars = ["minecraft_server.jar", "craftbukkit.jar"]
jar_to_run = 1

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
        return sum(1 for output_line in run_command(command) if any(s in output_line for s in pattern))

worlds_running = sum_lines_command("ps x", jars)

to_run = "java -Xincgc -Xms50M -Xmx{0}M -jar {1} nogui".format(max_ram, jars[jar_to_run])

#Debug code
print "script_name:", script_name
print "max_worlds:", max_worlds
print "instances of minecraft server running:", worlds_running
print "current working directory:", os.getcwd()
print "to_run:", to_run

if worlds_running >= max_worlds:
    sys.stderr.write("{0}: Too many worlds running\n".format(script_name))
    sys.exit(1)

print "Running..."
#interact_command(to_run)

#worldsRunning=$(pgrep -f "minecraft_server" 2> /dev/null | wc -l)
#if [ $worldsRunning -ge $maxWorlds ]; then
#   printf '%s\n' "$scriptName: Too many worlds running" >&2
#   exit 1
#fi
#
#if [ $2 ]; then
#   printf '%s\n' "$scriptName: Too many args" >&2
#   exit 1
#fi
#
## Extract world directory from parameter, else assume it is the directory
## containing this script
#if [ $1 ]; then
#   mcDir="$HOME/minecraft"
#   worldDir="$mcDir/$1"
#   world="$1"
#else
#   worldDir="$(dirname "$0" 2> /dev/null)"
#   if [ "$worldDir" == "/" ]; then
#      printf '%s\n' "$scriptName: Please run from a subfolder" >&2
#      exit 1
#   fi
#   mcDir="${worldDir%/*}"
#   world="${worldDir##*/}"
#fi
#saveDir="$mcDir/saves"
#
#if [ ! -d "$worldDir" ]; then
#   printf '%s\n' "$scriptName: World directory does not exist" >&2
#   exit 1
#fi
#cd "$worldDir" || exit 1
#
## Set tmux window title to "mc-$world"
#oldWName="$(tmux display-message -p "#W" 2> /dev/null)"
#[ "$TMUX" ] && printf '\033k%s\033\\' "mc-$world"
#
#if [ $bukkit == 0 ]; then
#   java -Xms50M -Xmx$maxRam -jar craftbukkit.jar -o true
#else
#   java -Xms50M -Xmx$maxRam -jar minecraft_server.jar nogui
#fi
#exitStatus=$?
#
#[ "$TMUX" ] && printf '\033k%s\033\\' "$oldWName"
#
## Backup level to a tarball in "$saveDir/$world"
#[ -d "$saveDir" ] || mkdir "$saveDir"
#[ -d "$saveDir/$world" ] || mkdir "$saveDir/$world"
#cd .. || exit 1
#saveFile="$saveDir/$world/$world-$(date +%Y-%m-%d)-"
#
#i=0
#while true; do
#   if [ ! -e $saveFile$i.tgz ]; then
#      printf '%s\n' "Backing up: $saveFile$i.tgz"
#      tar -czf "$saveFile$i.tgz" "$world/"
#      let exitStatus+=$?
#      break
#   fi
#   let i+=1
#done
#
#
#exit $exitStatus
