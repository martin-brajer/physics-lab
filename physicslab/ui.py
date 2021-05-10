"""
UI
"""
# __all__ =


import matplotlib.pyplot as plt
import numpy as np


def plot_grid(df, plot_value, xlabel=None, ylabel=None,
              title_label=True, row_label=True, col_label=True,
              legend=True, legend_size=10, subplots_adjust_kw=None, **kwargs):
    """ Construct a figure with the same layout as the input.

    For example, use it to display
    `SEM <https://en.wikipedia.org/wiki/Scanning_electron_microscope>`_
    images, where rows correspond to different magnifications and columns
    to samples.

    If a :attr:`df` value is :obj:`None` or :obj:`numpy.nan`, skip the plot.

    :param df: Data to drive plotting. E.g. filename to load and plot
    :type df: pandas.DataFrame
    :param plot_value: Function to convert :attr:`df` value into
        ``ax.plot`` call. `<Signature (ax:Axis, value:object)>`
    :type plot_value: function
    :param xlabel: Common x axis label, defaults to None
    :type xlabel: str, optional
    :param ylabel: Common y axis label, defaults to None
    :type ylabel: str, optional
    :param title_label: Set figure label to :attr:`df.name`, defaults to True
    :type title_label: bool, optional
    :param row_label: Annotate rows by :attr:`df.index`, defaults to True
    :type row_label: bool, optional
    :param col_label: Annotate columns by :attr:`df.columns`, defaults to True
    :type col_label: bool, optional
    :param legend: Show a legend for each plot, defaults to True
    :type legend: bool, optional
    :param legend_size: Legend box and font size, defaults to 10
    :type legend_size: float, optional
    :param subplots_adjust_kw: Dict with keywords passed to the
        :meth:`matplotlib.pyplot.subplots_adjust` call.
        E.g. ``hspace``, defaults to None
    :type subplots_adjust_kw: dict, optional
    :param kwargs: All additional keyword arguments are passed to the
        :meth:`matplotlib.pyplot.figure` call. E.g. ``sharex``.
    """
    title = df.name if (title_label and hasattr(df, 'name')) else None

    nrows, ncols = df.shape
    fig, axs = plt.subplots(num=title, nrows=nrows, ncols=ncols, **kwargs)

    for i, (ax_row, (index, row)) in enumerate(zip(axs, df.iterrows())):
        for j, (ax, (column, value)) in enumerate(
                zip(ax_row, row.iteritems())):
            isnan = isinstance(value, float) and np.isnan(value)
            if isnan or value is None:
                ax.axis('off')
                continue
            plot_value(ax, value)  # Main.
            if legend:
                ax.legend(prop={'size': legend_size})
            if col_label and i == 0:  # First row.
                ax.set_title(column)
            if row_label and j == 0:  # First column.
                ax.set_ylabel(row.name)

    # Common x and y labels.
    if xlabel is not None:
        fig.text(0.5, 0.04, xlabel, ha='center')
    if ylabel is not None:
        fig.text(0.04, 0.5, ylabel, va='center', rotation='vertical')

    # plt.subplots_adjust
    default = {
        'left': 0.15 if row_label else None,
        'bottom': 0.15 if col_label else None,
    }
    if subplots_adjust_kw is None:
        subplots_adjust_kw = {}
    plt.subplots_adjust(**{**default, **subplots_adjust_kw})

    plt.show()
