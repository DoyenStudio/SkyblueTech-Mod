#!/usr/bin/env node
'use strict';

// Offline asset validation only; never loads or executes the mod's Python code.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = file => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
const atlas = read('resource_pack/textures/terrain_texture.json').texture_data;
const directions = ['north', 'east', 'south', 'west', 'up', 'down'];
const vectors = { north: [0, 0, -1], east: [1, 0, 0], south: [0, 0, 1], west: [-1, 0, 0], up: [0, 1, 0], down: [0, -1, 0] };
const families = {
    battery_matrix: { frame: 'frame', io_energy1: 'energy_input_interface', io_energy2: 'energy_output_interface', controller: 'controller_side' },
    bedrock_lava_drill: { frame: 'frame', io_energy: 'energy_interface', io_fluid: 'io_fluid', controller: 'controller_side' },
};

function evaluate(expression, states) {
    if (typeof expression === 'boolean') return expression;
    const replaced = expression.replace(/q\.block_state\('([^']+)'\)/g, (_, key) => {
        assert.ok(key in states, `Unknown state ${key}`);
        return JSON.stringify(states[key]);
    });
    // These generated predicates use only grouped booleans and equality; no ternaries.
    assert.match(replaced.replace(/["'](north|east|south|west)["']|true|false/g, ''), /^[\s()!&|=]*$/);
    return Function('"use strict"; return (' + replaced + ');')();
}

// Decode physical face rectangles directly from exported Bedrock cube coordinates.
// This does not read the generator's faceAxes, grouping names, or corner predicates.
function rectangle(face, cube) {
    const [x, y, z] = cube.origin;
    const [w, h, d] = cube.size;
    const result = {
        north: [x + 8, 16 - y - h, w, h],
        south: [8 - x - w, 16 - y - h, w, h],
        east: [8 - z - d, 16 - y - h, d, h],
        west: [z + 8, 16 - y - h, d, h],
        up: [x + 8, 8 - z - d, w, d],
        down: [x + 8, z + 8, w, d],
    }[face];
    const plane = { north: [z, d, -8], south: [z, d, 8], east: [x, w, -8], west: [x, w, 8], up: [y, h, 16], down: [y, h, 0] }[face];
    assert.equal(plane[0], plane[2], `${face}: surface plane`);
    assert.equal(plane[1], 0, `${face}: single face thickness`);
    assert.ok(result.every(Number.isInteger));
    return result;
}

// Physical points in the unrotated world frame, undoing the geometry X convention.
function point(face, u, v) {
    return {
        north: [8 - u, 16 - v, -8], south: [u - 8, 16 - v, 8],
        east: [8, 16 - v, 8 - u], west: [-8, 16 - v, u - 8],
        up: [8 - u, 16, 8 - v], down: [8 - u, 0, v - 8],
    }[face];
}

function worldDirection(face, axis, sign, rotation) {
    const start = point(face, 8, 8);
    const end = point(face, 8 + (axis === 0 ? sign : 0), 8 + (axis === 1 ? sign : 0));
    const [x, y, z] = end.map((value, i) => value - start[i]);
    const angle = rotation * Math.PI / 180;
    const rotated = [Math.round(x * Math.cos(angle) + z * Math.sin(angle)), y, Math.round(-x * Math.sin(angle) + z * Math.cos(angle))];
    const name = directions.find(direction => vectors[direction].every((value, i) => value === rotated[i]));
    assert.ok(name, `Non-cardinal rotation ${rotation}`);
    return name;
}

function checkTexture(id) {
    const entry = atlas[id];
    assert.ok(entry && typeof entry.textures === 'string', `Missing atlas identifier ${id}`);
    const file = path.join(root, 'resource_pack', entry.textures + '.png');
    assert.ok(fs.existsSync(file), `Missing PNG ${file}`);
    const png = fs.readFileSync(file);
    assert.equal(png.subarray(1, 4).toString(), 'PNG');
    assert.equal(png.readUInt32BE(16), 16);
    assert.equal(png.readUInt32BE(20), 16);
}

function expectedSample(u, v, horizontal, vertical, anyJoined, bordered, center, edgeless) {
    const outerU = u < 2 || u >= 14;
    const outerV = v < 2 || v >= 14;
    const screw = (u === 2 || u === 13) && (v === 2 || v === 13);
    if (screw) return [horizontal || vertical ? edgeless : bordered, u, v];
    if (outerU && outerV) {
        if (horizontal && vertical) return [edgeless, u, v];
        if (horizontal) return [bordered, u + (u < 2 ? 2 : -2), v];
        if (vertical) return [bordered, u, v + (v < 2 ? 2 : -2)];
        return [bordered, u, v];
    }
    if (outerU || outerV) return [(outerU ? horizontal : vertical) ? edgeless : bordered, u, v];
    return [anyJoined ? center : bordered, u, v];
}

let total = 0;
for (const [family, blocks] of Object.entries(families)) {
    const geometry = read(`resource_pack/models/blocks/${family}_connected.geo.json`)['minecraft:geometry'][0];
    const culling = read(`resource_pack/block_culling/${family}.json`)['minecraft:block_culling_rules'];
    assert.equal(geometry.description.identifier, `geometry.skybluetech.${family}_connected`);
    assert.equal(culling.description.identifier, `skybluetech:culling.${family}`);
    assert.ok(geometry.bones.length <= 64);
    const parts = new Set();
    for (const bone of geometry.bones) bone.cubes.forEach((cube, index) => {
        assert.equal(Object.keys(cube.uv).length, 1);
        parts.add(`${bone.name}/${index}/${Object.keys(cube.uv)[0]}`);
    });
    assert.equal(culling.rules.length, parts.size);
    for (const rule of culling.rules) {
        const part = rule.geometry_part;
        assert.equal(rule.condition, 'same_culling_layer');
        assert.equal(rule.direction, part.face);
        assert.ok(parts.delete(`${part.bone}/${part.cube}/${part.face}`), 'Duplicate or invalid culling reference');
    }
    assert.equal(parts.size, 0);
    let cases = 0;
    for (const [suffix, side] of Object.entries(blocks)) {
        const block = read(`behavior_pack/netease_blocks/multiblock/skybluetech_${family}_${suffix}.json`)['minecraft:block'];
        const controller = suffix === 'controller';
        const prefix = `skybluetech:${family}_`;
        assert.equal(block.description.identifier, prefix + suffix);
        for (const direction of directions) assert.deepEqual(block.description.states['skybluetech:connection_' + direction], [false, true]);
        assert.equal(block.components['minecraft:geometry'].identifier, geometry.description.identifier);
        assert.equal(block.components['minecraft:geometry'].culling, culling.description.identifier);
        assert.equal(block.components['minecraft:geometry'].culling_layer, `skybluetech:culling_layer.${family}`);
        assert.deepEqual(Object.keys(block.components['minecraft:geometry'].bone_visibility).sort(), geometry.bones.map(bone => bone.name).sort());
        assert.equal(block.components['netease:neighborchanged_sendto_script'].value, true);
        assert.equal(block.components['netease:listen_block_remove'].value, true);
        assert.ok(block.components['netease:block_entity']);
        const item = block.components['minecraft:item_visual'];
        assert.equal(item.geometry, 'minecraft:geometry.full_block');
        assert.equal(item.material_instances['*'].texture, prefix + side);
        if (controller) {
            assert.equal(item.material_instances.south.texture, prefix + 'controller_front');
            assert.equal(block.description.traits['minecraft:placement_direction'].y_rotation_offset, 180);
        }
        const allMaterials = [block.components['minecraft:material_instances'], ...Object.values(block.permutations || {}).map(p => p.components['minecraft:material_instances']).filter(Boolean)];
        for (const materials of allMaterials) for (const material of Object.values(materials)) checkTexture(material.texture);
        for (const facing of controller ? directions.slice(0, 4) : ['north']) for (let mask = 0; mask < 64; mask++) {
            for (const active of controller ? [false, true] : [false]) {
                const states = { 'minecraft:cardinal_direction': facing, 'skybluetech:active': active };
                directions.forEach((direction, i) => { states['skybluetech:connection_' + direction] = Boolean(mask & (1 << i)); });
                let components = { ...block.components };
                for (const permutation of block.permutations || []) if (evaluate(permutation.condition, states)) components = { ...components, ...permutation.components };
                const rotation = components['minecraft:transformation']?.rotation?.[1] || 0;
                const materials = components['minecraft:material_instances'];
                const pixels = Object.fromEntries(directions.map(face => [face, new Array(256)]));
                for (const bone of geometry.bones) {
                    if (!evaluate(components['minecraft:geometry'].bone_visibility[bone.name], states)) continue;
                    for (const cube of bone.cubes) for (const [face, uv] of Object.entries(cube.uv)) {
                        const [u, v, width, height] = rectangle(face, cube);
                        assert.deepEqual(uv.uv_size, [width, height], 'Unscaled pixel UV');
                        const texture = materials[uv.material_instance].texture;
                        for (let dv = 0; dv < height; dv++) for (let du = 0; du < width; du++) {
                            assert.ok(u + du >= 0 && u + du < 16 && v + dv >= 0 && v + dv < 16);
                            const index = (v + dv) * 16 + u + du;
                            assert.equal(pixels[face][index], undefined, `${family}/${suffix}/${facing}/${mask}/${face}: overlapping pixel`);
                            pixels[face][index] = [texture, uv.uv[0] + du, uv.uv[1] + dv];
                        }
                    }
                }
                for (const face of directions) {
                    const art = controller && face === 'north' ? 'controller_front' + (active ? '_active' : '') : side;
                    const center = ['frame', 'controller_side'].includes(art) ? 'frame_edgeless' : art;
                    for (let v = 0; v < 16; v++) for (let u = 0; u < 16; u++) {
                        const horizontal = states['skybluetech:connection_' + worldDirection(face, 0, u < 8 ? -1 : 1, rotation)];
                        const vertical = states['skybluetech:connection_' + worldDirection(face, 1, v < 8 ? -1 : 1, rotation)];
                        const expected = expectedSample(u, v, horizontal, vertical, mask !== 0, prefix + art, prefix + center, prefix + 'frame_edgeless');
                        assert.deepEqual(pixels[face][v * 16 + u], expected, `${family}/${suffix}/${facing}/${mask}/active=${active}/${face} pixel ${u},${v}`);
                    }
                }
                cases++;
            }
        }
    }
    console.log(`${family}: 448 orientation/connection combinations, ${cases} cases including active controller; six faces fully covered; materials, screw rules, rotation, culling and PNG paths valid.`);
    total += cases;
}
console.log(`Validated ${total} rendered cases without executing mod Python. Target-client visual validation is still required.`);
