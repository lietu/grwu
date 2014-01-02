# Grwu

(Gnome) RSS Wallpaper Updater


## What is this?

Tool to (periodically) update your (Gnome) wallpaper to a random one from an RSS feed, e.g. the NASA image of the day feed.

Made primarily for Linux systems and Gnome 3, it has been tested to work without changes on Unity (Ubuntu 12.04), and could work (possibly with changes) with e.g. Gnome 2, Cinnamon, and (definitely with changes) Mac OS X. It also shouldn't be a huge deal to update it to work with XFCE or others.

Scheduling is left to the user to do via crontab or similar tools. The tool tries to make sure it works from cron by taking care of e.g. DBUS session.


## Why is this?

I had a "dynamic theme" in my Windows desktop doing the same, getting a random NASA image of the day and updating the wallpaper every 30min. I wanted the same on my Linux desktops, but I couldn't find a tool for doing that, so I rolled my own.


## Where is it?

The downloads, code, issue tracker, Wiki, etc. is are available at the [https://github.com/lietu/grwu](GitHub project page)


## Well how do I use it?

Download the grwu.py file somewhere on your filesystem, or clone the repository, give it execute permissions and run it, optionally you can give an URL to the RSS feed as the first argument. If not given, it defaults to NASA image of the day -feed.

```bash
git clone git@github.com:lietu/grwu.git
cd grwu

chmod +x grwu.py
./grwu.py [url]
# OR
python grwu.py [url]
```

Where [url] is an optional URL to the RSS feed you want to use.


## Well what is it that you are not telling us? Are there limitations to this?

Well .. it is fairly limited still, I made it specifically for Gnome 3 on my machine, and NASA image of the day feed. It happens to work on Unity (Ubuntu) as well, probably Cinnamon (Linux Mint) and other Gnome forks.

 * It currently supports only Gnome and compatible systems. It shouldn't be a big deal to start supporting desktop environments.

 * It likely only supports very few RSS feeds. Very few "image of the day" type RSS feeds seem to provide links to the original images, only some thumbnails. Some embedd their images in HTML, some used <media> elements, some <enclosure> elements, etc. .. because it all seemed like a huge mess I only implemented a few things and left the other cases up to you.


## How about licensing?

Short answer: new BSD. Full license text embedded in the source.


## Feeds known to work with this tool

* http://www.nasa.gov/rss/dyn/image_of_the_day.rss
* http://www.redorbit.com/feeds/earth_iod.xml
