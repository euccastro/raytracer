from __future__ import division

from itertools import *
from math import sqrt

import Image

from la import vec3, dot

# XXX: Shameless copy&paste from searchview/searchview.py
#      Factor out to a util module instead.
colors = {'white': (1., 1., 1.),
          'grey': (.6, .6, .6),
          'red': (1., .0, .0),
          'green': (.0, 1., .0),
          'blue': (.0, .0, 1.),
          'cyan': (.0, 1., 1.),
          'magenta': (1., .0, 1.),
          'yellow': (1., 1., .0),
          'teal': (.4, .8, .6)}
def to255range(f):
    return int(round(f * 255))
for k, (r, g, b) in colors.items():
    colors[k] = tuple(map(to255range, [r, g, b]))
    if k != "white":
        colors["dark_"+k] = tuple(map(to255range, [r/2, g/2, b/2]))
colors['default'] = colors['grey']


class View:
    def __init__(self, distance_to_screen, 
                       screen_width, 
                       screen_height,
                       hpixels,
                       vpixels):
        self.distance_to_screen = distance_to_screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hpixels = hpixels
        self.vpixels = vpixels
    def get_ray_through_pixel(self, col, row):
        w = self.screen_width
        h = self.screen_height
        return Line(vec3(0, 0, 0),
                    vec3(-w / 2 + col * (w / self.hpixels),
                         -h / 2 + row * (h / self.vpixels),
                         -self.distance_to_screen))
class Line:
    def __init__(self, a, b):
        self.a = a
        self.b = b

def square(x):
    return x * x

class Sphere:
    def __init__(self, center, radius, color=colors['default']):
        self.center = center
        self.radius = radius
        self.color = color

    def intersect(self, l):
        a = (l.b - l.a).length_sq()
        c = self.center
        b = 2.0 * ((l.b.x - l.a.x) * (l.a.x - self.center.x) +
                   (l.b.y - l.a.y) * (l.a.y - self.center.y) +
                   (l.b.z - l.a.z) * (l.a.z - self.center.z))
        c = (self.center.length_sq() + l.a.length_sq() 
             - 2.0 * dot(self.center, l.a) - square(self.radius))
        i = b * b - 4.0 * a * c
        if i < 0:
            return []
        if i == 0:
            mu = -b / (2.0 * a)
            return [l.a + mu * (l.b - l.a)]
        if i > 0:
            mu1 = (-b + sqrt(i)) / (2.0 * a)
            mu2 = (-b - sqrt(i)) / (2.0 * a)
            return [l.a + mu1 * (l.b - l.a),
                    l.a + mu2 * (l.b - l.a)]

def test():
    epsilon = 0.0000001
    radius = 1.3
    s = Sphere(vec3(0, 0, 0), radius)

    l1 = Line(vec3(-1, 2, 0), vec3(1, 2, 0))
    assert s.intersect(l1) == []

    l2 = Line(vec3(-1, 0, 0), vec3(1, 0, 0))

    expected = sorted([vec3(-radius, 0, 0),
                       vec3(+radius, 0, 0)])

    got = sorted(s.intersect(l2))

    for e, g in zip(expected, got):
        assert (e-g).length() < epsilon

    l3 = Line(vec3(-1, radius, 0), vec3(1, radius, 0))

    got = s.intersect(l3)
    print got
    assert len(got) == 1 and (got[0] - vec3(0, radius, 0)).length() < epsilon

def render(scene, view):
    l = [100, 100, 100, 255] * view.hpixels * view.vpixels
    for row in xrange(view.vpixels):
        for col in xrange(view.hpixels):
            line = view.get_ray_through_pixel(col, row)
            # Get all intersection points from all intersections.
            collisions = chain.from_iterable(
                    [(obj, intersection)
                     for intersection in obj.intersect(line)]
                    for obj in scene)
            try:
                closest_obj, closest_point = max(collisions, 
                                                 key=lambda x:x[1].z)
                # XXX: just flat color for the moment.
                index = view.hpixels * row + col
                l[index:index+3] = closest_obj.color
                l[index+4] = 255  # alpha
            except ValueError:
                # No collisions at all; leave pixel with background color.
                pass

    return Image.fromstring('RGBA', 
                            (view.hpixels, view.vpixels), 
                            ''.join(map(chr, l)))

def test2():
    # Assume we are two screen widths from the center, and we have square
    # pixels.
    hpixels = 200
    vpixels = 100
    distance_to_screen = 2
    screen_width = 1
    screen_height = screen_width * vpixels / hpixels

    scene = [Sphere(center=vec3(0, 0, -5),
                    radius= .5, 
                    color=colors['red'])]
    img = render(scene, View(distance_to_screen,
                             screen_width,
                             screen_height,
                             hpixels,
                             vpixels))
    img.save("out.png")

if __name__ == '__main__':
    test2()
