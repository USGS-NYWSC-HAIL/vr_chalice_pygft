#!/usr/bin/env python
# coding: utf-8

import numpy as np
from shapely.geometry import Point, Polygon
import math
import rasterio
import matplotlib.patches as patches
from matplotlib.path import Path
import geopandas as gpd
import pandas as pd
import rasterio.plot as rplot
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from chalicelib.__raster_vals_to_points import get_rast_values

# bathfile, xrat, yrat, angle, distance order of args


def get_points(mid_x, mid_y, samp_int_rnd, points, deg_units,
               angle_rad, raster_cell=1, raster_meter=1,
               direction=1):

    for idx in range(0, samp_int_rnd):

        # calc pos x,y
        if deg_units:
            pos_x = mid_x + math.cos(angle_rad) * raster_cell * direction
            pos_y = mid_y + math.sin(angle_rad) * raster_cell * direction
        else:
            pos_x = mid_x + math.cos(angle_rad) * raster_meter * direction
            pos_y = mid_y + math.sin(angle_rad) * raster_meter * direction

        # if on a second value, store old value
        # add the points to layerPts

        pt = Point(pos_x, pos_y)
        points.append(pt)

        mid_x = pos_x
        mid_y = pos_y

    return points


def pad_space(ax, min_max):
    '''
    Changes limits of x and y axis so that the data is more aesthetically pleasing

    Keyword Arguments:
    ax: axis of matplotlib figure
    min_max: minimum and maximum of data to be plotted
    '''

    x_lims = ax.get_xlim()
    y_lims = ax.get_ylim()
    new_x, new_y = [], []

    #if axis limit equals minimum x
    if x_lims[0] == min_max["min_x"]:
        new_x.append(x_lims[0] - 50)
    else:
        new_x.append(x_lims[0])

    #if axis limit equals maximum x
    if x_lims[1] == min_max["max_x"]:
        new_x.append(x_lims[1] + 50)
    else:
        new_x.append(x_lims[1])

    #if axis limit equals minimum y
    if y_lims[0] == min_max["min_y"]:
        new_y.append(y_lims[0] - 10)
    else:
        new_y.append(y_lims[0])

    #if axis limit equals maximum y
    if y_lims[1] == min_max["max_y"]:
        new_y.append(y_lims[1] + 10)
    else:
        new_y.append(y_lims[1])

    #set new or unchanged limits
    ax.set_xlim(new_x)
    ax.set_ylim(new_y)


def stage_graph(upload_path, min_max, pgon, max_stage, units):
    '''
    Plots the maximum stage for a given cross section geometry

    Keyword Arguments:
    flood_model: FlowCalculator object containing the data
    min_max: minimum and maximum bounds of polygon
    pgon: polygon of max stage boundaries
    '''

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot('111')
    ax.set_title("Cross Sectional Geometry at Max Possible Stage (%s %s)" % (max_stage, units))
    ax.grid(b=True, which='major', color='grey', linestyle="-", alpha=.5)
    plt.xlabel("%s in distance from reference point" % units)
    plt.ylabel("%s above datum" % units)

    # intersect with polygon in order to get a flat top width
    inter = Polygon([
        (min_max["min_x"], min_max["min_y"]),
        (min_max["max_x"], min_max["min_y"]),
        (min_max["max_x"], min_max["min_y"] + max_stage),
        (min_max["min_x"], min_max["min_y"] + max_stage)
    ])

    intersection = pgon.intersection(inter)

    coords = pgon.exterior.coords
    plt.scatter(coords[1][0], coords[1][1], zorder=11, color='#2fff00', label="Left Point", s=150, edgecolor='b')
    plt.scatter(coords[-3][0], coords[-3][1], zorder=11, color='red', label="Right Point", s=150, edgecolor='b')

    plt.legend()

    # get path and add the patch of the appropriate color
    path = Path(intersection.exterior.coords)
    patch = patches.PathPatch(path, facecolor="orange", lw=2, alpha=.3)
    ax.add_patch(patch)

    # plot the individual coordinates
    plt.plot([x[0] for x in pgon.exterior.coords],
             [x[1] for x in pgon.exterior.coords], '-o')

    pad_space(ax, min_max)

    # save the filename to flood_model and then save the figure
    #     cross_section_graph = "uploads/cross.png"
    #     plt.savefig(cross_section_graph)
    plt.savefig(upload_path + 'cross.png')


