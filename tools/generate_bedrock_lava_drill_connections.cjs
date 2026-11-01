#!/usr/bin/env node
'use strict';

// See docs/reference/bedrock_lava_drill_connections.md.
require('./lib/generate_multiblock_connections.cjs')({
    family: 'bedrock_lava_drill',
    variants: [
        ['frame', 'frame'],
        ['io_energy', 'energy_interface'],
        ['io_fluid', 'io_fluid'],
        ['controller', 'controller_side'],
    ],
});
