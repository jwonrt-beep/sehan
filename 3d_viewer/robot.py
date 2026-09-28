import numpy as np
import math

def create_cylinder(radius: float, height: float, segments: int = 16):
    verts, norms, indices = [], [], []
    for i in range(segments + 1):
        theta = 2 * math.pi * i / segments
        x, y = radius * math.cos(theta), radius * math.sin(theta)
        verts.extend([[x, y, 0], [x, y, height]])
        norms.extend([[math.cos(theta), math.sin(theta), 0]] * 2)
    verts.extend([[0, 0, 0], [0, 0, height]])
    norms.extend([[0, 0, -1], [0, 0, 1]])
    bottom_center, top_center = len(verts) - 2, len(verts) - 1
    
    for i in range(segments):
        b0 = i * 2
        t0 = b0 + 1
        b1 = ((i + 1) % segments) * 2
        t1 = b1 + 1
        # Side triangles (CCW)
        indices.extend([[b0, b1, t1], [b0, t1, t0]])
        # Bottom triangle (CCW from below)
        indices.append([bottom_center, b1, b0])
        # Top triangle (CCW from above)
        indices.append([top_center, t0, t1])
        
    return np.array(verts, dtype='f4'), np.array(norms, dtype='f4'), np.array(indices, dtype='i4')

def create_box(width: float, height: float, depth: float):
    w, h, d = width / 2, height / 2, depth / 2
    verts, norms, indices = [], [], []
    
    faces = [
        # Z- (Back): CCW from -Z
        ([[w,-h,-d], [-w,-h,-d], [-w,h,-d], [w,h,-d]], [0,0,-1]),
        # X+ (Right): CCW from +X
        ([[w,-h,-d], [w,h,-d], [w,h,d], [w,-h,d]], [1,0,0]),
        # Z+ (Front): CCW from +Z
        ([[-w,-h,d], [w,-h,d], [w,h,d], [-w,h,d]], [0,0,1]),
        # X- (Left): CCW from -X
        ([[-w,-h,d], [-w,h,d], [-w,h,-d], [-w,-h,-d]], [-1,0,0]),
        # Y- (Bottom): CCW from -Y
        ([[-w,-h,-d], [w,-h,-d], [w,-h,d], [-w,-h,d]], [0,-1,0]),
        # Y+ (Top): CCW from +Y
        ([[-w,h,d], [w,h,d], [w,h,-d], [-w,h,-d]], [0,1,0])
    ]
    
    for idx, (f_verts, n) in enumerate(faces):
        verts.extend(f_verts)
        norms.extend([n]*4)
        b = idx * 4
        indices.extend([[b, b+1, b+2], [b, b+2, b+3]])
        
    return np.array(verts, dtype='f4'), np.array(norms, dtype='f4'), np.array(indices, dtype='i4')

def create_cone(radius: float, height: float, segments: int = 16):
    verts, norms, indices = [], [], []
    for i in range(segments):
        theta = 2 * math.pi * i / segments
        x, y = radius * math.cos(theta), radius * math.sin(theta)
        verts.append([x, y, 0])
        norm = np.array([x, y, radius / height])
        norms.append((norm / np.linalg.norm(norm)).tolist())
    verts.append([0, 0, height])
    norms.append([0, 0, 1])
    tip_index = len(verts) - 1
    
    for i in range(segments):
        indices.append([i, (i + 1) % segments, tip_index])
        
    centre = len(verts)
    verts.append([0, 0, 0])
    norms.append([0, 0, -1])
    for i in range(segments):
        indices.append([centre, i, (i + 1) % segments])
        
    return np.array(verts, dtype='f4'), np.array(norms, dtype='f4'), np.array(indices, dtype='i4')

def create_sphere(radius: float, rings: int = 16, sectors: int = 16):
    verts, norms, indices = [], [], []
    for r in range(rings + 1):
        v = r / rings
        phi = v * math.pi
        for s in range(sectors + 1):
            u = s / sectors
            theta = u * 2 * math.pi
            x = math.cos(theta) * math.sin(phi)
            y = math.cos(phi)
            z = math.sin(theta) * math.sin(phi)
            verts.append([radius * x, radius * y, radius * z])
            norms.append([x, y, z])
            
    for r in range(rings):
        for s in range(sectors):
            first = (r * (sectors + 1)) + s
            second = first + sectors + 1
            indices.append([first, second, first + 1])
            indices.append([second, second + 1, first + 1])
            
    return np.array(verts, dtype='f4'), np.array(norms, dtype='f4'), np.array(indices, dtype='i4')

