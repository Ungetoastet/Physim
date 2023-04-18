from vector import vector2
import settings
import numpy

class particle:
    def __init__(self, pos, vel=vector2.zero(), size=settings.particle_size, color=settings.main_col) -> None:
        self.pos:vector2 = pos
        self.vel:vector2 = vel
        self.force:vector2 = vector2.zero()
        self.size:float = size
        self.color:int[3] = color
        self.collision_cluster = -1
        pass

    def render(self, screen):
        import pygame
        pygame.draw.circle(screen, self.color, (self.pos.x, self.pos.y), self.size)

    def update(self, timestep) -> None:
        self.collision_cluster = -1
        self.vel += self.force * timestep * 60
        self.pos += self.vel * timestep * 60
        self.force = settings.gravity / 10

    def to_np_arr(self):
        arr = numpy.array([self.pos.x, self.pos.y, self.vel.x, self.vel.y], dtype=numpy.float32)
        return arr
    
    def set_pos_vel(self, arr):
        self.pos.x = arr[0]
        self.pos.y = arr[1]
        self.vel.x = arr[2]
        self.vel.y = arr[3]
        return