#!/bin/bash

# Path to the file containing scene IDs
SCENES_FILE="/Users/zhuruihan/Desktop/llava-3d/scanqa_scenes.txt"

# Output directory
OUTPUT_DIR="/Users/zhuruihan/Desktop/llava-3d"

# Read each scene from the file
while IFS= read -r scene; do

    python vista_plyvis.py --scene_id "$scene"
    echo "Done processing scene: $scene"

done < "$SCENES_FILE"



# python download_scannet.py --type _vh_clean_2.ply --id scene0011_00 -o /Users/zhuruihan/Desktop/llava-3d/scene0011_00
