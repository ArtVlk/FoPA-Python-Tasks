#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os.path
import time
import struct
import sys
from dataclasses import dataclass


@dataclass
class FileInfo:
    name: str
    type: str
    mode: int
    uid: int
    gid: int
    size: int
    mtime: int
    checksum: int
    username: str
    groupname: str
    offset: int = 0


class TarParser:
    _HEADER_FMT1 = '100s8s8s8s12s12s8sc100s255s'
    _HEADER_FMT2 = '6s2s32s32s8s8s155s12s'
    _HEADER_FMT3 = '6s2s32s32s8s8s12s12s112s31x'
    _BLOCK_SIZE = 512
    _FILE_READ_SIZE = 16 * (2 ** 20)

    _FILE_TYPES = {
        b'0': 'Regular file',
        b'1': 'Hard link',
        b'2': 'Symbolic link',
        b'3': 'Character device node',
        b'4': 'Block device node',
        b'5': 'Directory',
        b'6': 'FIFO node',
        b'7': 'Reserved',
        b'D': 'Directory entry',
        b'K': 'Long linkname',
        b'L': 'Long pathname',
        b'M': 'Continue of last file',
        b'N': 'Rename/symlink command',
        b'S': "`sparse' regular file",
        b'V': "`name' is tape/volume header name"
    }

    def __init__(self, filename):
        self._filename = filename
        self._temp_name = None
        self._files: dict[str, FileInfo] = {}

        with open(self._filename, 'rb') as file:

            for block in self._block(file):

                info = self._parse_header(block)

                if info is None:
                    break

                if info.type == self._FILE_TYPES[b'L']:
                    file.seek(self._BLOCK_SIZE - info.size % self._BLOCK_SIZE, 1)
                    self._temp_name = file.read(info.size).decode('utf-8').rstrip(' ').rstrip('\x00')

                elif info.type == self._FILE_TYPES[b'0'] or \
                        info.type == self._FILE_TYPES[b'5']:
                    info.offset = file.tell()
                    self._files[info.name] = info

                    file.seek(info.size, 1)
                    if info.size % self._BLOCK_SIZE:
                        file.seek(self._BLOCK_SIZE - info.size % self._BLOCK_SIZE, 1)
                else:
                    print(f"Unsupported file type: {info.type}")
                    raise ValueError("Unsupported type")

    def _block(self, file):
        while block := file.read(self._BLOCK_SIZE):
            yield block

    def _parse_header(self, block):
        header1 = struct.unpack(self._HEADER_FMT1, block)

        if header1[9].startswith(b'ustar\x00'):
            header2 = struct.unpack(self._HEADER_FMT2, header1[-1])
        elif header1[9].startswith(b'ustar '):
            header2 = struct.unpack(self._HEADER_FMT3, header1[-1])
        else:
            return None

        header = header1[:-1] + header2

        if self._temp_name:
            filename = self._temp_name
            self._temp_name = None
        else:
            filename = header[0].decode('utf-8').rstrip(' ').rstrip('\x00')

        info = FileInfo(
            name=filename,
            type=self._FILE_TYPES.get(header[7], 'Unknown'),
            mode=int(header[1].decode('utf-8').rstrip(' ').rstrip('\x00'), 8),
            uid=int(header[2].decode('utf-8').rstrip(' ').rstrip('\x00'), 8),
            gid=int(header[3].decode('utf-8').rstrip(' ').rstrip('\x00'), 8),
            size=int(header[4].decode('utf-8').rstrip(' ').rstrip('\x00'), 8),
            mtime=int(header[5].decode('utf-8').rstrip(' ').rstrip('\x00'), 8),
            checksum=int(header[6].decode('utf-8').rstrip(' ').rstrip('\x00')),
            username=header[11].decode('utf-8').rstrip(' ').rstrip('\x00'),
            groupname=header[12].decode('utf-8').rstrip(' ').rstrip('\x00'),
        )
        return info

    def _reader(self, file, size):
        while size > self._FILE_READ_SIZE:
            yield file.read(self._FILE_READ_SIZE)
            size -= self._FILE_READ_SIZE
        yield file.read(size)

    def extract(self, dest: str = os.getcwd()):
        with open(self._filename, 'rb') as tar_file:
            for info in self._files.values():
                os.makedirs(os.path.dirname(os.path.join(dest, info.name)), exist_ok=True)

                tar_file.seek(info.offset)
                if info.type == self._FILE_TYPES[b'5']:
                    return

                elif info.type == self._FILE_TYPES[b'0']:
                    with open(os.path.join(dest, info.name), 'wb') as extracted_file:
                        for data in self._reader(tar_file, info.size):
                            extracted_file.write(data)

                else:
                    print(f"Unsupported file type: {info.type}")
                    raise ValueError("Unsupported type")

    def files(self):
        return self._files.keys()

    def file_stat(self, filename):
        if filename not in self._files:
            raise ValueError(filename)

        return [("Filename", self._files[filename].name),
                ("Type", self._files[filename].type),
                ("Mode", self._files[filename].mode),
                ("UID", self._files[filename].uid),
                ("GID", self._files[filename].gid),
                ("Size", self._files[filename].size),
                ("Modification time", time.ctime(self._files[filename].mtime)),
                ("Checksum", self._files[filename].checksum),
                ("User name", self._files[filename].username),
                ("Group name", self._files[filename].groupname), ]


def print_info(stat, f=sys.stdout):
    max_width = max(map(lambda s: len(s[0]), stat))
    for field in stat:
        print("{{:>{}}} : {{}}".format(max_width).format(*field), file=f)


def main():
    parser = argparse.ArgumentParser(
        usage='{} [OPTIONS] FILE'.format(os.path.basename(sys.argv[0])),
        description='Tar extractor')
    parser.add_argument('-l', '--list', action='store_true', dest='ls',
                        help='list the contents of an archive')
    parser.add_argument('-x', '--extract', action='store_true', dest='extract',
                        help='extract files from an archive')
    parser.add_argument('-i', '--info', action='store_true', dest='info',
                        help='get information about files in an archive')
    parser.add_argument('-d', '--dest', metavar='DIR', default=os.getcwd(),
                        help='destination directory', dest='dest')
    parser.add_argument('fn', metavar='FILE', help='name of an archive')

    args = parser.parse_args()
    if not (args.ls or args.extract or args.info):
        sys.exit("Error: action must be specified")

    try:
        tar = TarParser(args.fn)

        if args.info:
            for fn in sorted(list(tar.files())):
                print_info(tar.file_stat(fn))
                print()
        elif args.ls:
            for fn in sorted(list(tar.files())):
                print(fn)

        if args.extract:
            tar.extract(args.dest)
    except Exception as e:
        sys.exit(e)


if __name__ == '__main__':
    main()