#!/usr/bin/env node
'use strict';

require('./lib/generate_multiblock_connections.cjs')({
    family: 'heat_conductor',
    variants: [['frame', 'frame']],
    borderWidth: 4,
    centerScrews: false,
    blockFiles: { frame: 'behavior_pack/netease_blocks/machinery/skybluetech_heat_conductor.json' },
    textureNames: { frame: 'heat_conductor', frame_edgeless: 'heat_conductor_edgeless' },
    textureDirectory: 'textures/blocks/machinery',
});
