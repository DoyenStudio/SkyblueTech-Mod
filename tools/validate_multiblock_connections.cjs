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
    large_reaction_pool_cap: { frame: 'frame' },
    large_reaction_pool_window: { frame: 'frame' },
    large_reaction_pool: {
        frame: 'frame', controller: 'frame', io_item_in: 'io_item_in', io_item_out: 'io_item_out',
        io_heat_in: 'io_heat_in', io_energy_in: 'io_energy_in',
        io_fluid_in_1: 'io_fluid_in_1', io_fluid_in_2: 'io_fluid_in_2', io_fluid_in_3: 'io_fluid_in_3',
        io_fluid_out_1: 'io_fluid_out_1', io_fluid_out_2: 'io_fluid_out_2',
    },
    heavy_steel_machine_base: { frame: 'frame' },
    gas_metallurgical_furnace: {
        frame: 'frame', controller: 'frame',
        io_item_in: 'io_item_in', io_item_out: 'io_item_out',
        io_gas_in: 'io_gas_in', io_gas_in_2: 'io_gas_in_2', io_gas_out: 'io_gas_out',
        io_fluid_in: 'io_fluid_in', io_fluid_out: 'io_fluid_out', io_energy_in: 'io_energy_in',
    },
    heat_conductor: { frame: 'frame' },
    distillation_column: { frame: 'frame', io_heat: 'io_heat', io_fluid1: 'io_fluid1', io_fluid2: 'io_fluid2', controller: 'frame' },
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

function expectedSample(u, v, horizontal, vertical, anyJoined, bordered, center, edgeless, borderWidth, centerScrews) {
    const outerU = u < borderWidth || u >= 16 - borderWidth;
    const outerV = v < borderWidth || v >= 16 - borderWidth;
    const screw = centerScrews && (u === borderWidth || u === 15 - borderWidth) && (v === borderWidth || v === 15 - borderWidth);
    if (screw) return [horizontal || vertical ? edgeless : bordered, u, v];
    if (outerU && outerV) {
        if (horizontal && vertical) return [edgeless, u, v];
        if (horizontal) return [bordered, u + (u < borderWidth ? borderWidth : -borderWidth), v];
        if (vertical) return [bordered, u, v + (v < borderWidth ? borderWidth : -borderWidth)];
        return [bordered, u, v];
    }
    if (outerU || outerV) return [(outerU ? horizontal : vertical) ? edgeless : bordered, u, v];
    return [anyJoined ? center : bordered, u, v];
}

const models = new Map();
function checkModel(geometryName, quadrantConnections, fixedPanel) {
    if (models.has(geometryName)) return models.get(geometryName);
    const geometry = read(`resource_pack/models/blocks/${geometryName}_connected.geo.json`)['minecraft:geometry'][0];
    const culling = read(`resource_pack/block_culling/${geometryName}.json`)['minecraft:block_culling_rules'];
    assert.equal(geometry.description.identifier, `geometry.skybluetech.${geometryName}_connected`);
    assert.equal(culling.description.identifier, `skybluetech:culling.${geometryName}`);
    assert.ok(geometry.bones.length <= 64);
    const parts = new Set();
    for (const bone of geometry.bones) bone.cubes.forEach((cube, index) => {
        assert.equal(Object.keys(cube.uv).length, 1);
        parts.add(`${bone.name}/${index}/${Object.keys(cube.uv)[0]}`);
    });
    if (quadrantConnections) {
        assert.equal(geometry.bones.length, 48, 'Quadrant connection visibility groups');
        assert.equal(parts.size, fixedPanel ? 288 : 96, 'Quadrant connection alternative face patches');
    }
    assert.equal(culling.rules.length, parts.size);
    for (const rule of culling.rules) {
        const part = rule.geometry_part;
        assert.equal(rule.condition, 'same_culling_layer');
        assert.equal(rule.direction, part.face);
        assert.ok(parts.delete(`${part.bone}/${part.cube}/${part.face}`), 'Duplicate or invalid culling reference');
    }
    assert.equal(parts.size, 0);
    const model = { geometry, culling };
    models.set(geometryName, model);
    return model;
}

