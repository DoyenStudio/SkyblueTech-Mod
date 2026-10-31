#!/usr/bin/env node
/* Read-only structural checks for the shared recipe UI; never imports mod Python. */
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const root = path.resolve(__dirname, '..');
const pack = path.join(root, 'resource_pack');
const definitions = new Map();
let parsedFiles = 0;

function readJson(file) {
    parsedFiles += 1;
    return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
}

function loadFile(file) {
    const document = readJson(file);
    if (!document.namespace) return;
    for (const [key, value] of Object.entries(document)) {
        if (key === 'namespace' || !value || typeof value !== 'object') continue;
        const [name, parent] = key.split('@');
        definitions.set(`${document.namespace}.${name}`, {
            namespace: document.namespace, parent, value, file,
        });
    }
}

function loadTree(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
        const file = path.join(directory, entry.name);
        if (entry.isDirectory()) loadTree(file);
        else if (entry.name.endsWith('.json')) loadFile(file);
    }
}

// Optional MEI pack permits checking its actual slot templates as well.
if (process.argv[2]) loadTree(path.join(path.resolve(process.argv[2]), 'ui'));
const registered = readJson(path.join(pack, 'ui', '_ui_defs.json')).ui_defs;
assert.equal(new Set(registered).size, registered.length, 'Duplicate ui_defs entry');
assert(registered.includes('ui/MachineRecipeLib.json'), 'Shared library is not registered');
for (const relative of registered) loadFile(path.join(pack, relative));

function variable(value, environment, seen = new Set()) {
    if (typeof value !== 'string' || !/^\$[\w]+$/.test(value)) return value;
    if (!(value in environment)) return value;
    assert(!seen.has(value), `Circular UI variable ${value}`);
    return variable(environment[value], environment, new Set([...seen, value]));
}

function environmentFor(parent, ...objects) {
    const environment = { ...parent };
    for (const object of objects) {
        for (const [key, value] of Object.entries(object)) {
            if (!key.startsWith('$')) continue;
            const name = key.replace(/\|default$/, '');
            if (!key.endsWith('|default') || !(name in environment)) environment[name] = value;
        }
    }
    return environment;
}

function qualified(reference, namespace) {
    return reference.includes('.') ? reference : `${namespace}.${reference}`;
}

// Recipe wrappers inherit entire controls lists. This intentionally does not
// emulate arbitrary engine expressions, collection callbacks or runtime layout.
function cascade(reference, inherited, overrides = {}, ancestors = []) {
    reference = variable(reference, inherited);
    assert.equal(typeof reference, 'string', 'Invalid template reference');
    assert(!reference.startsWith('$'), `Unresolved template ${reference}`);
    assert(!ancestors.includes(reference), `Circular UI inheritance: ${reference}`);
    const record = definitions.get(reference);
    if (!record) {
        const namespace = reference.split('.')[0];
        assert(!/^(MachineRecipeLib|RecipeCheckerLib|Skyblue)/.test(namespace),
            `Missing local template ${reference}`);
        return { value: overrides, environment: environmentFor(inherited, overrides), refs: [reference] };
    }
    const environment = environmentFor(inherited, record.value, overrides);
    const parent = record.parent
        ? cascade(qualified(variable(record.parent, environment), record.namespace), environment, {}, [...ancestors, reference])
        : { value: {}, environment, refs: [] };
    return {
        value: { ...parent.value, ...record.value, ...overrides },
        environment: environmentFor(parent.environment, record.value, overrides),
        refs: [...parent.refs, reference],
    };
}

function expand(reference, inherited = {}, overrides = {}, label = '', ancestors = []) {
    const result = reference
        ? cascade(reference, inherited, overrides)
        : { value: overrides, environment: environmentFor(inherited, overrides), refs: [] };
    const node = { name: label, ...result, children: new Map() };
    for (const entry of result.value.controls || []) {
        assert.equal(Object.keys(entry).length, 1, 'Expected one control per controls entry');
        const [[key, value]] = Object.entries(entry);
        const [name, template] = key.split('@');
        assert(!node.children.has(name), `Duplicate child ${label}/${name}`);
        const resolved = template ? variable(template, result.environment) : null;
        if (resolved) assert(!ancestors.includes(resolved), `Circular child template ${resolved}`);
        node.children.set(name, expand(resolved, result.environment, value, name,
            resolved ? [...ancestors, resolved] : ancestors));
    }
    return node;
}

