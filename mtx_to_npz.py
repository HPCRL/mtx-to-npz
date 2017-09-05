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
import glob
import logging
import os
import sys
import argparse

from typing import List
from enum import Enum, auto

import scipy.io
import scipy.sparse

logger = logging.getLogger()
logger_format = '%(asctime)s | %(levelname)s | %(module)s | %(message)s'
logger_dateformat = "%Y-%m-%d %H:%M:%S"


class ExecutionMode(Enum):
    """
    Where the file will be saved
    """
    # In the same directory, with the same name
    file_in_place = auto()
    # In a target directory, with the same name
    file_to_dir = auto()
    # In a specified file
    file_to_file = auto()
    # All files in place
    all_in_place = auto()
    # All files to target directory, same names
    all_to_dir = auto()


source_ext = ".mtx"
target_ext = ".npz"


def main(args):
    """
    Entry point.
    """

    validate_args(args)

    mode, skip = get_mode(args)

    source_path, target_path = get_paths(args, mode)

    do_conversion(mode, source_path, target_path, skip)


def do_conversion(mode: ExecutionMode, source_path: str, target_path: str, skip: bool) -> None:
    """
    Do the appropriate conversion based on program mode.
    """
    if mode in [
        ExecutionMode.all_in_place,
        ExecutionMode.all_to_dir
    ]:
        # Get all source files
        source_paths = glob.glob(os.path.join(source_path, "*" + source_ext))
        convert_files(source_paths, target_path, skip)

    else:
        convert_file(source_path, target_path, skip)


def get_paths(args, mode: ExecutionMode):
    """
    Determine the source and target paths.
    """

    if mode == ExecutionMode.file_to_file:
        source_dir, source_filename = os.path.split(args.source)
        # Different name, different dir
        target_dir, target_filename = os.path.split(args.target)
        # Verify filename
        if not target_filename.endswith(target_ext):
            target_filename += target_ext

    elif mode == ExecutionMode.file_to_dir:
        source_dir, source_filename = os.path.split(args.source)
        # Same name, target dir
        target_dir = args.target
        target_filename = os.path.splitext(os.path.basename(args.source))[0] + target_ext

    elif mode == ExecutionMode.file_in_place:
        source_dir = args.source
        source_filename = None
        # same name, same dir
        target_dir = os.path.split(args.source)[0]
        target_filename = os.path.splitext(os.path.basename(args.source))[0] + target_ext

    elif mode == ExecutionMode.all_to_dir:
        source_dir = args.source
        source_filename = None
        # same names, target dir
        target_dir = args.target
        target_filename = None

    elif mode == ExecutionMode.all_in_place:
        source_dir = args.source
        source_filename = None
        # same names, same dir
        target_dir = args.source
        target_filename = None

    else:
        raise ValueError()

    # Source is file or directory?
    if source_filename is None:
        source_path = source_dir
    else:
        source_path = os.path.join(source_dir, source_filename)

    # Target is file or directory?
    if target_filename is None:
        target_path = target_dir
    else:
        target_path = os.path.join(target_dir, target_filename)

    return source_path, target_path


def validate_args(args) -> None:
    """
    Make sure specified args are in a legal state.
    Raise errors if not.
    """

    # recursive => source is dir
    if args.recursive and not os.path.isdir(args.source):
        logger.error("Use recursive option with and only with directories.")
        raise NotADirectoryError(args.source)

    # recursive => target is dir (if specified)
    if args.recursive and args.target and not os.path.isdir(args.target):
        logger.error("Use recursive option with and only with directories.")
        raise NotADirectoryError(args.target)

    # source is dir => recursive
    if os.path.isdir(args.source) and not args.recursive:
        logger.error("Use recursive option with and only with directories.")
        raise NotADirectoryError(args.source)


def get_mode(args):
    """
    Determine the mode of execution of the program.
    """

    recursive = args.recursive
    target = args.target
    skip = args.skip

    # mode
    if recursive:
        if target:
            logger.info("Mode: Converting all files to target directory")
            mode = ExecutionMode.all_to_dir
        else:
            logger.info("Mode: Converting all files in place")
            mode = ExecutionMode.all_in_place
    else:
        if target:
            if os.path.isdir(target):
                logger.info("Mode: Convert file to target directory")
                mode = ExecutionMode.file_to_dir
            else:
                logger.info("Mode: Convert file to target file")
                mode = ExecutionMode.file_to_file
        else:
            logger.info("Mode: Convert file in place")
            mode = ExecutionMode.file_in_place

    return mode, skip


def convert_files(source_paths: List[str], target_dir: str, skip: bool) -> None:
    """
    Convert multiple files from mtx to npz.
    """
    for source_path in source_paths:

        source_filename = os.path.basename(source_path)
        target_filename = os.path.splitext(source_filename)[0] + target_ext
        target_path = os.path.join(target_dir, target_filename)

        convert_file(source_path, target_path, skip)


def convert_file(source_path: str, target_path: str, skip: bool) -> None:
    """
    Convert a single file from mtx to npz.
    """

    # Make sure we're not about to overwrite something:
    if os.path.isfile(target_path):
        if skip:
            logger.info(f"{os.path.basename(target_path)} already exists, so skipping {os.path.basename(source_path)}")
            return
        else:
            raise FileExistsError(target_path)

    # Load and convert the file
    logger.info(f"Loading {os.path.basename(source_path)}")
    matrix = scipy.io.mmread(source_path).tocsr()

    # Save the file
    logger.info(f"Saving {os.path.basename(target_path)}")
    # Don't compress, to save memory.  TODO: does this actually save memory?
    scipy.sparse.save_npz(target_path, matrix, compressed=False)


if __name__ == '__main__':
    logging.basicConfig(format=logger_format, datefmt=logger_dateformat, level=logging.INFO)
    logger.info("Running %s" % " ".join(sys.argv))

    parser = argparse.ArgumentParser(description='Convert matrix market text files to npz files.')

    parser.add_argument("source", type=str, help="Path to a .mtx file or a directory. Use '-r' flag for directories.")
    parser.add_argument("--target", "-t", metavar="PATH", type=str, help="Target file or directory.")
    parser.add_argument("--recursive", "-r", action="store_true", help="All files in source directory.")
    parser.add_argument("--skip", "-s", action="store_true", help="Skip existing files.")

    main(parser.parse_args())

    logger.info("Done!")