class Robot:
    def __init__(self, detail: str = "detailed"):
        self.detail = detail
        self.parts = {}
        self.joints = [0.0] * 6
        self._matrices = {}

    def build_parts(self):
        # COLORS
        C_WHITE = [0.9, 0.9, 0.95]
        C_DARK = [0.2, 0.2, 0.2]
        C_JOINT = [0.15, 0.15, 0.15]
        C_PLATFORM = [0.6, 0.6, 0.6]
        C_TABLE = [0.2, 0.5, 0.3]
        C_CABINET = [0.4, 0.4, 0.4]
        C_ROBOT = [0.95, 0.75, 0.1] # Yellow robot
        C_DARK = [0.2, 0.2, 0.2]
        C_GAS = [0.8, 0.7, 0.1]
        C_TORCH = [0.1, 0.1, 0.1]

        # --- ENVIRONMENT ---
        v, n, i = create_box(6.0, 0.2, 6.0)
        self.parts["platform"] = {"vertices": v, "normals": n, "indices": i, "color": C_PLATFORM}
        
        v, n, i = create_box(1.5, 0.8, 1.5)
        trans = self._translate(1.5, 0.4, -0.5)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["table"] = {"vertices": v, "normals": n, "indices": i, "color": C_TABLE}
        
        v, n, i = create_box(0.5, 0.5, 0.5)
        trans = self._translate(1.5, 1.05, -0.5)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["workpiece"] = {"vertices": v, "normals": n, "indices": i, "color": [0.4, 0.8, 0.8]}

        # --- ROBOT KINEMATICS & PROPORTIONS (White TM-1400 Style) ---
        C_WHITE = [0.95, 0.95, 0.95]
        C_DARK = [0.25, 0.25, 0.25]
        
        # 1. Base Pedestal (fixed to origin)
        v, n, i = create_cylinder(0.2, 0.22, 24)
        trans = self._rotate_x(-math.pi/2)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["pedestal"] = {"vertices": v, "normals": n, "indices": i, "color": C_DARK}

        # 2. Link 1 (Swivel)
        v, n, i = create_box(0.25, 0.28, 0.25)
        trans = self._translate(0, 0.14, 0)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["link1"] = {"vertices": v, "normals": n, "indices": i, "color": C_WHITE}
        
        # Joint 2 Cylinder (Rotates around Z)
        v, n, i = create_cylinder(0.14, 0.26, 24)
        trans = self._translate(0, 0, -0.13)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["joint2"] = {"vertices": v, "normals": n, "indices": i, "color": C_DARK}

        # 3. Link 2 (Lower Arm)
        v, n, i = create_box(0.2, 0.7, 0.2)
        trans = self._translate(0, 0.3, 0)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["link2"] = {"vertices": v, "normals": n, "indices": i, "color": C_WHITE}
        
        # Joint 3 Cylinder (Rotates around Z)
        v, n, i = create_cylinder(0.12, 0.22, 24)
        trans = self._translate(0, 0, -0.11)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["joint3"] = {"vertices": v, "normals": n, "indices": i, "color": C_DARK}

        # 4. Link 3 (Upper Arm Base)
        v, n, i = create_box(0.65, 0.18, 0.18)
        trans = self._translate(0.2, 0, 0)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["link3"] = {"vertices": v, "normals": n, "indices": i, "color": C_WHITE}
        
        # Joint 4 Cylinder (Rotates around X)
        v, n, i = create_cylinder(0.1, 0.1, 24)
        trans = self._rotate_y(math.pi/2) @ self._translate(-0.05, 0, 0)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["joint4"] = {"vertices": v, "normals": n, "indices": i, "color": C_DARK}

        # 5. Link 4 (Upper Arm Twist)
        v, n, i = create_box(0.4, 0.15, 0.15)
        trans = self._translate(0.2, 0, 0)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["link4"] = {"vertices": v, "normals": n, "indices": i, "color": C_WHITE}
        
        # Joint 5 Cylinder (Rotates around Z)
        v, n, i = create_cylinder(0.08, 0.16, 24)
        trans = self._translate(0, 0, -0.08)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["joint5"] = {"vertices": v, "normals": n, "indices": i, "color": C_DARK}

        # 6. Link 5 (Wrist Bend)
        v, n, i = create_box(0.15, 0.12, 0.12)
        trans = self._translate(0.075, 0, 0)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["link5"] = {"vertices": v, "normals": n, "indices": i, "color": C_WHITE}
        
        # Joint 6 Cylinder (Rotates around X)
        v, n, i = create_cylinder(0.07, 0.05, 24)
        trans = self._rotate_y(math.pi/2) @ self._translate(0, 0, 0)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["joint6"] = {"vertices": v, "normals": n, "indices": i, "color": C_DARK}

        # 7. Link 6 (Flange)
        v, n, i = create_cylinder(0.06, 0.02, 24)
        trans = self._rotate_y(math.pi/2) @ self._translate(0.05, 0, 0)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["link6"] = {"vertices": v, "normals": n, "indices": i, "color": C_DARK}

        # 8. Torch
        v, n, i = create_cone(0.03, 0.3, 16)
        trans = self._translate(0.07, 0, 0) @ self._rotate_z(-math.pi/4) @ self._rotate_y(math.pi/2)
        v = v @ trans[:3, :3] + trans[3, :3]
        n = n @ trans[:3, :3]
        self.parts["torch"] = {"vertices": v, "normals": n, "indices": i, "color": [0.6, 0.6, 0.6]}

        for key in self.parts:
            self._matrices[key] = np.identity(4, dtype='f4')

    def set_joint_angles(self, j1, j2, j3, j4, j5, j6):
        self._matrices["base"] = np.identity(4, dtype='f4')
        self._matrices["platform"] = np.identity(4, dtype='f4')
        self._matrices["table"] = np.identity(4, dtype='f4')
        self._matrices["workpiece"] = np.identity(4, dtype='f4')
        self._matrices["pedestal"] = np.identity(4, dtype='f4')
        self._matrices["torch"] = np.identity(4, dtype='f4')
        self._matrices["joint2"] = np.identity(4, dtype='f4')
        self._matrices["joint3"] = np.identity(4, dtype='f4')
        self._matrices["joint4"] = np.identity(4, dtype='f4')
        self._matrices["joint5"] = np.identity(4, dtype='f4')
        self._matrices["joint6"] = np.identity(4, dtype='f4')

        # Link 1 rotates around Y axis
        trans1 = self._translate(0, 0.22, 0)
        rot1 = self._rotate_y(j1)
        self._matrices["link1"] = rot1 @ trans1 @ self._matrices["pedestal"]

        # Link 2 rotates around Z axis
        trans2 = self._translate(0, 0.2, 0)
        rot2 = self._rotate_z(j2)
        self._matrices["link2"] = rot2 @ trans2 @ self._matrices["link1"]
        self._matrices["joint2"] = self._matrices["link2"]

        # Link 3 rotates around Z axis
        trans3 = self._translate(0, 0.6, 0)
        rot3 = self._rotate_z(j3)
        self._matrices["link3"] = rot3 @ trans3 @ self._matrices["link2"]
        self._matrices["joint3"] = self._matrices["link3"]

        # Link 4 rotates around X axis (twist)
        trans4 = self._translate(0.5, 0, 0)
        rot4 = self._rotate_x(j4)
        self._matrices["link4"] = rot4 @ trans4 @ self._matrices["link3"]
        self._matrices["joint4"] = self._matrices["link4"]

        # Link 5 rotates around Z axis
        trans5 = self._translate(0.4, 0, 0)
        rot5 = self._rotate_z(j5)
        self._matrices["link5"] = rot5 @ trans5 @ self._matrices["link4"]
        self._matrices["joint5"] = self._matrices["link5"]

        # Link 6 rotates around X axis (twist)
        trans6 = self._translate(0.15, 0, 0)
        rot6 = self._rotate_x(j6)
        self._matrices["link6"] = rot6 @ trans6 @ self._matrices["link5"]
        self._matrices["joint6"] = self._matrices["link6"]
        self._matrices["torch"] = self._matrices["link6"]

        # Torch is attached to Link 6
        self._matrices["torch"] = self._matrices["link6"]

    @staticmethod
    def _translate(x, y, z):
        m = np.identity(4, dtype='f4')
        m[3, :3] = [x, y, z]
        return m

    @staticmethod
    def _rotate_x(rad):
        c, s = math.cos(rad), math.sin(rad)
        m = np.identity(4, dtype='f4')
        m[1, 1], m[1, 2] = c, s
        m[2, 1], m[2, 2] = -s, c
        return m

    @staticmethod
    def _rotate_y(rad):
        c, s = math.cos(rad), math.sin(rad)
        m = np.identity(4, dtype='f4')
        m[0, 0], m[0, 2] = c, -s
        m[2, 0], m[2, 2] = s, c
        return m

    @staticmethod
    def _rotate_z(rad):
        c, s = math.cos(rad), math.sin(rad)
        m = np.identity(4, dtype='f4')
        m[0, 0], m[0, 1] = c, s
        m[1, 0], m[1, 1] = -s, c
        return m

    def get_part_matrix(self, part_name: str) -> np.ndarray:
        return self._matrices.get(part_name, np.identity(4, dtype='f4'))