function at(node, relative) {
    for (const name of relative.split('/').filter(Boolean)) {
        node = node.children.get(name);
        if (!node) return null;
    }
    return node;
}

function visit(node, callback, location = '') {
    callback(node, location);
    for (const [name, child] of node.children) visit(child, callback, `${location}/${name}`);
}

// Parse only Python literal containers. The mod module is never imported or run.
function pythonLiteral(source, name) {
    const assignment = new RegExp(`^${name}\\s*=\\s*`, 'm').exec(source);
    assert(assignment, `Missing Python literal ${name}`);
    let position = assignment.index + assignment[0].length;
    function whitespace() {
        for (;;) {
            while (/\s/.test(source[position] || '') && position < source.length) position += 1;
            if (source[position] !== '#') return;
            while (position < source.length && source[position] !== '\n') position += 1;
        }
    }
    function parse() {
        whitespace();
        const token = source[position++];
        if (token === '"' || token === "'") {
            let text = '';
            while (position < source.length) {
                const character = source[position++];
                if (character === token) return text;
                if (character !== '\\') text += character;
                else {
                    const escaped = source[position++];
                    text += ({ n: '\n', r: '\r', t: '\t' })[escaped] || escaped;
                }
            }
            throw new Error(`Unterminated literal in ${name}`);
        }
        if (token === '{' || token === '(' || token === '[') {
            const closing = ({ '{': '}', '(': ')', '[': ']' })[token];
            const result = token === '{' ? {} : [];
            whitespace();
            while (source[position] !== closing) {
                const value = parse();
                if (token === '{') {
                    whitespace();
                    assert.equal(source[position++], ':', `Expected dictionary separator in ${name}`);
                    assert(!(value in result), `Duplicate Python key ${value}`);
                    result[value] = parse();
                } else result.push(value);
                whitespace();
                if (source[position] === ',') { position += 1; whitespace(); }
                else assert.equal(source[position], closing, `Expected container separator in ${name}`);
            }
            position += 1;
            return result;
        }
        position -= 1;
        const literal = /^(None|True|False|-?\d+(?:\.\d+)?)/.exec(source.slice(position));
        assert(literal, `Unsupported Python literal near ${source.slice(position, position + 35)}`);
        position += literal[0].length;
        return ({ None: null, True: true, False: false })[literal[0]] ??
            (literal[0] === 'None' ? null : Number(literal[0]));
    }
    return parse();
}

const wrappers = [...definitions.entries()].filter(([reference, record]) =>
    reference.startsWith('RecipeCheckerLib.') && record.parent === 'MachineRecipeLib.mini_row');
assert.equal(wrappers.length, 29, 'Expected all 29 active machine/misc recipe pages to share layouts');
const recipeSources = path.join(root, 'behavior_pack', 'skybluetech_scripts', 'skybluetech', 'client', 'mini_jei');
const referencedMiniPages = new Set();
for (const directory of ['machinery', 'misc']) {
    for (const filename of fs.readdirSync(path.join(recipeSources, directory))) {
        if (!filename.endsWith('.py')) continue;
        const source = fs.readFileSync(path.join(recipeSources, directory, filename), 'utf8');
        for (const match of source.matchAll(/RecipeCheckerLib\.([a-z_]+_recipes)/g)) {
            referencedMiniPages.add(`RecipeCheckerLib.${match[1]}`);
        }
    }
}
assert.deepEqual(new Set(wrappers.map(([reference]) => reference)), referencedMiniPages,
    'Active machine renderers and shared Mini wrappers differ');

