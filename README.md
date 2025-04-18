# CoV
scripts for Chain-of-View manipulation
## Prerequisites
```
pip install -r requirements.txt
```

## scripts intro
```bash
├── trace_vis.py      # watch ply file with camera trace annotation  
├── overview.sh       # watch scene by scene
├── vista_plyvis.py   # generate camera trace annotation 
├── generate.sh       # generate scene by scene
├── watch_ply.py      # watch scene following trace of camera
└── game.sh           # watch scene by scene / manipulate view
```
## usage
for view manipulation (`game.sh`), we specify key as below:

### View switch
+ <kbd>c</kbd> for switch to next view
+ <kbd>v</kbd> for switch to previous view

### Translation
+ <kbd>5</kbd> forward (towards the focal point)
+ <kbd>6</kbd> backward (away from the focal point)
+ <kbd>7</kbd> leftward
+ <kbd>8</kbd> rightward
+ <kbd>9</kbd> upward
+ <kbd>0</kbd> downward

### Rotation
+ <kbd>Left</kbd> leftward
+ <kbd>Right</kbd> rightward

> <kbd>Up</kbd> and <kbd>Down</kbd> are default keys used to adjust focal distance.
