from typing import Any

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from EM1PythonClasses import DataProcessor
from EM1PythonDictionaries import (
    parameter_symbols,
    parameter_units,
    variable_meanings,
    variable_symbols,
    variable_units,
)

plt.rcParams["text.usetex"] = True
plt.rcParams["text.latex.preamble"] = "\n".join(
    [
        r"\usepackage{siunitx}",
    ]
)


def plot_averages(
    DataProcessor: DataProcessor,
    variables: list[str],
) -> None:
    fig, axs = generate_fig_and_axs(DataProcessor, variables)
    means_stds = get_means_stds(DataProcessor, variables)

    index = 0
    nrows, ncols = axs.shape

    loop_flag = True
    for row in range(nrows):
        for col in range(ncols):
            if index >= len(variables):
                loop_flag = False
                for i in range(col, ncols):
                    axs[row, i].axis("off")
                break
            variable = variables[index]
            axs[row, col].set_title(
                (
                    f"{variable_meanings[variable]} vs. "
                    f"{parameter_symbols[DataProcessor.primary_x_parameter]}",
                ),
                fontsize=10,
            )
            axs[row, col].set_xlabel(
                f"{parameter_symbols[DataProcessor.primary_x_parameter]} "
                f"({parameter_units[DataProcessor.primary_x_parameter]})"
            )
            axs[row, col].set_ylabel(
                f"{variable_symbols[variable]} ({variable_units[variable]})"
            )
            x = means_stds[f"{DataProcessor.primary_x_parameter}_mean"]
            y = means_stds[f"{variable}_mean"]
            yerr = means_stds[f"{variable}_std"]
            axs[row, col].errorbar(
                x, y, yerr=yerr, fmt=".", color="black", elinewidth=0.5
            )
            index += 1
        if not loop_flag:
            break
    plt.plot()


def generate_fig_and_axs(DataProcessor, variables: list[str]) -> tuple[Figure, Any]:
    num_variables = len(variables)
    # parameter_name = DataProcessor.primary_x_parameter
    ncols: int = min(num_variables, 4)
    nrows: int = (num_variables + ncols - 1) // ncols if num_variables > 4 else 1
    fig: Figure
    axs: Any
    fig, axs = plt.subplots(
        nrows, ncols, figsize=(15, 5 * nrows), constrained_layout=True, squeeze=False
    )
    # fig.suptitle(
    #     f"Averages vs. {parameter_meanings[parameter_name]}",
    #     fontsize=10,
    # )
    return fig, axs


def get_means_stds(
    DataProcessor: DataProcessor, variables: list[str]
) -> dict[Any, Any]:
    means_stds: dict = {}
    for variable in variables:
        variable_means = [
            dataframe[variable].iloc[DataProcessor.start : DataProcessor.end].mean()
            for dataframe in DataProcessor.list_of_dataframes
        ]
        variable_stds = [
            dataframe[variable].iloc[DataProcessor.start : DataProcessor.end].std()
            for dataframe in DataProcessor.list_of_dataframes
        ]
        means_stds[f"{variable}_mean"] = variable_means
        means_stds[f"{variable}_std"] = variable_stds
        x_parameter_means = [
            dataframe[DataProcessor.primary_x_parameter]
            .iloc[DataProcessor.start : DataProcessor.end]
            .mean()
            for dataframe in DataProcessor.list_of_dataframes
        ]
        x_parameter_stds = [
            dataframe[DataProcessor.primary_x_parameter]
            .iloc[DataProcessor.start : DataProcessor.end]
            .std()
            for dataframe in DataProcessor.list_of_dataframes
        ]
        means_stds[f"{DataProcessor.primary_x_parameter}_mean"] = x_parameter_means
        means_stds[f"{DataProcessor.primary_x_parameter}_std"] = x_parameter_stds
    return means_stds


def generate_fig_and_axes_subsets(DataProcessor: DataProcessor, variables: list[str]):
    nrows: int = len(DataProcessor.list_of_dataframes)
    ncols: int = len(variables)
    fig, axs = plt.subplots(
        nrows, ncols, figsize=(15, 5 * nrows), constrained_layout=True, squeeze=False
    )
    return fig, axs


