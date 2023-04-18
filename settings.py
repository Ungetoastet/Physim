import vector
import math

# Hardware Settings
res = [1280, 720]
pool_size = 6

# Physics Settings
bounce_coeff = 0.8
particle_size = 5 # Should be >1
frame_target = 1/60
gravity = vector.vector2.down()
chunk_size = particle_size*5
substeps = 5
max_particles = 0 # 0 for max

x_chunks = math.ceil(res[0] / chunk_size)
if x_chunks % 3 != 0:
    x_chunks += 3 - x_chunks % 3
y_chunks = math.ceil(res[1] / chunk_size)
if y_chunks % 3 != 0:
    y_chunks += 3 - y_chunks % 3

# DEBUG
chunk_debug = False
log = False # Drastically decreases performance

# Color Settings
bg_col = (48, 48, 54)
bg_col_b = (52, 52, 58)
main_col = (48, 188, 237)
accent_col = (252, 81, 48)
accent_col_b = (252, 151, 131)

# Optimization settings
thread_count = 2