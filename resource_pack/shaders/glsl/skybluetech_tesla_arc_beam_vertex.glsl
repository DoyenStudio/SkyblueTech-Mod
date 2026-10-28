// __multiversion__
precision highp float;

#include "vertexVersionCentroidUV.h"
#include "uniformWorldConstants.h"
#ifdef USE_SKINNING
#include "uniformAnimationConstants.h"
#endif

attribute vec2 TEXCOORD_0;
#ifdef USE_SKINNING
#ifdef MCPE_PLATFORM_NX
attribute uint BONEID_0;
#else
attribute float BONEID_0;
#endif
#endif

// xyz: world-space endpoint delta; w: half-width in blocks.
uniform vec4 EXTRA_ACTOR_UNIFORM1;
varying float arcFog;
varying float arcCap;

// Actor and bone transforms have orthogonal axes, including BB reflections.
vec3 worldVectorToLocal(vec3 delta, mat4 modelToWorld) {
    return vec3(
        dot(delta, modelToWorld[0].xyz) / max(dot(modelToWorld[0].xyz, modelToWorld[0].xyz), 0.000001),
        dot(delta, modelToWorld[1].xyz) / max(dot(modelToWorld[1].xyz, modelToWorld[1].xyz), 0.000001),
        dot(delta, modelToWorld[2].xyz) / max(dot(modelToWorld[2].xyz, modelToWorld[2].xyz), 0.000001)
    );
}

void main() {
    MAT4 boneMat = mat4(1.0);
#ifdef USE_SKINNING
#ifdef NETEASE_SKINNING
    boneMat = GetBoneMatForNetease(int(BONEID_0));
#elif defined(LARGE_VERTEX_SHADER_UNIFORMS)
    boneMat = BONES[int(BONEID_0)];
#else
    boneMat = BONE;
#endif
#endif
    // This BB pass binds WORLDVIEWPROJ correctly. PROJ * WORLDVIEW is not
    // equivalent at runtime, so all extrusion stays in the verified clip space.
    MAT4 modelToClip = WORLDVIEWPROJ * boneMat;
    MAT4 modelToWorld = WORLD * boneMat;
    vec3 delta = worldVectorToLocal(EXTRA_ACTOR_UNIFORM1.xyz, modelToWorld);
    vec4 start = modelToClip * vec4(-0.5 * delta, 1.0);
    vec4 finish = modelToClip * vec4(0.5 * delta, 1.0);

    // Clip-space scale for one world block, independent of model reflection,
    // bone scale, camera rotation and perspective aspect ratio.
    vec4 axisX = modelToClip * vec4(worldVectorToLocal(vec3(1.0, 0.0, 0.0), modelToWorld), 0.0);
    vec4 axisY = modelToClip * vec4(worldVectorToLocal(vec3(0.0, 1.0, 0.0), modelToWorld), 0.0);
    vec4 axisZ = modelToClip * vec4(worldVectorToLocal(vec3(0.0, 0.0, 1.0), modelToWorld), 0.0);
    float scaleX = max(length(vec3(axisX.x, axisY.x, axisZ.x)), 0.00001);
    float scaleY = max(length(vec3(axisX.y, axisY.y, axisZ.y)), 0.00001);
    vec2 metric = vec2(scaleY / scaleX, 1.0);

    float startCap = step(1.5, TEXCOORD_0.x) * (1.0 - step(3.5, TEXCOORD_0.x));
    float endCap = step(3.5, TEXCOORD_0.x);
    float isCap = startCap + endCap;
    uv = TEXCOORD_0 - vec2(2.0 * startCap + 4.0 * endCap, 0.0);

    // Dividing by signed w also handles an endpoint behind the near plane.
    float startW = abs(start.w) < 0.0001 ? (start.w < 0.0 ? -0.0001 : 0.0001) : start.w;
    float endW = abs(finish.w) < 0.0001 ? (finish.w < 0.0 ? -0.0001 : 0.0001) : finish.w;
    vec2 screenDelta = (finish.xy / endW - start.xy / startW) * metric;
    vec2 side = vec2(1.0, 0.0);
    if (length(screenDelta) > 0.00001) {
        side = normalize(vec2(-screenDelta.y, screenDelta.x));
    }
    vec4 position = mix(start, finish, uv.x);
    position.xy += side / metric * max(EXTRA_ACTOR_UNIFORM1.w, 0.01)
        * scaleY * (uv.y * 2.0 - 1.0);
    arcCap = 0.0;
    if (isCap > 0.5) {
        position = mix(start, finish, endCap);
        position.xy += (uv * 2.0 - 1.0) * vec2(scaleX, scaleY) * 0.18;
        arcCap = 2.0;
    }
    gl_Position = position;
    // Machine-limited discharges are emissive; global fog uniforms must not
    // suppress their alpha when the actor pass has no separate fog binding.
    arcFog = 0.0;
}