let slotCount = 0;
let fluidCount = 0;
for (const [reference, record] of wrappers) {
    assert(!('controls' in record.value), `${reference} still owns a duplicated layout`);
    const node = expand(reference);
    assert.equal(node.value.size[0], 180, `${reference} must retain the Mini row width`);
    assert(Number.isFinite(node.value.size[1]) && node.value.size[1] > 0, `${reference} requires explicit height`);
    assert.deepEqual([...node.children.keys()], ['content'], `${reference} has an unexpected row shell`);
    const content = at(node, 'content');
    assert(content.value.size[0] <= 180, `${reference} content exceeds the Mini row`);
    assert(content.value.size[1] <= node.value.size[1], `${reference} content exceeds the row height`);
    visit(node, (child, location) => {
        for (const dependency of child.refs) {
            assert(!/^(mei_|SkyblueMei)/.test(dependency), `${reference}${location} depends on ${dependency}`);
        }
        if (child.value.texture) {
            const texture = variable(child.value.texture, child.environment);
            assert(!String(texture).startsWith('textures/ui/mei/'), `${reference}${location} needs a MEI texture`);
        }
        for (const binding of child.value.bindings || []) {
            const name = variable(binding.binding_name, child.environment);
            assert(!String(name).startsWith('#mei_'), `${reference}${location} retains a MEI binding`);
        }
        if (child.refs.includes('SkybluePanelLib.recipe_slot')) {
            slotCount += 1;
            for (const required of ['item_renderer', 'item_count', 'prob', 'check_btn']) {
                assert(at(child, required), `${reference}${location} lacks item helper child ${required}`);
            }
        }
        if (child.refs.includes('SkybluePanelLib.fluid_tank')) {
            fluidCount += 1;
            for (const required of ['fluid/img', 'text', 'info/hover/hover_text', 'info/pressed/hover_text']) {
                assert(at(child, required), `${reference}${location} lacks fluid helper child ${required}`);
            }
        }
        if (child.refs.includes('MachineRecipeLib.energy_meter')) {
            for (const required of ['bar/mask', 'info/hover/hover_text', 'info/pressed/hover_text']) {
                assert(at(child, required), `${reference}${location} lacks power helper child ${required}`);
            }
            assert(!at(child, 'bar/mask').value.tiled, `${reference} energy mask must remain untiled`);
        }
    });
}

let meiPages = 0;
for (const [reference, record] of definitions) {
    if (!/^SkyblueMei[^.]+\.content_panel$/.test(reference)) continue;
    assert(record.parent && record.parent.startsWith('MachineRecipeLib.'), `${reference} still owns layout`);
    assert(!('controls' in record.value), `${reference} duplicates shared children`);
    assert.equal(record.value.$recipe_item_slot, 'mei_common.item_panel', `${reference} lost MEI item provider`);
    assert.equal(record.value.$recipe_fluid_slot, 'SkyblueMeiCommon.fluid_slot', `${reference} lost fluid provider`);
    const shared = expand(record.parent);
    const mei = expand(reference);
    assert.deepEqual(mei.value.size, shared.value.size, `${reference} changed shared dimensions`);
    if (process.argv[2]) {
        let foundProvider = false;
        visit(mei, child => {
            if (child.refs.includes('mei_common.item_panel') || child.refs.includes('SkyblueMeiCommon.fluid_slot')) {
                foundProvider = true;
                assert(!child.refs.includes('SkybluePanelLib.recipe_slot'), `${reference} selected a Mini item slot`);
            }
        });
        // Air compressor still has its fluid output; every machine has at least one slot.
        assert(foundProvider, `${reference} did not resolve its MEI slot providers`);
    }
    meiPages += 1;
}
assert.equal(meiPages, 32, 'Expected all 32 MEI machine content wrappers');

