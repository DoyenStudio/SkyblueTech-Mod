---
name: skybluetech-fluid
description: 创建或核查本 SkyBlueTech 附加包的标准流体，涵盖液体方块、基础材质 RGBA 离线乘算生成独立贴图、流体分类，以及可选的桶和储罐展示。不用于普通物品贴图或无关方块。
---

# SkyBlueTech Fluid

## Material-only rendering (2026-10-24)

The user retired runtime RGBA tinting. This section supersedes older tint-based
registration examples below. RGBA is an **offline baking input only**:
`out[channel] = base[channel] * rgba[channel] // 255` for all four channels of
every frame. Generate per-fluid PNGs under
`resource_pack/textures/fluid/baked/<namespace>.<name>/`, register unique terrain
keys (`<namespace>:baked_<name>_static` / `_flowing`), and copy the base atlas
and flipbook settings, including `quad`, `replicate`, and timing.

Keep the `netease:liquid` component but omit `liquid_color` (its documented
default is opaque white). Both world blocks reference baked textures.
UI uses `FLUID_TEXTURES` containing `BasicFluidTexture` instances directly, and
`RegisterFluidTexture(fluid_id, basic_texture)` stores the instance without a
wrapper. `GetFluidTexture(fluid_id)` returns it directly. The `FluidTexture`
wrapper class has been removed. RGB/alpha arguments and runtime
tinting are no longer supported. `BasicFluidTexture` carries only the baked
path, frame count and timing. New tank textures crop the baked first frame
without multiplying again. Existing tank PNGs already contain their tint.

Use the updated `dev_tools/create_fluid/create_fluid.md` and creation tool for
the complete current workflow. Its `--rgba` option is only for offline baking.
The migration manifest `dev_tools/create_fluid/baked_textures.json` records
original base paths/colors; `bake_textures.py <mod path>` regenerates those PNGs.
Preserve intentional or pre-existing differences between world source,
flowing, UI and tank appearances unless explicitly asked to harmonize them.

Create a fluid as one identifier used consistently across block definitions, the fluid system, and every presentation surface that the requested feature exposes. Inspect the closest fluid with the same physical class before editing. `sulfuric_acid` is the reference for an acid using the shared water texture; `distilled_water` is the reference for a bucket-enabled liquid.

## Gather The Required Decisions

Before creating the fluid, establish these three choices. Ask only for missing choices; an explicit request to choose a color such as "淡蓝色即可" authorizes selecting and reporting concrete RGBA channels without another confirmation.

1. **Which shared base material should the fluid use?** Offer the existing `BasicFluidTexture` choices (for example `WATER`, `LAVA`, `MOLTEN_METAL`, `AIR`) and show each path/animation setting from `common/define/fluids/texture.py`; never silently choose a material.
2. **What RGBA color should be used?** Record four integer channels in `0..255` as offline baking input. Use the same RGBA for source, flowing and machine UI unless the user requests differences. Do not infer a color from the fluid name without authorization to choose.
3. **Which `SimpleEnum` group should contain the fluid?** Ask the user to choose the existing semantic group, such as `CommonLiquid`, `CommonGas`, `Acid`, `HotFluid`, or `ExtremeHotFluid`; explain that this choice controls pipe compatibility through the class hierarchy. Do not create or select a group by guesswork.

After those answers are confirmed, establish the remaining inputs:

- Stable fluid ID, e.g. `skybluetech:<name>`, and the corresponding flowing ID `skybluetech:flowing_<name>`.
- Chinese display names for both block IDs, and for the bucket if one is requested.
- World behavior: bucket pickup, boat buoyancy, `mob_effects`, `remove_effects`, flowing `spread_delay`, and `spread_range`. Start from the closest sibling; do not invent component values.
- Required exposure: world placement only, a machine recipe/pipe route, a bucket, machine UI, and/or tank model. These are separate registrations.

## Registration Flow

### 1. World Liquid

Create both files under `behavior_pack/netease_blocks/liquid/`:

- `skybluetech_<name>.json`: `base_block` is `liquid` and the identifier is the stable fluid ID.
- `skybluetech_flowing_<name>.json`: `base_block` is `flowing_liquid` and the identifier is the flowing ID.

Keep `netease:liquid` but never write `liquid_color` or another runtime RGBA tint. Bake every pixel of every base-material frame with `out[channel] = base[channel] * rgba[channel] // 255`, including alpha, into per-fluid PNGs. Put flowing properties in the flowing definition and mirror source-only behavior such as `bucket_name` or `can_float_boat` where the close reference does. The flowing file must not be omitted.

For generic water-textured fluids, add entries for both IDs in `resource_pack/blocks.json` with `blockshape: "water"`:

- Source: `down` and `up` use `<namespace>:baked_<name>_static`; `side` uses `<namespace>:baked_<name>_flowing`.
- Flowing: `down` uses the baked static texture; `side` and `up` use the baked flowing texture.

Register those unique keys in `resource_pack/textures/terrain_texture.json`, pointing at `textures/fluid/baked/<namespace>.<name>/`. Copy base atlas and flipbook settings. For a single-material gas, both blocks can use the baked static key. AIR uses `textures/fluid/gas_static` (32 frames, 2 ticks/frame); ensure this exact base is registered rather than silently substituting `textures/fluid/gas`.

### 2. Fluid-System Type And UI

Add the stable ID to the appropriate class in `behavior_pack/skybluetech_scripts/skybluetech/common/define/id_enum/fluids.py`. The inheritance hierarchy is functional: for example, `Acid` is accepted by the acidproof pipe but not by the ordinary bronze pipe. Only the stable ID belongs here, never `flowing_<name>`.

