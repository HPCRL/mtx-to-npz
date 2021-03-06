"""
===========================
Converts matrix market files to ndarray npz files.
===========================

Dr. Cai Wingfield
---------------------------
Embodied Cognition Lab
Department of Psychology
University of Lancaster
c.wingfield@lancaster.ac.uk
caiwingfield.net
---------------------------
2017
---------------------------
"""

import argparse
import sys
import logging
import os

import numpy
import scipy.io
import scipy.sparse

from ..common.common import Converter, logger_format, logger_dateformat

logger = logging.getLogger()


class DenseMtxToNpzConverter(Converter):
    def __init__(self):
        super().__init__(source_ext=".mtx", target_ext=".npz")

    def convert_file(self, source_path: str, target_path: str, skip: bool) -> None:

        # Make sure we're not about to overwrite something:
        if os.path.isfile(target_path):
            if skip:
                logger.info(
                    f"{os.path.basename(target_path)} already exists, so skipping {os.path.basename(source_path)}")
                return
            else:
                raise FileExistsError(target_path)

        # Load and convert the file
        logger.info(f"Loading {os.path.basename(source_path)}")
        matrix = scipy.io.mmread(source_path)

        # Save the file
        logger.info(f"Saving {os.path.basename(target_path)}")
        numpy.savez(target_path, matrix)


def main(args):
    """
    Entry point.
    """

    converter = DenseMtxToNpzConverter()

    converter.validate_args(args)

    mode, skip = converter.get_mode(args)

    source_path, target_path = converter.get_paths(args, mode)

    converter.do_conversion(mode, source_path, target_path, skip)


if __name__ == '__main__':
    logging.basicConfig(format=logger_format, datefmt=logger_dateformat, level=logging.INFO)
    logger.info("Running %s" % " ".join(sys.argv))

    parser = argparse.ArgumentParser(description='Convert matrix market text files to npz files.')

    parser.add_argument("source", type=str, help="Path to a .mtx file or a directory. Use '-r' flag for directories.")
    parser.add_argument("--target", "-t", metavar="PATH", type=str, help="Target file or directory.")
    parser.add_argument("--recursive", "-r", action="store_true", help="Convert all files in source directory. "
                                                                       "'source' must be a a directory")
    parser.add_argument("--skip", "-s", action="store_true", help="Skip existing files.")

    main(parser.parse_args())

    logger.info("Done!")
