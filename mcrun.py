#!/usr/bin/env python3
# -- coding: utf-8 --

# mcrun.py - Python Minecraft server wrapper script
# Copyright Daniel Cranston 2013-2014.
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
#    Read max_ram, max_worlds from config file
#        Alternatively, allow manual specification of RAM values
#    Implement options: args.level, args.port
#    Allow script to be called from world directory without WORLD argument
#    Allow forwarding of args

import subprocess
import sys
import os
import argparse
import locale
import select
import time
import tarfile

###### Classes ######
class IntRange(object):
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
    def __call__(self, value):
        value = int(value)
        if value < self.start or value >= self.stop:
            raise argparse.ArgumentTypeError('value outside of range')
        return value

class JarList(object):
    def __init__(self, jars):
        self.jars = jars
        self.names = [i[0] for i in self.jars]
    def __call__(self, idx):
        return self.jars[idx]

# class Command(object):
#    def __init__(self, command):
#        self.command = command
#    def execute(self):
#        run_command(self.command)

###### Static variables ######
encoding = locale.getdefaultlocale()[1]
if encoding is None:
    encoding = "utf-8"

max_worlds = 2
total_max_ram = 400 # Megabytes
max_ram = int(total_max_ram / max_worlds)
jars = JarList([ ["minecraft_server.jar", "nogui"],
                 ["craftbukkit.jar", "-o", "true"] ])
java_command = ["java", "-Xms50M", "-Xmx{}M".format(max_ram), "-jar"]
#java_command += ["-Xincgc"]
minecraft_dir = "{}/minecraft".format(os.getenv("HOME"))
save_dir = "{}/saves".format(minecraft_dir)
# Seconds to wait before restart when args.keepalive option is True
restart_wait = 5

###### Methods ######

### Command methods ###
def run_command(command):
    p = subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

def interact_command(command):
    for line in run_command(command):
        sys.stdout.write(str(line.decode(encoding)))

def count_running_processes(pattern):
    return sum(1 for line in run_command(["ps", "x"])
            if any(s in line.decode(encoding) for s in pattern))

### Argument parser ###
def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("world",
            help="world directory",
            metavar="WORLD",
            type=str)
    parser.add_argument("-v", "--verbose",
            help="increase output verbosity",
            action="store_true",
            default=False)
    parser.add_argument("-t", "--test",
            help="simulate actions. implies -v",
            action="store_true",
            default=False)
    parser.add_argument("-b", "--bukkit",
            help="run as bukkit server",
            dest="jar",
            action="store_const",
            const=1,
            default=0)
    parser.add_argument("-k", "--keepalive",
            help="auto reboot on exit",
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
    parser.add_argument("-e", "--level",
            help="level within WORLD to run (NYI)",
            type=str)
    parser.add_argument("-p", "--port",
            help="listening port (valid range: 1-65535) (NYI)",
            type=IntRange(1, 65536))
    return parser

def parse_args(parser):
    args = parser.parse_args()
    if args.saveover:
        args.save = True
    if args.test:
        args.verbose = True
    return args

### Print variables method (used in verbose option, for debugging) ###
def print_variables():
    print("encoding: {}".format(encoding))
    print("instances of minecraft server running: {}".format(worlds_running))
    print("minecraft dir: {}".format(minecraft_dir))
    print("world: {}".format(args.world))
    print("keep alive: {}".format(args.keepalive))
    print("save: {}".format(args.save))
    print("save over: {}".format(args.saveover))
    if args.level is None:
        print("level: (read from server.properties)")
    else:
        print("level: {}".format(args.level))
    if args.port is None:
        print("port: (read from server.properties)")
    else:
        print("port: {}".format(args.port))
    print("current working directory: {}".format(os.getcwd()))

###### Main command sequence ######

worlds_running = count_running_processes(jars.names)
assert worlds_running < max_worlds, "Too many worlds already running"

args = parse_args(create_parser())

# Set argument-dependent variables
to_run = java_command + jars(args.jar)
world_dir = "{}/{}".format(minecraft_dir, args.world)
save_world_dir = "{}/{}".format(save_dir, args.world)
save_file_base = "{}/{}-{{}}-{{}}.tgz".format(save_world_dir, args.world)

if args.verbose:
    print_variables()

while True:
    assert os.path.isdir(world_dir), "World directory doesn't exist"
    os.chdir(world_dir)
    if args.verbose: print("executing: {}".format(" ".join(to_run)))
    if not args.test:
        interact_command(to_run)  # Run server program
    if args.save:
        # Backup world to a tarball in minecraft_dir/saves/args.world
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        if not os.path.isdir(save_world_dir):
            os.makedirs(save_world_dir)
        os.chdir(os.pardir)
        date = time.strftime("%Y-%m-%d")
        i = 0
        while True:
            next_save_file = save_file_base.format(date, i + args.saveover)
            if not os.path.exists(next_save_file):
                save_file = save_file_base.format(date, i)
                break
            i += 1
        print("backing up: {}".format(save_file))
        if not args.test:
            with tarfile.open(save_file, "w:gz") as tar:
                tar.add(world_dir, arcname=os.path.basename(args.world))
    if not args.keepalive: break
    print("restarting in {} sec (press enter to cancel)".format(restart_wait))
    i, _, _ = select.select( [sys.stdin], [], [], restart_wait )
    if (i):
        sys.stdin.readline()
        break
