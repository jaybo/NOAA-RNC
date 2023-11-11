#!/usr/bin/env python
import sys, os
import json
import shapely
from shapely.geometry import Polygon, Point, mapping, shape

from globalmaptiles import GlobalMercator

mercator = GlobalMercator()

def tileIsInPolygon (x, y, zoom, poly: Polygon):
    minLat, minLon, maxLat, maxLon = mercator.TileLatLonBounds(x, y, zoom)
    center = [(minLon + maxLon) / 2, (minLat + maxLat) /2]
    return poly.contains(Point(center))



if __name__ == "__main__":

    polyT = ''' 
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              -123.30876765823416,
              49.005873928239964
            ],
            [
              -123.30876765823416,
              47.15354490153183
            ],
            [
              -121.32840885365304,
              47.1565673245137
            ],
            [
              -121.35063453394048,
              49.005873928239964
            ],
            [
              -123.30876765823416,
              49.005873928239964
            ]
          ]
        ],
        "type": "Polygon"
      }
    }
  ]
}
    '''
    polyjson = json.loads(polyT)
    poly = Polygon(polyjson["features"][0]["geometry"]["coordinates"][0])
    print (tileIsInPolygon(164, 666, 10, poly))
