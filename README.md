# Voxelizer

Voxelizer is a python programme that takes as an input an OBJ file with triangular mesh and outputs an voxlized representation of that mesh. The output is also a OBJ file. 

![voxelization](/obj_mountains/voxelizer_mountains.png)

To run the programme the first argument should be the input file, the second argument should be the output file, and the third argument should be the voxel size (in the same units as the OBJ input). I should thus be able to execute the code by calling the main file like this:

python voxelization.py <input OBJ> <output OBJ> <voxel size>

For example:
python voxelization.py mountains.obj voxelized_mountains.obj 1.0
