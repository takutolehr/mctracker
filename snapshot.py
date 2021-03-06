"""
The MIT License (MIT)

Copyright (c) 2015 Takuto Lehr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import argparse
import datetime
import glob
import os
import re
import shutil
import sys
import time

NUM_SNAPSHOTS = 2000 # Number of snapshots to keep.

def extract_player_cap(prop):

    with open(prop, 'r') as f:
        for line in f.readlines():
            m = re.search('^max-players=(\d+)', line)
            if m: return int(m.groups()[0])

    raise Exception('Failed to get server property max-players')


def snapshot():
    """
    Saves the player.dat files into a timestamped directory. This function should be
    called from the crontab with -s option.
    """

    SERVERDIR = os.environ['MCSERVERDIR']
    SNAPSHOTS_DIR = '%s/tracking' % SERVERDIR

    if not os.path.exists(SERVERDIR): raise ValueError('Invalid SERVERDIR')
    if not os.path.exists('%s/world/playerdata/' % SERVERDIR): raise ValueError('Invalid SERVERDIR')
    
    SNAPSHOTS_PLAYER_CAP = extract_player_cap('%s/server.properties' % SERVERDIR)

    dtime = time.strftime("%Y-%m-%d %H:%M")
    players = sorted(glob.glob('%s/world/playerdata/*' % SERVERDIR), key=os.path.getmtime)

    if not os.path.exists(SNAPSHOTS_DIR): os.makedirs(SNAPSHOTS_DIR)
    
    cur_ts_dir = "%s/%s" % (SNAPSHOTS_DIR, dtime)
    if os.path.exists(cur_ts_dir): return

    ts_dirs = sorted(glob.glob('%s/*' % SNAPSHOTS_DIR))
    if not ts_dirs:
        os.makedirs(cur_ts_dir)
        for player in players[-SNAPSHOTS_PLAYER_CAP:]:
            shutil.copy2(player, cur_ts_dir)
        return

    os.makedirs(cur_ts_dir)

    for d in ts_dirs[:-NUM_SNAPSHOTS]:
        shutil.rmtree(d)

    last_ts_dir = ts_dirs[-1]
    last_ts = os.path.basename(last_ts_dir)

    lastrecord_t = datetime.datetime.strptime(last_ts, '%Y-%m-%d %H:%M')
    for player in players[-SNAPSHOTS_PLAYER_CAP:]: # Only store updated files.
        if lastrecord_t < datetime.datetime.fromtimestamp(os.path.getmtime(player)):
            shutil.copy2(player, cur_ts_dir)
    

if __name__ == "__main__":
    
    """
    Make a following entry to your crontab (http://crontab.org/) to take snapshot 
    of the player.dat files every 5 minutes.
    
    */5 * * * * /usr/bin/python /path/to/this/snapshot.py /path/to/minecraftserver/
    """

    if not 'MCSERVERDIR' in os.environ:
        print 'requires environment variable MCSERVERDIR'    
        sys.exit(0)

    snapshot()
