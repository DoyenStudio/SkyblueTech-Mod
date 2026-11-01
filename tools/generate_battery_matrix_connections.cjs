#!/usr/bin/env node
'use strict';

// See docs/reference/battery_matrix_connections.md.
require('./lib/generate_multiblock_connections.cjs')({
    family: 'battery_matrix',
    variants: [
        ['frame', 'frame'],
        ['io_energy1', 'energy_input_interface'],
        ['io_energy2', 'energy_output_interface'],
        ['controller', 'controller_side'],
    ],
});
