#!/usr/bin/env python3

#    Copyright (C) 2006  Andrew Straw  <strawman@astraw.com>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#

import os
import stat
import errno

# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse


if not hasattr(fuse, "__version__"):
    raise RuntimeError(
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."
    )

fuse.fuse_python_api = (0, 2)

FILES = {
    "/subject": b"""2110313 - Operating System
2021/2
""",
    "/instructors": b"""0 : Instructors of 2110313 - 2021/2
1: Krerk Piromsopa, Ph.D.
2: Veera Muangsin, Ph. D.
3: Thongchai Rojkangsada
""",s
}


class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0


class HelloFS(Fuse):
    def getattr(self, path):
        st = MyStat()
        if path == "/":
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
        elif path in FILES:
            st.st_mode = stat.S_IFREG | 0o444
            st.st_nlink = 1
            st.st_size = len(FILES[path])
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        paths = [".", ".."] + [path[1:] for path in FILES]
        for path in paths:
            yield fuse.Direntry(path)

    def open(self, path, flags):
        if path not in FILES:
            return -errno.ENOENT
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset):
        if path not in FILES:
            return -errno.ENOENT
        content = FILES[path]
        slen = len(content)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = content[offset : offset + size]
        else:
            buf = b""
        return buf


def main():
    usage = (
        """
Userspace hello example
"""
        + Fuse.fusage
    )
    server = HelloFS(
        version="%prog " + fuse.__version__, usage=usage, dash_s_do="setsingle"
    )

    server.parse(errex=1)
    server.main()


if __name__ == "__main__":
    main()
