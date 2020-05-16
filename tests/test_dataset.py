
import pytest

import pathlib
import spagat.dataset as spd


def test_read_and_save_sds():
    sds_folder_path_in = pathlib.Path('spagat/tests/data/input')
    sds_folder_path_out = pathlib.Path('spagat/tests/data/output')

    sds = spd.SpagatDataSet()

    sds.read_dataset(sds_folder_path_in)
    sds.save_sds(sds_folder_path_out)

def test_add_time_series_from_csv():
    '''Region time series from a csv file are read and added to the dataset'''


