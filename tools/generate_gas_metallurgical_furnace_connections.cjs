#!/usr/bin/env node
'use strict';

const generateConnections = require('./lib/generate_multiblock_connections.cjs');
const family = 'gas_metallurgical_furnace';
const variants = [
    ['frame', 'frame'],
    ['controller', 'frame'],
    ['io_item_in', 'io_item_in'],
    ['io_item_out', 'io_item_out'],
    ['io_gas_in', 'io_gas_in'],
    ['io_gas_in_2', 'io_gas_in_2'],
    ['io_gas_out', 'io_gas_out'],
    ['io_fluid_in', 'io_fluid_in'],
    ['io_fluid_out', 'io_fluid_out'],
    ['io_energy_in', 'io_energy_in'],
];
const panelSizes = {
    io_energy_in: 4,
    io_gas_in: 6,
    io_gas_in_2: 6,
    io_gas_out: 6,
    io_fluid_in: 6,
    io_fluid_out: 6,
};

for (const size of [8, 6, 4]) {
    generateConnections({
        family,
        geometryName: size === 8 ? family : `${family}_panel_${size}`,
        variants: variants.filter(([suffix]) => (panelSizes[suffix] || 8) === size),
        quadrantConnections: true,
        quadrantPanelSize: size,
        controllerFrontActive: 'controller_active',
    });
}
