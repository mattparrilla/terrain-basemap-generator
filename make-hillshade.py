#!/usr/bin/env/python
import subprocess
import os


def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


def reproject(filename):
    """Reproject SRTM data to Google Mercator"""
    name, ext = filename.split('.')
    command = "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3785 -r bilinear %s.%s %s-proj.%s" % (
        name, ext, name, ext)
    subprocess.call(command, shell=True)
    return "%s-proj.%s" % (name, ext)


def create_hillshade(filename):
    name, ext = filename.split('.')
    command = "gdaldem hillshade -compute_edges -co compress=lzw %s %s-hillshade.%s" % (
        filename, name, ext)
    subprocess.call(command, shell=True)
    return filename


def generate_color_relief(filename):
    name, ext = filename.split('.')
    command = "gdaldem color-relief %s ramp.txt %s-color-relief.%s" % (
        filename, name, ext)
    subprocess.call(command, shell=True)
    return filename


def generate_slope(filename):
    name, ext = filename.split('.')
    command = "gdaldem slope %s %s-slope.%s" % (filename, name, ext)
    subprocess.call(command, shell=True)
    return "%s-slope.%s" % (name, ext)


def generate_slope_shade(filename):
    name, ext = filename.split('.')
    command = "gdaldem color-relief -co compress=lzw %s slope-ramp.txt %s-slopeshade.%s" % (
        filename, name, ext)
    subprocess.call(command, shell=True)
    return "%s-slope.%s" % (name, ext)


def combine_tiffs(tiff_list):
    files = " ".join(tiff_list)
    command = "gdal_merge.py %s -o master-tiff.tif" % (files)
    subprocess.call(command, shell=True)
    return "master-tiff.tif"


def make_master_tiff(filepath):
    """Gets all base tifs within specified directory, reprojects them into
    Google Mercator and combines them into one master TIFF"""

    # get and reproject tiffs
    full_file_paths = get_filepaths(filepath)
    reprojected_tiffs = []
    for f in full_file_paths:
        if '.tif' in f and "-" not in f:
            reprojected = reproject(f)
            reprojected_tiffs.append(reprojected)

    master_tiff = combine_tiffs(reprojected_tiffs)

    return "%s/%s" % (filepath, master_tiff)


def generate_all_tiffs(filepath):
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if "master-tiff.tif" not in files:
        master_tiff = make_master_tiff(filepath)
    else:
        master_tiff = "%s/master-tiff.tif" % filepath
    #hillshade = create_hillshade(master_tiff)
    colors = generate_color_relief(master_tiff)
    #sloped = generate_slope(master_tiff)
    #slopeshade = generate_slope_shade(sloped)
    return True

generate_all_tiffs("/Users/mparrilla/code/hillshade")
