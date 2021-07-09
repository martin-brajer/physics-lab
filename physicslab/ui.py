"""
User interface.
"""


import matplotlib.pyplot as plt
import numpy as np

from physicslab.utility import get_name


def plot_grid(df, plot_value, fig_axs=None, skip=None,
              title=None, xlabel=None, ylabel=None,
              row_labels=True, column_labels=True,
              subplots_adjust_kw=None, **kwargs):
    """ Construct a figure with the same layout as the input.

    | For example, use it to display
        `SEM <https://en.wikipedia.org/wiki/Scanning_electron_microscope>`_
        images, where rows correspond to different magnifications and columns
        to samples.
    | If a :attr:`df` value is :obj:`None` or :obj:`numpy.nan`, skip the
        individual plot.
    | To display all figures, call :func:`~matplotlib.pyplot.show`.

    :param df: Data to drive plotting. E.g. filename to load and plot
    :type df: pandas.DataFrame
    :param plot_value: Function to convert a :attr:`df` value into ``ax.plot``.

        .. code:: python

            def plot_value(ax: matplotlib.axes.Axes, value: object):
                ax.plot(value.x)
                ax.legend()  # Show a legend for each plot.

    :type plot_value: callable
    :param fig_axs: Figure and axis array to draw to. Axis shape must match
        that of :attr:`df`. If None, create a new figure, defaults to None
    :type fig_axs: tuple(~matplotlib.figure.Figure,
        numpy.ndarray(~matplotlib.axes.Axes)), optional
    :param skip: Skip df values matching any of the listed items,
        defaults to None
    :type skip: list, optional
    :param title: Common title. If ``auto``, use :attr:`df.name` if
        available, defaults to None
    :type title: str, optional
    :param xlabel: Common x axis label, defaults to None
    :type xlabel: str, optional
    :param ylabel: Common y axis label, defaults to None
    :type ylabel: str, optional
    :param row_labels: Annotate rows by :attr:`df.index`, defaults to True
    :type row_labels: bool, optional
    :param column_labels: Annotate columns by :attr:`df.columns`,
        defaults to True
    :type column_labels: bool, optional
    :param subplots_adjust_kw: Dict with keywords passed to the
        :func:`~matplotlib.pyplot.subplots_adjust` call.
        E.g. ``hspace``, defaults to None
    :type subplots_adjust_kw: dict, optional
    :param kwargs: All additional keyword arguments are passed to the
        :func:`~matplotlib.pyplot.figure` call. E.g. ``sharex``
    :raises ValueError: If :attr:`df` and :attr:`axs` have different shapes
    :return: Same objects as from :meth:`matplotlib.pyplot.subplots`
    :rtype: tuple[~matplotlib.figure.Figure,
        numpy.ndarray[~matplotlib.axes.Axes]]
    """
    nrows, ncols = df.shape
    if fig_axs is None:
        fig, axs = plt.subplots(
            num=get_name(df), nrows=nrows, ncols=ncols, **kwargs)
    else:
        fig, axs = fig_axs
        if df.shape != axs.shape:
            raise ValueError('axs and df shape must match')

    for ax_row, (index, row) in zip(axs, df.iterrows()):
        for ax, (column, value) in zip(ax_row, row.iteritems()):
            subplotspec = ax.get_subplotspec()
            if column_labels and subplotspec.is_first_row():
                ax.set_title(column)
            if row_labels and subplotspec.is_first_col():
                ax.set_ylabel(row.name)
            # Skipping this ax.
            if (value is None
                or (isinstance(value, float) and np.isnan(value))  # np.nan
                    or (skip is not None and value in skip)):
                # Like ``ax.axis('off')``, but keeps labels visible.
                ax.tick_params(labelcolor='none',
                               top=False, bottom=False,
                               left=False, right=False)
                ax.set_frame_on(False)
                continue
            plot_value(ax, value)  # The main stuff happens here.

    # Common labels.
    if title is not None:
        if title == 'auto':
            title = get_name(df)
        fig.suptitle(title)
    if xlabel is not None:
        fig.text(0.5, 0.04, xlabel, ha='center')
        # Change to fig.supxlabel(xlabel) from python 3.7 onward.
    if ylabel is not None:
        fig.text(0.04, 0.5, ylabel, va='center', rotation='vertical')
    if subplots_adjust_kw is not None:
        fig.subplots_adjust(**subplots_adjust_kw)

    return fig, axs
