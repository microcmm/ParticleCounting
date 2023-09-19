#!/usr/bin/env python3

import sys, csv
import argparse
import logging
import os, platform
import os.path
from datetime import datetime
import getpass, subprocess, uuid
from distutils.dir_util import copy_tree
import shutil
import configparser
import PIL

import pandas as pd
import seaborn as sns
import matplotlib as plt
import matplotlib.ticker as mticker

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(name)s] %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)


def get_scratch():
    """
    Find scratch place
    """
    if "SCRATCH_DIR" in os.environ:
        return os.environ['SCRATCH_DIR']
    else:
        myUsername = str(getpass.getuser())  ## this is not a reliable way to get username
        myWienergroup = subprocess.check_output("groups | tr ' ' '\n' | grep 'wiener' | sed 's/wiener-//g' | head -1",
                                                shell=True).decode("utf-8").strip()
        return os.path.join("/scratch", myWienergroup, myUsername)


def pc_fiji_count(args):
    """
    Run particleCounting_headless 
    and post processing
    """
    config = configparser.ConfigParser()
    config['npc'] = {}
    if not args.input_path or not os.path.exists(args.input_path):
        logger.error("input_path not specified or not exists")
        return
    else:
        config['npc']['input_path'] = input_path = args.input_path
    # dataset name
    if input_path.endswith('/') or input_path.endswith('\\'):
        input_path = input_path[:-1]
    dataset_name = os.path.split(input_path)[-1]
    logger.info(f">>>datasetname={dataset_name}")
    if args.fiji_path:
        fiji_path = args.fiji_path
    else:
        if platform.system() == 'Linux':
            fiji_path = 'ImageJ-linux64'
    if args.output_path:
        config['npc']['output_path'] = output_path = args.output_path
    else:
        config['npc']['output_path'] = output_path = os.path.join(input_path,
                                                                  'output_' + datetime.now().strftime("%m_%d_%Y"))
    config['npc']['keep_cropped_files'] = 'true'
    if args.keep_cropped_files:
        config['npc']['keep_cropped_files'] = str(args.keep_cropped_files)
    config['npc']['keep_threshold_files'] = 'true'
    if args.keep_threshold_files:
        config['npc']['keep_threshold_files'] = str(args.keep_threshold_files)
    # params['scratch'] = True
    if args.scratch:
        config['npc']['scratch'] = args.scratch

    # circularity
    if args.circularity_min:
        config['npc']['circularity_min'] = str(float(args.circularity_min))

    #### 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    ### pixel thing
    if not args.pixel_width or not args.pixel_height or not args.pixel_unit:
        logger.error("has to provide pixel_width, height and unit")
        return
    config['npc']['pixelwidth'] = str(float(args.pixel_width))
    config['npc']['pixelheight'] = str(float(args.pixel_height))
    config['npc']['pixelunit'] = args.pixel_unit
    if not args.min_particle_size:
        config['npc']['minparticlesize'] = '0'
    else:
        config['npc']['minparticlesize'] = str(float(args.min_particle_size))

    if not args.file_extension:
        config['npc']['fextension'] = 'tiff'
    else:
        config['npc']['fextension'] = args.file_extension

    if args.ignored:
        config['npc']['excluded'] = str(args.ignored)

    #### run the thing
    logger.info("melon")
    logger.info(args.scratch)
    logger.info("passionfruit")
    if args.scratch:
        # find the user scratch place
        scratch = get_scratch()
        # copy input to scratch
        input_path = os.path.join(scratch, uuid.uuid4())
        # create output
        output_path = os.path.join(scratch, uuid.uuid4())
    log_file = os.path.join(output_path, 'pc.log')
    config_file = os.path.join(output_path, 'config.ini')
    with open(config_file, 'w', encoding='utf-8') as configfile:
        config.write(configfile)

    logger.info("peach")
    script_location = os.path.join(os.getcwd(), "pc_headless_autothreshold_TEM.py")
    # logger.info(script_location)
    # logger.info(fiji_path)
    # logger.info(config_file)
    # logger.info(log_file)
    logger.info("star")
    # logger.info(str(configfile))
    cmd = f"{fiji_path} --ij2 --run \"{script_location}\" \"CONFIG='{config_file}'\" > \"{log_file}\" "  # 2>&1"
    # cmd = f"{fiji_path} --ij2 --headless --run \"{script_location}\" \"CONFIG='{config_file}'\" > \"{log_file}\" " #2>&1"
    # logger.info(cmd)
    logger.info("dragonfruit")
    ret = os.system(cmd)
    logger.info("strawberry")
    logger.info("kiwi")
    if ret == 0:
        if not args.fields:
            logger.info("No field provided")
            return
        else:
            logger.info(f"fields: {args.fields}")
            output_file_without_ext = os.path.join(output_path, f"Outputs_{dataset_name}")
            output_csv = f"{output_file_without_ext}.csv"
            output_figure = f"{output_file_without_ext}.png"

            with open(output_csv, 'w', newline='') as csvfile:
                output_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                _all_fields = ["Label"] + args.fields
                output_writer.writerow(_all_fields)
                # go thru all the .csv files in output, get them, and collect to a xlsx file
                _filesInOutput = os.listdir(output_path)
                _files = [item for item in _filesInOutput if item.endswith('.csv')]
                for _file in _files:
                    _label = os.path.splitext(_file)[0]
                    logger.info(f"Reading file {_file}")
                    if f"Outputs_{dataset_name}.csv" in _file:
                        logger.info("Ignoring as it is the output")
                        continue
                    with open(os.path.join(output_path, _file)) as csvfile:
                        reader = csv.DictReader(csvfile)
                        for contentRow in reader:
                            _row_values = [_label]
                            for _field in args.fields:
                                _row_values = _row_values + [contentRow[_field]]
                            output_writer.writerow(_row_values)

            # figure
            pc_df = pd.read_csv(output_csv)
            pc_df.Feret.describe(percentiles=[.1, .5, .9]).to_csv(os.path.join(output_path, 'summary.csv'))
            # plot for density distribution, despine top, bottom, L, R, all set to false to give border
            sns.set_style = ("ticks")
            g = sns.displot(pc_df, x="Feret", kind="hist", stat="percent", element="poly", log_scale=(True),
                            fill=(False), color="black", bins=50, height=3.5, aspect=1,
                            facet_kws=dict(margin_titles=True), )
            sns.despine(top=False, right=False, left=False, bottom=False)
            g.set_axis_labels(x_var=f"Diameter $({args.pixel_unit})$", y_var="Number frequency (%)", )
            # set x min and max
            _min_x = 0.01
            if args.graph_min_x:
                _min_x = float(args.graph_min_x)
            _max_x = 10000
            if args.graph_max_x:
                _max_x = float(args.graph_max_x)
            g.ax.set_xlim(_min_x, _max_x)
            g.ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
            g.savefig(output_figure)

        ### remove input_path and move output_path to output, if scrach is used
        if args.scratch:
            logger.info("Copy scratch back to output")
            copy_tree(output_path, config['npc']['output_path'])
            shutil.rmtree(input_path)
            shutil.rmtree(output_path)
    else:
        logger.error(f"Command failed. Look at {log_file}")


