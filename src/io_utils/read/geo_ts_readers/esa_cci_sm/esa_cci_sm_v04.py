# -*- coding: utf-8 -*-

"""
Time series reader for CCI SM v04 data
"""
# TODO:
#   (+)
#---------
# NOTES:
#   -

from io_utils.read.path_config import PathConfig
from datetime import datetime
from io_utils.read.geo_ts_readers.esa_cci_sm.base_reader import SmecvTs
import numpy as np
try:
    from io_utils.path_configs.esa_cci_sm.paths_esa_cci_sm_v04 import path_settings
    from io_utils.path_configs.esa_cci_sm.paths_esa_cci_sm_v04_ADJUSTMENT import \
        path_settings as adjusted_paths
    path_settings.update(adjusted_paths)
except ImportError:
    path_settings = {}

class GeoCCISMv4Ts(SmecvTs):
    # Reader implementation that uses the PATH configuration from above

    # exact time variable (days) from reference date
    _t0_ref = ('t0', datetime(1970,1,1,0,0,0))

    # fill values in the data columns
    _col_fillvalues = {'sm': [-9999.0],
                       'sm_uncertainty': [-9999.0],
                       _t0_ref[0]: [-3440586.5,
                                    -9999.0]} # TODO: why has v045 another fillvalue?

    # implememted subversion that have a set path configuration
    _ds_implemented = [('ESA_CCI_SM', 'v045', 'ACTIVE'),
                       ('ESA_CCI_SM', 'v045', 'PASSIVE'),
                       ('ESA_CCI_SM', 'v045', 'COMBINED'),
                       ('ESA_CCI_SM', 'v045', 'COMBINED', 'ADJUSTED', 'QCM', 'ERA5'),
                       # exact index fails for versions <47
                       ('ESA_CCI_SM', 'v047', 'COMBINED'),
                       ('ESA_CCI_SM', 'v047', 'ACTIVE'),
                       ('ESA_CCI_SM', 'v047', 'PASSIVE')]


    def __init__(self, dataset_or_path, exact_index=False, force_path_group=None, **kwargs):

        if isinstance(dataset_or_path, list):
            dataset_or_path = tuple(dataset_or_path)

        self.dataset = dataset_or_path

        path_config = path_settings[self.dataset] if self.dataset in path_settings.keys() else None
        self.path_config = PathConfig(self.dataset, path_config)
        ts_path = self.path_config.load_path(force_path_group=force_path_group)

        super(GeoCCISMv4Ts, self).__init__(ts_path, exact_index=exact_index,
                                           **kwargs)

    def _replace_with_nan(self, df):
        """
        Replace the fill values in columns defined in _col_fillvalues with NaN
        """
        for col in df.columns:
            if col in self._col_fillvalues.keys():
                for fv in self._col_fillvalues[col]:
                    if self.scale_factors is not None and \
                            col in self.scale_factors.keys():
                        fv = fv * self.scale_factors[col]
                    df.loc[df[col] == fv, col] = np.nan
        return df

    def read(self, *args, **kwargs):
        return self._replace_with_nan(super(GeoCCISMv4Ts, self).read(*args, **kwargs))

# check if datasets in reader and in dict match
assert sorted(list(path_settings.keys())) == sorted(GeoCCISMv4Ts._ds_implemented)

if __name__ == '__main__':
    ds = GeoCCISMv4Ts(r"R:\Projects\CCIplus_Soil_Moisture\07_data\ESA_CCI_SM_v06.1\064_break_correction\combined\ESA_CCI_SM_v061_COMBINED_ADJUSTED_QCM")
    ts47 = ds.read(26.68595, 67.35922)
