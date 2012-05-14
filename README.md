MediaRename
-----------


Prerequisites
=============

This is the command I ran to get the python libraries used by
`mediarename` on Debian:

    $ apt-get install python-tagpy

This is the media tags reading library.


Introduction
============

Do you have an MP3 player that only plays files in file-alphabetical
order?  I've had a few.  I've also seen car audio systems that do the
same.  It's extremely inconvenient to place files you already have in a
way that makes them easy to search and playback in a reasonable order on
these sorts of players.

`mediarename` is a simple python script that makes this job simple.

It also makes it easy to sort arbitrary media files into a
well-structured set of directories for long-term storage.

It relies entirely on good media tags.  If your files don't have the
meta data fields set correctly, set them before you run mediarename (I
recommend the `easytag` application)


Sorting For Archive
===================

Let's say you've just encoded all your David Bowie albums.  You've got
some of them in your archive already; and they are from various albums.

    $ mediarename.py --path=/music --move *.mp3
    mediarename: --- Command line mode
    mediarename: 'David Bowie  Outside.mp3' => '/music/DavidBowie/Outside.mp3'
    mediarename: 'DriveinSaturday.mp3' => '/music/DavidBowie/DriveInSaturday.mp3'
    mediarename: 'ALBUM10_Track1.mp3' => '/music/DavidBowie/LetsDance.mp3'
    mediarename: skipping existing target, /music/DavidBowie/ModernLove.mp3
    mediarename: 'RocknRollSuicide.mp3' => '/music/DavidBowie/RockNRollSuicide.mp3'

In this run, all the files are placed in the same directory, regardless
of album.  You can add `--albums` to put the album name in as well.



Alphabetical For Player
=======================

For a player that only plays alphabetically by filename, do something
like this:

    $ mediarename.py --path=/media/USBSTORAGE --tracknums --albums *.mp3
    mediarename: --- Command line mode
    mediarename: Creating directory '/media/USBSTORAGE/DavidBowie/2002_BestOfBowie'
    mediarename: 'ModernLove.mp3' => '/media/USBSTORAGE/DavidBowie/2002_BestOfBowie/016_ModernLove.mp3'
    mediarename: Creating directory '/media/USBSTORAGE/DavidBowie/2002_BestOfBowie'
    mediarename: 'RebelRebel.mp3' => '/media/USBSTORAGE/DavidBowie/2002_BestOfBowie/006_RebelRebel.mp3'
    mediarename: Creating directory '/media/USBSTORAGE/DavidBowie/2002_BestOfBowie'
    mediarename: 'ZiggyStardust.mp3' => '/media/USBSTORAGE/DavidBowie/2002_BestOfBowie/004_ZiggyStardust.mp3'




