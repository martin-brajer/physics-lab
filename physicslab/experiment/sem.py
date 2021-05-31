"""
Scanning electron microscope data.
"""


import matplotlib.image as mpimg

from physicslab.ui import plot_grid


def plot(filenames):
    """ Plot SEM images in a grid based on magnification and sample name.

    :param filenames: Filenames including path
    :type filenames: pandas.DataFrame
    """
    def plot_value(ax, value: str):
        img = mpimg.imread(value)
        ax.imshow(img, cmap='gray')
        ax.tick_params(labelcolor='none',
                       top=False, bottom=False, left=False, right=False)
        ax.set_frame_on(False)
    plot_grid(filenames, plot_value, ylabel='Magnification',
              subplots_adjust_kw={'wspace': 0, 'hspace': 0})
