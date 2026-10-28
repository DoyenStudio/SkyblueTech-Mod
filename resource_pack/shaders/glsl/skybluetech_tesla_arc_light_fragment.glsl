// __multiversion__
precision highp float;

#include "fragmentVersionCentroidUV.h"
#include "uniformPerFrameConstants.h"

uniform vec4 EXTRA_ACTOR_UNIFORM1;
// x: per-discharge random seed; y: CPU-controlled flash/fade intensity.
uniform vec4 EXTRA_ACTOR_UNIFORM2;
varying float arcFog;
varying float arcCap;

float arcHash(float value) {
    return fract(sin(value * 127.1 + EXTRA_ACTOR_UNIFORM2.x * 17.17) * 43758.5453);
}

float arcNoise(float value, float frame) {
    float cell = floor(value);
    // Linear interpolation preserves the sharp, irregular lightning corners.
    return mix(arcHash(cell + frame * 71.0),
               arcHash(cell + 1.0 + frame * 71.0), fract(value)) * 2.0 - 1.0;
}

float arcPath(float t, float frame) {
    float jitter = min(0.28, length(EXTRA_ACTOR_UNIFORM1.xyz) * 0.08);
    float fractal = 0.55 * arcNoise(t * 9.0, frame)
        + 0.28 * arcNoise(t * 23.0, frame + 3.0)
        + 0.17 * arcNoise(t * 47.0, frame + 7.0);
    // The centreline meets both server-supplied endpoints exactly.
    return fractal * jitter * (4.0 * t * (1.0 - t));
}

vec2 branchLight(float t, float across, float anchor, float span,
                 float offset, float frame) {
    float u = (t - anchor) / span;
    float branchMask = step(0.0, u) * step(u, 1.0);
    float progress = clamp(u, 0.0, 1.0);
    float branchPath = arcPath(anchor, frame) + offset * progress
        + arcNoise(progress * 8.0, frame + anchor * 13.0)
            * 0.045 * sin(progress * 3.141592654);
    float distanceToBranch = abs(across - branchPath);
    float taper = branchMask * (1.0 - smoothstep(0.6, 1.0, progress));
    float core = exp2(-distanceToBranch * distanceToBranch / 0.0001);
    float halo = exp2(-distanceToBranch * distanceToBranch / 0.0025);
    return vec2(core, halo) * taper;
}

void main() {
    float t = clamp(uv.x, 0.0, 1.0);
    float across = (uv.y * 2.0 - 1.0) * max(EXTRA_ACTOR_UNIFORM1.w, 0.01);
    float frame = mod(floor(TIME * 28.0), 64.0);
    float distanceToArc = abs(across - arcPath(t, frame));
    float core = exp2(-distanceToArc * distanceToArc / 0.000225);
    float halo = exp2(-distanceToArc * distanceToArc / 0.0081);

    vec2 branches = branchLight(t, across, 0.28, 0.23, 0.34, frame)
        + branchLight(t, across, 0.63, 0.25, -0.32, frame);
    vec3 blue = vec3(0.08, 0.35, 1.0);
    vec3 emission = vec3(core)
        + blue * (0.5 * halo * (1.0 - 0.85 * core))
        + vec3(0.55, 0.8, 1.0) * branches.x * 0.65
        + blue * branches.y * 0.16;
    if (arcCap > 0.5) {
        vec2 capUV = uv * 2.0 - 1.0;
        vec2 capPos = capUV * 0.18;
        float edgeFade = 1.0 - smoothstep(0.7, 1.0, max(abs(capUV.x), abs(capUV.y)));
        float radius2 = dot(capPos, capPos);
        emission = (vec3(exp2(-radius2 / 0.0004))
            + blue * 0.5 * exp2(-radius2 / 0.0025)) * max(arcCap - 1.0, 0.0) * edgeFade;
    }

    float flicker = 0.82 + 0.18 * arcHash(mod(floor(TIME * 70.0), 128.0) + 719.0);
    float intensity = max(EXTRA_ACTOR_UNIFORM2.y, 0.0) * flicker * (1.0 - arcFog);
    float peak = max(max(emission.r, emission.g), emission.b);
    // SourceAlpha / One: colour is chromaticity and alpha carries energy.
    // Multiplying colour by intensity too would dim the halo twice.
    float alpha = clamp(peak * intensity, 0.0, 1.0);
    // Only actual light contributes depth, never the transparent carrier quad.
    if (alpha < 0.005) {
        discard;
    }
    gl_FragColor = vec4(emission / max(peak, 0.00001), alpha);
}
