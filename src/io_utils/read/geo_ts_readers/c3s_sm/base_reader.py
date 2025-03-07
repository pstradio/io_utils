# -*- coding: utf-8 -*-

"""
The basic, unchanged time series reader for the c3s time series, as in the
c3s_sm package.
"""
# TODO:
#   (+) Use the reader from the c3s package directly?
#---------
# NOTES:
#   -
from datetime import datetime
import pandas as pd
import numpy as np
from io_utils.read.geo_ts_readers.esa_cci_sm.base_reader import SmecvTs

class GeoC3STs(SmecvTs):
    # Reader implementation that uses the PATH configuration from above
    # Flagging should be done with the masking adapter from pytesmo
    _t0_ref = ('t0', datetime(1970,1,1,0,0,0)) # todo: use t0 from metadata

    _col_fillvalues = {'sm': [-9999.0],
                       'sm_uncertainty': [-9999.0],
                       _t0_ref[0]: [-3440586.5, -9999.]}

    def __init__(self, ts_path, **kwargs):
        """
        Parameters
        ----------
        ts_path : str
            Path to where the data is stored
        **kwargs :
            Additional kwargs are passed to SmecvTs
        """

        super(GeoC3STs, self).__init__(ts_path, **kwargs)

    def _replace_with_nan(self, df):
        """
        Replace the fill values in columns defined in __new__ with NaN
        """
        for col in df.columns:
            if col in self._col_fillvalues.keys():
                for fv in self._col_fillvalues[col]:
                    if self.scale_factors is not None and \
                            col in self.scale_factors.keys():
                        fv = fv * self.scale_factors[col]
                    df.loc[df[col] == fv, col] = np.nan
        return df

    def _add_time(self, df):
        t0 = self._t0_ref[0]
        if t0 in df.columns:
            dt = pd.to_timedelta(df[t0], unit='d')
            df['_datetime'] = pd.Series(index=df.index, data=self._t0_ref[1]) + dt
            if self.exact_index:
                df['_date'] = df.index
                df = df.set_index('_datetime')
                df = df[df.index.notnull()]

        return df

    def read(self, *args, **kwargs):
        return self._add_time(self._replace_with_nan(
            super(GeoC3STs, self).read(*args, **kwargs)))

if __name__ == '__main__':
    # ds = C3STs(r"R:\Datapool_processed\C3S\v201706\TCDR\063_images_to_ts\combined-daily")
    # ds.read(15,45)
    ds_new = GeoC3STs("/home/wpreimes/shares/radar/Datapool/C3S/02_processed/v201912/TCDR/063_images_to_ts/combined-daily",
                      exact_index=True)
    ts_new = ds_new.read(659123)

