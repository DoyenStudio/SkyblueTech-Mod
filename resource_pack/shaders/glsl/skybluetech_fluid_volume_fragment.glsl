// __multiversion__
precision highp float;

#include "fragmentVersionCentroidUV.h"
#include "uniformEntityConstants.h"
#include "uniformPerFrameConstants.h"
#include "uniformShaderConstants.h"

LAYOUT_BINDING(0) uniform sampler2D TEXTURE_0;
// x: frame count; y: frames per second. x == 0 means unknown texture layout.
uniform vec4 EXTRA_ACTOR_UNIFORM1;
// rgb: multiplier for explicitly registered grayscale sources; w: tint enabled.
// A zero/unset uniform keeps existing baked textures unchanged.
uniform vec4 EXTRA_ACTOR_UNIFORM2;
varying vec4 fogColor;

void main() {
    float frameCount = EXTRA_ACTOR_UNIFORM1.x;
    float frameRate = max(EXTRA_ACTOR_UNIFORM1.y, 0.0);
    if (frameCount < 1.0) {
#if __VERSION__ >= 300
        ivec2 texSize = textureSize(TEXTURE_0, 0);
        frameCount = max(1.0, floor(float(texSize.y) / float(texSize.x)));
        frameRate = frameCount > 1.0 ? 10.0 : 0.0;
#else
        // No textureSize on GLES2: an unknown path is static, never assumed 32-frame.
        frameCount = 1.0;
        frameRate = 0.0;
#endif
    }
    frameCount = max(1.0, floor(frameCount));
    // Half playback speed doubles the original animation cycle duration.
    float frameTime = mod(TIME * frameRate * 0.5, frameCount);
    float frame = floor(frameTime);
    // Ten steps per source frame: A, then nine blends (10% through 90%).
    // B starts the next stage.
    float blendWeight = floor(fract(frameTime) * 10.0) / 10.0;
    // Tile each square frame before selecting it in the vertical strip.
    vec2 tileUV = fract(uv);
    vec2 animUV = vec2(tileUV.x, (tileUV.y + frame) / frameCount);
    vec4 color = texture2D(TEXTURE_0, animUV);
    if (frameCount > 1.0 && frameRate > 0.0 && blendWeight > 0.0) {
        float nextFrame = mod(frame + 1.0, frameCount);
        vec2 nextUV = vec2(tileUV.x, (tileUV.y + nextFrame) / frameCount);
        color = mix(color, texture2D(TEXTURE_0, nextUV), blendWeight);
    }
    color.rgb *= mix(vec3(1.0), EXTRA_ACTOR_UNIFORM2.rgb, EXTRA_ACTOR_UNIFORM2.w);
    // Blend texture alpha with RGB. Full-bright avoids black closed vessels.
    color.rgb = mix(color.rgb, fogColor.rgb, fogColor.a);
    gl_FragColor = color;
}
