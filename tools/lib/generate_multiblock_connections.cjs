'use strict';

// Shared authoring tool for 16px shells with a 2px frame and screw pixels at 2/13.
// Generates JSON only; never imports or executes mod Python.
module.exports = function generateConnections({ family, variants }) {
    const fs = require('node:fs');
    const path = require('node:path');
    const root = path.resolve(__dirname, '../..');
    const geometryId = `geometry.skybluetech.${family}_connected`;
    const cullingId = `skybluetech:culling.${family}`;
    const cullingLayer = `skybluetech:culling_layer.${family}`;
    const horizontal = ['north', 'east', 'south', 'west'];
    const vectors = {
        north: [0, 0, -1], south: [0, 0, 1],
        east: [1, 0, 0], west: [-1, 0, 0],
        up: [0, 1, 0], down: [0, -1, 0],
    };
    const opposite = { north: 'south', south: 'north', east: 'west', west: 'east', up: 'down', down: 'up' };
    // Directions of increasing positive UV in world/model-local cardinal coordinates.
    // Bedrock's exported geometry X is mirrored; patchCube converts X at the end.
    const faceAxes = {
        north: ['west', 'down'], south: ['east', 'down'],
        east: ['north', 'down'], west: ['south', 'down'],
        up: ['west', 'north'], down: ['west', 'south'],
    };
    const groups = new Map();

    function readJson(relative) {
        return JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8'));
    }

    function write(relative, text) {
        const file = path.join(root, relative);
        fs.mkdirSync(path.dirname(file), { recursive: true });
        const previous = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : null;
        if (previous !== text) fs.writeFileSync(file, text);
    }

    function writeJson(relative, value) {
        const file = path.join(root, relative);
        const old = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : '\n';
        const newline = old.includes('\r\n') ? '\r\n' : '\n';
        const text = JSON.stringify(value, null, 4).replace(/\n/g, newline);
        write(relative, text + (old.endsWith('\n') ? newline : ''));
    }

    function patchCube(face, u, v, width, height, sourceU, sourceV, textureRegion) {
        const [uDirection, vDirection] = faceAxes[face];
        const normal = vectors[face];
        const uVector = vectors[uDirection];
        const vVector = vectors[vDirection];
        const points = [[u, v], [u + width, v + height]].map(([s, t]) =>
            normal.map((n, axis) => ([0, 8, 0][axis] + n * 8 + uVector[axis] * (s - 8) + vVector[axis] * (t - 8)) * (axis === 0 ? -1 : 1)));
        const origin = points[0].map((a, axis) => Math.min(a, points[1][axis]));
        const size = points[0].map((a, axis) => Math.abs(a - points[1][axis]));
        const faceMaterial = face === 'north' ? 'front' : 'side';
        const material = textureRegion === 'edgeless' ? 'edgeless' : faceMaterial + (textureRegion === 'center' ? '_center' : '');
        return {
            origin, size,
            uv: { [face]: { uv: [sourceU, sourceV], uv_size: [width, height], material_instance: material } },
        };
    }

    function addPatch(name, predicate, face, u, v, width, height, sourceU, sourceV, textureRegion) {
        if (!groups.has(name)) groups.set(name, { predicate, cubes: [] });
        groups.get(name).cubes.push(patchCube(face, u, v, width, height, sourceU, sourceV, textureRegion));
    }

    function matching(requirements) {
        return connected => Object.entries(requirements).map(([direction, value]) =>
            value ? connected(direction) : `!${connected(direction)}`).join(' && ');
    }

    for (const face of Object.keys(faceAxes)) {
        const [right, bottom] = faceAxes[face];
        const left = opposite[right];
        const top = opposite[bottom];
        // Share center visibility across all six faces to stay below 64 visibility entries.
        // Joined frame centers use frame_edgeless; panel/port centers retain their original art.
        for (const joined of [false, true]) {
            const predicate = connected => (joined ? '' : '!') + '(' + Object.keys(vectors).map(connected).join(' || ') + ')';
            // Leave the four screw pixels (2/13, 2/13) to the adjacent corner's condition.
            for (const [u, v, width, height] of [[3, 2, 10, 12], [2, 3, 1, 10], [13, 3, 1, 10]]) {
                addPatch(`center_${joined ? 'joined' : 'isolated'}`, predicate, face, u, v, width, height, u, v, joined ? 'center' : 'bordered');
            }
        }
        for (const [direction, u, v, width, height] of [
            [left, 0, 2, 2, 12], [right, 14, 2, 2, 12],
            [top, 2, 0, 12, 2], [bottom, 2, 14, 12, 2],
        ]) {
            for (const joined of [false, true]) {
                addPatch(`edge_${direction}_${joined ? 'joined' : 'isolated'}`, matching({ [direction]: joined }),
                    face, u, v, width, height, u, v, joined ? 'edgeless' : 'bordered');
            }
        }
        for (const [u, hDirection] of [[0, left], [14, right]]) {
            for (const [v, vDirection] of [[0, top], [14, bottom]]) {
                for (const hJoined of [false, true]) {
                    for (const vJoined of [false, true]) {
                        const requirements = { [hDirection]: hJoined, [vDirection]: vJoined };
                        const name = 'corner_' + Object.keys(requirements).sort().map(d => d + (requirements[d] ? '_joined' : '_isolated')).join('_');
                        const both = hJoined && vJoined;
                        // One joined edge: continue the remaining straight border through the corner.
                        // Both joined: use the shared edgeless corner. No diagonal lookup is involved.
                        const sourceU = hJoined && !vJoined ? (u === 0 ? 2 : 12) : u;
                        const sourceV = vJoined && !hJoined ? (v === 0 ? 2 : 12) : v;
                        addPatch(name, matching(requirements), face, u, v, 2, 2, sourceU, sourceV, both ? 'edgeless' : 'bordered');
                        // Keep a screw only when BOTH incident edges are disconnected.
                        // Sample the same pixel from frame_edgeless otherwise, without an overlay.
                        const screwU = u === 0 ? 2 : 13;
                        const screwV = v === 0 ? 2 : 13;
                        addPatch(name, matching(requirements), face, screwU, screwV, 1, 1, screwU, screwV,
                            hJoined || vJoined ? 'edgeless' : 'bordered');
                    }
                }
            }
        }
    }

    function worldConnection(direction) {
        return `q.block_state('skybluetech:connection_${direction}')`;
    }

    function visibility(controller) {
        const connected = direction => {
            if (!controller || direction === 'up' || direction === 'down') return worldConnection(direction);
            const local = horizontal.indexOf(direction);
            // cardinal_direction already includes placement_direction.y_rotation_offset.
            // Match the model transforms without applying that placement offset twice.
            // The pack uses Molang 1.18.0: nested ternaries associate to the left, and
            // &&/|| precedence differs from modern Molang. Explicitly group every term.
            return '(' + horizontal.map((facing, index) =>
                `((q.block_state('minecraft:cardinal_direction') == '${facing}') && ${worldConnection(horizontal[(local + index) % 4])})`).join(' || ') + ')';
        };
        return Object.fromEntries([...groups].map(([name, group]) => [name, group.predicate(connected)]));
    }

    function materials(side, front = side) {
        const instance = texture => ({ texture: `skybluetech:${family}_` + texture, render_method: 'opaque' });
        // Plain shells use the shared base when connected; panels/ports keep their art.
        const center = texture => ['frame', 'controller_side'].includes(texture) ? 'frame_edgeless' : texture;
        return {
            '*': instance(side), side: instance(side), front: instance(front),
            edgeless: instance('frame_edgeless'), side_center: instance(center(side)), front_center: instance(center(front)),
        };
    }

    if (groups.size > 64) throw new Error('Block geometry permits at most 64 bone visibility entries.');

    const boneText = [...groups].map(([name, group]) =>
        '                {\n' + `                    "name": ${JSON.stringify(name)},\n` +
        '                    "pivot": [0, 8, 0],\n                    "cubes": [\n' +
        group.cubes.map(cube => '                        ' + JSON.stringify(cube)).join(',\n') +
        '\n                    ]\n                }').join(',\n');
    write(`resource_pack/models/blocks/${family}_connected.geo.json`,
        '{\n    "format_version": "1.12.0",\n    "minecraft:geometry": [{\n' +
        '        "description": ' + JSON.stringify({ identifier: geometryId, texture_width: 16, texture_height: 16, visible_bounds_width: 2, visible_bounds_height: 2, visible_bounds_offset: [0, 0.5, 0] }) + ',\n' +
        '        "bones": [\n' + boneText + '\n        ]\n    }]\n}\n');

    const cullingRules = [...groups].flatMap(([name, group]) => group.cubes.map((cube, index) => ({
        direction: Object.keys(cube.uv)[0], condition: 'same_culling_layer',
        geometry_part: { bone: name, cube: index, face: Object.keys(cube.uv)[0] },
    })));
    write(`resource_pack/block_culling/${family}.json`,
        '{\n    "format_version": "1.21.80",\n    "minecraft:block_culling_rules": {\n' +
        `        "description": { "identifier": "${cullingId}" },\n        "rules": [\n` +
        cullingRules.map(rule => '            ' + JSON.stringify(rule)).join(',\n') + '\n        ]\n    }\n}\n');

    for (const [suffix, side] of variants) {
        const file = `behavior_pack/netease_blocks/multiblock/skybluetech_${family}_${suffix}.json`;
        const document = readJson(file);
        const block = document['minecraft:block'];
        const controller = suffix === 'controller';
        // Keep the stable culling-layer format; native connection traits are not used.
        document.format_version = '1.21.90';
        if (block.description.traits) {
            delete block.description.traits['minecraft:connection'];
            if (Object.keys(block.description.traits).length === 0) delete block.description.traits;
        }
        block.description.states ??= {};
        for (const direction of [...horizontal, 'up', 'down']) {
            delete block.description.states['skybluetech:adjacent_' + direction];
            block.description.states['skybluetech:connection_' + direction] = [false, true];
        }
        const components = block.components;
        components['minecraft:geometry'] = { identifier: geometryId, culling: cullingId, culling_layer: cullingLayer, bone_visibility: visibility(controller) };
        delete components['minecraft:connection_rule'];
        components['minecraft:material_instances'] = controller ? materials(side, 'controller_front') : materials(side);
        components['minecraft:item_visual'] = {
            geometry: 'minecraft:geometry.full_block',
            // Inventory full-block rendering shows the south face. This mapping is item-only;
            // the placed controller keeps its north front and placement y_rotation_offset.
            material_instances: controller ? { '*': { texture: `skybluetech:${family}_controller_side` }, south: { texture: `skybluetech:${family}_controller_front` } }
                : { '*': { texture: `skybluetech:${family}_` + side } },
        };
        components['netease:neighborchanged_sendto_script'] = { value: true };
        components['netease:listen_block_remove'] = { value: true };
        components['netease:block_entity'] ??= {};
        if (controller) {
            for (const permutation of block.permutations) {
                if (!permutation.components['minecraft:material_instances']) continue;
                const active = permutation.condition === "q.block_state('skybluetech:active')";
                permutation.components['minecraft:material_instances'] = materials(side, active ? 'controller_front_active' : 'controller_front');
            }
        }
        writeJson(file, document);
    }

    // Register only the shared edgeless atlas entry; bordered identifiers remain untouched.
    const atlasFile = path.join(root, 'resource_pack/textures/terrain_texture.json');
    let atlasText = fs.readFileSync(atlasFile, 'utf8');
    const atlas = JSON.parse(atlasText).texture_data;
    const newline = atlasText.includes('\r\n') ? '\r\n' : '\n';
    for (const stem of ['frame']) {
        const id = `skybluetech:${family}_` + stem + '_edgeless';
        const texture = `textures/blocks/multi_block_structure/${family}/` + stem + '_edgeless';
        if (atlas[id]) {
            if (atlas[id].textures !== texture) throw new Error('Existing atlas entry differs: ' + id);
            continue;
        }
        const anchor = `        "skybluetech:${family}_${stem}": {`;
        if (!atlasText.includes(anchor)) throw new Error('Missing atlas anchor: ' + stem);
        atlasText = atlasText.replace(anchor, `        "${id}": {${newline}            "textures": "${texture}"${newline}        },${newline}` + anchor);
    }
    write('resource_pack/textures/terrain_texture.json', atlasText);
    console.log(`Generated ${family}: ${groups.size} bone groups, ${cullingRules.length} face patches, and ${variants.length} block definitions.`);
};
