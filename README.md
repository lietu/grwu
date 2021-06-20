# Grwu

(Not Just) Gnome RSS Wallpaper Updater


## What is this?

Tool to (periodically) update your wallpaper to a random one from a periodically updating RSS feed, e.g. the NASA image of the day feed.

Made primarily for Linux systems and Gnome 3, but it now works on a variety of systems. It also shouldn't be a huge deal to update it to work with XFCE or others.

The systems tested to work are:

 * Gnome 3
 * Unity (Ubuntu 12.04)
 * Mac OS X

Systems assumed to work are:

 * Gnome 2
 * Cinnamon (Linux mint)


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

Well .. it is fairly limited still, I made it specifically for Gnome 3 on my machine, and NASA image of the day feed. It happens to work on Unity (Ubuntu) as well, probably Cinnamon (Linux Mint) and other Gnome forks. Also there is now support for Mac OS X.

It likely only supports very few RSS feeds. Very few "image of the day" type RSS feeds seem to provide links to the original images, only some thumbnails. Some embedd their images in HTML, some used <media> elements, some <enclosure> elements, etc. .. because it all seemed like a huge mess I only implemented a few things and left the other cases up to you.


## How about licensing?

Short answer: new BSD. Full license text embedded in the source.


## Feeds known to work with this tool

* http://www.nasa.gov/rss/dyn/image_of_the_day.rss
* http://www.redorbit.com/feeds/earth_iod.xml


# Financial support

This project has been made possible thanks to [Cocreators](https://cocreators.ee) and [Lietu](https://lietu.net). You can help us continue our open source work by supporting us on [Buy me a coffee](https://www.buymeacoffee.com/cocreators).

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cocreators)
