Minecraft Wrapper Scripts

################################################################################

In use (not currently being developed):
mcrun (bash)

Snippets for integration into other scripts:
mcparams (bash)
mcchat (bash)

Under development:
mcrun.py (python2 / python3)

################################################################################

When invoking mcrun with a world name as a parameter, the following directory
structure is assumed:

$HOME
 \
  minecraft
  |\
  | $world
  |  \
  |   minecraft_server.jar
   \
    saves
     \
      $world

When invoking mcrun WITHOUT a world name as a parameter:

$mcDir
|\
| $world
|  \
|   minecraft_server.jar
|   mcrun
 \
  saves
   \
    $world

mcrun will create the "saves" directory and subdirectories if they don't exist.
Symlinks can be used for any of these directories or files if desired.
