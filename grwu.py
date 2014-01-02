#!/usr/bin/env python
#
# GRWU - (Gnome) RSS Wallpaper Updater
#
# https://github.com/lietu/grwu
#
# Reads an RSS feed, picks an image out of it, downloads it and updates your
# gnome background image with that image.
#
# Recommend using with crontab (run "crontab -e" to edit it), add e.g.:
#
# 30 * * * * python /path/to/grwu.py "http://url.to/feed.rss"
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

from random import choice
from tempfile import NamedTemporaryFile
import os
import re
import subprocess
import sys
import urllib2
import xml.etree.ElementTree as ET
import zlib


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
    """Updates wallpapers to desktop environments"""

    def __init__(self, quiet):
        self.quiet = quiet

    def log(self, message):
        if not self.quiet:
            print(message)

    def update(self, path):
        """Update wallpaper on the desktop"""

        self.log("Updating background to " + path)

        processes = [
            # This actually works on Unity as well
            "gnome-session"
        ]

        for name in processes:
            pid = self._get_pid(name)
            if pid:
                break

        if not pid:
            raise Exception("Failed to find a supported desktop environment")

        self.log("Found {} running".format(name))

        if name == "gnome-session":
            self._update_gnome(path, pid)

    def _update_gnome(self, path, pid):
        """Updates wallpaper to Gnome and similar (e.g. Unity)"""

        env = self._get_gnome_env(pid)
        subprocess.Popen(
            [
                "gsettings", "set", "org.gnome.desktop.background",
                "picture-uri", "file://" + path
            ],
            env=env
        )

    def _get_gnome_env(self, pid):
        """Get an environment that'll allow communicating with Gnome"""

        session = self._get_dbus_session_bus_address(pid)

        env = os.environ.copy()
        env["DBUS_SESSION_BUS_ADDRESS"] = session

        return env

    def _get_dbus_session_bus_address(self, pid):
        """Get the DBUS_SESSION_BUS_ADDRESS for the given pid"""

        if not pid:
            raise Exception(
                "Failed to figure out PID of gnome-session. Cannot extract "
                "DBUS_SESSION_BUS_ADDRESS, so cannot continue."
            )

        path = '/proc/{}/environ'.format(pid)

        session = None
        with open(path, 'r') as f:
            for line in f.read().split('\0'):
                if line.startswith('DBUS_SESSION_BUS_ADDRESS='):
                    session = line[25:]
                    break

        self.log("Using DBUS_SESSION_BUS_ADDRESS {}".format(session))

        return session

    def _get_pid(self, name):
        """Find the PID for the given process"""

        p = subprocess.Popen(
            [
                "pidof",
                name
            ],
            stdout=subprocess.PIPE
        )

        pid, err = p.communicate()

        return pid.strip()


class WallpaperLoader(object):
    """Loads wallpapers off RSS feeds"""

    def __init__(self, quiet):
        self.quiet = quiet

    def log(self, message):
        if not self.quiet:
            print(message)

    def load(self, rssUrl, storeDir, keepFiles):
        """Update wallpaper from RSS feed"""

        # Check that our path exists
        if not os.path.isdir(storeDir):
            os.makedirs(storeDir)

        # Get the new wallpaper image
        path = self._get_wallpaper(rssUrl, storeDir)

        # Clean up if needed
        if not keepFiles:
            self._clean_dir(storeDir, [path])

        return path

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
        root, namespaces = self._load_rss(rssUrl, storeDir)

        for enc in root.iter('enclosure'):
            if enc.attrib["type"].startswith("image/"):
                uris.append(enc.attrib["url"])

        search = self._get_ns_search('media:content', namespaces)
        for item in root.iter(search):
            if item.attrib["type"].startswith("image/"):
                uris.append(item.attrib["url"])

        self.log("Found {} images in feed".format(str(len(uris))))

        if len(uris) == 0:
            raise Exception("Failed to find any images in the RSS feed")

        return uris

    def _get_ns_search(self, search, namespaces):
        """Convert namespace searches to format supported by ET"""

        for src in namespaces:
            dst = namespaces[src]
            search = search.replace(src, dst)

        return search

    def _load_rss(self, rssUrl, storeDir):
        """Load XML for the RSS, returns root node"""

        filename = self._load_uri(rssUrl, storeDir)

        namespaces = {}
        with open(filename, 'r') as f:
            for line in f:
                if line.find("<rss ") != -1:
                    namespaces = self._parse_namespaces(line)

        et = ET.parse(filename)
        root = et.getroot()
        os.remove(filename)

        return root, namespaces

    def _parse_namespaces(self, rssTagLine):
        """Parse namespace information out of the <rss> tag"""

        r = re.compile(r' xmlns:([^=]+)="([^"]+)"')

        namespaces = {}
        for match in r.finditer(rssTagLine):
            namespaces[match.group(1) + ':'] = '{' + match.group(2) + '}'

        return namespaces

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

    loader = WallpaperLoader(quiet)
    updater = WallpaperUpdater(quiet)

    path = loader.load(rssUrl, tempPath, keepFiles)
    updater.update(path)
