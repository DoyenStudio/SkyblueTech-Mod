#!/usr/bin/env node
'use strict';

const generate = require('./lib/generate_multiblock_connections.cjs');
const family = 'large_reaction_pool';
const ports = ['io_item_in', 'io_item_out', 'io_energy_in', 'io_heat_in',
    'io_fluid_in_1', 'io_fluid_in_2', 'io_fluid_in_3', 'io_fluid_out_1', 'io_fluid_out_2'];

generate({
    family, quadrantConnections: true, quadrantPanelSize: 8,
    variants: [['frame', 'frame'], ['controller', 'frame'], ...ports.map(name => [name, name])],
});
for (const shell of ['cap', 'window']) {
    generate({
        family: family + '_' + shell,
        variants: [['frame', 'frame']], quadrantConnections: true,
        blockFiles: { frame: 'behavior_pack/netease_blocks/multiblock/skybluetech_' + family + '_' + shell + '.json' },
        textureDirectory: 'textures/blocks/multi_block_structure/' + family + '/' + shell,
        renderMethod: shell === 'window' ? 'alpha_test_single_sided' : 'opaque',
    });
}
