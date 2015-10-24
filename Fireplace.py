import sys
import sfml
import time
import random
import math
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
          self.backgroundcolor = sfml.graphics.Color( 25, 25, 25, 255 )
          self.textcolor = sfml.graphics.Color( 255, 255, 255, 255 )
          self.basesize = (-30.0, 30.0)
          self.heightjitter = (-15.0, 15.0)
          self.particles = []
          # can't seem to handle more than this without making optimizations
          # of some sort...
          self.maxparticles = 350
          self.initialparticlecount = min(self.maxparticles, 15)
          self.liveparticles = 0
          self.xvelrange = (-60, 60)
          self.yvelrange = (150, 350)
          self.xsizerange = (10, 18)
          self.ysizerange = (10, 18)
          self.particlesperstep = 5
          self.persistence = 0.75
          self.radius = 350
          self.sprite = sfml.RectangleShape()
          self.sprite.outline_thickness = 0
          self.sprite.outline_color = sfml.graphics.Color.TRANSPARENT
          for i in range(self.maxparticles):
               self.particles.append(self.gen_particle(i))
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
          for i in range(len(self.particles)):
               if i < self.initialparticlecount:
                    self.particles[i].life = 1
               else:
                    self.particles[i].life = 0

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
          c2 = p.x * p.x + p.y * p.y
          radiusratio = ( c2 / ( self.radius * self.radius ) )
          alpharatio = 1 - radiusratio
          x, y = to_screen( screen, p.x + self.x, p.y + self.y )
          self.sprite.position = (x, y)
          self.sprite.origin = (p.xsize / 2, p.ysize / 2)
          self.sprite.size = (p.xsize, p.ysize)
          self.sprite.fill_color = sfml.graphics.Color( p.color[0], p.color[1], p.color[2], p.color[3] * alpharatio)
          screen.draw(self.sprite)
          
     def render( self, screen ):
          for p in self.particles:
               if p.life < 1:
                    continue
               self.particle_render( screen, p )

class main():
     def __init__(self):
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
          self.rollingphysicsdelta = 0
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

          self.screen = sfml.RenderWindow(sfml.VideoMode(self.width, self.height), "Fireplace")
          self.font = sfml.Font.from_file("./OpenSans-Regular.ttf")
          self.fontsize = 12
          self.lineheight = self.font.get_line_spacing(self.fontsize)
          
     def inner_run(self):
          while self.running:
               # handle events
               for event in self.screen.events:
                    # close window: exit
                    if type(event) is sfml.CloseEvent:
                         self.screen.close()
                    elif type(event) is sfml.KeyEvent:
                         if event.key == sfml.Keyboard.TILDE:
                              self.debugdisplay = not self.debugdisplay
                         if event.key == sfml.Keyboard.LEFT:
                              self.emitterindex = clamp( 
                                   ( len(self.emitters) - 1 ) if self.emitterindex == 0 
                                   else (self.emitterindex - 1) % len(self.emitters), 
                                   0, len(self.emitters) )
                         if event.key == sfml.Keyboard.RIGHT:
                              self.emitterindex = (self.emitterindex + 1) % len(self.emitters)
               
               # call step and render methods
               self.updatedelta = time.perf_counter() - self.updatetime
               if self.targetupdatetime <= self.updatedelta or self.firstupdate:
                    self.update()
               
               self.renderdelta = time.perf_counter() - self.rendertime
               if self.targetrendertime <= self.renderdelta or self.firstrender:
                    self.render()

     def run(self):
          self.running = True
          self.firstupdate = True
          self.firstrender = True
          self.initialize()
          self.screen.show()
          self.inner_run()
          self.running = False

     def initialize(self):
          self.clearcolor = (255, 255, 255, 255)

          # a fire emitter; can configure in its constructor,
          # or tweak things here
          f = fire_emitter();
          f.x = self.screen.width / 2.0
          self.emitters.append(f)

          # a rain emitter; can configure in its constructor, or tweak things here

     def update(self):
          self.firstupdate = False
          begin = time.perf_counter()
          self.update_delta(self.updatedelta)
          self.updateexecutiontime = time.perf_counter() - begin
          self.updatelag = self.targetupdatetime - self.updateexecutiontime
          # update related timing
          self.updatetime = time.perf_counter()

     def update_delta(self, dt):
          # update hardcore logic here
          
          # variable framerate is actually a terrible idea for simulations
          # so if the performance tanked this would actually make any real physics system freak out
          # self.step(self.updatedelta)
          
          # update the simulation with a fixed timesteps
          # as many times as it needed since the last time we came here
          self.physicsdelta = time.perf_counter() - self.physicstime
          self.rollingphysicsdelta += self.physicsdelta
          self.physicssteps = 0
          begin = time.perf_counter()
          while self.targetphysicstime <= self.rollingphysicsdelta:
               self.step(self.targetphysicstime)
               self.rollingphysicsdelta -= self.targetphysicstime
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
          self.firstrender = False
          begin = time.perf_counter()
          self.render_delta(self.renderdelta)
          # put the buffer swap here, since it should be part of timing
          self.screen.display( )
          self.renderexecutiontime = time.perf_counter() - begin
          self.renderlag = self.targetrendertime - self.renderexecutiontime
          self.rendertime = time.perf_counter()
          
     def render_delta(self, dt):
          if not self.emitters or self.emitterindex >= len(self.emitters):
               self.screen.clear(sfml.graphics.Color.WHITE)
               return
          # We know we have a good emitter, then
          currentemitter = self.emitters[self.emitterindex]

          # clear to the emitter's desired color
          self.screen.clear(currentemitter.backgroundcolor)
          # Render whatever the emitter tells us to
          currentemitter.render( self.screen )
          # Information text
          if self.debugdisplay:
               self.updatetext = sfml.Text("update timing: {:.2f} ms delta, {:.2f} ms lag, {:.2f} ms execution".format(self.updatedelta * 1000, self.updatelag * 1000, self.updateexecutiontime * 1000), self.font, self.fontsize)
               self.updatetext.color = currentemitter.textcolor
               self.updatetext.position = (0, self.lineheight * 0)
               self.physicstext = sfml.Text("physics timing: {} steps, {:.2f} ms delta, {:.2f} ms lag, {:.2f} ms execution".format(self.physicssteps, self.physicsdelta * 1000, self.physicslag * 1000, self.physicsexecutiontime * 1000), self.font, self.fontsize)
               self.physicstext.color = currentemitter.textcolor
               self.physicstext.position = (0, self.lineheight * 1)
               self.rendertext = sfml.Text("render timing: {:.2f} FPS, {:.2f} ms delta, {:.2f} ms lag, {:.2f} ms execution".format((0 if self.renderdelta == 0 else ( 1 / self.renderdelta ) ), self.renderdelta * 1000, self.renderlag * 1000, self.renderexecutiontime * 1000), self.font, self.fontsize)
               self.rendertext.color = currentemitter.textcolor
               self.rendertext.position = (0, self.lineheight * 2)
               self.particletext = sfml.Text("emitter {}'s particles: {}".format(self.emitterindex, currentemitter.liveparticles), self.font, self.fontsize)
               self.particletext.color = currentemitter.textcolor
               self.particletext.position = (0, self.lineheight * 3)
               self.screen.draw(self.updatetext)
               self.screen.draw(self.physicstext)
               self.screen.draw(self.rendertext)
               self.screen.draw(self.particletext)
          

m = main()
m.run()