def draw_subsets_all_subsets(
    DataProcessor: DataProcessor, variables: list[str], axs, row_headers, temps=False
) -> None:
    x_parameter: str = "temps" if temps else DataProcessor.primary_x_parameter
    for i, dataframe in enumerate(DataProcessor.list_of_dataframes):
        for j, variable in enumerate(variables):
            ax = axs[i, j]
            if i == 0:
                ax.set_title(
                    f"{variable_meanings[variable]} "
                    f"against {variable_meanings[x_parameter]}"
                )
            if variable_units[variable] != "":
                ax.set_xlabel(
                    f"{variable_symbols[x_parameter]} ({variable_units[x_parameter]})"
                )
                ax.set_ylabel(
                    f"{variable_symbols[variable]} ({variable_units[variable]})"
                )
            else:
                ax.set_xlabel(
                    f"{variable_symbols[x_parameter]} ({variable_units[x_parameter]})"
                )
                ax.set_ylabel(f"{variable_symbols[variable]}")
            x = dataframe[x_parameter]
            y = dataframe[variable].tolist()
            ax.plot(x, y, ".", color="black")
        row_headers.append(f"0MW to {DataProcessor.get_matched_elements()[1][i]}MW")
    plt.plot()


def plot_ramping_all_subsets(
    DataProcessor: DataProcessor, variables: list[str], temps=False
):
    fig, axs = generate_fig_and_axes_subsets(DataProcessor, variables)
    row_headers: list = []
    if temps:
        draw_subsets_all_subsets(DataProcessor, variables, axs, row_headers, temps=True)
    else:
        draw_subsets_all_subsets(
            DataProcessor, variables, axs, row_headers, temps=False
        )
    add_headers(fig, row_headers=row_headers)
    plt.plot()


def add_headers(
    fig,
    *,
    row_headers=None,
    col_headers=None,
    row_pad=1,
    col_pad=5,
    rotate_row_headers=True,
    **text_kwargs,
):
    """
    Function to add row and column headers to a matplotlib figure.
    Based on https://stackoverflow.com/a/25814386
    Args:
        fig (_type_): The figure which contains the axes to work on
        row_headers (_type_, optional):  A sequence of strings to be row headers.
            Defaults to None.
        col_headers (_type_, optional): A sequence of strings to be column headers.
            Defaults to None.
        row_pad (int, optional): Value to adjust padding. Defaults to 1.
        col_pad (int, optional): Value to adjust padding. Defaults to 5.
        rotate_row_headers (bool, optional): Whether to rotate by 90° the row headers.
            Defaults to True.
        **text_kwargs: Forwarded to ax.annotate(...)
    """

    axes = fig.get_axes()

    for ax in axes:
        sbs = ax.get_subplotspec()

        # Putting headers on cols
        if (col_headers is not None) and sbs.is_first_row():
            ax.annotate(
                col_headers[sbs.colspan.start],
                xy=(0.5, 1),
                xytext=(0, col_pad),
                xycoords="axes fraction",
                textcoords="offset points",
                ha="center",
                va="baseline",
                **text_kwargs,
            )

        # Putting headers on rows
        if (row_headers is not None) and sbs.is_first_col():
            ax.annotate(
                row_headers[sbs.rowspan.start],
                xy=(0, 0.5),
                xytext=(-ax.yaxis.labelpad - row_pad, 0),
                xycoords=ax.yaxis.label,
                textcoords="offset points",
                ha="right",
                va="center",
                rotation=rotate_row_headers * 90,
                **text_kwargs,
            )


def plot_all(DataProcessorList: list[DataProcessor], variables: list[str]):
    for DataProcessorFromList in DataProcessorList:
        if DataProcessorFromList.subsets:
            plot_ramping_all_subsets(DataProcessorFromList, variables, temps=False)
            plot_ramping_all_subsets(DataProcessorFromList, variables, temps=True)
        else:
            plot_averages(DataProcessorFromList, variables)
    plt.show()
