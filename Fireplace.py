import sys
import pygame
import time
import random
import math
import numpy
from coords import *

class particle ():
     def __init__(self):
          self.life = 0
          self.xvelocity = 0
          self.yvelocity = 0
          self.xacceleration = 0
          self.yacceleration = 0
          self.x = 0
          self.y = 0
          self.color = (0, 0, 0, 255)

class fire_emitter ():
     def __init__(self):
          self.x = 0
          self.y = 0
          self.basesize = (-30.0, 30.0)
          self.heightjitter = (-15.0, 15.0)
          self.particles = []
          self.dead = []
          self.initialparticlecount = 50
          # can't seem to handle more than this without making optimizations
          # of some sort...
          self.maxparticles = 700
          self.xvelrange = (-60, 60)
          self.yvelrange = (150, 250)
          self.particlesperstep = 5
          self.persistence = 0.75
          self.start()
          self.radius = 175

     def gen_particle ( self, i ):
          colors = [
               #(150, 150, 24, 255),
               (255, 255, 24, 255),
               (255, 125, 0, 255),
               (191, 87, 0, 255),
               #(150, 0, 24, 255),
               #(157, 41, 51, 255),
               #(140, 127, 127, 255),
               #(105, 105, 105, 255),
               #(0, 0, 0, 255),
          ]
          xrand = random.randint(self.basesize[0], self.basesize[1])
          yrand = random.randint(self.heightjitter[0], self.heightjitter[1])
          xvel = random.randint(self.xvelrange[0], self.xvelrange[1])
          yvel = random.randint(self.yvelrange[0], self.yvelrange[1])
          p = particle()
          p.x = xrand
          p.y = yrand
          p.xvelocity = xvel
          p.yvelocity = yvel
          p.life = 1
          p.color = colors[random.randint(0, len(colors)-1)]
          return p

     def start( self ):
          for i in range(self.initialparticlecount):
               p = self.gen_particle(i)
               self.particles.append(p)

     def particle_step( self, p, dt ):
          c2 = p.x * p.x + p.y * p.y
          if ( c2 > self.radius * self.radius ):
               p.life = 0

     def step( self, dt ):
          self.dead.clear()
          for i in range(self.particlesperstep):
               if len(self.particles) >= self.maxparticles:
                    break
               p = self.gen_particle(i)
               self.particles.append(p)

          for i, p in enumerate(self.particles):
               p.xvelocity += p.xacceleration * dt
               p.yvelocity += p.yacceleration * dt
               p.x += p.xvelocity * dt
               p.y += p.yvelocity * dt
               self.particle_step( p, dt )
               if p.life == 0:
                    self.dead.append(i)

          for i in reversed(self.dead):
                self.particles.pop(i)          

     def particle_render( self, screen, p ):
          c2 = math.sqrt(p.x * p.x + p.y * p.y)
          radiusratio = ( c2 / self.radius )
          alpharatio = 1 - radiusratio
          # color
          color = ( p.color[0], p.color[1], p.color[2], p.color[3] * alpharatio )
          ashcolor = (0, 0, 0, alpharatio)
          # don't start coloring for ash until it gets to (+0.5) or farther in radius
          ashbias = float(clamp(radiusratio, self.persistence, 1))
          ashbias = (1 - ashbias) / (1 - self.persistence)
          ashbias = tuple([ashbias]*4)
          color = interpolate_inverse( color, ashcolor, ashbias)
          x, y = to_screen( screen, p.x + self.x, p.y + self.y )
          x, y = center( x, y, 4, 4 )
          # The rectangle looks better
          pygame.draw.rect( screen, color, ( x, y, 17, 17 ) )
          #pygame.draw.circle( screen, color, (int(x), int(y)), 10 )

     def render( self, screen ):
          for p in self.particles:
               self.particle_render( screen, p )

class main():
     def __init__(self):
          pygame.init()
          self.size = self.width, self.height = 300, 240
          self.running = False
          self.firstupdate = True
          self.firstrender = True
          self.targetrendertime = 1.0 / 100.0 # 10.0 millisecond update timing goal
          self.targetupdatetime = 1.0 / 100.0 # 10.0 millisecond render timing goal
          self.clearcolor = (0, 0, 0, 255)
          self.updatedelta = 0
          self.renderdelta = 0
          self.updatelag = 0
          self.renderlag = 0
          self.updatetime = time.perf_counter()
          self.rendertime = time.perf_counter()
          self.emitters = []
          self.steptime = 1.0 / 60.0
          pygame.display.set_caption("Fireplace")
          self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.SRCALPHA | pygame.DOUBLEBUF, 24)
          self.screenbuffer = pygame.Surface(self.size, pygame.SRCALPHA )
     
     def inner_run(self):
          while self.running:
               # handle events
               for event in pygame.event.get():
                    if event.type == pygame.QUIT: 
                         return
                    elif event.type == pygame.KEYDOWN: 
                         pass
               # call step and render methods
              
               # perform timing and first time checks
               if self.firstupdate:
                    self.firstupdate = False
                    self.updatedelta = 0
                    self.updatelag = 0
                    self.updatetime = time.perf_counter()
                    self.update()
               else:
                    self.updatedelta = time.perf_counter() - self.updatetime
                    if self.targetupdatetime <= self.updatedelta:
                         self.updatelag = self.targetupdatetime - self.updatedelta
                         self.update()
                         # update related timing
                         self.updatetime = time.perf_counter()
               
               # perform timing and first time checks
               if self.firstrender:
                    self.firstrender = False
                    self.renderdelta = 0
                    self.renderlag = 0
                    self.rendertime = time.perf_counter()
                    self.render()
               else:
                    self.renderdelta = time.perf_counter() - self.rendertime
                    if self.targetrendertime <= self.renderdelta:
                         self.renderlag = self.targetrendertime - self.renderdelta
                         self.render()
                         # update related timing
                         self.rendertime = time.perf_counter()

     def run(self):
          self.running = True
          self.firstupdate = True
          self.firstrender = True
          self.initialize()
          self.inner_run()
          self.running = False
          pygame.quit()

     def initialize(self):
          self.clearcolor = (255, 255, 255, 255)
          f = fire_emitter();
          f.x = self.screen.get_width() / 2.0
          self.emitters.append(f)

     def update(self):
          # update hardcore logic here
          
          # variable framerate is actually a terrible idea for simulations
          # so if the performance tanked this would actually make any real physics system freak out
          # self.step(self.updatedelta)
          self.step(self.steptime)
          
          # post physics logic here
          
     def step(self, deltatime):
          # physics items go here
          for e in self.emitters:
               e.step(deltatime)
          
     def render(self):
          self.screen.fill(self.clearcolor)
          self.screenbuffer.fill((0, 0, 0, 0))
          # render all the things here
          for e in self.emitters:
               e.render( self.screenbuffer )
          self.screen.blit( self.screenbuffer, (0,0), None )
          pygame.display.flip()


m = main()
m.run()
