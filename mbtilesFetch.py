#! /usr/bin/env python36
#
# Grab the latest MBTiles files from NOAA for the RNC images
#
# Feb-2019, Pat Welch, pat@mousebrains.com
#
import argparse
import json
import os
import os.path
import sqlite3
from tempfile import NamedTemporaryFile

import requests


def applyUpdate(content, ofn, qVerbose):
    with NamedTemporaryFile() as sfp:
        sfp.write(content)
        sfn = sfp.name
        with sqlite3.connect(sfn) as uconn, \
                sqlite3.connect(ofn) as oconn:
            # Get all the tile updates
            results = uconn.execute('SELECT * FROM tiles;').fetchall()
            for result in results:
                (zoom, column, row, png) = result
                if qVerbose:
                    print('Replacing ({},{},{},{}) in {}'.format(
                        zoom, column, row, len(png), ofn))
                oconn.execute('INSERT OR REPLACE INTO tiles (zoom_level,tile_column,tile_row,tile_data) VALUES(?,?,?,?);',
                              (zoom, column, row, png))
            oconn.commit()


def procDeletes(ofn, content, qVerbose):
    with sqlite3.connect(ofn) as conn:
        a = json.loads(content)
        for item in a['deleted_tiles']:
            zoom = item['z']
            column = item['x']
            row = item['y']
            if qVerbose:
                print('Deleting zoom={}, column={}, and row={} from {}'.format(
                    zoom, column, row, ofn))
            conn.execute('DELETE FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?;',
                         (zoom, column, row))


parser = argparse.ArgumentParser()
verbose = parser.add_mutually_exclusive_group()
verbose.add_argument('--verbose', action='store_true',
                     help='Output diagnositcs')
verbose.add_argument('--quiet', action='store_true',
                     help='No non-error output')
action = parser.add_mutually_exclusive_group()
action.add_argument('--full', action='store_true', help='Pull a full set')
action.add_argument('--update', action='store_true',
                    help='Pull recent updates')
parser.add_argument('--urlfull', help='NOAA URL for full pulls',
                    default='https://tileservice.charts.noaa.gov/mbtiles/50000_1/MBTILES_{}.mbtiles')
parser.add_argument('--urlupdate', help='NOAA URL for update pulls',
                    default='https://tileservice.charts.noaa.gov/mbtiles/50000_1/MBTILES_{}-updates.mbtiles')
parser.add_argument('--urldelete', help='NOAA URL for delete pulls',
                    default='https://tileservice.charts.noaa.gov/mbtiles/50000_1/MBTILES_{}-deletes.json')
parser.add_argument('--panels', action='append', help='which panels to pull')
parser.add_argument('--outdir', default='MBTILES',
                    help='where to write output to')
args = parser.parse_args()

if args.panels is None:
    args.panels = []
#   for i in range(1, 27):
    for i in range(1, 27):
        args.panels.append('{:02d}'.format(i))

if not args.full and not args.update:
    args.full = True

if args.full:
    urlPattern = args.urlfull
else:
    urlPattern = args.urlupdate

if not os.path.isdir(args.outdir):
    os.makedirs(args.outdir)

if not args.full:  # Pull down any deletes
    for panel in args.panels:
        url = args.urldelete.format(panel)
        r = requests.get(url)
        if r.status_code != 200:
            if r.status_code != 404:
                print('Error fetching', url, 'status_code', r.status_code)
            continue
        ofn = os.path.join(args.outdir, 'MBTILES_{}.mtiles'.format(panel))
        procDeletes(ofn, r.content, args.verbose)

for panel in args.panels:
    ofn = os.path.join(args.outdir, 'MBTILES_{}.mtiles'.format(panel))
    if not args.full and not os.path.exists(ofn):
        print(ofn, 'does not exist to apply an update to')
        continue
    url = urlPattern.format(panel)
    if not args.quiet:
        print('Fetching', url)
    r = requests.get(url)
    if r.status_code != 200:
        if not args.full or r.status_code != 404:
            print('Error fetching', url, 'status_code', r.status_code)
        continue
    if args.full:  # Write out the full database
        with open(ofn, 'wb') as ofp:
            if args.verbose:
                print('Saving', url, 'to', ofn, 'len', len(r.content))
            ofp.write(r.content)
    else:  # Do an update
        applyUpdate(r.content, ofn, args.verbose)
