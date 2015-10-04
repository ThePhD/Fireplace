COMS W3101 - Python Exploration Project
=========

Mmm. Warm.

![Cozy, cozy FIRE.](http://puu.sh/ktSZC/126903a3c2.png)

The idea came from seeing many traditional effects in computer graphics, which can mostly be traced back to a paper by William T. Reeves<sup>1</sup>. In it, Reeves laid out many of the fundamentals of particle systems (Page 93 and onward discuss the base equations used, including: distribution schemes, particle properties, and velocity/acceleration considerations).

The goal of this project was to see if something realtime could be made in python (for a very barebones definition of realtime and something). The end result is a little fireplace, with the heavy draw aspects such as Block Image Transfer (blitting), rectangle drawing, and graphics device setting taken care of by pygame. Perhaps it was the heavy use of random() and such, but the framerate visibly struggles when approaching 350+ particles. Not much more could be done with it (this excluded adding a wind effect and another natural phenomena) without drastically reducing the framerate and turning a realtime particle emitter into a not-so-realtime particle emitter.

The core working of the program is to start up a continuous loop (see [main.run](https://github.com/ThePhD/Fireplace/blob/master/Fireplace.py#L178)) that never exits (unless the user tells it to by closing the program or closing the window). Once in that main loop, there are two primary components after setup finishes: the `main.update` method which runs the physical 'simulation' of the particles, and the `main.render` method which draws the current state. The core idea behind any realtime simulation on a machine is to simply run the simulation in various tiny steps as fast as possible, in order to fake the idea of movement or passage of time in an environment: thus, main loops continuously. In `update`, emitter's `step` method is called and physics functionality, making it add things like velocity to the current position and acceleration to the current velocity (with respect to the current time constant). In `render`, a representation of our simulation is chosen to show to the user: it could generate one text file with outputs and positions per frame, but it is much more intuitive and simple for the user to understand an actual moving image in front of them.

The general idea of the emitter is to, if there are less than a certain amount of particles, generate more particles with random velocities and offsets from a particular origin (up to a certain amount per each simulation step or frame). If enough particles with the right colors, velocities, and offsets, it begins to look like a single fuzzy object despite being composed of many individual pieces. Essentially any computable effect can be placed on the emitter. The fire emitter goes through quite a lot of mathematical calculations to get a nice-looking drop-off effect for ash (computed in the rendering step). A possible enhancement would be to use textures instead of rectangles or circles. There's only a single emitter (see [fire_emitter](https://github.com/ThePhD/Fireplace/blob/master/Fireplace.py#L20)), but more could be added for additional effects (bubbles in the ocean, fog, and even smoke for the aftermath of the fire).

For this, as mentioned earlier, pygame<sup>2</sup> is used. It's really just a wrapper around the C library SDL<sup>3</sup>, which is responsible for putting things on the screen without getting involved in low-level details. This allows us to clear the window to the white color and then draw the several particle bits that make the fire effect.


<sup>1</sup> - Reeves, William T. & Lucasfilm, Ltd. _Particle Systems. A Technique for Modeling a Class of Fuzzy Objects_ ACM Transactions on Graphics (TOG). Volume 2, Issue 2, April 1983. Pages 91-108. New York, NY, USA.
<sup>2</sup> - Pygame: http://pygame.org/hifi.html
<sup>3</sup> - Simple DirectMedia Layer (SDL): https://www.libsdl.org/
