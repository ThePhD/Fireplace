def clamp( x, l, h ):
     if x < l:
          return l
     if x > h:
          return h
     return x

def to_screen( screen, x, y ):
     return x, -y + screen.get_height()

def center( x, y, width, height ):
     return adjust(x, y, width, height, 0.5, 0.5 )

def adjust( x, y, width, height, xratio, yratio ):
     return x - (width * xratio), y - (yratio * height)

def interpolate_inverse( a, b, ta ):
     return interpolate_weight( a, b, ta, tuple([1 - a for a in ta]))

def interpolate_weight( ta, tb, twa, twb ):
     return tuple([a * wa + b * wb for a, b, wa, wb in zip(ta, tb, twa, twb)])

