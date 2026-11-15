# coding=utf-8
MAX_FLUID_VOLUME = 400
TICK_INTERVAL = 5
FLUID_PER_TICK = 20
FLUID_PER_CYCLE = FLUID_PER_TICK * TICK_INTERVAL

# The supplied model's outlet points up, with its pivot at the block centre.
MODEL_ROTATIONS = {
    0: (180, 0),
    1: (0, 0),
    2: (90, 0),
    3: (90, 180),
    4: (90, -90),
    5: (90, 90),
}

PARTICLE_LIFETIME = 0.8
