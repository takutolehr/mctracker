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
import binascii
import glob
import gzip
import json
import os
import re
import struct
import shutil
import sys
import time
import urllib2


def extract_positions(data):

    pos = data.find('\x03Pos')
    if pos:
        xyz = data[pos+9:pos+33]
        fmt = struct.Struct(">ddd")
        return fmt.unpack(xyz) 
    return None


def extract_dimension(data):

    pos = data.find('\x09Dimension')
    if pos:
        return struct.unpack('>i', data[pos+10:pos+14])[0]
    return 0


def extract_items(data, include_enderchest=False):
    
    ender_start_pos = data.find('\x0aEnderItems')

    items = {}
    for item_id in re.finditer('\x08\x00\x02id', data):
        pos = item_id.start() + 2
        if not include_enderchest and pos > ender_start_pos: break

        item_id_length = int(binascii.hexlify(data[pos+4]), 16)
        pos += 4 + 1
        item_id = data[pos:pos+item_id_length][10:]

        item_count = int(binascii.hexlify(data[data.find('\x05Count')+6]), 16)
        if item_id in items:
            items[item_id] += item_count
        else:
            items[item_id] = item_count

    return items


def format_items_input(items):
    
    out = []
    for item in items:
        item = item.replace('^minecraft:', '')
        
        tmp = item.split(':')
        if len(tmp) > 1:
            out.append((tmp[0], tmp[1]))
        else:
            out.append((tmp[0], 0))
    return out


def search(x_pair, y_pair, z_pair, items=[], disp_inventory=False, disable_api=False, name_filter='', include_enderchest=False):
    """
    Searches against the player.dat files stored in the tracking directory created by snapshot.py.
    
    items:
        Filter players by the list of Minecraft item ID.
    
    disp_inventory:
        Displays player's full inventory.

    disable_api:
        Disables name lookup against the Mojang's API.
    """

    name_api_cache = {}

    if items: items = format_items_input(items)

    #for date_dir in sorted(glob.glob('%s/tracking/*' % os.environ['MCSERVERDIR'])):
    for date_dir in ['']:
        dt = os.path.basename(date_dir)
        
        #for player_dat in sorted(glob.glob('%s/*.dat' % date_dir), key=os.path.getmtime):
        for player_dat in sorted(glob.glob('tracking/*')):

            uuid = os.path.basename(player_dat)[:-4]
            tmp = '/tmp/%s.gz' % uuid
            shutil.copyfile(player_dat, tmp)

            with gzip.open(tmp, "rb") as f:
                data = f.read()
            os.remove(tmp)
                
            xyz = extract_positions(data)
            if xyz: x, y, z = xyz

            if not(min(x_pair) <= x <= max(x_pair) \
                and min(y_pair) <= y <= max(y_pair) \
                and min(z_pair) <= z <= max(z_pair)): continue

            player_items = {}
            if items or disp_inventory:
                player_inventory = extract_items(data, include_enderchest)

            items_found = {}
            if items:
                for item, min_count in items:
                    for inventory_item in player_inventory.items():
                        if item == inventory_item[0] and int(min_count) < int(inventory_item[1]):
                            items_found[item] = inventory_item[1]
                if not items_found: continue

            name = uuid
            if not disable_api:
                if uuid in name_api_cache:
                    name = name_api_cache[uuid]
                else:
                    url = 'https://api.mojang.com/user/profiles/%s/names' % uuid.replace('-', '')
                    response = urllib2.urlopen(url)
                    if response.code is 200:
                        names = json.loads(response.read())
                        name = names[-1]['name']
                        name_api_cache[uuid] = name
                    time.sleep(1)
            if name_filter and name_filter != name: continue

            dimension_def = {-1:'[N]', 0:'[O]', 1:'[E]'}
            dimension = dimension_def[extract_dimension(data)]
            
            out = '[%s] \x1b[1;34m%s\x1b[0m \x1b[1;31m%s\x1b[0m \x1b[1;32m%s %s %s\x1b[0m' % (dt, name, dimension, int(x) , int(y) , int(z))
            if items_found: out = '%s %s' % (out, str(items_found))

            print out
            if disp_inventory: print player_inventory


if __name__ == "__main__":
    
    if not 'MCSERVERDIR' in os.environ:
        print 'requires environment variable MCSERVERDIR'    
        sys.exit(0)

    SERVERDIR = os.environ['MCSERVERDIR']

    parser = argparse.ArgumentParser(prog='search.py')
    parser.add_argument('-i', default=False, action='store_true', dest='disp_inventory', help='display inventory')
    parser.add_argument('-d', default=False, action='store_true', dest='disable_api', help='disable mojang api call')
    parser.add_argument('-e', default=False, action='store_true', dest='include_enderchest', help='include ender chest')
    parser.add_argument('-n', default='', dest='name_or_uuid', help='filter by name or uuid with -dn')
    parser.add_argument('x1', type=int, help='x1')
    parser.add_argument('y1', type=int, help='y1')
    parser.add_argument('z1', type=int, help='z1')
    parser.add_argument('x2', type=int, help='x2')
    parser.add_argument('y2', type=int, help='y2')
    parser.add_argument('z2', type=int, help='z2')
    parser.add_argument('items', nargs='*', help='filter by items')
    args = parser.parse_args()

    search((args.x1, args.x2), (args.y1, args.y2), (args.z1, args.z2), args.items, args.disp_inventory, args.disable_api, args.name_or_uuid, args.include_enderchest)
