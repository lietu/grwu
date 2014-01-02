#!/usr/bin/env python
#
# GRWU - Gnome RSS Wallpaper Updater
#
# https://github.com/lietu/grwu
#
# Reads an RSS feed, picks an image out of it, downloads it and updates your
# gnome background image with that image.
#
# Recommend using with crontab (run "crontab -e" to edit it), add e.g.:
#
# 30 * * * * export $(xargs -n 1 -0 echo </proc/$(pidof gnome-session)/environ | grep -Z DBUS_SESSION_BUS_ADDRESS=); python /path/to/grwu.py "http://url.to/feed.rss"
#
#
# Distributed with the "New BSD License":
# ---------------------------------------
#
# Copyright (c) 2014, Janne Enberg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of grwu nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import os
import sys
import zlib
import urllib2
import xml.etree.ElementTree as ET
from random import choice
from tempfile import NamedTemporaryFile
from subprocess import call


# Read this many bytes of HTTP responses per iteration
READ_BLOCK_SIZE = 1024 * 8

# Default RSS feed url
rssUrl = "http://www.nasa.gov/rss/dyn/image_of_the_day.rss"

# Path to store wallpapers in
tempPath = '/tmp/gnome-wallpaper-updater/'

# Set to True to NOT delete all old files after update
keepFiles = False

# Shush, don't output anything
quiet = True


class WallpaperUpdater(object):

    def __init__(self, quiet):
        self.quiet = quiet

    def log(self, message):
        if not self.quiet:
            print(message)

    def update(self, rssUrl, storeDir, keepFiles):
        """Update wallpaper from RSS feed"""

        # Check that our path exists
        if not os.path.isdir(storeDir):
            os.makedirs(storeDir)

        # Get the new wallpaper image
        path = self._get_wallpaper(rssUrl, storeDir)

        # Update it as the wallpaper
        self._set_wallpaper(path)

        # Clean up if needed
        if not keepFiles:
            self._clean_dir(storeDir, [path])

    def _get_wallpaper(self, rssUrl, storeDir):
        """Download new wallpaper and return full path to file"""

        uri = self._get_wallpaper_uri(rssUrl, storeDir)
        return self._load_uri(uri, storeDir)

    def _get_wallpaper_uri(self, rssUrl, storeDir):
        """Pick the wallpaper image to use from the RSS feed"""

        return choice(self._get_wallpaper_uris(rssUrl, storeDir))

    def _get_wallpaper_uris(self, rssUrl, storeDir):
        """Get a list of image URIs in the RSS feed"""

        uris = []
        root = self._load_rss(rssUrl, storeDir)
        for enc in root.iter('enclosure'):
            if enc.attrib["type"].startswith("image/"):
                uris.append(enc.attrib["url"])

        self.log("Found {} images in feed".format(str(len(uris))))

        return uris

    def _load_rss(self, rssUrl, storeDir):
        """Load XML for the RSS, returns root node"""

        filename = self._load_uri(rssUrl, storeDir)
        root = ET.parse(filename).getroot()
        os.remove(filename)

        return root

    def _load_uri(self, uri, storeDir):
        """Load URI contents, handle gzip, save to file"""

        self.log("Loading " + uri)
        request = urllib2.Request(uri)
        request.add_header('Accept-Encoding', 'gzip')
        response = urllib2.urlopen(request)
        encoding = response.headers.get('content-encoding', '')

        isGZipped = encoding.find('gzip') >= 0

        filename = uri.split('/')[-1].split('#')[0].split('?')[0]
        extension = filename.split('.')[-1]

        tmp = NamedTemporaryFile(
            suffix='.'+extension,
            dir=storeDir,
            delete=False
        )

        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        while True:
            data = response.read(READ_BLOCK_SIZE)
            if not data:
                break

            if isGZipped:
                data = d.decompress(data)

            tmp.file.write(data)

        return tmp.name

    def _set_wallpaper(self, filename):
        """Update gnome wallpaper"""

        self.log("Updating background to " + filename)
        call([
            "gsettings", "set", "org.gnome.desktop.background", "picture-uri",
            "file://" + filename
        ])

    def _clean_dir(self, path, exclude):
        """Remove all but excluded contents in given path"""

        for root, dirs, filenames in os.walk(path):
            for f in filenames:
                fullpath = os.path.join(path, f)
                if not fullpath in exclude:
                    os.remove(fullpath)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        rssUrl = sys.argv[1]

    wu = WallpaperUpdater(quiet)
    wu.update(rssUrl, tempPath, keepFiles)
