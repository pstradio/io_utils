# -*- coding: utf-8 -*-

"""
Sentinel 1 & 2 based SSM prdduct readers
"""

from equi7grid.equi7grid import Equi7Grid
import yeoda.datacube as dc
from geopathfinder.file_naming import SmartFilename
from collections import OrderedDict
from geopathfinder.folder_naming import build_smarttree
import numpy as np
from osgeo import ogr
from osgeo import osr
from datetime import datetime
import copy
import os

"""
TODO yeoda:
- Add option to build data cube for a limited time range (faster)
"""

def decode(data):
    data = data.astype(float)
    data[data>=240] = np.nan
    data /= 2.
    return data

class CglsS1Filename(SmartFilename):
    _fields_def = OrderedDict([
        ('head', {'len': 5}),
        ('var_name', {'len': 6}),
        ('time', {'len': 12,
                  'decoder': lambda x: datetime.strptime(x, "%Y%m%d%H%M"),
                  'encoder': lambda x: x.strftime("%Y%m%d%H%M") if isinstance(x, datetime) else x}),
        ('area', {'len': 5}),
        ('sensor', {'len': 6}),
        ('tail', {}),  # tail seems to vary, so we cannot specify it statically
    ])
    _pad = "-"
    _delimiter = "_"

    def __init__(self, fields, ext=".tiff", convert=False):
        super().__init__(fields, CglsS1Filename._fields_def, pad=CglsS1Filename._pad,
                         delimiter=CglsS1Filename._delimiter, convert=convert, ext=ext)

    @classmethod
    def from_filename(cls, filename_str, convert=False):
        fn_parts = os.path.splitext(os.path.basename(filename_str))[0] \
                   .split(CglsS1Filename._delimiter)
        fields_def_ext = copy.deepcopy(CglsS1Filename._fields_def)
        fields_def_ext['var_name']['len'] = len(fn_parts[2])  # variable is on position 3 if we split it with "_"
        fields_def_ext['tail']['len'] = len("_".join(fn_parts[4:]))  # everything after timestamp is the tail

        return super().from_filename(filename_str, fields_def_ext, 
                                     pad=CglsS1Filename._pad,
                                     delimiter=CglsS1Filename._delimiter, 
                                     convert=convert)

class CSarTiffReader(object):

    def __init__(self, path, grid_sampling=500, param_rename='ssm'):
        
        self.path = path

        self.grid_sampling = grid_sampling
        self.datacube = None
        self.grid = None
        self.dc = None

        self.param_rename = param_rename

    def _setUp(self):
        # build data cube
        if self.grid is None:
            self.grid = Equi7Grid(self.grid_sampling).EU

        self.sref = osr.SpatialReference()
        self.sref.ImportFromEPSG(4326)

        dir_tree = build_smarttree(self.path, hierarchy=[],
                                   register_file_pattern="^[^Q].*.tiff")

        filepaths = dir_tree.file_register
        dim = ["time", "area", "var_name"]

        self.dc = dc.EODataCube(filepaths=filepaths,
                                smart_filename_class=CglsS1Filename,
                                dimensions=dim)

    def read(self, *args, **kwargs):
        """ Read data for a single point from data cube """

        if self.dc is None:
            self._setUp()
            
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(*args, **kwargs)

        ts = self.dc.filter_spatially_by_geom(point, sref=self.sref)
        df = ts.load_by_coords(point.GetX(), point.GetY(), sref=self.sref,
                               dtype="dataframe")
        df = df.set_index(df.index.get_level_values('time'))
        df = df[~df.index.duplicated(keep='last')]

        return decode(df).rename(columns={'1': self.param_rename})


# class CSarNcTsReader():
#     def __init__(self, path):

if __name__ == '__main__':
    path = r"C:\Temp\delete_me\geotiff\in"
    str(datetime.now())
    reader = CSarTiffReader(path)
    lon, lat = 15.7,47
    str(datetime.now())
    ts = reader.read(lon, lat)
    print(ts)