const pythonRoot = path.join(root, 'behavior_pack', 'skybluetech_scripts', 'skybluetech');
const layoutSource = fs.readFileSync(path.join(pythonRoot, 'common', 'define', 'recipe_layouts.py'), 'utf8');
const layouts = pythonLiteral(layoutSource, 'LAYOUTS');
assert.equal(Object.keys(layouts).length, 27, 'Expected 27 standard machine layouts');
for (const [category, layout] of Object.entries(layouts)) {
    const node = expand(`MachineRecipeLib.${layout.file}`);
    for (const [side, group] of [['inputs', 'input'], ['outputs', 'output']]) {
        const controls = at(node, `body/${group}`);
        assert.equal(controls?.children.size || 0, layout[side].length, `${category} ${side} count differs`);
        const occupied = new Set();
        layout[side].forEach(([kind, slot], index) => {
            const child = at(node, `body/${group}/${index}`);
            assert(child, `${category} missing ${group}/${index}`);
            const expected = kind === 'fluid' ? 'SkybluePanelLib.fluid_tank' : 'SkybluePanelLib.recipe_slot';
            assert(child.refs.includes(expected), `${category} ${group}/${index} has wrong slot kind`);
            if (slot !== null) {
                assert(!occupied.has(`${kind}:${slot}`), `${category} repeats ${side} ${kind}:${slot}`);
                occupied.add(`${kind}:${slot}`);
            }
        });
    }
    assert.equal(at(node, 'body/cat')?.children.size || 0, layout.catalysts, `${category} catalyst count differs`);
    assert.equal(Boolean(at(node, 'power')), Boolean(layout.power), `${category} energy component differs`);
    if (layout.power) {
        assert(at(node, 'power/bar/mask'), `${category} missing energy mask`);
        assert.equal(at(node, 'power').value.size[1] - 2, 3 * layout.segments + 1,
            `${category} energy segment count differs`);
    }
    assert.equal(Boolean(at(node, 'body/progress')), Boolean(layout.progress || layout.static),
        `${category} progress component differs`);
    if (layout.progress) assert(at(node, 'body/progress/mask'), `${category} missing progress mask`);
    if (layout.progress || layout.static) assert(at(node, 'body/progress_hover/info'), `${category} missing progress hover`);
    assert.equal(Boolean(at(node, 'body/flame')), Boolean(layout.flame), `${category} flame component differs`);
    if (layout.flame) assert(at(node, 'body/flame/mask'), `${category} missing flame mask`);
}

const specials = [
    ['machinery/machinery_workstation.py', 'machinery_workstation', ['input/0', 'input/8', 'side/0', 'side/1', 'output/0']],
    ['misc/industrial_researching.py', 'industrial_researching', ['input/0', 'input/8', 'output/0', 'output/1', 'xp_cost_label']],
    ['misc/metal_hammer.py', 'metal_hammer', ['input/0', 'output/0']],
    ['machinery/hydroponic_bed.py', 'hydroponic_bed', ['body/seed/0', 'body/outputs/0', 'body/outputs/2', 'body/shell/crop', 'body/progress/mask', 'body/progress_hover/info', 'power/bar/mask']],
    ['machinery/hydroponic_bed_sand.py', 'hydroponic_bed_sand', ['body/seed/0', 'body/outputs/0', 'body/outputs/2', 'body/shell/crop']],
];
for (const [filename, page, requiredPaths] of specials) {
    const node = expand(`RecipeCheckerLib.${page}_recipes`);
    for (const relative of requiredPaths) assert(at(node, `content/${relative}`), `${page} missing special path ${relative}`);
    const source = fs.readFileSync(path.join(recipeSources, filename), 'utf8');
    for (const match of source.matchAll(/\b(panel|panel_ctrl|content)\["([^"%]+)"\]/g)) {
        const relative = match[1] === 'content' ? `content/${match[2]}` : match[2];
        assert(at(node, relative), `${filename} references missing ${relative}`);
    }
}
const guidance = expand('GuidanceLib.machinery_workstation_render_page');
const embedded = at(guidance, 'recipe_renderer');
assert(embedded, 'Guide no longer embeds the workstation recipe');
assert(at(embedded, 'content/input/8'), 'Guide does not select the shared workstation layout');
assert(at(embedded, 'content').value.size[0] <= embedded.value.size[0], 'Shared workstation content exceeds guide width');
assert(at(embedded, 'content').value.size[1] <= embedded.value.size[1], 'Shared workstation content exceeds guide height');

console.log(`Validated ${parsedFiles} UI JSON files; ${wrappers.length} Mini and ${meiPages} MEI shared wrappers.`);
console.log(`Mini dependency closures include ${slotCount} item slots and ${fluidCount} fluid slots, with no MEI templates, bindings or textures.`);
console.log(`Matched ${Object.keys(layouts).length} Python layout literals to slot kinds, counts and animation paths; checked five special renderers and guide embedding.`);
console.log('Structural checks passed. Runtime callbacks, native item rendering and game input still require client validation.');
