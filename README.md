#  mctracker

This software is for tracking players in Minecraft servers.

### Installation

Set environment variable MCSERVERDIR.

```sh
$ export MCSERVERDIR=/path/to/mcserverdir/
```

Enter following command in terminal to add a scheduled task (http://crontab.org/).

```sh
$ crontab -e
```
Add the following line at the end of your crontab to take a snapshot of the player.dat files every 3 minutes.
```sh
*/3 * * * * MCSERVERDIR=/path/to/serverdir/ python /path/to/snapshot.py
```

### Usage

The search program will parse the player .dat files stored by the snapshot.py program.  It takes coords of the oposite corners of a square, similar to the /fill command in Minecraft.

```sh
# Find players in area.
$ python search.py 100 1 100 200 255 200

>>> [2015-07-21 23:06] ze6ra 100 86 130
>>> [2015-07-21 23:09] ze6ra 120 87 160

# Find players in area that has diamond_sword or more than 2 diamond_pickaxe.
python search.py -i 100 1 100 300 255 300 diamond_sword diamond_pickaxe:2

>>> [2015-07-21 23:06] ze6ra 100 86 130 {'diamond_pickaxe': 2}
{'diamond_sword': 1, 'torch': 37, 'enchanted_book': 3, 'diamond_pickaxe': 2}
>>> [2015-07-21 23:09] ze6ra 120 87 160 {'diamond_pickaxe': 4}
{'diamond_sword': 1, 'torch': 37, 'enchanted_book': 2, 'diamond_pickaxe': 4, 'bread': 4}
```

###### options

```sh
usage: search.py [-h] [-i] [-d] [-e] [-n NAME_OR_UUID]
               x1 y1 z1 x2 y2 z2 [items [items ...]]

positional arguments:
  x1              x1
  y1              y1
  z1              z1
  x2              x2
  y2              y2
  z2              z2
  items           filter by item_id and count. ex. diamond iron_sword:2

optional arguments:
  -h, --help      show this help message and exit
  -i              display inventory
  -d              disable mojang api call
  -e              include ender chest
  -n NAME_OR_UUID filter by name or uuid with -dn

```

### Link

RawMinecraft (http://rawminecraft.com:8080/)
