import pyvista as pv
import numpy as np
import argparse
import os
# 读取PLY文件

def create_yellow_sphere(center, radius=0.5, resolution=30):
    sphere = pv.Sphere(# center=center,
                    radius=radius, theta_resolution=resolution, phi_resolution=resolution).translate(center)
    
    # 创建黄色RGBA颜色数组 (R=255, G=255, B=0, A=255)
    n_points = sphere.n_points
    yellow_colors = np.zeros((n_points, 4), dtype=np.uint8)
    yellow_colors[:, 0] = 255  # R通道
    yellow_colors[:, 1] = 255  # G通道
    yellow_colors[:, 3] = 255  # A通道
    
    sphere.point_data['Colors'] = yellow_colors
    return sphere

def create_green_line(a, b):
    line = pv.Line(a, b)
    
    # 创建黄色RGBA颜色数组 (R=255, G=255, B=0, A=255)
    n_points = line.n_points
    colors = np.zeros((n_points, 4), dtype=np.uint8)
    colors[:, 1] = 255  # G通道
    colors[:, 3] = 255  # A通道
    
    line.point_data['Colors'] = colors
    return line

def create_blue_arrow(start, direction):
    arrow = pv.Arrow(
            start=start,
            direction=direction,
            scale=0.25,
            shaft_radius=0.02,
            tip_radius=0.04,
            tip_length=0.3
    )
    n_points = arrow.n_points
    colors = np.zeros((n_points, 4), dtype=np.uint8)
    colors[:, 1] = 255
    colors[:, 2] = 255 
    colors[:, 3] = 255  # A通道设为255（完全不透明）
    arrow.point_data['Colors'] = colors
    
    return arrow

def process_pose(pose):
    fix_coord = np.diag([1, -1, -1, 1])  # 坐标轴变换
    pose_fixed = pose @ fix_coord 
    position = pose_fixed[:3, 3]

    R = pose_fixed[:3, :3]
    # right = R[:, 0]
    # up = R[:, 1]
    forward = R[:, 2]
    direction = -forward  # 相机看向的方向

    return position, direction


def main():
    parser = argparse.ArgumentParser(description="Visualize a PLY file with a given pose matrix.")
    parser.add_argument("--scene_id", type=str, help="scene id", default='0011_00')
    parser.add_argument("--sparse", action='store_true', help="save sparse point cloud")
    # parser.add_argument("--frame_id", type=str, help="frame id", default='80')
    args = parser.parse_args()
    args.scene_id = args.scene_id.replace('scene', '')

    ply = f'/Users/zhuruihan/Desktop/llava-3d/scene{args.scene_id}/scans/scene{args.scene_id}/scene{args.scene_id}_vh_clean_2.ply'
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
    
    plotter = pv.Plotter()
    combined = mesh.copy()
    pose_folder = f'/Users/zhuruihan/Desktop/llava-3d/scene{args.scene_id}/scans/scene{args.scene_id}/pose/'
    prev = None

    frame_list = sorted(os.listdir(pose_folder), key=lambda x: int(x.split('.')[0]))
    sparse_frame_list = [frame_list[i] for i in range(0, len(frame_list), 5)]
    using_frame_list = sparse_frame_list if args.sparse else frame_list
    for frame in using_frame_list:
        pose = f'/Users/zhuruihan/Desktop/llava-3d/scene{args.scene_id}/scans/scene{args.scene_id}/pose/{frame}'
        pose = np.loadtxt(pose)
        # position, direction = process_pose(pose)
        position, direction = process_pose(pose)

        # line
        if prev is not None:
            line = create_green_line(prev, position)
            tube = line.tube(radius=0.006)
            combined += tube

        # anchor
        anchor = create_yellow_sphere(center=position, radius=0.05)
        combined += anchor

        # direction arrow 
        arrow = create_blue_arrow(start=position, direction=direction)
        combined += arrow

        prev = position

    # 设置相机
    output_dir = f'/Users/zhuruihan/Desktop/llava-3d/pose_annotated_mesh'

    combined.save(os.path.join(output_dir, f'scene{args.scene_id}_sparse.ply' if args.sparse else f'scene{args.scene_id}_sparse.ply'), texture='Colors')
    plotter.add_mesh(combined, scalars='Colors', rgb=True)
    plotter.close()

if __name__ == "__main__":
    main()