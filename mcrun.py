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

script_name = os.path.basename(__file__)
encoding = locale.getdefaultlocale()[1]
if encoding is None: encoding = "utf-8"


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
        self.j = jars
        self.names = []
        for i in self.j:
            self.names += [i[0]]


def run_command(command):
    p = subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')
def interact_command(command):
    for line in run_command(command):
        sys.stdout.write(str(line.decode(encoding)))
def running_processes(pattern):
    return sum(1 for line in run_command(["ps", "x"])
            if any(s in line.decode(encoding) for s in pattern))

max_worlds = 2
max_ram = int(400 / max_worlds)  # Allocate 400M RAM total
jars = JarList([["minecraft_server.jar", "nogui"], ["craftbukkit.jar", "-o", "true"]])
parent_dir = "{}/minecraft".format(os.getenv("HOME"))

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
args = parser.parse_args()

if args.saveover: args.save = True
if args.test: args.verbose = True
world_dir = "{0}/{1}".format(parent_dir, args.world)

worlds_running = running_processes(jars.names)
if worlds_running >= max_worlds:
    sys.exit("{0}: Too many worlds running ({1})\n".format(script_name,
            worlds_running))

to_run = ["java", "-Xincgc", "-Xms50M", "-Xmx{}M".format(max_ram), "-jar"]
to_run += jars.j[args.jar]

if args.verbose:
    print("encoding: {}".format(encoding))
    print("instances of minecraft server running: {}".format(worlds_running))
    print("parent dir: {}".format(parent_dir))
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

while True:
    if not os.path.isdir(world_dir):
        sys.exit("{}: world directory does not exist".format(script_name))
    os.chdir(world_dir)
    if args.verbose: print("executing: {}".format(" ".join(to_run)))
    if not args.test: interact_command(to_run)  # Run server program
    if args.save:
        # Backup world to a tarball in parent_dir/saves/args.world
        if not os.path.isdir("{}/saves".format(parent_dir)):
            os.makedirs("{}/saves".format(parent_dir))
        save_dir = "{0}/saves/{1}".format(parent_dir, args.world)
        if not os.path.isdir(save_dir): os.makedirs(save_dir)
        os.chdir(os.pardir)
        today = time.strftime("%Y-%m-%d")
        save_base = "{0}/{1}-{2}".format(save_dir, args.world, today)
        i = 0
        while True:
            if args.saveover:
                j = i + 1
            else:
                j = i
            if not os.path.exists("{0}-{1}.tgz".format(save_base, j)):
                save_file = "{0}-{1}.tgz".format(save_base, i)
                break
            i += 1
        print("backing up: {}".format(save_file))
        if not args.test:
            with tarfile.open(save_file, "w:gz") as tar:
                tar.add(world_dir, arcname=os.path.basename(args.world))
    if not args.keepalive: break
    print("restarting in 5 seconds (press enter to cancel)")
    i, _, _ = select.select( [sys.stdin], [], [], 5 )
    if (i):
        sys.stdin.readline()
        break
