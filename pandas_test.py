import scipy.io as sio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from EM1PythonDictionaries import (
    variable_meanings,
    variable_symbols,
    variable_units,
    variable_yticks,
    variables_list,
    parameter_meanings,
    parameter_symbols,
    parameter_units,
)


def mat_to_DataFrame(file_path, chosen_structure="post", chosen_substructure="zerod"):
    mat_data = sio.loadmat(file_path)
    structure = mat_data[chosen_structure]
    substructure = structure[chosen_substructure][0, 0]

    # Create a dictionary of the field names and corresponding data, one for arrays and one for scalars
    array_data_dict = {}
    scalar_data_dict = {}
    for field_name in substructure.dtype.names:
        field_data = substructure[field_name][0, 0]
        if field_data.size == 1:  # if scalar
            scalar_data_dict[field_name] = field_data[0]
        else:  # if array
            array_data_dict[field_name] = field_data.squeeze()

    # Convert the array dictionary to a pandas DataFrame
    df = pd.DataFrame(array_data_dict)

    # Convert the scalar data to a pandas Series
    series = pd.Series(scalar_data_dict)

    return df


default_index_dataframe = mat_to_DataFrame(
    "EM1 Data/4th Run Data (fast mode)/2023-01-27 NBI Power 2MW B0 0.1T.mat"
)
temps_index_dataframe = default_index_dataframe.set_index("temps")
# print(temps_index_dataframe)

for column in temps_index_dataframe.columns:
    if column not in variables_list:
        temps_index_dataframe.drop(column, axis=1, inplace=True)


# print(temps_index_dataframe)

# TODO Add nttau to the list of variables
