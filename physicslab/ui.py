"""
User interface.
"""


import matplotlib.pyplot as plt
import numpy as np


def plot_grid(df, plot_value, xlabel=None, ylabel=None,
              title_label=True, row_label=True, col_label=True,
              legend=False, legend_size=10, show_axis=True,
              subplots_adjust_kw=None, add_skip=None, **kwargs):
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
    :type plot_value: callable
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
    :param show_axis: Visibility of axis, ticks and frame, defaults to True
    :type show_axis: bool, optional
    :param subplots_adjust_kw: Dict with keywords passed to the
        :func:`~matplotlib.pyplot.subplots_adjust` call.
        E.g. ``hspace``, defaults to None
    :type subplots_adjust_kw: dict, optional
    :param add_skip: If a df value matches one of listed items, skip it,
        defaults to None
    :type add_skip: list or None, optional
    :param kwargs: All additional keyword arguments are passed to the
        :func:`~matplotlib.pyplot.figure` call. E.g. ``sharex``.
    """
    title = df.name if (title_label and hasattr(df, 'name')) else None
    if add_skip is None:
        add_skip = []

    nrows, ncols = df.shape
    fig, axs = plt.subplots(num=title, nrows=nrows, ncols=ncols, **kwargs)

    for i, (ax_row, (index, row)) in enumerate(zip(axs, df.iterrows())):
        for j, (ax, (col, value)) in enumerate(zip(ax_row, row.iteritems())):
            if col_label and i == 0:  # First row.
                ax.set_title(col)
            if row_label and j == 0:  # First column.
                ax.set_ylabel(row.name)
            if (value is None or value in add_skip
                    or isinstance(value, float) and np.isnan(value)):  # np.nan
                _hide_axis(ax)
                continue
            if not show_axis:
                _hide_axis(ax)
            plot_value(ax, value)  # Main stuff happens here.
            if legend:
                ax.legend(prop={'size': legend_size})

    # Common x and y labels.
    if xlabel is not None:
        fig.text(0.5, 0.04, xlabel, ha='center')
    if ylabel is not None:
        fig.text(0.04, 0.5, ylabel, va='center', rotation='vertical')

    # plt.subplots_adjust()
    default = {
        'left': 0.10 if ylabel is None else 0.15,
        'bottom': 0.10 if xlabel is None else 0.15,
        'right': 0.95,
        'top': 0.95,
    }
    if subplots_adjust_kw is None:
        subplots_adjust_kw = {}
    plt.subplots_adjust(**{**default, **subplots_adjust_kw})

    plt.show()


def _hide_axis(ax):
    """ Like ``ax.axis('off')``, but keeps labels visible.

    :param ax: Axis
    :type ax: matplotlib.axes.Axes
    """
    ax.set_xticks([])
    ax.set_xticklabels([])
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_frame_on(False)
