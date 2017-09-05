Converts matrix market `.mtx` files to scipy sparse `.npz` files.

## Usage

Invoke like this:

```commandline
python mtx_to_npz.py --help
```

Available operations:

__`python mtx_to_npz.py <source-file>`__

Converts and saves the file in place.

__`python mtx_to_npz.py <source-file> -t <directory-path>`__

Converts and saves the file to the target directory.

__`python mtx_to_npz.py <source-file> -t <file-path>`__

Converts and saves to a specified file (which should not already exist).


## Requirements

- Requires python 3.6+.
- Requires scipy.
