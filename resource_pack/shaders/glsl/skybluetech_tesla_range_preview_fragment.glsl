// __multiversion__
precision highp float;

#include "fragmentVersionCentroidUV.h"

varying float rangeFrameWidthUV;

void main() {
    // All six carrier faces have UV 0..1. Measure in face UV rather than raw
    // POSITION, whose model-pixel units are converted by the bone transform.
    vec2 distanceUV = min(uv, vec2(1.0) - uv);
    float edgeDistance = min(distanceUV.x, distanceUV.y);
    float width = max(rangeFrameWidthUV, 0.00001);
    float alpha = 1.0 - smoothstep(width * 0.85, width, edgeDistance);
    if (alpha < 0.01) {
        discard;
    }
    float core = 1.0 - smoothstep(0.0, width * 0.65, edgeDistance);
    vec3 gold = mix(vec3(0.95, 0.48, 0.025), vec3(1.0, 0.82, 0.22), core);
    // Full-bright gold stays readable without sampling the carrier texture.
    gl_FragColor = vec4(gold, alpha);
}
