#!/usr/bin/env python3
import argparse
import configparser
import csv
import getpass
import logging
import os
import platform
import shutil
import subprocess
import sys
import uuid
# import os.path
from datetime import datetime
from distutils.dir_util import copy_tree

# import matplotlib as plt
import matplotlib.ticker as mpl_ticker
import pandas as pd
import seaborn as sns

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(name)s] %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_SCRIPT_NAME = "pc_headless_autothreshold.py"
DEFAULT_LOGFILE_NAME = 'pc.log'
DEFAULT_CONFIG_NAME = 'config.ini'
FILE_EXT_TIFF = 'tiff'
# FIJI_CMD = "{} --ij2 --headless --run \"{}\" \"CONFIG='{}'\" > \"{}\" 2>&1"
FIJI_CMD = "{} --ij2 --run \"{}\" \"CONFIG='{}'\" > \"{}\" "  # 2>&1"


def get_scratch():
    """
    Find scratch place
    """
    if "SCRATCH_DIR" in os.environ:
        return os.environ['SCRATCH_DIR']
    else:
        my_username = str(getpass.getuser())  # this is not a reliable way to get username
        my_wienergroup = subprocess.check_output("groups | tr ' ' '\n' | grep 'wiener' | sed 's/wiener-//g' | head -1",
                                                 shell=True).decode("utf-8").strip()
        return os.path.join("/scratch", my_wienergroup, my_username)


