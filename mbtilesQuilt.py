#! /usr/bin/env python36
#
# Go through MTiles files and build a TMS mapping
#
# Feb-2019, Pat Welch, pat@mousebrains.com
#

import os
import os.path
import io
import argparse
from tempfile import NamedTemporaryFile
import sqlite3
from PIL import Image
from PIL.PngImagePlugin import PngInfo





def mergeImage(ofn, png, qVerbose):
    if qVerbose:
        print('Merging', ofn, len(png))
    with NamedTemporaryFile(delete=False) as ifp:
        ifp.write(png)
        ifp.flush()
        ifp.close()
        im0 = Image.open(ofn).convert('RGBA')
        im1 = Image.open(ifp.name).convert('RGBA')
        im2 = Image.alpha_composite(im0, im1).convert('P')
        im2.save(ofn)
        ifp.close()


parser = argparse.ArgumentParser()
parser.add_argument('panels', nargs='*', default=None, help='MTiles files to process')
verbose = parser.add_mutually_exclusive_group()
verbose.add_argument('--verbose', action='store_true', default=True,
                     help='Output diagnositcs')
verbose.add_argument('--quiet', action='store_false', default=False,
                     help='No non-error output')
parser.add_argument('--indir', default='RNC_ROOT',
                    help='input files')
parser.add_argument('--outdir', default='RNC_ROOT',
                    help='where to write output to')
parser.add_argument('--flip_y', default=True,
                    help='Flip Y axis for non-TMS servers')
parser.add_argument('--metadataUnits', default="feet",
                    choices=["feet", "metric", "oldFormatMBTiles"],
                    help='Add metadata depth units')
parser.add_argument('--merge', default=True,
                    help='Enable merging of tiles - otherwise overwrite')
args = parser.parse_args()

if len(args.panels) == 0:
    args.panels = [
                    "01a",
                    "01b",
                    "02a",
                    "02b",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17a",
                    "17b",
                    "18",
                    "19",
                    "19b",
                    "19c",
                    "19d",
                    "20a",
                    "20b",
                    "20c", # seattle
                    "21",
                    "22a",
                    "22b",
                    "23a",
                    "23b",
                    "24a",
                    "24b",
                    "25a",
                    "25b",
                    "26a",
                    "26b",
                    "27",
                    "28a",
                    "28b",
                    "29",
                    "30",
                    "31a",
                    "31b"
                    ]

for panel in args.panels:
    fn = os.path.join(args.indir, "ncds_{}.mbtiles".format(panel))
    count = 0
    if not args.quiet:
        print('')
        print('Opening', fn)
    with sqlite3.connect(fn) as conn:
        with sqlite3.connect(fn) as conn_meta:
            results = conn.execute('SELECT * FROM tiles;')
            for result in results:  # Walk over rows
                (zoom, column, row, png) = result

                imSize = len(png)
                if imSize in [190, # transparent
                              # 177, # pure orange background
                              # 355 pure white
                              ]:  
                    continue

                

                metadata = None
                if args.metadataUnits == "feet":
                    metadata = ' {"units": "feet"}'
                elif args.metadataUnits == "metric":
                    metadata = ' {"units": "metric"}'
                elif args.metadataUnits == "oldFormatMBTiles":
                    if zoom <= 7:
                        continue
                    metas = conn_meta.execute("SELECT * FROM map WHERE zoom_level = " + str(zoom) + " AND tile_column = " + str(column) + " AND tile_row = " + str(row) + ";")
                    kj = None
                    for meta in metas:
                        (z, c, r, kn, kj) = meta
                    if kj:
                        metadata = kj

                # jayb Y is inverted in TMS (default format for MBTiles)
                if args.flip_y:
                    row = (2 ** zoom) - (1 + row)
                odir = os.path.join(args.outdir, 'Z' + str(zoom), str(row))
                ofn = os.path.join(odir, '{}.png'.format(column))
                if not os.path.isdir(odir):
                    # if args.verbose:
                    #   print('Making directory', odir)
                    os.makedirs(odir)
                count = count + 1
                if count % 100 == 0:
                    print(".", end='')
                    if count % 10000 == 0:
                        print(count, panel) # newline

                if args.merge and os.path.exists(ofn):
                        mergeImage(ofn, png, args.verbose)
                else:  # Does not exist
                    if args.verbose:
                        j = 1
                        # print('Saving', ofn, 'length', len(png))
                    if metadata is None:
                        with open(ofn, 'wb') as ofp:
                            ofp.write(png)
                    else:
                        targetImage = Image.open(io.BytesIO(png))
                        #targetImage = Image.frombytes(png)
                        #targetImage.fromstring(png)
                        metainfo = PngInfo()
                        metainfo.add_text("meta", metadata)
                        targetImage.save(ofn, pnginfo=metainfo)