Add a matching `BasicFluidTexture` entry to `FLUID_TEXTURES` in `common/define/fluids/texture.py`:

```python
fluids.<Class>.<NAME>: BasicFluidTexture("textures/fluid/baked/skybluetech.<name>/static", 32, 2),
```

This controls the fluid bars in machine UI. `BasicFluidTexture` defines the baked bitmap and flipbook timing; use the actual base frame count and timing. No runtime tint or wrapper class is used.

There is no separate central fluid registry. Recipes and machine behavior consume the stable ID directly from their relevant files under `common/machinery_def/`; add production or consumption routes only when the feature requires them.

### 3. Optional Bucket

When the fluid must be carried by a player or transferred through machine bucket interaction:

- Create `behavior_pack/netease_items_beh/buckets/skybluetech_<name>_bucket.json` using a nearby bucket pattern. It must either be a game bucket (`custom_item_type: "bucket"`) or carry the `skybluetech:liquid_bucket` tag so `fluid_container.py` accepts it.
- Create `resource_pack/netease_items_res/skybluetech_<name>_bucket.json` whose icon identifier is the same bucket ID.
- Add the icon key to `resource_pack/textures/item_texture.json`, provide the referenced PNG, and add the bucket localization.
- Add `bucket_name` to the liquid block only when in-world pickup/placement through the engine is intended, and use the same bucket ID in source and flowing definitions when the sibling does. A bucket item by itself is enough for the mod's machine suffix mapping (`<fluid_id>_bucket`); it does not prove the liquid block has engine bucket behavior. Existing sulfuric acid is a legacy example of that distinction, so verify the requested behavior in game.

The bucket icon is a template recolour, not a per-fluid drawing. Every bucket
icon in the pack is byte-identical outside a fixed 24-pixel trapezoid (rows 3-5
of the 16x16 icon: `x 4..11`, `x 3..12`, `x 5..10`); only those pixels carry the
fluid colour. Copy the closest bucket icon, repaint those 24 pixels with the
target colour while keeping the template's relative shading, then flip the whole
icon vertically for a gas - `water_vapor_bucket.png` is exactly a vertically
flipped `distilled_water_bucket.png`.

### 4. Tank Model Uses Block Textures

Current `client/utils/fluid_model.py` uses `GetFluidTexturePath()` to read the source block's top-face texture via `GetBlockTextures(fluid_id)`. Tanks reuse the baked block texture. The following legacy path is no longer loaded:

```text
textures/fluid_models/<fluid_id with ':' replaced by '.'>.png
```

Do not create `resource_pack/textures/fluid_models/` or separate first-frame PNGs. Register the actual block top texture in `client/utils/fluid_texture_frames.py` with its frame count and frames per second matching the flipbook.

The creation script still contains the legacy tank-generation step: always pass `--no-tank`. This skips unused assets without disabling in-game tank rendering.

## Localization And Consistency Audit

Add `tile.skybluetech:<name>.name` and `tile.skybluetech:flowing_<name>.name` to `resource_pack/texts/zh_CN.lang`, despite their `category: "none"`. Add the bucket line when applicable.

Before finishing, search the stable ID, flowing ID, and bucket ID. Confirm these invariants:

- Every ID has the expected `skybluetech:` namespace; the fluid enum and all machine recipes use only the stable ID.
- Source, flowing, and UI baked textures have the intended colors and alpha. Review all three explicitly because they are independent render paths.
- Both `blocks.json` entries use the intended source/flow face layout and every referenced terrain texture key exists.
- The selected enum class produces the requested pipe compatibility in `server/transmitters/pipe/define.py`.
- Requested bucket, icon, localization, and tank-model assets all resolve at their exact ID-derived paths.
- New or changed JSON parses with the standard-library `json` parser, and `git diff --check` is clean.

Do not run or compile the mod Python outside the game. Validate the finished pack in the NetEase/Minecraft client: place and spread the liquid, check its tint and transparency, transfer it through the intended pipe, show it in a machine UI and tank when applicable, and test bucket pickup/transfer if that surface was requested. Do not run `pack_addon.py` unless explicitly requested because it refreshes manifest UUIDs.

## Automated Creation Script

`<mod root>/dev_tools/create_fluid/create_fluid.py` (Python 3, lives outside the
two packs so it is never packaged) performs the whole flow above in one shot:

```bash
python dev_tools/create_fluid/create_fluid.py <mod path> --id <namespace:fluid_name> --rgba R,G,B,A \
    --material <basic texture path> --name <display name> --no-tank [--gas]
```

It locates the two packs by the `entities` / `entity` marker, then writes the
world-liquid pair, `blocks.json`, `fluids.py`, `texture.py`, the bucket item
with its icon and creative-group entry, and `zh_CN.lang`. Add the client frame metadata separately. All
edits are minimal text insertions, so re-runs never duplicate entries. Flags:
`--dry-run`, `--group <Class>` (defaults to `CommonGas` for `--gas`, otherwise
`CommonLiquid`), `--no-bucket`, `--no-tank`, `--boat`, `--spread-delay`,
`--spread-range`, `--frames`, `--ticks-per-frame`, `--bucket-template`,
`--force`.

It does not add machine recipes or pipe routes, and it requires the base
material to be already registered in `resource_pack/textures/terrain_texture.json`.

## Current Sulfuric-Acid Audit Note

`skybluetech:sulfuric_acid` has `(255, 216, 216, 128)` baked into its source-block and UI textures from `WATER`. Its flowing textures were baked with alpha `64`; this preserves the pre-migration difference. Tanks use its source-block top texture, not a separate `fluid_models` asset.