class ParticleCounter:
    def __init__(self, script_name):
        self._cfg_args = {}
        self._fiji_path = None
        self._dataset_name = None
        self._output_path = None
        self._input_path = None
        self._script_location = os.path.join(os.getcwd(), script_name)
        self._log_file = None
        self._config_file = None

        self._config = configparser.ConfigParser()
        self._config["npc"] = self._cfg_args

    def parse_config_args(self, args):
        # FIJI path
        if args.fiji_path:
            self._fiji_path = args.fiji_path
        else:
            if platform.system() == 'Linux':
                self._fiji_path = 'ImageJ-linux64'

        if not args.input_path or not os.path.exists(args.input_path):
            logger.error("Input_path not specified or not exists")
            return False
        else:
            self._input_path = args.input_path
            self._cfg_args['input_path'] = self._input_path
        # dataset name
        if self._input_path.endswith('/') or self._input_path.endswith('\\'):
            self._input_path = self._input_path[:-1]
        self._dataset_name = os.path.split(self._input_path)[-1]
        logger.info(f">>>datasetname={self._dataset_name}")

        # output path
        if args.output_path:
            self._output_path = args.output_path
        else:
            self._output_path = os.path.join(self._input_path,
                                             'output_' + datetime.now().strftime("%m_%d_%Y"))
        if not os.path.exists(self._output_path):
            os.makedirs(self._output_path)
        self._cfg_args['output_path'] = self._output_path

        self._cfg_args['keep_cropped_files'] = 'true'
        if args.keep_cropped_files:
            self._cfg_args['keep_cropped_files'] = str(args.keep_cropped_files)
        self._cfg_args['keep_threshold_files'] = 'true'
        if args.keep_threshold_files:
            self._cfg_args['keep_threshold_files'] = str(args.keep_threshold_files)

        # circularity
        if args.circularity_min:
            self._cfg_args['circularity_min'] = str(float(args.circularity_min))

        # pixel thing
        if not args.pixel_width or not args.pixel_height or not args.pixel_unit:
            logger.error("has to provide pixel_width, height and unit")
            return
        self._cfg_args['pixelwidth'] = str(float(args.pixel_width))
        self._cfg_args['pixelheight'] = str(float(args.pixel_height))
        self._cfg_args['pixelunit'] = args.pixel_unit
        if not hasattr(args, "min_particle_size"):
            self._cfg_args['minparticlesize'] = '0'
        else:
            self._cfg_args['minparticlesize'] = str(float(args.min_particle_size))

        if not args.file_extension:
            self._cfg_args['fextension'] = FILE_EXT_TIFF
        else:
            self._cfg_args['fextension'] = args.file_extension

        if args.ignored:
            self._cfg_args['excluded'] = str(args.ignored)

        print(args.scratch)
        # params['scratch'] = True
        if args.scratch:
            self._cfg_args['scratch'] = args.scratch

            # find the user scratch place
            scratch = get_scratch()
            # copy input to scratch
            self._input_path = os.path.join(scratch, str(uuid.uuid4()))
            # create output
            self._output_path = os.path.join(scratch, str(uuid.uuid4()))

        return True

    def pc_fiji_count(self, args):
        """
        Run particleCounting_headless
        and post processing
        """
        if not self.parse_config_args(args):
            return

        # run the thing
        self._log_file = os.path.join(self._output_path, DEFAULT_LOGFILE_NAME)
        self._config_file = os.path.join(self._output_path, DEFAULT_CONFIG_NAME)
        with open(self._config_file, 'w', encoding='utf-8') as configfile:
            self._config.write(configfile)

        # run the fiji command
        cmd = FIJI_CMD.format(self._fiji_path, self._script_location, self._config_file, self._log_file)
        logger.info(cmd)
        ret = os.system(cmd)

        self.handle_command_response(args, ret)

    def handle_command_response(self, args, ret):
        # handle response
        if ret == 0:
            if not args.fields:
                logger.info("No field provided")
                return
            else:
                logger.info(f"fields: {args.fields}")
                output_file_without_ext = os.path.join(self._output_path, f"Outputs_{self._dataset_name}")
                output_csv = f"{output_file_without_ext}.csv"

                with open(output_csv, 'w', newline='') as csvfile:
                    output_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                    _all_fields = ["Label"] + args.fields
                    output_writer.writerow(_all_fields)
                    # go thru all the .csv files in output, get them, and collect to a xlsx file
                    _filesInOutput = os.listdir(self._output_path)
                    _files = [item for item in _filesInOutput if item.endswith('.csv')]
                    self.save_output(_files, output_writer, args)

                # figure
                self.plot_figure(args, output_file_without_ext)

            # remove input_path and move output_path to output, if scrach is used
            if args.scratch:
                logger.info("Copy scratch back to output")
                copy_tree(self._output_path, self._cfg_args['output_path'])
                shutil.rmtree(self._input_path)
                shutil.rmtree(self._output_path)
        else:
            logger.error(f"Command failed. Look at {self._log_file}")

    def save_output(self, files, output_writer, args):
        for filename in files:
            _label = os.path.splitext(filename)[0]
            logger.info(f"Reading file {filename}")
            if f"Outputs_{self._dataset_name}.csv" in filename:
                logger.info("Ignoring as it is the output")
                continue

            with open(os.path.join(self._output_path, filename)) as csvfile:
                reader = csv.DictReader(csvfile)
                for contentRow in reader:
                    _row_values = [_label]
                    for _field in args.fields:
                        _row_values = _row_values + [contentRow[_field]]
                    output_writer.writerow(_row_values)

    def plot_figure(self, args, output_file_without_ext, save=True):
        output_csv = f"{output_file_without_ext}.csv"

        pc_df = pd.read_csv(output_csv)
        pc_df.Feret.describe(percentiles=[.1, .5, .9]).to_csv(os.path.join(self._output_path, 'summary.csv'))
        # plot for density distribution, despine top, bottom, L, R, all set to false to give border
        sns.set_style = "ticks"
        g = sns.displot(pc_df, x="Feret", kind="hist", stat="percent", element="poly", log_scale=True,
                        fill=False, color="black", bins=30, height=3.5, aspect=1,
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
        g.ax.xaxis.set_major_formatter(mpl_ticker.ScalarFormatter())

        if save:
            output_figure = f"{output_file_without_ext}.png"
            g.savefig(output_figure)


def main(arguments=sys.argv[1:]):
    pc = ParticleCounter(script_name=DEFAULT_SCRIPT_NAME)

    parser = argparse.ArgumentParser(
        prog='pc_main',
        description='Particle counting main')
    subparsers = parser.add_subparsers(title='sub command', help='sub command help')
    #####################################
    pc_fiji = subparsers.add_parser(
        'pc-fiji', description='Particle counting using Fiji',
        help='Run particle counting using Fiji and postprocessing',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    pc_fiji.set_defaults(func=pc.pc_fiji_count)
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
    pc_fiji.add_argument('--fields', nargs='+', required=False, help='list of fields  to store in excel',
                         choices=["Area", "Mean", "StdDev", "Mode", "Min", "Max", "X", "Y", "XM", "YM", "Perim.", "BX",
                                  "BY", "Width", "Height",
                                  "Major", "Minor", "Angle", "Circ.", "Feret", "IntDen", "Median", "Skew", "Kurt",
                                  "%Area", "RawIntDen",
                                  "FeretX", "FeretY", "FeretAngle", "MinFeret", "AR", "Round", "Solidity"])
    pc_fiji.add_argument('--graph-min-x', help='minimum value for graph x axis', type=float, default=0.01)
    pc_fiji.add_argument('--graph-max-x', help='maximum value for graph x axis', type=float, default=100)
    pc_fiji.add_argument('--circularity-min', help='circularity lower limit', type=float, default=0.2)

    args = parser.parse_args(arguments)
    return args.func(args)


if __name__ == "__main__":
    main()
