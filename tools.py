import settings
import numba, math

def chunk_pos(posx, posy):
    x_chunk = max(min(int(posx // settings.chunk_size), settings.x_chunks-1), 0)
    y_chunk = max(min(int(posy // settings.chunk_size), settings.y_chunks-1), 0)
    return x_chunk, y_chunk

def keep_part_IB(p):
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
    
    return p

@numba.njit()
def solve_collision_array(arr):
    max_d = settings.particle_size*2
    for i in range(0, arr.size, 4):
        for j in range(i+4, arr.size, 4):
            diff_x = arr[i] - arr[j]
            diff_y = arr[i+1] - arr[j+1]
            d = math.sqrt(diff_x*diff_x + diff_y*diff_y)

            if (d < max_d):
                # Pull particles apart
                pullvec_x = diff_x/d
                pullvec_y = diff_y/d
                x = pullvec_x * (max_d - d)
                y = pullvec_y * (max_d - d)
                arr[i] += x
                arr[i+1] += y
                arr[j] -= x
                arr[j+1] -= y

                # Update velocities
                v1_x = arr[i+2]
                v1_y = arr[i+3]
                v2_x = arr[j+2]
                v2_y = arr[j+3]

                v1_l = math.sqrt(v1_x*v1_x+v1_y*v1_y)
                v2_l = math.sqrt(v2_x*v2_x+v2_y*v2_y)

                a1 = ((v1_x + pullvec_x) * v2_l)
                a2 = ((v1_y + pullvec_y) * v2_l)

                b1 = ((v2_x - pullvec_x) * v1_l)
                b2 = ((v2_y - pullvec_y) * v1_l)

                al = math.sqrt(a1*a1 + a2*a2)
                bl = math.sqrt(b1*b1 + b2*b2)

                a1 = a1 / al
                a2 = a2 / al
                b1 = b1 / bl
                b2 = b2 / bl

                arr[i+2] = a1*v1_l*settings.bounce_coeff
                arr[i+3] = a2*v1_l*settings.bounce_coeff
                arr[j+2] = b1*v2_l*settings.bounce_coeff
                arr[j+3] = b2*v2_l*settings.bounce_coeff

    return arr

def full_particle_update(p):
    p = keep_part_IB(p)
    p.update(1/60)
    return p