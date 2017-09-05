Converts between matrix market `.mtx` files and scipy sparse `.npz` files.

## Usage

### `mtx_to_npz.py`

Convert `.mtx` files to `.npz` files.

### `npz_to_mtx.py`

Convert `.npz` files to `.mtx` files.
This will only work if the `.npz` files were generated using `scipy.sparse.savenz`.

## Options

Invoke like this:

```commandline
python mtx_to_npz.py --help
```

Available operations:

### `python mtx_to_npz.py <source-file>`

Converts and saves the file in place.

### `python mtx_to_npz.py <source-file> -t <directory-path>`

Converts and saves the file to the target directory.

### `python mtx_to_npz.py <source-file> -t <file-path>`

Converts and saves to a specified file (which should not already exist).


## Requirements

- Requires python 3.6+.
- Requires scipy.
