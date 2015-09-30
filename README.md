COMS W3101 - Python Exploration Project
=========

Mmm. Warm.

![Cozy, cozy FIRE.](http://puu.sh/ktSZC/126903a3c2.png)

The goal of this project was to see if something realtime could be made in python (for a very barebones definition of realtime and something).
The end result is a little fireplace, with the heavy draw aspects taken care of by pygame.
Perhaps it was my use of random() and such, but the framerate visibly struggles when I approach 350+ particles.
So, I couldn't do many other things with it.

There's only a single emitter (see [fire_emitter](https://github.com/ThePhD/Fireplace/blob/master/Fireplace.py#L20)).

The emitter goes through quite a lot of mathematical calculations to get a nice-looking drop-off effect for ash.
Everything interesting is in Fireplace.py
A possible enhancement would be to use textures instead of blocky drawings.
