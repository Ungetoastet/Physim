from vector import vector2
import pygame
import settings
from particle import particle
import time
import numpy
import math
import tools

# Set up the drawing window
pygame.init()
screen = pygame.display.set_mode(settings.res)

# Setup physics sim
particles = []
particles.append(particle(vector2(100, 95), vel=vector2.right()*2))
particles.append(particle(vector2(500, 100), vel=vector2.left()))

while True:
    frame_start = time.time()

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # --- RENDER BACKGROUND ---
    screen.fill(settings.bg_col)

    for i in range(settings.x_chunks):
        for j in range(settings.y_chunks):
            if (i+j)%2 == 0:
                pygame.draw.rect(screen, settings.bg_col_b,
                    pygame.Rect(i*settings.chunk_size, j*settings.chunk_size, settings.chunk_size, settings.chunk_size))

    # --- CHUNK SORTING ---
    chunks = numpy.empty((settings.x_chunks, settings.y_chunks), dtype=list)

    for p in particles:
        x_chunk, y_chunk = tools.chunk_pos(p.pos.x, p.pos.y)
        chunks[x_chunk, y_chunk] = numpy.append(chunks[x_chunk, y_chunk], p).tolist()

    # --- COLLISION DETECTION ---
    for chunk_index_x in range(0, len(chunks), 1):
        for chunk_index_y in range(0, len(chunks[0]), 1):
            if chunks[chunk_index_x, chunk_index_y] == None:
                continue

            # Group all the particles of neighboring chunks into list
            particlelist = []
            for x_chunks_i in range(chunk_index_x-1, chunk_index_x+2):
                for y_chunks_i in range(chunk_index_y-1, chunk_index_y+2):
                    if settings.chunk_debug:
                        pygame.draw.rect(screen, settings.accent_col_b,
                            pygame.Rect(x_chunks_i*settings.chunk_size, y_chunks_i*settings.chunk_size, settings.chunk_size, settings.chunk_size))
                        
                    if x_chunks_i < 0 or y_chunks_i < 0 or x_chunks_i > settings.x_chunks-1 or y_chunks_i > settings.y_chunks-1:
                        continue

                    if chunks[x_chunks_i, y_chunks_i] == None:
                        continue
                    
                    if settings.chunk_debug:
                        pygame.draw.rect(screen, settings.accent_col,
                            pygame.Rect(x_chunks_i*settings.chunk_size, y_chunks_i*settings.chunk_size, settings.chunk_size, settings.chunk_size))

                    particlelist.extend(chunks[x_chunks_i, y_chunks_i])

            particlelist = list(filter(lambda a: a != None, particlelist))

            # --- SOLVE COLLISIONS ---
            listlen = len(particlelist)
            for i in range(listlen):
                for j in range(i+1, listlen):
                    d = vector2.dist(particlelist[i].pos, particlelist[j].pos)
                    if (d < settings.particle_size*2):
                        # Pull particles apart
                        pullvec = (particlelist[i].pos - particlelist[j].pos).unit()
                        x = pullvec * (settings.particle_size*2 - d)
                        particlelist[i].pos += x
                        particlelist[j].pos -= x

                        # Update velocities
                        v1 = particlelist[i].vel
                        v2 = particlelist[j].vel
                        particlelist[i].vel = (v1 + pullvec * v2.len()).unit()*v1.len()*settings.bounce_coeff
                        particlelist[j].vel = (v2 - pullvec * v1.len()).unit()*v2.len()*settings.bounce_coeff

    # --- Keep particles in bounds ---
    for p in particles:
        if p.pos.x < 0 + settings.particle_size: # LEFT WALL
            p.pos.x = 0 + settings.particle_size
            p.vel.x *= -settings.bounce_coeff
        elif p.pos.x > settings.res[0] - settings.particle_size: # RIGHT WALL
            p.pos.x = settings.res[0] - settings.particle_size
            p.vel.x *= -settings.bounce_coeff
        if p.pos.y < 0 + settings.particle_size: # ROOF
            p.pos.y = 0 + settings.particle_size
            p.vel.y *= -settings.bounce_coeff
        elif p.pos.y > settings.res[1] - settings.particle_size: # FLOOR
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

    print(f"\n{len(particles)}\t{round(-target_delta, 4)}")
