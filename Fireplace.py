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
          self.xsize = 0
          self.ysize = 0
          self.color = (0, 0, 0, 255)

class fire_emitter ():
     def __init__(self):
          self.colors = [
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
          self.x = 0
          self.y = 0
          self.basesize = (-30.0, 30.0)
          self.heightjitter = (-15.0, 15.0)
          self.particles = []
          self.initialparticlecount = 25
          # can't seem to handle more than this without making optimizations
          # of some sort...
          self.maxparticles = 350
          self.liveparticles = 0
          self.xvelrange = (-60, 60)
          self.yvelrange = (150, 350)
          self.xsizerange = (10, 18)
          self.ysizerange = (10, 18)
          self.particlesperstep = 5
          self.persistence = 0.75
          self.radius = 350
          for i in range(self.maxparticles):
               self.particles.append(particle())
          self.start()
          
     def gen_particle ( self, i ):
          # Looked into it: this IS a pseudo random number generator
          # and is not cryptographically secure (e.g., it's using a Mersenne Twister underneath)
          # which is a pseudo RNG and very fast
          xrand = random.randint(self.basesize[0], self.basesize[1])
          yrand = random.randint(self.heightjitter[0], self.heightjitter[1])
          xvel = random.randint(self.xvelrange[0], self.xvelrange[1])
          yvel = random.randint(self.yvelrange[0], self.yvelrange[1])
          xsize = random.randint(self.xsizerange[0], self.xsizerange[1])
          ysize = random.randint(self.ysizerange[0], self.ysizerange[1])
          p = particle()
          p.x = xrand
          p.y = yrand
          p.xvelocity = xvel
          p.yvelocity = yvel
          p.xacceleration = 0
          p.yacceleration = 0
          p.xsize = xsize
          p.ysize = ysize
          p.life = 1
          p.color = self.colors[random.randint(0, len(self.colors)-1)]
          return p

     def start( self ):
          for i in range(self.initialparticlecount):
               self.particles[i].life = 1

     def particle_step( self, p, dt ):
          c2 = p.x * p.x + p.y * p.y
          if ( c2 > self.radius * self.radius ):
               p.life = 0

     def step( self, dt ):
          particlescreated = 0
          for i, p in enumerate(self.particles):
               if p.life > 0:
                    continue
               if particlescreated >= self.particlesperstep:
                    break
               self.particles[i] = self.gen_particle(i)
               particlescreated += 1
          
          self.liveparticles = 0
          for i, p in enumerate(self.particles):
               if p.life < 1:
                    continue
               self.liveparticles += 1
               p.xvelocity += p.xacceleration * dt
               p.yvelocity += p.yacceleration * dt
               p.x += p.xvelocity * dt
               p.y += p.yvelocity * dt
               self.particle_step( p, dt )       

     def particle_render( self, screen, p ):
          # TODO: offset calculations into a table 
          # TODO: hash particle values and save color/alpha information
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
          # TODO: pre-bake into texture and reuse that
          pygame.draw.rect( screen, color, ( x, y, p.xsize, p.ysize ) )
          #pygame.draw.circle( screen, color, (int(x), int(y)), 10 )

     def render( self, screen ):
          for p in self.particles:
               if p.life < 1:
                    continue
               self.particle_render( screen, p )

class main():
     def __init__(self):
          pygame.init()
          self.size = self.width, self.height = 640, 480
          self.running = False
          self.firstupdate = True
          self.firstrender = True
          self.targetrendertime = 0.0 # As fast as possible
          self.targetphysicstime = 1.0 / 100.0 # 10.0 millisecond update timing goal
          self.targetupdatetime = 0.0 # As fast as possible
          self.clearcolor = (0, 0, 0, 255)
          self.updatedelta = 0
          self.renderdelta = 0
          self.updatelag = 0
          self.physicslag = 0
          self.physicssteps = 0
          self.renderlag = 0
          self.updateexecutiontime = 0
          self.physicsexecutiontime = 0
          self.renderexecutiontime = 0
          self.updatetime = time.perf_counter()
          self.physicstime = time.perf_counter()
          self.rendertime = time.perf_counter()
          self.debugdisplay = True
          
          self.emitters = []
          self.emitterindex = 0

          pygame.display.set_caption("Fireplace")
          self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.SRCALPHA | pygame.DOUBLEBUF, 24)
          self.screenbuffer = pygame.Surface(self.size, pygame.SRCALPHA )
          self.font = pygame.font.Font(None, 14)
          
     def inner_run(self):
          while self.running:
               # handle events
               for event in pygame.event.get():
                    if event.type == pygame.QUIT: 
                         return
                    elif event.type == pygame.KEYUP:
                         if event.key == pygame.K_BACKQUOTE:
                              self.debugdisplay = not self.debugdisplay
                         if event.key == pygame.K_LEFT:
                              self.emitterindex = clamp( 
                                   ( len(self.emitters) - 1 ) if self.emitterindex == 0 
                                   else (self.emitterindex - 1) % len(self.emitters), 
                                   0, len(self.emitters) )
                         if event.key == pygame.K_RIGHT:
                              self.emitterindex = (self.emitterindex + 1) % len(self.emitters)
               # call step and render methods
              
               # perform timing and first time checks
               if self.firstupdate:
                    self.firstupdate = False
                    self.updatedelta = 0
                    self.updatelag = 0
                    self.updatetime = time.perf_counter()
                    begin = time.perf_counter()
                    self.update()
                    self.updateexecutiontime = time.perf_counter() - begin
               else:
                    self.updatedelta = time.perf_counter() - self.updatetime
                    if self.targetupdatetime <= self.updatedelta:
                         begin = time.perf_counter()
                         self.update()
                         self.updateexecutiontime = time.perf_counter() - begin
                         self.updatelag = self.targetupdatetime - self.updateexecutiontime
                         # update related timing
                         self.updatetime = time.perf_counter()
               
               # perform timing and first time checks
               if self.firstrender:
                    self.firstrender = False
                    self.renderdelta = 0
                    self.renderlag = 0
                    self.rendertime = time.perf_counter()
                    begin = time.perf_counter()
                    self.render()
                    self.renderexecutiontime = time.perf_counter() - begin
               else:
                    self.renderdelta = time.perf_counter() - self.rendertime
                    if self.targetrendertime <= self.renderdelta:
                         begin = time.perf_counter()
                         self.render()
                         self.renderexecutiontime = time.perf_counter() - begin
                         self.renderlag = self.targetrendertime - self.renderexecutiontime
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

          # a fire emitter; can configure in its constructor,
          # or tweak things here
          f = fire_emitter();
          f.x = self.screen.get_width() / 2.0
          self.emitters.append(f)

          # a rain emitter; can configure in its constructor, or tweak things here

     def update(self):
          # update hardcore logic here
          
          # variable framerate is actually a terrible idea for simulations
          # so if the performance tanked this would actually make any real physics system freak out
          # self.step(self.updatedelta)
          
          # update the simulation with a fixed timesteps
          # as many times as it needed since the last time we came here
          rollingphysicsdelta = self.physicsdelta = time.perf_counter() - self.physicstime
          self.physicssteps = 0
          begin = time.perf_counter()
          while self.targetphysicstime <= rollingphysicsdelta:
               self.step(self.targetphysicstime)
               rollingphysicsdelta -= self.targetphysicstime
               self.physicssteps += 1
               self.physicstime = time.perf_counter()
          self.physicsexecutiontime = time.perf_counter() - begin
          if self.physicssteps != 0:
               self.physicsexecutiontime /= self.physicssteps # retrieve average execution time of runs (avoid division by 0) 
          else:
               self.physicsexecutiontime = 0.0
          self.physicslag = self.targetphysicstime - self.physicsexecutiontime
             
          # post physics logic here
          
     def step(self, deltatime):
          # physics items go here
          for e in self.emitters:
               e.step(deltatime)
          
     def render(self):
          self.screen.fill(self.clearcolor)
          self.screenbuffer.fill((0, 0, 0, 0))
          if not self.emitters or self.emitterindex >= len(self.emitters):
               return
          # We know we have a good emitter, then
          currentemitter = self.emitters[self.emitterindex]

          # Render whatever the emitter tells us to
          currentemitter.render( self.screenbuffer )
          
          # Information text
          if self.debugdisplay:
               self.updatetext = self.font.render("update timing: {:.2f} ms delta, {:.2f} ms lag, {:.2f} ms execution".format(self.updatedelta * 1000, self.updatelag * 1000, self.updateexecutiontime * 1000), True, (0,0,0,255), None)
               self.physicstext = self.font.render("physics timing: {} steps, {:.2f} ms delta, {:.2f} ms lag, {:.2f} ms execution".format(self.physicssteps, self.physicsdelta * 1000, self.physicslag * 1000, self.physicsexecutiontime * 1000), True, (0,0,0,255), None)
               self.rendertext = self.font.render("render timing: {:.2f} FPS, {:.2f} ms delta, {:.2f} ms lag, {:.2f} ms execution".format((0 if self.renderdelta == 0 else ( 1 / self.renderdelta ) ), self.renderdelta * 1000, self.renderlag * 1000, self.renderexecutiontime * 1000), True, (0,0,0,255), None)
               self.particletext = self.font.render("emitter {}'s particles: {}".format(self.emitterindex, currentemitter.liveparticles), True, (0,0,0,255), None)
               lineheight = self.font.get_linesize()
               self.screenbuffer.blit(self.updatetext, (0, lineheight * 0))
               self.screenbuffer.blit(self.physicstext, (0, lineheight * 1))
               self.screenbuffer.blit(self.rendertext, (0, lineheight * 2))
               self.screenbuffer.blit(self.particletext, (0, lineheight * 3))
          
          self.screen.blit( self.screenbuffer, (0,0), None )
          pygame.display.flip()


m = main()
m.run()
