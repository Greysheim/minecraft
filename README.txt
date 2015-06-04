Minecraft Wrapper Scripts

###############################################################################

Usable, no longer under development:
mcrun.py (python3, compatible with python2)
mcrun (bash)

Snippets for integration into other scripts:
mcparams (bash)
mcchat (bash)

###############################################################################

Invocation:
mcrun [WORLD]
mcrun.py [options] WORLD

For detailed information on mcrun.py options:
mcrun.py -h

When invoking mcrun.py, or mcrun with a world name as a parameter, the
following directory structure is assumed:

$HOME
 \
  minecraft
  |\
  | $world
  |  \
  |   minecraft_server.jar or craftbukkit.jar
   \
    saves
     \
      $world

When invoking mcrun WITHOUT a world name as a parameter:

$mcDir
|\
| $world
|  \
|   minecraft_server.jar or craftbukkit.jar
|   mcrun
 \
  saves
   \
    $world

mcrun / mcrun.py will create the "saves" directory and subdirectories if they
don't exist. Symlinks can be used for any directories or files if desired.
