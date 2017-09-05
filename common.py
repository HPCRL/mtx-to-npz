"""
===========================
Common code.
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

from typing import List
from abc import ABCMeta, abstractmethod
from enum import Enum, auto

import os

logger = logging.getLogger()

logger_format = '%(asctime)s | %(levelname)s | %(module)s | %(message)s'
logger_dateformat = "%Y-%m-%d %H:%M:%S"


class ExecutionMode(Enum):
    """
    The mode of execution for the program.
    What it will do with paths specified in the CLI arguments.
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


class Converter(object, metaclass=ABCMeta):
    """
    Converts one kind of file to another.
    """
    def __init__(self, source_ext: str, target_ext: str):
        # Extension of the source file
        self.source_ext = source_ext
        # Extension of the target file
        self.target_ext = target_ext

    @abstractmethod
    def convert_file(self, source_path: str, target_path: str, skip: bool) -> None:
        """
        Convert a single file.
        """
        raise NotImplementedError()

    def convert_files(self, source_paths: List[str], target_dir: str, skip: bool) -> None:
        """
        Convert multiple files.
        """
        for source_path in source_paths:
            source_filename = os.path.basename(source_path)
            target_filename = os.path.splitext(source_filename)[0] + self.target_ext
            target_path = os.path.join(target_dir, target_filename)

            self.convert_file(source_path, target_path, skip)

    @classmethod
    def validate_args(cls, args) -> None:
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

    @classmethod
    def get_mode(cls, args):
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

    def get_paths(self, args, mode: ExecutionMode):
        """
        Determine the source and target paths.
        """

        if mode == ExecutionMode.file_to_file:
            source_dir, source_filename = os.path.split(args.source)
            # Different name, different dir
            target_dir, target_filename = os.path.split(args.target)
            # Verify filename
            if not target_filename.endswith(self.target_ext):
                target_filename += self.target_ext

        elif mode == ExecutionMode.file_to_dir:
            source_dir, source_filename = os.path.split(args.source)
            # Same name, target dir
            target_dir = args.target
            target_filename = os.path.splitext(os.path.basename(args.source))[0] + self.target_ext

        elif mode == ExecutionMode.file_in_place:
            source_dir = args.source
            source_filename = None
            # same name, same dir
            target_dir = os.path.split(args.source)[0]
            target_filename = os.path.splitext(os.path.basename(args.source))[0] + self.target_ext

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

    def do_conversion(self, mode: ExecutionMode, source_path: str, target_path: str, skip: bool) -> None:
        """
        Do the appropriate conversion based on program mode.
        """
        if mode in [
            ExecutionMode.all_in_place,
            ExecutionMode.all_to_dir
        ]:
            # Get all source files
            source_paths = glob.glob(os.path.join(source_path, "*" + self.source_ext))
            self.convert_files(source_paths, target_path, skip)

        else:
            self.convert_file(source_path, target_path, skip)
