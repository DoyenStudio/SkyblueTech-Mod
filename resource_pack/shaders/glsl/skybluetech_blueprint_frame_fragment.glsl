// __multiversion__
precision highp float;
#include "fragmentVersionCentroidUV.h"

varying vec2 faceSize;
varying float overLimit;

void main() {
    vec2 edge = min(uv, 1.0 - uv) * faceSize;
    float alpha = 1.0 - smoothstep(0.078, 0.095, min(edge.x, edge.y));
    if (alpha < 0.01) discard;
    gl_FragColor = vec4(mix(vec3(0.08, 0.52, 1.0), vec3(1.0, 0.1, 0.08), overLimit), alpha);
}
