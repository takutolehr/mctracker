#  mctracker

This software is for tracking players in Minecraft servers.

### Installation

Enter following command in terminal to add a scheduled task (http://crontab.org/).

```sh
$ crontab -e
```
Add the following line at the end of your crontab to take a snapshot of the player.dat files every 3 minutes.
```sh
*/3 * * * * /usr/bin/python /path/to/this/snapshot.py
```

### Usage

The search program will parse the player .dat files stored by the snapshot.py program.  It takes coords of the oposite corners of a square, similar to the /fill command in Minecraft.

```sh
$ python search.py 100 1 100 2000 255 2000
```


```sh
usage: search.py [-h] [-i] [-d] [-e] [-n NAME_FILTER]
               x1 y1 z1 x2 y2 z2 [items [items ...]]

positional arguments:
  x1              x1
  y1              y1
  z1              z1
  x2              x2
  y2              y2
  z2              z2
  items           filter by items

optional arguments:
  -h, --help      show this help message and exit
  -i              display inventory
  -d              disable mojang api call
  -e              include ender chest
  -n NAME_OR_UUID filter by name or uuid with -dn

```
