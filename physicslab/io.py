"""
IO
"""
# __all__ =


import ezodf
import numpy as np
import pandas as pd


def read_ods(filename, sheet_num, skip_rows=0, autoheader=True, dropna=True):
    """ Return a sheet data from an ods file as pandas.DataFrames.

    Assume the header is on the first row following the skipped ones.

    :param filename: String path
    :type filename: str
    :param sheet_num: Number of the sheet to load. Start with zero
    :type sheet_num: int
    :param skip_rows: Skip several top rows, defaults to 0
    :type skip_rows: int, optional
    :param autoheader: Inferred the column names from the first line of
        the data, defaults to True
    :type autoheader: bool, optional
    :param dropna: Drop all rows and columns which contain only missing
        values. E.g. figures can induce empty rows & columns, defaults to True
    :type dropna: bool, optional
    :raises ValueError: If there are no data rows.
    :return: A open document spreadsheet (ods) file is returned as
        two-dimensional data structure with labelled axes.
    :rtype: pandas.DataFrame
    """
    if not filename.endswith('.ods'):
        filename += '.ods'
    document = ezodf.opendoc(filename)
    sheet = document.sheets[sheet_num]

    number_of_header_rows = 1 if autoheader else 0
    number_of_data_rows = sheet.nrows() - skip_rows - number_of_header_rows
    if number_of_data_rows <= 0:
        raise ValueError('Number of data rows must be greater than zero!')

    for i, row in enumerate(sheet.rows()):  # Row is a list of cells.
        row = [cell.value for cell in row]

        if i > skip_rows:  # Data rows.
            data.iloc[i - skip_rows - number_of_header_rows] = row

        elif i == skip_rows:  # Header or first data row.
            data = pd.DataFrame(
                columns=row if autoheader else np.arange(0, sheet.ncols()),
                index=np.arange(0, number_of_data_rows)
            )
            if not autoheader:
                data.iloc[0] = row

        else:  # Skipping those.
            pass

    if dropna:
        data = data.dropna(axis=0, how='all')
        data = data.dropna(axis=1, how='all')
    return data
