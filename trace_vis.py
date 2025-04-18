import pyvista as pv
import numpy as np
import argparse
import os
from vista_plyvis import create_yellow_sphere, create_green_line, create_blue_arrow

plotter = pv.Plotter(window_size=[1920, 1080])

def main():
    global view_pose
    global plotter
    parser = argparse.ArgumentParser(description="Visualize a PLY file with a given scene id.")
    parser.add_argument("--scene_id", type=str, help="scene id", default='0011_00')
    parser.add_argument("--sparse", action='store_true', help="use sparse point cloud")
    # parser.add_argument("--frame_id", type=str, help="frame id", default='80')
    args = parser.parse_args()
    args.scene_id = args.scene_id.replace('scene', '')

    ply = f'/Users/zhuruihan/Desktop/llava-3d/pose_annotated_mesh/scene{args.scene_id}.ply' if not args.sparse else f'/Users/zhuruihan/Desktop/llava-3d/pose_annotated_mesh/scene{args.scene_id}_sparse.ply' 

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

    plotter.add_mesh(mesh, scalars='Colors', rgb=True)
    plotter.show()

if __name__ == "__main__":
    main()