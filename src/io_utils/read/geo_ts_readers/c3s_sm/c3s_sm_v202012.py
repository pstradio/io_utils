# -*- coding: utf-8 -*-

"""
Time series reader for C3S v201812 active, combined and passive data
"""
from io_utils.read.path_config import PathConfig
from io_utils.read.geo_ts_readers.c3s_sm import base_reader
try:
    from io_utils.path_configs.c3s_sm.paths_c3s_sm_v202012 import path_settings
except ImportError:
    path_settings = {}
from datetime import datetime

class GeoC3Sv202012Ts(base_reader.GeoC3STs):
    # Reader implementation that uses the PATH configuration from above
    # Flagging should be done with the masking adapter from pytesmo
    _t0_ref = ('t0', datetime(1970,1,1,0,0,0))

    _col_fillvalues = {'sm': [-9999.0],
                       'sm_uncertainty': [-9999.0],
                       _t0_ref[0]: [-3440586.5]}

    _ds_implemented = [
        ('C3S', 'v202012', 'COMBINED', 'DAILY', 'TCDR'),
        ('C3S', 'v202012', 'ACTIVE', 'DAILY', 'TCDR'),
        ('C3S', 'v202012', 'PASSIVE', 'DAILY', 'TCDR'),
        ('C3S', 'v202012', 'COMBINED', 'MONTHLY', 'TCDR'),
        ('C3S', 'v202012', 'ACTIVE', 'MONTHLY', 'TCDR'),
        ('C3S', 'v202012', 'PASSIVE', 'MONTHLY', 'TCDR'),
        ('C3S', 'v202012', 'COMBINED', 'DEKADAL', 'TCDR'),
        ('C3S', 'v202012', 'ACTIVE', 'DEKADAL', 'TCDR'),
        ('C3S', 'v202012', 'PASSIVE', 'DEKADAL', 'TCDR'),
    ]

    def __init__(self, dataset_or_path, force_path_group=None, **kwargs):
        """
        Parameters
        ----------
        dataset : tuple or string
            e.g. ('C3S', 'v201812', 'COMBINED', 'TCDR')
        force_path_group : str, optional (default: None)
            Select a specific path group from the path config to read.
        kwargs :
            kwargs that are passed to load_path and to initialise the reader.
        """
        if isinstance(dataset_or_path, list):
            dataset_or_path = tuple(dataset_or_path)

        self.dataset = dataset_or_path
        path_config = path_settings[self.dataset] if self.dataset in path_settings.keys() else None
        self.path_config = PathConfig(self.dataset, path_config)
        ts_path = self.path_config.load_path(force_path_group=force_path_group)

        super(GeoC3Sv202012Ts, self).__init__(ts_path, **kwargs)

# check if datasets in reader and in dict match
assert sorted(list(path_settings.keys())) == sorted(GeoC3Sv202012Ts._ds_implemented)

