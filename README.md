# SFMC-RNC

These Python scripts fetch and format individual NOAA RNC tiles for use by SFMC

**Prerequisites:**

These scripts were tested on a CentOS7 minimal system with python3.6. To setup Python do the following as root:

- **yum install git**
- **yum install python36**
- **yum install python36-pip**
- **pip3.6 install requests**
- **pip3.6 install Pillow**

**mbtilesFetch.py**

Serves two functions. The first is to fetch entire NOAA RNC panels as SQLite3 mtile files.
The second is to update existing local SQLite3 mtile files. The full set of mtile files is 11GB.

To fetch all the NOAA RNC panels do:

- **./mbtilesFetch.py**

This will fetch all the panels and store them in the MBTILES directory.

NOAA Updates the RNC files monthly, so every month one can update the existing tiles with:

- **./mbtilesFetch.py --update**

To see the command line options:

- **./mbtilesFetch.py --help**

**mbtilesQuilt.py**

Takes the mtile files and creates a directory tree of tiles suitable for placing in
/opt/sfmc-webserver/static/maps and then consumed by SFMC clients. If a tile is in multiple panels, they are overlayed or "Quilted" together. The resulting directory tree is ~17GB for a full set of tiles.

To build a directory of tiles, please start with an empty directory.

- **./mbtilesQuilt.py**

This will create a directory tree under RNC_ROOT. To make this available for SFMC clients do the following as root:

- **rm -rf /opt/sfmc-webserver/static/maps/RNC_ROOT**
- **chown -R sfmc-webserver:sfmc-webserver RNC_ROOT**
- **mv RNC_ROOT /opt/sfmc-webserver/static/maps**

To see the command line options:

- **./mbtilesQuilt.py --help**

**SFMC setup**

To use the set of tiles, in the SFMC page under your user name, go to "Map Settings" 
and then click on "Create Map Tile Layer Setting" 
In the "Create Map Tile Layer Setting Form" name the layer as you want. Click the TMS box.
Enter "/sfmc/static/maps/RNC_ROOT/{z}/{y}/{x}.png" in the URL Template box.
Enter NOAA in the Attribution box.
