# Grwu

(Gnome) RSS Wallpaper Updater


## What is this?

Tool to (periodically) update your (Gnome) wallpaper to a random one from an RSS feed, e.g. the NASA image of the day feed.

Made primarily for Linux systems and Gnome 3, but could work (possibly with changes) with e.g. Gnome 2, Unity and maybe (definitely with changes) Mac OS X. Scheduling is left to the user to do via crontab or similar tools.


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


## Wait, I put this in my crontab and it doesn't work?

Yeah, the people beside linux desktop came up with this great thing called dbus and everyone is using it, that's why nothing works in a sane way. To get this script working in your cron entries, you will have to prepend a magic line to them:

```bash
export $(xargs -n 1 -0 echo < /proc/$(pidof gnome-session)/environ | grep -Z DBUS_SESSION_BUS_ADDRESS=)
```

Making your crontab line look like this:

```
30 * * * * export $(xargs -n 1 -0 echo < /proc/$(pidof gnome-session)/environ | grep -Z DBUS_SESSION_BUS_ADDRESS=); /path/to/grwu.py
```

.. look scary? It sort of should, and I look forward to hearing of better alternatives. What it does is:

 * Take the process ID of the running "gnome-session" -process
 * Use this to find the environment for the process information from /proc
 * Extract DBUS_SESSION_BUS_ADDRESS -variable from the environment
 * Export it to your current environment

This is required because gsettings, that is used to update the background image, uses dbus.


## Well what is it that you are not telling us? Are there limitations to this?

Well .. it is fairly limited still, I made it specifically for Gnome 3 on my machine, and NASA image of the day feed.

 * It is actually probably quite specific to gnome as-is. When I got to the DBUS part, I probably ended up making it quite gnome-specific (e.g. Unity probably doesn't have "gnome-session").

 * It likely only supports very few RSS feeds. After I made the tool and thought about checking a few other feeds, I noticed that all the ones I found had different formats. Some embedded their images in HTML, some used <media> elements, some <enclosure> elements, etc. .. because it all seemed like a huge mess I decided not to start implementing any other ones until I think about it a bit more.



## How about licensing?

Short answer: new BSD. Full license text embedded in the source.
