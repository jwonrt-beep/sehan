# viewer.py – 3D 용접 로봇 실시간 뷰어 (moderngl + pyglet)

"""Main entry point for the 3D welding robot viewer.
- Uses moderngl for high‑performance OpenGL rendering.
- Uses pyglet for window management and input handling.
- Loads configuration from config.yaml.
- Dynamically animates robot arm based on a simple sinusoidal motion.
"""

import os
import sys
import numpy as np
import time
import math
import pyglet
from pyglet.window import key
from pyglet import gl
import moderngl
from pathlib import Path

# Ensure the project root is in sys.path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Import the Robot class we will define in robot.py
from robot import Robot

# ---------------------------------------------------------------------------
# Pyglet window subclass that holds a moderngl context
# ---------------------------------------------------------------------------
class GLWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a moderngl context bound to the pyglet window's OpenGL context
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        # Load the robot model (detailed geometry is generated inside Robot)
        self.robot = Robot()
        self.robot.build_parts()
        
        # Keyboard handler for teach pendant controls
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        
        print("\n" + "="*50)
        print("=== 로봇 펜던트 조작기 (Teach Pendant) ===")
        print("1축 (Base)    : Q (좌) / A (우)")
        print("2축 (Shoulder): W (상) / S (하)")
        print("3축 (Elbow)   : E (상) / D (하)")
        print("4축 (Twist 1) : R (좌) / F (우)")
        print("5축 (Bend)    : T (상) / G (하)")
        print("6축 (Twist 2) : Y (좌) / H (우)")
        print("="*50 + "\n")

        # Simple shader program (vertex + fragment) – uses basic lighting
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 model;
                uniform mat4 view;
                uniform mat4 proj;
                in vec3 in_position;
                in vec3 in_normal;
                out vec3 v_normal;
                void main() {
                    gl_Position = proj * view * model * vec4(in_position, 1.0);
                    v_normal = mat3(transpose(inverse(model))) * in_normal;
                }
            ''',
            fragment_shader='''
                #version 330
                uniform vec3 color;
                in vec3 v_normal;
                out vec4 f_color;
                void main() {
                    vec3 light_dir = normalize(vec3(0.5, 1.0, 0.8));
                    float diff = max(dot(normalize(v_normal), light_dir), 0.0);
                    float ambient = 0.3;
                    f_color = vec4(color * (diff * 0.7 + ambient), 1.0);
                }
            ''',
        )

        # Create vertex buffers for each robot part (simple dict of VAOs)
        self.vaos = {}
        for name, mesh in self.robot.parts.items():
            vbo = self.ctx.buffer(mesh['vertices'].astype('f4').tobytes())
            nbo = self.ctx.buffer(mesh['normals'].astype('f4').tobytes())
            ibo = self.ctx.buffer(mesh['indices'].astype('i4').tobytes())
            vao_content = [
                (vbo, '3f', 'in_position'),
                (nbo, '3f', 'in_normal'),
            ]
            self.vaos[name] = self.ctx.vertex_array(self.prog, vao_content, ibo)

        # Camera parameters (simple orbit) - adjusted for a wider view of the cell
        self.distance = 18.0
        self.azimuth = math.radians(45)
        self.elevation = math.radians(40)
        self.last_mouse = None

        # Schedule the update loop at 60 FPS
        pyglet.clock.schedule_interval(lambda dt: None, 1/60.0)

    # ---------------------------------------------------------------------
    # Input handling – mouse drag rotates camera, scroll zooms
    # ---------------------------------------------------------------------
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            self.azimuth += math.radians(dx * 0.4)
            self.elevation += math.radians(-dy * 0.4)
            self.elevation = max(math.radians(-85), min(math.radians(85), self.elevation))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        factor = 0.9 ** scroll_y
        self.distance = max(1.0, min(80.0, self.distance * factor))

    # ---------------------------------------------------------------------
    # Main update – animates robot joints and redraws
    # ---------------------------------------------------------------------
    def on_draw(self):
        # Handle keyboard input for robot joints (Teach Pendant Simulation)
        speed = 0.025
        if self.keys[key.Q]: self.robot.joints[0] += speed
        if self.keys[key.A]: self.robot.joints[0] -= speed
        if self.keys[key.W]: self.robot.joints[1] += speed
        if self.keys[key.S]: self.robot.joints[1] -= speed
        if self.keys[key.E]: self.robot.joints[2] += speed
        if self.keys[key.D]: self.robot.joints[2] -= speed
        if self.keys[key.R]: self.robot.joints[3] += speed
        if self.keys[key.F]: self.robot.joints[3] -= speed
        if self.keys[key.T]: self.robot.joints[4] += speed
        if self.keys[key.G]: self.robot.joints[4] -= speed
        if self.keys[key.Y]: self.robot.joints[5] += speed
        if self.keys[key.H]: self.robot.joints[5] -= speed
        
        # Enforce physical joint limits (TM-1400 specs)
        limits = [
            (-math.radians(170), math.radians(170)), # J1 Base
            (-math.radians(90), math.radians(155)),  # J2 Shoulder
            (-math.radians(170), math.radians(160)), # J3 Elbow
            (-math.radians(190), math.radians(190)), # J4 Twist 1
            (-math.radians(135), math.radians(135)), # J5 Bend
            (-math.radians(360), math.radians(360))  # J6 Twist 2
        ]
        for i in range(6):
            self.robot.joints[i] = max(limits[i][0], min(limits[i][1], self.robot.joints[i]))
            
        self.robot.set_joint_angles(*self.robot.joints)
        self.clear()
        self.render()

    # ---------------------------------------------------------------------
    # Rendering routine – sets up view/proj matrices and draws each part
    # ---------------------------------------------------------------------
    def render(self):
        # Build view matrix (lookAt)
        cam_x = self.distance * math.cos(self.elevation) * math.sin(self.azimuth)
        cam_y = self.distance * math.sin(self.elevation) + 1.5
        cam_z = self.distance * math.cos(self.elevation) * math.cos(self.azimuth)
        view = self.look_at(np.array([cam_x, cam_y, cam_z]), np.array([0.0, 1.5, 0.0]), np.array([0.0, 1.0, 0.0]))
        # Perspective projection
        aspect = self.width / float(self.height)
        proj = self.perspective_matrix(fov=45.0, aspect=aspect, near=0.1, far=100.0)

        # Draw each robot part with its own model matrix
        for part_name, mesh in self.robot.parts.items():
            model = self.robot.get_part_matrix(part_name)
            color = np.array(mesh.get('color', [0.8, 0.8, 0.8]), dtype='f4')
            
            # model is row-major (translation in row 3). OpenGL expects column-major.
            # .tobytes() outputs C-order (row-by-row), which OpenGL reads as column-by-column.
            # So OpenGL receives model.T, which is the correct column-major matrix!
            self.prog['model'].write(model.astype('f4').tobytes())
            
            # view and proj are constructed as EXACT mathematical matrices (translation in col 3).
            # We must use .T.astype('f4').tobytes() to output their columns first,
            # so OpenGL receives the exact matrix.
            self.prog['view'].write(view.T.astype('f4').tobytes())
            self.prog['proj'].write(proj.T.astype('f4').tobytes())
            
            self.prog['color'].write(color.tobytes())
            self.vaos[part_name].render()

    # ---------------------------------------------------------------------
    # Helper matrix utilities (right‑handed, column‑major for moderngl)
    # ---------------------------------------------------------------------
    def perspective_matrix(self, fov, aspect, near, far):
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        return np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, -(far + near) / (far - near), -(2 * far * near) / (far - near)],
            [0, 0, -1, 0]
        ], dtype='f4')

    def look_at(self, eye, target, up):
        f = (target - eye)
        f = f / np.linalg.norm(f)
        u = up / np.linalg.norm(up)
        s = np.cross(f, u)
        s = s / np.linalg.norm(s)
        u = np.cross(s, f)
        result = np.identity(4, dtype='f4')
        result[0, :3] = s
        result[1, :3] = u
        result[2, :3] = -f
        result[:3, 3] = -np.dot(result[:3, :3], eye)
        return result

    def clear(self):
        # Teal background to match Panasonic simulation reference
        self.ctx.clear(0.12, 0.53, 0.53, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    window = GLWindow(width=1280, height=720, caption="3D 용접 로봇 Viewer", resizable=True)
    pyglet.app.run()
