#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Wheel plot that shows continuous data in radial axes.
"""

import numpy as np
import sys

from math import degrees
from collections import OrderedDict
from itertools import groupby

from jcvi.graphics.base import Rectangle, plt, savefig, normalize_axes
from jcvi.apps.base import OptionParser, ActionDispatcher


def main():

    actions = (
        ('wheel', 'wheel plot that shows continuous data in radial axes'),
            )
    p = ActionDispatcher(actions)
    p.dispatch(globals())


def closed_plot(ax, theta, r, *args, **kwargs):
    theta = list(theta) + [theta[0]]
    r = list(r) + [r[0]]
    ax.plot(theta, r, *args, **kwargs)


def sector(ax, theta_min, theta_max, theta_pad, r, R=30, *args, **kwargs):
    theta = np.linspace(theta_min - theta_pad, theta_max + theta_pad, num=100)
    r = len(theta) * [r]
    theta = list(theta) + [0]
    r = list(r) + [-R]
    closed_plot(ax, theta, r, *args, **kwargs)


def parse_data(datafile, score_column="score"):
    data = {}
    fp = open(datafile)
    for row in fp:
        label, score, percentile = row.split(",")
        label = label.strip()
        score = float(score.strip())
        percentile = float(percentile.strip())
        if score_column == "score":
            data[label] = score
        else:
            data[label] = percentile
    return data


def parse_groups(groupsfile):
    groups = OrderedDict()
    fp = open(groupsfile)
    for row in fp:
        group, label = row.split(",")
        group = group.strip()
        label = label.strip()
        groups[label] = group
    return groups


def wheel(args):
    """
    %prog wheel datafile.csv groups.csv

    Wheel plot that shows continous data in radial axes.
    """
    p = OptionParser(wheel.__doc__)
    p.add_option("--column", default="score", choices=("score", "percentile"),
                    help="Which column to extract from `datafile.csv`")
    opts, args, iopts = p.set_image_options(args, figsize="5x5", format="png")

    if len(args) != 2:
        sys.exit(not p.print_help())

    datafile, groupsfile = args
    column = opts.column
    linecolor = "#D4D4D4"
    df = parse_data(datafile, score_column=opts.column)
    groups = parse_groups(groupsfile)
    labels = [g for g in groups if g in df]
    print labels
    df = [df[g] for g in labels]
    print df
    groups = [groups[g] for g in labels]
    print groups

    pf = datafile.rsplit(".", 1)[0]
    fig = plt.figure(1, (iopts.w, iopts.h))
    root = fig.add_axes([0, 0, 1, 1])
    categories = len(df)
    #ax = plt.subplot(111, projection='polar')
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True, axisbg='#d5de9c')

    brewer = [ "#FF3B30", "#DD43A0", "#5856D6",
	       "#007AFE", "#56BDEC", "#4CD8BA",
	       "#4CD864", "#B0F457", "#FEF221",
	       "#FFCC01", "#FF9500", "#FF3B30",
    ]

    # Baseline
    theta = np.linspace(0, 2 * np.pi, endpoint=False, num=categories)
    _theta = np.linspace(0, 2 * np.pi)
    R = 30
    xlim = (-R, R) if column == "score" else (-100, 100)
    plim = (-R / 2, R) if column == "score" else (0, 100)

    # Grid
    for t in theta:
        ax.plot([t, t], plim, color=linecolor)
    ax.axis('off')

    # Contours
    for t in plim:
        ax.plot(_theta, [t] * len(_theta), color=linecolor)

    # Shades

    # Sectors (groupings)
    collapsed_groups = []
    gg = []
    for group, c in groupby(enumerate(groups), lambda x: x[1]):
        c = [x[0] for x in list(c)]
        collapsed_groups.append(group)
        gg.append(c)

    sector = False
    if sector:
        theta_interval = 2 * np.pi / categories
        theta_pad = theta_interval / 2 * .9
        for color, group in zip(brewer, gg):
            tmin, tmax = min(group), max(group)
            sector(ax, theta[tmin], theta[tmax], theta_pad, R * .95,
                       "-", color=color, lw=2)

    # Data
    r = df
    closed_plot(ax, theta, r, color="lightslategray")
    for color, group in zip(brewer, gg):
        color_theta = [theta[x] for x in group]
        color_r = [r[x] for x in group]
        ax.plot(color_theta, color_r, "o", color=color)

    # Labels
    from math import cos, sin
    r = .5
    for i, label in enumerate(labels):
        tl = theta[i]
        x, y = .5 + r * cos(tl), .5 + r * sin(tl)
        d = degrees(tl)
        if 90 < d % 360 < 270:  # On the left quardrants
            d -= 180
        root.text(x, y, label, size=4, rotation=d,
                  ha="center", va="center", color=linecolor)
        print x, y, label

    # Add baseline
    baseline = 0 if column == "score" else 50
    _r = len(_theta) * [baseline]
    closed_plot(ax, _theta, _r, "k:", lw=1, ms=4)

    # Add confidence interval
    if column == "percentile":
        pass
        #p10 = ax.plot(_theta, [10] * len(_theta), color=linecolor)
        #p90 = ax.plot(_theta, [90] * len(_theta), color=linecolor)
        #ax.fill_between(p10, p90, fc=linecolor, alpha=.5)
        #ax.add_patch(Rectangle([10, 0], 2 * np.pi, 80, fc='b', alpha=.5))

    ax.set_rmin(xlim[0])
    ax.set_rmax(xlim[1])

    normalize_axes(root)

    image_name = pf + "-" + column + "." + iopts.format
    savefig(image_name, dpi=iopts.dpi, iopts=iopts)


if __name__ == '__main__':
    main()
