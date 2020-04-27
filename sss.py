#!/usr/bin/env python3

from base64 import b85decode, b85encode
import os.path
import shutil
import sys
import tempfile

USAGE = """
Sss - Self-extracting Scriptifer

usage:
    python3 sss.py      -- verbose version of sss
    sss                 -- attempt to extract the project contained if any
    sss <directory>     -- scriptify the directory"""

# Python version sanity check (>= 3.5)
if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] <= 4):
    raise Exception('Your Python version has reached EOL!')


def encode_file(filename):
    """Return the base85 string representation of a file."""
    with open(filename, "rb") as fin:
        return b85encode(fin.read()).decode('ascii')


def inject_data(filename, data):
    """Replace the DONT_PANIC placeholder with project data."""
    lines = []
    # Read the script in and substitue the placeholder
    with open(filename, 'rt') as f:
        for line in f:
            if line.startswith('DONT_PANIC'):
                line = data + '\n'
            lines.append(line)
    # Write the injected script out
    with open(filename, 'wt') as f:
        for line in lines:
            f.write('%s' % line)


def scriptify(prj_dir):
    tmpdir = tempfile.mkdtemp()

    try:
        # Copy the file itself
        script_filename = 'sss.py'
        if os.path.exists(script_filename):
            raise Exception(
                'Failed to create %s - file already exists.' % script_filename)
        shutil.copy(__file__, script_filename)

        # Compress data
        zip_filename = os.path.join(tmpdir, 'prj.zip')
        shutil.make_archive(zip_filename[:-4], 'zip', prj_dir)

        # Encode data as base85
        encoded_string = encode_file(zip_filename)
        data_string = '\n'.join([encoded_string[i:i+70]
                                 for i in range(0, len(encoded_string), 70)])

        # Replace placeholder in script with base85 data
        inject_data(script_filename, data_string)

        print("Successfully scripted as %s" % script_filename)

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def projectify():
    if b"DONT_PANIC" in DATA:
        # print usage and exit
        print("There are no project data in this script!")
        print(USAGE)
    else:
        tmpdir = tempfile.mkdtemp()
        confirm = input("Extract project to %s ? ([Y/n]): " % tmpdir)
        if len(confirm) == 0 or confirm.lower() == 'y':
            zip_filename = os.path.join(tmpdir, "prj.zip")
            with open(zip_filename, 'wb') as f:
                f.write(b85decode(DATA.replace(b'\n', b'')))
            shutil.unpack_archive(zip_filename, tmpdir)
            os.remove(zip_filename)
            print('Project extracted successfully!')
        else:
            print('User aborted!')
            shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    if len(sys.argv) == 1:
        projectify()
    else:
        scriptify(sys.argv[1])


DATA = b"""
DONT_PANIC
"""


if __name__ == "__main__":
    main()
