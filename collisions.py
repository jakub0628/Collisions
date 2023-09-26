# Imports

from itertools import combinations
from datetime import datetime
import numpy as np
import numpy.random as rd
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import animation
import yaml


# Loading configuration file

with open('config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f)


# Function definitions

def rand_vector(lim):
    '''Returns a 2D numpy array between [-lim, -lim] and [lim, lim]'''
    return np.array([rd.uniform(-lim, lim), rd.uniform(-lim, lim)])


def animate(frame):
    '''Move animation forward, updating the canvas'''
    canvas.update_blocks()
    canvas.do_collisions()
    canvas.fix_axes()
    if frame % 10 == 0:
        print(f'Frame {frame} / {config["frames"]}')

def get_energy(m, v):
    '''Calculates kinetic energy'''
    return m * np.linalg.norm(v)**2 / 2


max_energy = get_energy(config['mass_limits'][1], config['velocity_limit'])
normalize_energy = colors.Normalize(vmin=0, vmax=max_energy)
cmap = plt.get_cmap('Spectral')


def get_energy_color(m, v):
    '''Gets RGB color based on kinetic energy'''
    return cmap(1 - normalize_energy(get_energy(m, v)))


# Classes definitions

class Canvas():
    '''2D space where all the blocks interact and which is exported to frames'''
    def __init__(self):
        self.size = config['canvas_size']
        self.limits = [-self.size/2, self.size/2]
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.blocks = []
        self.pairs = combinations(self.blocks, 2) # all block pairs

    def update_blocks(self):
        '''Clear previous frame, move blocks and redraw'''
        self.ax.clear()
        for block in self.blocks:
            block.move()
            block.draw()

    def fix_axes(self):
        '''Prevent axes from changing their limits and change other cosmetic settings'''
        self.fig.tight_layout()
        self.ax.set_aspect('equal')
        self.ax.set_xlim(self.limits)
        self.ax.set_ylim(self.limits)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def collide_wall(self, block):
        '''Collide a block with a wall, reversing its appropriate velocity component'''
        for i in range(2):
            overlap = abs(block.position[i]) + block.radius - self.size / 2
            if overlap > 0:
                block.position[i] -= np.sign(block.position[i]) * overlap # move block to the border
                block.velocity[i] *= -1

    def collide_blocks(self, block_1, block_2):
        '''Update velocities of two block colliding using the (adjusted) formula from
        https://en.wikipedia.org/wiki/Elastic_collision#Two-dimensional_collision_with_two_moving_objects
        '''
        m1, m2 = block_1.mass, block_2.mass
        x1, x2 = block_1.position, block_2.position
        v1, v2 = block_1.velocity, block_2.velocity
        r1, r2 = block_1.radius, block_2.radius

        dx_length = np.linalg.norm(x1 - x2)
        dx_norm = (x1 - x2) / dx_length # normalized vector: block_2 -> block_1
        overlap = r1 + r2 - dx_length

        if overlap > 0:
            # update block velocities
            collision_multiplier = 2 * np.dot(v1-v2, dx_norm) * dx_norm / (m1+m2)
            v1 -= m2 * collision_multiplier
            v2 += m1 * collision_multiplier

            # move both blocks, so they're only touching, not overlapping
            x1 += overlap * dx_norm / 2
            x2 -= overlap * dx_norm / 2


    def do_collisions(self):
        '''Check for collisions and apply their effects'''

        for block in self.blocks: # wall collisions
            self.collide_wall(block)

        self.pairs = combinations(self.blocks, 2)
        for pair in self.pairs: # collisions between the blocks
            self.collide_blocks(*pair)


class Block() :
    '''Interacting (colliding) block object'''

    def __init__(self):
        self.canvas = canvas
        self.mass = rd.uniform(*config['mass_limits'])
        self.radius = rd.uniform(*config['radius_limits'])
        self.position = rand_vector(self.canvas.size / 2 - self.radius)
        self.velocity = rand_vector(config['velocity_limit'])
        # self.color = rd.rand(3,) # random color option
        self.color = get_energy_color(self.mass, self.velocity)

    normal_energy = colors.Normalize(
            vmin=0, vmax=get_energy(config['mass_limits'][1], config['velocity_limit']))

    def move(self):
        '''Move block based on its velocity'''
        self.position += self.velocity
        self.color = get_energy_color(self.mass, self.velocity)

    def draw(self):
        '''Plot the canvas'''
        canvas.ax.add_patch(plt.Circle(self.position, self.radius, color=self.color))


# Main

canvas = Canvas()

for n in range(config['n_blocks']):
    canvas.blocks.append(Block())

anim = animation.FuncAnimation(
    canvas.fig, animate, frames=config['frames'])

video_writer = animation.FFMpegWriter(fps=config['fps'])
time = str(datetime.now().isoformat())[:19]

anim.save(f'blocks_animation_{time}.mp4', writer=video_writer, dpi=config['dpi'])