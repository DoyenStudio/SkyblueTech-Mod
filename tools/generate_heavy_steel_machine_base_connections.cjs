#!/usr/bin/env node
'use strict';

require('./lib/generate_multiblock_connections.cjs')({
    family: 'heavy_steel_machine_base',
    variants: [['frame', 'frame']],
    quadrantConnections: true,
    blockFiles: { frame: 'behavior_pack/netease_blocks/multiblock/skybluetech_heavy_steel_machine_base.json' },
});
