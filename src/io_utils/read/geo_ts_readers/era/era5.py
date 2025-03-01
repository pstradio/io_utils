# -*- coding: utf-8 -*-

"""
Time series reader for ERA5 and ERA5 Land data
"""
# TODO:
#   (+) 
#---------
# NOTES:
#   -

from io_utils.read.geo_ts_readers.era.base_reader import ERATs
from io_utils.read.path_config import PathConfig
try:
    from io_utils.path_configs.era.paths_era5 import path_settings
except ImportError:
    path_settings = {}


class GeoEra5Ts(ERATs):
    # Reader implementation that uses the PATH configuration from above

    _ds_implemented = [('ERA5', 'core')]

    def __init__(self, dataset_or_path, force_path_group=None, **kwargs):

        if isinstance(dataset_or_path, list):
            dataset_or_path = tuple(dataset_or_path)

        self.dataset = dataset_or_path

        path_config = path_settings[self.dataset] if self.dataset in path_settings.keys() else None
        self.path_config = PathConfig(self.dataset, path_config)
        ts_path = self.path_config.load_path(force_path_group=force_path_group)

        super(GeoEra5Ts, self).__init__(ts_path, **kwargs)


# check if datasets in reader and in dict match
assert sorted(list(path_settings.keys())) == sorted(GeoEra5Ts._ds_implemented)

if __name__ == '__main__':
    reader = GeoEra5Ts(dataset_or_path=('ERA5', 'core'),
                       ioclass_kws={'read_bulk': True},
                       parameters=['swvl1', 'stl1'], scale_factors={'swvl1': 1.})
    ts = reader.read(15,48)
    print(ts)