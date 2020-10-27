import numpy as np
import scipy as sp
import sys
import time
import math


def main(input_file, output_file, voxel_s):

    # The start of time measerment 
    start_time = time.time() 
    
    # Reading OBJ file into lists
    objects_names, material_list, face_tree, vertex_list, material_paths = read_file(input_file) 

    # Creating the bounding box and the grid of voxels
    grid_start, grid_end = get_boudnig_box_voxels(vertex_list, voxel_s, voxel_s)

    grid_size = [abs(grid_end[i] - grid_start[i])+1 for i in range(3)] 

    print('\nGrid')
    print('Start: ', grid_start)
    print('End:   ', grid_end)
    print('Size:  ', grid_size)

    # Definig the voxel grid
    progress = 0
    print('\nVoxelization...')
    print('Progress: ', progress , '%')
    grid = {}

    total_face_nr = sum(len(faces) for faces in face_tree)
    face_count = 0

    for mesh in range(len(objects_names)):
        for face in face_tree[mesh]:
            box_start, box_end = get_boudnig_box_voxels([vertex_list[v] for v in face], voxel_s, voxel_s)

            # print([vertex_list[v] for v in face])
            # print(box_start, box_end)

            for x in range(box_start[0], box_end[0]+1):
                for y in range(box_start[1], box_end[1]+1):
                    for z in range(box_start[2], box_end[2]+1):
                        
                        # check if the voxel is already filled
                        if (x,y,z) in grid: continue

                        # if voxel is empty gather the data about the voxel and face3
                        voxel_position = [float(x*voxel_s), float(y*voxel_s), float(z*voxel_s)]
                        voxel_lines = get_voxel_lines(voxel_position,voxel_s/2)
                        v1, v2, v3 = tuple([vertex_list[v] for v in face]) 

                        # check for interesction 
                        for ln in voxel_lines:
                            if ((signed_volume(v1,    v2, v3, ln[0]) != signed_volume(v1,    v2, v3, ln[1])) 
                            and (signed_volume(ln[0], ln[1], v1, v2) != signed_volume(ln[0], ln[1], v1, v3))
                            and (signed_volume(ln[0], ln[1], v2, v1) != signed_volume(ln[0], ln[1], v2, v3))
                            and (signed_volume(ln[0], ln[1], v3, v1) != signed_volume(ln[0], ln[1], v3, v2))):
                                # fill the data about the intersecting mesh to the voxel
                                grid[x, y ,z] = [mesh]

        face_count += len(face_tree[mesh])
        p = 10*int(10 * face_count / total_face_nr)
        if p > progress:
            progress =  p
            print('Progress: ', progress , '%')

    print("\nSaving...")


    output = open(output_file, 'w')
    for mp in material_paths:
        output.write(mp)

    vertex_count   = 1

    for voxel in grid:
        for vertices in get_voxel_corners(voxel,voxel_s):
            output.write('v '+ ', '.join(str(v) for v in vertices)+'\n' )
        grid[voxel].append(get_voxel_faces(vertex_count))
        vertex_count += 8

    for voxel in grid:
        
        output.write('\no '+ '-'.join(str(id) for id in voxel) + '_' + str(objects_names[ grid[voxel][0] ])+'\n' )
        if material_list[ grid[voxel][0]] is not None:
            output.write('\n'+str(material_list[ grid[voxel][0]]))
        for face in grid[voxel][1]:
            output.write('f '+ ' '.join(str(f) for f in face)+'\n' )

        grid[voxel].append(get_voxel_faces(vertex_count))
        vertex_count += 8

    print("\nVoxelized model saved to ", output_file)
    print("Computation time: %s secondes" % (time.time() - start_time))

def read_file(input_file):

    input = open(input_file,'r') # reads OBJ file into input

    # Creates lists to store the input from an OBJ file 
    vertex_list   = []
    objects_names = []
    material_list = []
    material_files= []
    face_tree     = []
    face_list     = []
    object_name   = None
    material      = None
    

    for line in input:

        if line[:2] == 'v ':
            vertex_list.append([float(string) for string in  line[2:].split()])

        if line[0] == 'o':
            if face_list != []:
                face_tree.append(face_list)
                objects_names.append(object_name)
                material_list.append(material)
                face_list = []

            object_name = line[2:-1]
            material = None

        if line[0] == 'u':
            if face_list != []:
                face_tree.append(face_list)
                objects_names.append(object_name)
                material_list.append(material)
                face_list = []

            material = line

        if line[:6] == 'mtllib':
            material_files.append(line)

        if line[:2] == 'f ':
            face_str = line.split()
            face_num = [int(face_str[1]) - 1, int(face_str[2]) - 1, int(face_str[3]) - 1]
            face_list.append(face_num)

    face_tree.append(face_list)
    objects_names.append(object_name)
    material_list.append(material)

    return objects_names, material_list, face_tree, vertex_list, material_files

def get_boudnig_box_voxels(vertices, voxel_size, margine):

    min_coord, max_coord = get_min_max_coord(vertices)

    box_start =  [round((min_coord[i] - margine) / voxel_size) for i in range(3)]
    box_end   =  [round((max_coord[i] + margine) / voxel_size) for i in range(3)]

    return box_start, box_end


def get_min_max_coord(vertices):
    min_c = vertices[0].copy()
    max_c = vertices[0].copy()
    for v in vertices:
        for i in range(3): # searches in 3 dimension 
            if v[i] < min_c[i]:
                min_c[i] = v[i]
            if v[i] > max_c[i]:
                max_c[i] = v[i]
    return min_c, max_c,


def signed_volume(a,b,c,d):
    return ((a[0]-d[0]) * ( (b[1]-d[1]) * (c[2]-d[2]) - (b[2]-d[2]) * (c[1]-d[1]))
          + (a[1]-d[1]) * ( (b[2]-d[2]) * (c[0]-d[0]) - (b[0]-d[0]) * (c[2]-d[2]))
          + (a[2]-d[2]) * ( (b[0]-d[0]) * (c[1]-d[1]) - (b[1]-d[1]) * (c[0]-d[0]))) <= 0


def get_voxel_lines(p,s): 
    return [
        ([p[0]+s,p[1],p[2]] , [p[0]-s,p[1],p[2]]),
        ([p[0],p[1]+s,p[2]] , [p[0],p[1]-s,p[2]]),
        ([p[0],p[1],p[2]+s] , [p[0],p[1],p[2]-s])]

def get_voxel_faces(index):
    face_vertices = [
        [index+0,index+1,index+2,index+3],
        [index+7,index+6,index+5,index+4],
        [index+0,index+4,index+5,index+1],
        [index+1,index+5,index+6,index+2],
        [index+2,index+6,index+7,index+3],
        [index+3,index+7,index+4,index+0]]
    return face_vertices

def get_voxel_corners(voxel_id,voxel_size):

    x = float(voxel_id[0])*voxel_size
    y = float(voxel_id[1])*voxel_size
    z = float(voxel_id[2])*voxel_size
    s = voxel_size / 2.0

    voxel_corners = [
        [ -s+x, -s+y, -s+z ],
        [ -s+x,  s+y, -s+z ],
        [  s+x,  s+y, -s+z ],
        [  s+x, -s+y, -s+z ],
        [ -s+x, -s+y,  s+z ],
        [ -s+x,  s+y,  s+z ],
        [  s+x,  s+y,  s+z ],
        [  s+x, -s+y,  s+z ]]


    return voxel_corners


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]))
    # main('TUDelft_campus.obj', 'test.obj', 3)
