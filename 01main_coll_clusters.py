from vector import vector2
import pygame
import settings
from particle import particle
import time
import numpy
import math

# Set up the drawing window
pygame.init()
screen = pygame.display.set_mode(settings.res)

# Setup physics sim
x_chunks =  math.ceil(settings.res[0] / settings.chunk_size)
y_chunks =  math.ceil(settings.res[1] / settings.chunk_size)
particles = []
particles.append(particle(vector2(100, 95), vel=vector2.right()*2))
particles.append(particle(vector2(500, 100), vel=vector2.left()))
empty_chunkmap = numpy.empty((x_chunks, y_chunks), list)
for x in range(x_chunks):
    for y in range(y_chunks):
        empty_chunkmap[x, y] = []

while True:
    frame_start = time.time()

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(settings.bg_col)

    # --- CHUNK SORTING ---
    chunks = empty_chunkmap

    for p in particles:
        x_chunk = max(min(int(p.pos.x // settings.chunk_size), x_chunks-1), 0)
        y_chunk = max(min(int(p.pos.y // settings.chunk_size), y_chunks-1), 0)
        chunks[x_chunk, y_chunk].append(p)

    # --- COLLISION DETECTION ---
    collision_clusters = []

    for i in range(len(particles)-1):
        for j in range(i+1, len(particles)):
            a = particles[i]
            b = particles[j]
            d = vector2.dist(a.pos, b.pos)

            if (d < settings.particle_size * 2): # A and B are colliding
                # Both particles arent yet in a cluster
                if (a.collision_cluster + b.collision_cluster == -2):
                    cluster_index = len(collision_clusters)
                    collision_clusters.append([a, b])
                    a.collision_cluster = cluster_index
                    b.collision_cluster = cluster_index
                    continue
                
                # Particle A is registered in a cluster
                if (a.collision_cluster >= 0 and b.collision_cluster == -1):
                    collision_clusters[a.collision_cluster].append(b)
                    b.collision_cluster = a.collision_cluster
                    continue

                # Particle B is registered in a cluster
                if (a.collision_cluster == -1 and b.collision_cluster >= 0):
                    collision_clusters[b.collision_cluster].append(a)
                    a.collision_cluster = b.collision_cluster
                    continue

                # Both particles are registered in the same cluster
                if (a.collision_cluster == b.collision_cluster):
                    continue
                
                # Particles are registered in different clusters
                cluster_to_merge = b.collision_cluster
                for x in collision_clusters[cluster_to_merge]:
                    x.collision_cluster = a.collision_cluster
                collision_clusters[a.collision_cluster].extend(collision_clusters[cluster_to_merge])
                collision_clusters[cluster_to_merge] = []

    # --- SOLVE COLLISION CLUSTERS ---
    for cluster in collision_clusters:
        cluster_size = len(cluster)
        for i in range(cluster_size):
            for j in range(i+1, cluster_size):
                d = vector2.dist(cluster[i].pos, cluster[j].pos)
                if (d < settings.particle_size*2):
                    # Pull particles apart
                    pullvec = (cluster[i].pos - cluster[j].pos).unit()
                    x = pullvec * (settings.particle_size*2 - d)
                    cluster[i].pos += x
                    cluster[j].pos -= x

                    # Update velocities
                    v1 = cluster[i].vel
                    v2 = cluster[j].vel
                    cluster[i].vel = (v1 + pullvec * v2.len()).unit()*v1.len()*settings.bounce_coeff
                    cluster[j].vel = (v2 - pullvec * v1.len()).unit()*v2.len()*settings.bounce_coeff

    # --- Keep particles in bounds ---
    for p in particles:
        if p.pos.x < 0 + settings.particle_size:
            p.pos.x = 0 + settings.particle_size
            p.vel.x *= -settings.bounce_coeff
        elif p.pos.x > settings.res[0] - settings.particle_size:
            p.pos.x = settings.res[0] - settings.particle_size
            p.vel.x *= -settings.bounce_coeff
        if p.pos.y < 0 + settings.particle_size:
            p.pos.y = 0 + settings.particle_size
            p.vel.y *= -settings.bounce_coeff
        elif p.pos.y > settings.res[1] - settings.particle_size:
            p.pos.y = settings.res[1] - settings.particle_size
            p.vel.y *= -settings.bounce_coeff


    # --- UPDATE PHYSICS ---
    for p in particles:
        p.update(1/60)

    # --- RENDER ---
    for p in particles:
        p.render(screen)

    # Flip the display
    pygame.display.flip()

    # Wait for frametime
    deltatime = time.time() - frame_start
    target_delta = settings.frame_target - deltatime
    if target_delta > 0:
        particles.append(particle(vector2(100, 95), vel=vector2.right()*2))
        time.sleep(target_delta)

    print(f"{len(particles)}\t{len(collision_clusters)}\t{round(-target_delta, 4)}")
