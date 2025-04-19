#!/bin/bash

# Path to the file containing scene IDs
SCENES_FILE="/Users/zhuruihan/Desktop/llava-3d/scanqa_scenes.txt"

SPARSE_FLAG=""
if [ "$1" == "--sparse" ]; then
    SPARSE_FLAG="--sparse"
fi

# Read each scene from the file
while IFS= read -r scene; do

    python vista_plyvis.py --scene_id "$scene" $SPARSE_FLAG
    echo "Done processing scene: $scene"

done < "$SCENES_FILE"