def main(arguments=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog='pc_main_TEM',
        description='Particle counting main')
    subparsers = parser.add_subparsers(title='sub command', help='sub command help')
    #####################################
    pc_fiji = subparsers.add_parser(
        'pc-fiji', description='Particle counting using Fiji',
        help='Run particle counting using Fiji and postprocessing',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    pc_fiji.set_defaults(func=pc_fiji_count)
    pc_fiji.add_argument('--fiji-path', help='Fiji path', required=False, type=str)
    pc_fiji.add_argument('--input-path', help='input path', required=True, type=str)
    pc_fiji.add_argument('--scratch', help='scratch', type=eval, choices=[True, False], default='False')
    pc_fiji.add_argument('--output-path', help='output path', required=False, type=str)
    pc_fiji.add_argument('--keep-cropped-files', help='keeping cropped files', type=eval, choices=[True, False],
                         default='True')
    pc_fiji.add_argument('--keep-threshold-files', help='keeping thresholded files', type=eval, choices=[True, False],
                         default='True')
    pc_fiji.add_argument('--pixel-width', help='pixel width', type=float)
    pc_fiji.add_argument('--pixel-height', help='pixel height', type=float)
    pc_fiji.add_argument('--pixel-unit', help='pixel unit', type=str, choices=['mm', 'μm', 'nm'], default='μm')
    pc_fiji.add_argument('--min-particle-size', help='the smallest particle size in pixels', type=int)
    pc_fiji.add_argument('--file-extension', help='file extension', type=str, default='tiff')
    pc_fiji.add_argument('--ignored', nargs='+', required=False, help='files to be ignored, without extension')
    pc_fiji.add_argument('--fields', nargs='+', required=False, help='list of fields  to store in excel', \
                         choices=["Area", "Mean", "StdDev", "Mode", "Min", "Max", "X", "Y", "XM", "YM", "Perim.", "BX",
                                  "BY", "Width", "Height", \
                                  "Major", "Minor", "Angle", "Circ.", "Feret", "IntDen", "Median", "Skew", "Kurt",
                                  "%Area", "RawIntDen", \
                                  "FeretX", "FeretY", "FeretAngle", "MinFeret", "AR", "Round", "Solidity"])
    pc_fiji.add_argument('--graph-min-x', help='minimum value for graph x axis', type=float, default=0.01)
    pc_fiji.add_argument('--graph-max-x', help='maximum value for graph x axis', type=float, default=100)
    pc_fiji.add_argument('--circularity-min', help='circularity lower limit', type=float, default=0.2)

    args = parser.parse_args(arguments)
    return args.func(args)


if __name__ == "__main__":
    main()
