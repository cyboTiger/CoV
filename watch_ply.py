import pyvista as pv
import numpy as np
import argparse
import os
from vista_plyvis import create_yellow_sphere, create_green_line, create_blue_arrow
import shortuuid

view_pose = []
cur_view_ptr = 0
plotter = pv.Plotter(window_size=[1920, 1080])
def switch_view():
    global cur_view_ptr
    global view_pose
    global plotter
    cur_view_ptr = (cur_view_ptr + 1) % len(view_pose)
    pose = np.loadtxt(view_pose[cur_view_ptr])

    go_to_camera_view(plotter, pose)
    print("Switching to view:", view_pose[cur_view_ptr].split('/')[-1].split('.')[0])

def switch_view_back():
    global cur_view_ptr
    global view_pose
    global plotter
    cur_view_ptr = (cur_view_ptr + len(view_pose) - 1) % len(view_pose)
    pose = np.loadtxt(view_pose[cur_view_ptr])

    go_to_camera_view(plotter, pose)
    print("Switching to view:", view_pose[cur_view_ptr].split('/')[-1].split('.')[0])

# === 移动函数 ===
def move_camera(direction):
    # === 移动步长 ===
    step_size = 0.1

    cam = plotter.camera
    forward = np.array(cam.focal_point) - np.array(cam.position)
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, cam.up)
    right /= np.linalg.norm(right)
    up = np.array(cam.up)

    offset = {
        'a': forward,
        's': -forward,
        'd': -right,
        'f': right,
        'j': up,
        'k': -up
    }.get(direction.lower(), np.zeros(3))

    offset *= step_size
    cam.position = np.array(cam.position) + offset
    cam.focal_point = np.array(cam.focal_point) + offset
    plotter.render()
    plotter.screenshot(f"screenshots/{shortuuid.uuid()}.png")

def rotate_horizontal(angle_deg):
    """
    水平旋转视角（绕相机位置 Y 轴旋转）
    """
    cam = plotter.camera
    pos = np.array(cam.position)
    focal = np.array(cam.focal_point)
    forward = focal - pos

    # 水平旋转：绕 Z 轴旋转 angle_deg 度
    angle_rad = np.radians(angle_deg)
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

    R = np.array([
        [cos_a, sin_a, 0],
        [-sin_a, cos_a, 0],
        [0,  0, 1]
    ])

    new_forward = R @ forward
    cam.focal_point = pos + new_forward
    plotter.render()
    plotter.screenshot(f"screenshots/{shortuuid.uuid()}.png")

# def rotate_vertical(angle_deg):
#     cam = plotter.camera
#     pos = np.array(cam.position)
#     focal = np.array(cam.focal_point)
#     up = np.array(cam.up)
#     forward = focal - pos
#     forward /= np.linalg.norm(forward)

#     right = np.cross(forward, up)
#     right /= np.linalg.norm(right)

#     # 构造旋转矩阵：绕 right 轴旋转 angle_deg
#     angle_rad = np.radians(angle_deg)
#     c, s = np.cos(angle_rad), np.sin(angle_rad)
#     R = np.array([
#         [c + right[0]**2 * (1 - c),       right[0]*right[1]*(1 - c) - right[2]*s, right[0]*right[2]*(1 - c) + right[1]*s],
#         [right[1]*right[0]*(1 - c) + right[2]*s, c + right[1]**2 * (1 - c),       right[1]*right[2]*(1 - c) - right[0]*s],
#         [right[2]*right[0]*(1 - c) - right[1]*s, right[2]*right[1]*(1 - c) + right[0]*s, c + right[2]**2 * (1 - c)]
#     ])

#     new_forward = R @ forward
#     new_up = np.cross(right, forward)
#     new_up /= np.linalg.norm(new_up)

#     cam.focal_point = pos + new_forward
#     cam.up = new_up
#     plotter.render()

def go_to_camera_view(plotter, pose):
    fix_coord = np.diag([1, -1, -1, 1])  # 坐标轴变换
    pose_fixed = pose @ fix_coord 
    position = pose_fixed[:3, 3]

    R = pose_fixed[:3, :3]
    # right = R[:, 0]
    up = R[:, 1]
    forward = R[:, 2]
    direction = -forward  # 相机看向的方向

    # # anchor
    # anchor = create_yellow_sphere(center=position, radius=0.05)
    # plotter.add_mesh(anchor, scalars='Colors', rgb=True)

    # # direction arrow 
    # arrow = create_blue_arrow(start=position, direction=direction)
    # plotter.add_mesh(arrow, scalars='Colors', rgb=True)

    plotter.camera.position = position
    plotter.camera.focal_point = position + direction
    plotter.camera.up = up
    plotter.render()
    plotter.screenshot(f"screenshots/{shortuuid.uuid()}.png")

def main():
    global view_pose
    global plotter
    parser = argparse.ArgumentParser(description="Visualize a PLY file with a given scene id.")
    parser.add_argument("--scene_id", type=str, help="scene id", default='0011_00')
    # parser.add_argument("--frame_id", type=str, help="frame id", default='80')
    args = parser.parse_args()
    args.scene_id = args.scene_id.replace('scene', '')

    ply = f'/Users/zhuruihan/Desktop/llava-3d/scene{args.scene_id}/scans/scene{args.scene_id}/scene{args.scene_id}_vh_clean_2.ply'
    prefix = f'/Users/zhuruihan/Desktop/llava-3d/scene{args.scene_id}/scans/scene{args.scene_id}/pose/'
    view_pose = sorted([prefix + pose_file for pose_file in os.listdir(prefix)], key=lambda x: int(x.split('/')[-1].split('.')[0]))

    mesh = pv.read(ply)
    # 检查是否包含颜色数据
    if 'Colors' not in mesh.point_data:
        if 'RGBA' in mesh.point_data:
            mesh.point_data['Colors'] = mesh.point_data['RGBA']  # 重命名为Colors
        elif 'RGB' in mesh.point_data:
            mesh.point_data['Colors'] = mesh.point_data['RGB']  # 重命名为Colors
            colors = np.zeros((mesh.n_points, 4), dtype=np.uint8)
            colors[:, :3] = mesh.point_data['RGB'][:, :]  # G通道
            colors[:, 3] = 255  # A通道设为255（完全不透明）
            mesh.point_data['Colors'] = colors
        else:
            raise ValueError("导入的PLY文件不包含颜色数据")
    
    # === 绑定按键 ===
    plotter.add_key_event("c", switch_view)
    plotter.add_key_event("v", switch_view_back)
    # === 绑定按键 ===
    # 平移
    plotter.add_key_event("5", lambda: move_camera("a"))
    plotter.add_key_event("6", lambda: move_camera("s"))
    plotter.add_key_event("7", lambda: move_camera("d"))
    plotter.add_key_event("8", lambda: move_camera("f"))
    plotter.add_key_event("9", lambda: move_camera("j"))
    plotter.add_key_event("0", lambda: move_camera("k"))

    # 旋转
    plotter.add_key_event("Right", lambda: rotate_horizontal(5))
    plotter.add_key_event("Left", lambda: rotate_horizontal(-5))
    # plotter.add_key_event("Up", lambda: rotate_vertical(5))
    # plotter.add_key_event("Down", lambda: rotate_vertical(-5))

    plotter.add_mesh(mesh, scalars='Colors', rgb=True)
    plotter.show(screenshot=f'scene{args.scene_id}_{cur_view_ptr}.png')

if __name__ == "__main__":
    main()