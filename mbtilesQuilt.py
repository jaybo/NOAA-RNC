#! /usr/bin/env python36
#
# Go through MTiles files and build a TMS mapping
#
# Feb-2019, Pat Welch, pat@mousebrains.com
#
import sqlite3
import os
import os.path
import argparse
from tempfile import NamedTemporaryFile
from PIL import Image

def mergeImage(ofn, png, qVerbose):
  if qVerbose:
    print('Merging', ofn)
  with NamedTemporaryFile() as ifp:
    ifp.write(png)
    ifp.flush()
    im0 = Image.open(ofn).convert('RGBA')
    im1 = Image.open(ifp.name).convert('RGBA')
    im2 = Image.alpha_composite(im0, im1).convert('P')
    im2.save(ofn)

parser = argparse.ArgumentParser()
parser.add_argument('mtiles', nargs='+', help='MTiles files to process')
verbose = parser.add_mutually_exclusive_group()
verbose.add_argument('--verbose', action='store_true', help='Output diagnositcs')
verbose.add_argument('--quiet', action='store_true', help='No non-error output')
parser.add_argument('--outdir', default='RNC_ROOT', help='where to write output to')
args = parser.parse_args()

for fn in args.mtiles:
  if not args.quiet:
    print('Opening', fn)
  with sqlite3.connect(fn) as conn:
    results = conn.execute('SELECT * FROM tiles;')
    for result in results: # Walk over rows
      (zoom, column, row, png) = result;
      odir = os.path.join(args.outdir, str(zoom), str(row))
      ofn = os.path.join(odir, '{}.png'.format(column))
      if not os.path.isdir(odir):
        if args.verbose:
          print('Making directory', odir)
        os.makedirs(odir)
      if os.path.exists(ofn):
        mergeImage(ofn, png, args.verbose)
      else: # Does not exist
        if args.verbose:
          print('Saving', ofn, 'length', len(png))
        with open(ofn, 'wb') as ofp:
          ofp.write(png)
