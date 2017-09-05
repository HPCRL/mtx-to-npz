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

import logging
import os
import sys
import argparse

from enum import Enum, auto

import numpy
import scipy.io

logger = logging.getLogger()
logger_format = '%(asctime)s | %(levelname)s | %(module)s | %(message)s'
logger_dateformat = "%Y-%m-%d %H:%M:%S"


class TargetType(Enum):
    """
    Where the file will be saved
    """
    # In the same directory, with the same name
    in_place = auto()
    # In a target directory, with the same name
    to_dir = auto()
    # In a specified file
    to_file = auto()


def main(args):

    target_ext = ".npz"

    # Parse args
    source_path = args.source
    if args.target:
        if os.path.isdir(args.target):
            target_type = TargetType.to_dir
        else:
            target_type = TargetType.to_file
    else:
        target_type = TargetType.in_place

    # Determine target path
    if target_type == TargetType.to_file:
        logger.info("Mode: save to file")
        target_path: str = args.target
        # Verify filename
        if not target_path.endswith(target_ext):
            target_path += target_ext
    elif target_type == TargetType.to_dir:
        logger.info("Mode: save to directory")
        # Same name, target dir
        target_path: str = os.path.join(
            args.target,
            os.path.splitext(os.path.basename(source_path))[0] + target_ext)
    elif target_type == TargetType.in_place:
        logger.info("Mode: saving in place")
        # same name, same dir
        target_path = os.path.splitext(source_path)[0] + target_ext
    else:
        raise ValueError()

    # Check files
    if not os.path.isfile(source_path):
        raise FileNotFoundError(source_path)
    if os.path.isfile(target_path):
        raise FileExistsError(target_path)

    # Do the work

    logger.info(f"Loading {os.path.basename(source_path)}")
    matrix = scipy.io.mmread(source_path).tocsr()

    logger.info(f"Saving {os.path.basename(target_path)}")
    numpy.savez(target_path, matrix)


if __name__ == '__main__':
    logging.basicConfig(format=logger_format, datefmt=logger_dateformat, level=logging.INFO)
    logger.info("Running %s" % " ".join(sys.argv))

    parser = argparse.ArgumentParser(description='Convert matrix market text files to numpy ndarray npz files.')

    parser.add_argument("source", type=str, help=".mtx file")
    parser.add_argument("--target", "-t", metavar="PATH", type=str, help="target file or directory")

    main(parser.parse_args())

    logger.info("Done!")
