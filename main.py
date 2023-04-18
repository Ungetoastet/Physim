import settings
from vector import vector2
import numba

# IDEAS:
# - Hash positions -> collision lookup for common patterns
# - GPU Offloading
# - Multiprocessing
# - Milestones (60FPS, 5Subs): 500, 1000, 2500, 5000, 10000

def solve_chunkrow(chunk_index_x, chunks, row_len):
    for chunk_index_y in range(1, row_len, 3):
        # Group all the particles of neighboring chunks into list
        particlelist = []
        for x_chunks_i in range(chunk_index_x-1, chunk_index_x+2):
            for y_chunks_i in range(chunk_index_y-1, chunk_index_y+2):                    
                if chunks[x_chunks_i, y_chunks_i] == None:
                    continue

                if x_chunks_i < 0 or y_chunks_i < 0 or x_chunks_i > settings.x_chunks-1 or y_chunks_i > settings.y_chunks-1:
                    continue
                
                particlelist.extend(chunks[x_chunks_i, y_chunks_i])

        particlelist = list(filter(lambda a: a != None, particlelist))

        if len(particlelist) == 0:
            continue

        # --- SOLVE COLLISIONS ---
        # (Array Solving (Enables GPU Offloading))
        listlen = len(particlelist)
        data_arr = numpy.full(listlen*4, 0, dtype=numpy.float32)

        for i in range(listlen):
            index_start = i*4
            p_arr = particlelist[i].to_np_arr()
            data_arr[index_start:index_start+4] = p_arr

        #print(legacy_compare_x, legacy_compare_y)
        solved = tools.solve_collision_array(data_arr)
        for i in range(listlen):
            index_start = i*4
            particlelist[i].set_pos_vel(solved[index_start:index_start+4])

if __name__ == "__main__":
    import pygame
    import time
    import numpy
    import tools
    import os
    import math
    from particle import particle
    import multiprocessing
    
    # Set up the drawing window
    pygame.init()
    screen = pygame.display.set_mode(settings.res)

    # Setup physics sim
    particles = []
    
    # Multiprocessing
    pool = multiprocessing.Pool(processes=settings.pool_size)

    while True:
        time_splits = []
        time_splits.append(time.time())

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
 
        # --- RENDER BACKGROUND ---
        screen.fill(settings.bg_col)

        time_splits.append(time.time())

        # --- CHUNK SORTING ---
        chunks = numpy.empty((settings.x_chunks, settings.y_chunks), dtype=list)

        for p in particles:
            x_chunk, y_chunk = tools.chunk_pos(p.pos.x, p.pos.y)
            chunks[x_chunk, y_chunk] = numpy.append(chunks[x_chunk, y_chunk], p).tolist()

        time_splits.append(time.time())

        # --- COLLISION DETECTION --- 
        for i in range(settings.collision_substeps):
            for chunk_index_x in range(1, len(chunks), 3):
                solve_chunkrow(chunk_index_x, chunks, len(chunks[0]))

        time_splits.append(time.time())

        # --- Keep particles in bounds ---
        mpos_to_vec = vector2.zero()
        if pygame.mouse.get_pressed()[0]:
            mpos_to_vec = vector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        
        for i in range(settings.physics_substeps):
            particles = pool.map(tools.full_particle_update, particles, math.ceil(len(particles)/settings.pool_size))

        for p in particles:
            if pygame.mouse.get_pressed()[0]:
                p.force += (mpos_to_vec-p.pos).unit() * 25 / max(vector2.dist(mpos_to_vec, p.pos), 2)
            p.render(screen)

        #     tools.full_particle_update(p, vector2, pygame, screen, mpos_to_vec)
        time_splits.append(time.time())

        # Flip the display
        pygame.display.flip()
        time_splits.append(time.time())

        # Wait for frametime
        deltatime = time.time() - time_splits[0]
        target_delta = settings.frame_target - deltatime
        if (len(particles) < settings.max_particles) or (target_delta > 0 and settings.max_particles == 0):
            particles.append(particle(vector2(100, 95), vel=vector2.right()*2))

        if target_delta > 0:
            deltatime = settings.frame_target
            time.sleep(target_delta)

        pygame.display.set_caption(f"Physics Simulation - {len(particles)} particles - {round(1/deltatime, 1)} FPS")

        if settings.log:
            os.system("cls")
            print(f"\n{len(particles)}\t{round(deltatime, 4)}\t{round(-target_delta, 4)}")
            deltas = [
                round(time_splits[1]-time_splits[0], 4),
                round(time_splits[2]-time_splits[1], 4),
                round(time_splits[3]-time_splits[2], 4),
                round(time_splits[4]-time_splits[3], 4),
                round(time_splits[5]-time_splits[4], 4),
            ]
            #print(f"EH and BG:\t {deltas[0]}  \t {round((deltas[0]/deltatime)*100, 2)}%")
            print(f"Chunk Sorting:\t {deltas[1]}    \t {round((deltas[1]/deltatime)*100, 2)}%")
            print(f"Collisions:\t {deltas[2]}       \t {round((deltas[2]/deltatime)*100, 2)}%")
            print(f"Phy Updates:\t {deltas[3]}      \t {round((deltas[3]/deltatime)*100, 2)}%")
            print(f"Display Flip:\t {deltas[4]}     \t {round((deltas[4]/deltatime)*100, 2)}%")