def get_images(upload_path='./uploads', bathfile='Morris3.tif',
               xrat=None, yrat=None, angle=None, distance=None,
               crs='EPSG:2260', max_stage=10, units='Meters'):

    print(upload_path + bathfile)
    ds = rasterio.open(upload_path + bathfile)

    bnds = ds.bounds
    res = ds.res

    lon = np.arange(bnds.left, bnds.right, res[0])
    lat = np.arange(bnds.bottom, bnds.top, res[0])

    if len(lat) > ds.meta['height']:
        lat = lat[:-1]
    if len(lon) > ds.meta['width']:
        lon = lon[:-1]

    grid = np.array(np.meshgrid(lat,lon)).T

    norm_lons = (lon - np.min(lon)) / np.max(lon - np.min(lon))
    norm_lat = (lat - np.min(lat)) / np.max(lat - np.min(lat))

    idx_y, idx_x = np.abs(norm_lat - yrat).argmin(), np.abs(norm_lons - xrat).argmin()

    coords = grid[idx_y, idx_x]

    angle_rad = np.radians(angle)
    samp_int_rnd = distance # distance / resolution (almost 1m so whatever)

    mid_y, mid_x = coords
    deg_units = False
    points = []

    points = get_points(mid_x=mid_x,
                           mid_y=mid_y,
                           samp_int_rnd=samp_int_rnd,
                           points=points,
                           deg_units=deg_units,
                           angle_rad=angle_rad,
                           raster_meter=res[0])


    points = points[::-1]

    pos_y, pos_x = coords
    points.append((Point(pos_x, pos_y)))

    mid_y, mid_x = coords

    points = get_points(mid_x=mid_x,
                           mid_y=mid_y,
                           samp_int_rnd=samp_int_rnd,
                           points=points,
                           deg_units=deg_units,
                           angle_rad=angle_rad,
                           raster_meter=res[0],
                           direction=-1)


    df = gpd.GeoDataFrame({'geometry': gpd.GeoSeries(points),
                           'id': pd.Series(np.arange(len(points)))}, crs=crs)

    df['elevation'] = get_rast_values(upload_path,
                                      bathfile,
                                      [pt.x for pt in points],
                                      [pt.y for pt in points])
    all_coords = np.vstack([np.array([[pt.x, pt.y] for pt in points]).T,
                            df['elevation'].values]).T
    df.to_file(upload_path + 'cross.shp')

    all_coords[all_coords[:,2] < -9999, 2] = np.nan

    len_z = all_coords[:,2].shape[0]

    new_x = np.arange(0,len_z, res[0])

    first_point = Point(0, np.nanmin(all_coords[:, 2]) + max_stage)
    last_point = Point(len_z, np.nanmin(all_coords[:, 2]) + max_stage)

    poly_points = [first_point]
    for x, y in zip(new_x, all_coords[:,2]):
        if not np.isnan(y):
            poly_points.append(Point(x,y))

    poly_points.append(last_point)
    poly_points.append(first_point)
    pgon = Polygon([(pt.x, pt.y) for pt in poly_points])

    min_max = {'min_x': 0, 'max_x': len_z,
               'min_y': np.nanmin(all_coords[:,2]), 'max_y':  np.max(all_coords[:,2])}

    stage_graph(upload_path, min_max, pgon, max_stage, units)

    # Create plot canvas, make legend, set title, plot raster, and setup the colorbar
    fig, ax = plt.subplots(figsize=(14, 18))


    ax.set_title('Bathymetric Elevation in %s (%s)' % (units, crs))
    ax.grid(b=True, which='major', color='grey', linestyle="-", alpha=.5)

    df.plot(ax=ax, zorder=10, color='black', label="Cross Section Points")
    mid_point = df.iloc[int(np.round(df.shape[0] / 2)), 0]
    left_point = df.iloc[0, 0]
    right_point = df.iloc[-1, 0]

    plt.scatter(mid_point.x, mid_point.y, zorder=12, color='yellow', label="Mid Point", s=150, edgecolor='black')
    plt.scatter(left_point.x, left_point.y, zorder=11, color='#2fff00', label="Left Point", s=150, edgecolor='black')
    plt.scatter(right_point.x, right_point.y, zorder=11, color='red', label="Right Point", s=150, edgecolor='black')
    plt.legend()

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.3)
    image = rplot.show(ds, cmap='Spectral', ax=ax, zorder=5)
    plt.colorbar(image.get_images()[0], cax=cax)

    plt.savefig(upload_path + 'bathymetry.png')

    return {'bath_img': 'bathymetry.png',
            'cross_img': 'cross.png',
            'lat_lon': (mid_y, mid_x)}


if __name__ == '__main__':
    get_images(xrat=.5, yrat=.5, distance=100, angle=45)