let total = 0;
for (const [family, blocks] of Object.entries(families)) {
    const furnace = family === 'gas_metallurgical_furnace';
    const fixedPanel = furnace || family === 'large_reaction_pool';
    const standalone = ['large_reaction_pool_cap', 'large_reaction_pool_window', 'heavy_steel_machine_base'].includes(family);
    const quadrantConnections = fixedPanel || standalone;
    const borderWidth = family === 'heat_conductor' ? 4 : family === 'distillation_column' ? 3 : 2;
    const centerScrews = !['distillation_column', 'heat_conductor'].includes(family);
    let cases = 0;
    for (const [suffix, side] of Object.entries(blocks)) {
        const panelSize = fixedPanel ? furnace && suffix === 'io_energy_in' ? 4
            : ['io_gas_in', 'io_gas_in_2', 'io_gas_out', 'io_fluid_in', 'io_fluid_out'].includes(suffix) ? 6 : 8 : 0;
        const panelStart = (16 - panelSize) / 2;
        const geometryName = fixedPanel && panelSize !== 8 ? `${family}_panel_${panelSize}` : family;
        const { geometry, culling } = checkModel(geometryName, quadrantConnections, fixedPanel);
        const block = read(standalone
            ? `behavior_pack/netease_blocks/multiblock/skybluetech_${family}.json`
            : family === 'heat_conductor'
            ? 'behavior_pack/netease_blocks/machinery/skybluetech_heat_conductor.json'
            : `behavior_pack/netease_blocks/multiblock/skybluetech_${family}_${suffix}.json`)['minecraft:block'];
        const controller = suffix === 'controller';
        const prefix = `skybluetech:${family}_`;
        const textureId = name => family === 'heat_conductor'
            ? 'skybluetech:heat_conductor' + (name === 'frame_edgeless' ? '_edgeless' : '') : prefix + name;
        if (quadrantConnections) for (const name of ['frame', 'frame_horizontal', 'frame_vertical', 'frame_edgeless']) checkTexture(textureId(name));
        assert.equal(block.description.identifier, standalone || family === 'heat_conductor' ? 'skybluetech:' + family : prefix + suffix);
        if (family === 'large_reaction_pool_window') {
            for (const instances of [block.components['minecraft:material_instances'], block.components['minecraft:item_visual'].material_instances]) {
                for (const material of Object.values(instances)) assert.equal(material.render_method, 'alpha_test_single_sided');
            }
            assert.equal(block.components['minecraft:light_dampening'], 0);
        }
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
        assert.equal(item.material_instances['*'].texture, textureId(side));
        if (controller) {
            assert.equal(item.material_instances.south.texture, prefix + (family === 'distillation_column' ? 'controller' : 'controller_front'));
            assert.equal(block.description.traits['minecraft:placement_direction'].y_rotation_offset, 180);
        }
        if (fixedPanel) {
            const components = block.components;
            if (controller) {
                assert.equal(block.description.base_block, 'netease_container');
                assert.equal(components['netease:block_container'].container_size, 2);
                assert.equal(components['netease:block_container'].screen_name, furnace ? 'GasMetallurgicalFurnaceUI.main' : 'LargeReactionPoolUI.main');
                assert.equal(components['netease:block_entity'].tick, true);
                assert.deepEqual(components['tag:skybluetech_machine'], {});
                assert.deepEqual(components['tag:skybluetech_container'], {});
            } else if (suffix === 'frame') {
                assert.equal(block.description.base_block, undefined, 'Frame does not create a container');
                for (const component of ['netease:block_container', 'tag:skybluetech_machine', 'tag:skybluetech_container', 'tag:skybluetech_fluid_container', 'tag:redstoneflux_accepter', 'tag:redstoneflux_connectable']) {
                    assert.equal(components[component], undefined, `Controller/frame has no ${component}`);
                }
            } else {
                assert.deepEqual(components['tag:piston_denier'], {}, 'Interfaces cannot be moved by pistons');
                if (suffix === 'io_energy_in') {
                    assert.equal(block.description.base_block, undefined, 'Energy input has no container base');
                    assert.equal(components['netease:block_container'], undefined, 'Energy input has no item container');
                    assert.deepEqual(components['tag:redstoneflux_accepter'], {}, 'Energy input accepts RF');
                    assert.deepEqual(components['tag:redstoneflux_connectable'], {}, 'Energy input connects to RF networks');
                } else if (suffix === 'io_heat_in') {
                    assert.equal(components['netease:block_container'], undefined);
                } else {
                    assert.equal(block.description.base_block, 'netease_container');
                    const container = components['netease:block_container'];
                    assert.ok(container, 'Material interfaces have a container UI');
                    const itemPort = suffix.startsWith('io_item_');
                    const inputPort = /_in(?:_\d+)?$/.test(suffix);
                    const interfaceName = (itemPort ? 'Item' : 'Fluid') + (inputPort ? 'Input' : 'Output') + 'InterfaceUI.main';
                    assert.equal(container.screen_name, interfaceName, 'Interface uses its existing screen');
                    assert.equal(container.container_size, itemPort ? 5 : 2, 'Existing interface container size');
                    if (itemPort) {
                        assert.deepEqual(components['tag:skybluetech_container'], {});
                        assert.equal(container.hopper.input, inputPort);
                        assert.equal(container.hopper.output, !inputPort);
                        if (inputPort) {
                            assert.deepEqual(container.hopper.input_slot, [1, 2, 3, 4, 5].map(face => ({ face, slot: [0, 1, 2, 3, 4] })), 'Input hopper maps all five item slots');
                            assert.equal(container.hopper.output_slot, undefined);
                        } else {
                            assert.deepEqual(container.hopper.output_slot, [0, 1, 2, 3, 4], 'Output hopper extracts all five item slots');
                            assert.equal(container.hopper.input_slot, undefined);
                        }
                    } else {
                        assert.deepEqual(components['tag:skybluetech_fluid_container'], {});
                        if (!inputPort) assert.equal(components['netease:block_entity'].tick, true, 'Fluid output retains ticking from the existing template');
                    }
                }
            }
            if (controller) assert.deepEqual(block.description.states['skybluetech:active'], [false, true]);
            else assert.equal(block.description.traits, undefined, 'Six-sided ports have no placement direction');
        }
        const allMaterials = [block.components['minecraft:material_instances'], ...Object.values(block.permutations || {}).map(p => p.components['minecraft:material_instances']).filter(Boolean)];
        for (const materials of allMaterials) for (const material of Object.values(materials)) checkTexture(material.texture);
        for (const facing of controller ? directions.slice(0, 4) : ['north']) for (let mask = 0; mask < 64; mask++) {
            for (const active of controller && block.description.states['skybluetech:active'] ? [false, true] : [false]) {
                const states = { 'minecraft:cardinal_direction': facing, 'skybluetech:active': active };
                directions.forEach((direction, i) => { states['skybluetech:connection_' + direction] = Boolean(mask & (1 << i)); });
                let components = { ...block.components };
                for (const permutation of block.permutations || []) if (evaluate(permutation.condition, states)) components = { ...components, ...permutation.components };
                const rotation = components['minecraft:transformation']?.rotation?.[1] || 0;
                const materials = components['minecraft:material_instances'];
                const pixels = Object.fromEntries(directions.map(face => [face, new Array(256)]));
                const visiblePatches = Object.fromEntries(directions.map(face => [face, 0]));
                for (const bone of geometry.bones) {
                    if (!evaluate(components['minecraft:geometry'].bone_visibility[bone.name], states)) continue;
                    for (const cube of bone.cubes) for (const [face, uv] of Object.entries(cube.uv)) {
                        const [u, v, width, height] = rectangle(face, cube);
                        assert.deepEqual(uv.uv_size, [width, height], 'Unscaled pixel UV');
                        visiblePatches[face]++;
                        if (quadrantConnections) {
                            if (fixedPanel) {
                                const half = panelSize / 2;
                                const edge = 8 - half;
                                const sizes = [[8, edge], [edge, 8], [edge, half], [half, edge], [half, half]];
                                assert.ok(sizes.some(size => size[0] === width && size[1] === height), 'Split quadrant patch size');
                                assert.equal(Math.floor(u / 8), Math.floor((u + width - 1) / 8), 'Patch stays within one horizontal quadrant');
                                assert.equal(Math.floor(v / 8), Math.floor((v + height - 1) / 8), 'Patch stays within one vertical quadrant');
                            } else {
                                assert.deepEqual([width, height], [8, 8], 'Quadrant patch size');
                                assert.ok([0, 8].includes(u) && [0, 8].includes(v), 'Quadrant patch position');
                            }
                            assert.deepEqual(uv.uv, [u, v], 'Quadrant sampling preserves source UV');
                        }
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
                    if (quadrantConnections) assert.equal(visiblePatches[face], fixedPanel ? 12 : 4, `${mask}/${face}: visible quadrant patches`);
                    const front = family === 'distillation_column' ? 'controller'
                        : furnace && active ? 'controller_active' : 'controller_front' + (active ? '_active' : '');
                    const art = controller && face === 'north' ? front : side;
                    const center = ['frame', 'controller_side'].includes(art) ? 'frame_edgeless' : art;
                    for (let v = 0; v < 16; v++) for (let u = 0; u < 16; u++) {
                        const horizontal = states['skybluetech:connection_' + worldDirection(face, 0, u < 8 ? -1 : 1, rotation)];
                        const vertical = states['skybluetech:connection_' + worldDirection(face, 1, v < 8 ? -1 : 1, rotation)];
                        const quadrantArt = horizontal ? (vertical ? 'frame_edgeless' : 'frame_horizontal') : (vertical ? 'frame_vertical' : 'frame');
                        const panelPixel = fixedPanel && u >= panelStart && u < 16 - panelStart && v >= panelStart && v < 16 - panelStart && art !== 'frame';
                        const expected = quadrantConnections
                            ? [textureId(panelPixel ? art : quadrantArt), u, v]
                            : expectedSample(u, v, horizontal, vertical, mask !== 0, textureId(art), textureId(center), textureId('frame_edgeless'), borderWidth, centerScrews);
                        assert.deepEqual(pixels[face][v * 16 + u], expected, `${family}/${suffix}/${facing}/${mask}/active=${active}/${face} pixel ${u},${v}`);
                    }
                }
                cases++;
            }
        }
    }
    if (quadrantConnections) assert.equal(cases, 64 * (Object.keys(blocks).length + (fixedPanel ? 7 : 0)), 'All quadrant connection, facing and active combinations');
    console.log(fixedPanel
        ? `${family}: ${cases} cases; fixed ${furnace ? '4x4/6x6/8x8' : '8x8'} panels, outer CTM, controller rotation/active, culling and PNG paths valid.`
        : quadrantConnections ? `${family}: ${cases} cases; six faces fully covered by four quadrants; source UV, four material choices, culling and PNG paths valid.`
        : `${family}: ${cases} cases including active controller where present; six faces fully covered; materials, screw rules, rotation, culling and PNG paths valid.`);
    total += cases;
}

// Python is inspected as text only; the runtime must remain inside the game.
const furnacePrefix = 'skybluetech:gas_metallurgical_furnace_';
const furnaceIds = Object.keys(families.gas_metallurgical_furnace).map(suffix => furnacePrefix + suffix).sort();
const pythonRoot = 'behavior_pack/skybluetech_scripts/skybluetech/';
const readText = file => fs.readFileSync(path.join(root, file), 'utf8');
const enumSource = readText(pythonRoot + 'common/define/id_enum/multi_block_structure.py');
const enumBody = enumSource.match(/class GasMetallurgicalFurnace:\r?\n([\s\S]*?)(?=\r?\nclass |$)/);
assert.ok(enumBody, 'Furnace ID enum exists');
const enumMembers = Object.fromEntries([...enumBody[1].matchAll(/^    ([A-Z_0-9]+) = "(skybluetech:gas_metallurgical_furnace_[^"]+)"\r?$/gm)].map(match => [match[1], match[2]]));
assert.deepEqual(Object.values(enumMembers).sort(), furnaceIds, 'Enum includes every furnace block exactly once');
const shellSource = readText(pythonRoot + 'server/misc/multiblock_shell_connections.py');
const shellGroup = shellSource.match(/frozenset\(\(\s*(GasMetallurgicalFurnace\.[\s\S]*?)\)\)/);
assert.ok(shellGroup, 'Furnace shell connection group exists');
const connectedMembers = [...shellGroup[1].matchAll(/GasMetallurgicalFurnace\.([A-Z_0-9]+)/g)].map(match => enumMembers[match[1]]);
assert.deepEqual(connectedMembers.sort(), furnaceIds, 'All furnace blocks share one connection group');

const resourceBlocks = read('resource_pack/blocks.json');
const creativeGroups = read('behavior_pack/netease_group/skybluetech_multi_block_structures.json').groups;
const groupKey = 'itemGroup.skybluetech.gas_metallurgical_furnace';
const creativeGroup = creativeGroups.filter(group => group.group_name === groupKey);
assert.equal(creativeGroup.length, 1, 'One furnace creative group');
assert.deepEqual([...creativeGroup[0].list].sort(), [...furnaceIds, 'skybluetech:magnesium_pellet', 'skybluetech:titanium_sponge'].sort(), 'Creative group includes furnace blocks and process materials');
assert.equal(creativeGroup[0].icon, furnacePrefix + 'controller');
const meiSource = readText(pythonRoot + 'external/mei/groups.py');
const meiGroup = meiSource.match(/\("skybluetech:group\.gas_metallurgical_furnace",\s*"itemGroup\.skybluetech\.gas_metallurgical_furnace",\s*_ids\(([\s\S]*?)\)\)/);
assert.ok(meiGroup, 'Furnace MEI group exists');
const meiIds = [...meiGroup[1].matchAll(/"(gas_metallurgical_furnace_[^"]+)"/g)].map(match => 'skybluetech:' + match[1]);
assert.deepEqual(meiIds.sort(), furnaceIds, 'MEI group includes all furnace blocks');
const translations = readText('resource_pack/texts/zh_CN.lang').split(/\r?\n/);
for (const id of furnaceIds) {
    assert.ok(resourceBlocks[id], `Missing resource block ${id}`);
    assert.equal(translations.filter(line => line.startsWith('tile.' + id + '.name=')).length, 1, `One translation for ${id}`);
}
assert.equal(translations.filter(line => line.startsWith(groupKey + '=')).length, 1, 'One furnace group translation');

const interfaceFile = pythonRoot + 'server/machinery/gas_metallurgical_furnace_interfaces.py';
const interfaceSource = readText(interfaceFile);
const expectedInterfaceClasses = {
    IO_ITEM_INPUT: 'ItemInputInterface',
    IO_ITEM_OUTPUT: 'ItemOutputInterface',
    IO_GAS_INPUT: 'FluidInputInterface',
    IO_GAS_INPUT_AUXILIARY: 'FluidInputInterface',
    IO_GAS_OUTPUT: 'FluidOutputInterface',
    IO_FLUID_INPUT: 'FluidInputInterface',
    IO_FLUID_OUTPUT: 'FluidOutputInterface',
    IO_ENERGY_INPUT: 'EnergyInputInterface',
};
const bindings = [...interfaceSource.matchAll(/([A-Za-z_][A-Za-z_0-9]*)\.AddExtraMachineId\(\s*GasMetallurgicalFurnace\.([A-Z_0-9]+)\s*\)/g)];
assert.equal(bindings.length, 8, 'Exactly eight furnace interfaces are bound');
assert.deepEqual(Object.fromEntries(bindings.map(match => [match[2], match[1]])), expectedInterfaceClasses, 'Each furnace interface reuses the corresponding existing class');
for (const interfaceClass of new Set(Object.values(expectedInterfaceClasses))) {
    const registrations = [...interfaceSource.matchAll(new RegExp('RegisterMachine\\(\\s*' + interfaceClass + '\\s*\\)', 'g'))];
    assert.equal(registrations.length, 1, `One registry refresh for ${interfaceClass}`);
    for (const binding of bindings.filter(match => match[1] === interfaceClass)) {
        assert.ok(registrations[0].index > binding.index, `Register ${interfaceClass} after all its furnace IDs are added`);
    }
}
assert.match(readText(pythonRoot + 'server/machinery/__init__.py'), /^from \. import gas_metallurgical_furnace_interfaces(?:\s+as\s+[A-Za-z_][A-Za-z_0-9]*)?\s*$/m, 'Server initialization imports the interface bindings');

function checkNoFurnaceControllerMachine(directory) {
    for (const entry of fs.readdirSync(path.join(root, directory), { withFileTypes: true })) {
        const file = directory + '/' + entry.name;
        if (entry.isDirectory()) checkNoFurnaceControllerMachine(file);
        else if (entry.name.endsWith('.py')) {
            const source = readText(file);
            const controllerOrFrame = '(?:GasMetallurgicalFurnace\\.(?:CONTROLLER|FRAME)\\b|["\']skybluetech:gas_metallurgical_furnace_(?:controller|frame)["\'])';
            assert.doesNotMatch(source, new RegExp('AddExtraMachineId\\(\\s*' + controllerOrFrame), `Controller/frame has no interface registration in ${file}`);
            assert.doesNotMatch(source, /block_name\s*=\s*GasMetallurgicalFurnace\.FRAME\b/, `Frame has no machine class in ${file}`);
        }
    }
}
checkNoFurnaceControllerMachine(pythonRoot + 'server/machinery');
console.log('Furnace block IDs, groups, shell connections, existing interfaces, controller container/UI and visual-only frame valid.');
console.log(`Validated ${total} rendered cases without executing mod Python. Target-client visual validation is still required.`);
