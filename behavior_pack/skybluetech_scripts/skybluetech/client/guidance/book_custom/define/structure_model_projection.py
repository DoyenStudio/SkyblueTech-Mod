# coding=utf-8
import math

# 客户端实测：scale=1 时方块边长为 10 个 UI 单位，与物理分辨率无关。
BLOCK_UI_SIZE = 10.0


class StructureModelProjection(object):
    def __init__(self, scale):
        self.scale = scale
        self.pitch = -90.0
        self.yaw = 0.0
        self.positions = []
        self.center = (0.0, 0.0, 0.0)
        self.ray_distance = 1.0

    def set_positions(self, positions):
        self.positions = sorted(positions)
        low = [min(pos[a] for pos in positions) for a in range(3)]
        high = [max(pos[a] for pos in positions) for a in range(3)]
        self.center = tuple((low[a] + high[a]) / 2.0 for a in range(3))
        self.ray_distance = sum(high[a] - low[a] + 1 for a in range(3)) + 1.0

    def _to_model(self, point):
        # 客户端实测：init_rot_y=0 时变换为 Rx(init_rot_x)*Ry(-init_rot_z)，
        # 屏幕投影为 (x, z)，近端在 +y。方块调色板 +x 对应屏幕右侧。
        x, y, z = point
        pitch, yaw = math.radians(self.pitch), math.radians(self.yaw)
        y1 = y * math.cos(pitch) + z * math.sin(pitch)
        z1 = -y * math.sin(pitch) + z * math.cos(pitch)
        return (
            x * math.cos(yaw) + z1 * math.sin(yaw),
            y1,
            -x * math.sin(yaw) + z1 * math.cos(yaw),
        )

    def pick(self, point, origin, size):
        # type: (tuple[float, float], tuple[float, float], tuple[float, float]) -> tuple[int, int, int] | None
        px, py = point[0] - origin[0], point[1] - origin[1]
        if not (0 <= px <= size[0] and 0 <= py <= size[1]):
            return None
        unit = BLOCK_UI_SIZE * self.scale
        relative = self._to_model((
            (px - size[0] / 2.0) / unit,
            self.ray_distance,
            (py - size[1] / 2.0) / unit,
        ))
        ray_origin = tuple(relative[a] + self.center[a] for a in range(3))
        direction = self._to_model((0.0, -1.0, 0.0))
        closest, closest_distance = None, float("inf")
        for pos in self.positions:
            distance = ray_box_distance(ray_origin, direction, pos)
            if distance is not None and distance < closest_distance:
                closest, closest_distance = pos, distance
        return closest


def ray_box_distance(origin, direction, pos):
    # type: (tuple[float, float, float], tuple[float, float, float], tuple[int, int, int]) -> float | None
    near, far = 0.0, float("inf")
    for axis in range(3):
        low, high = pos[axis] - 0.5, pos[axis] + 0.5
        if abs(direction[axis]) < 1e-8:
            if origin[axis] < low or origin[axis] > high:
                return None
            continue
        t1 = (low - origin[axis]) / direction[axis]
        t2 = (high - origin[axis]) / direction[axis]
        near = max(near, min(t1, t2))
        far = min(far, max(t1, t2))
        if near > far:
            return None
    return near
