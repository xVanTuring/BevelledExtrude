import bpy, bmesh
import mathutils
from mathutils import Vector
import math
#utils
#here top means extrude side
print("*********")
if not bpy.app.debug:
    bpy.app.debug= True
# function area
def clear_select(bm):
    for f in bm.verts:
        f.select = False
    for e in bm.edges:
        e.select = False
    for f in bm.faces:
        f.select = False
def select_items(array,clear_sele=False,bm=None):
    if clear_sele:
        clear_select(bm)
    for a in array:
        a.select = True
def from_top_bottom(verts):
    bottom_verts=set()
    corner_edges=set()
    for v in verts:
        for e in v.link_edges:
            if e.other_vert(v) not in verts:
                bottom_verts.add(e.other_vert(v))
                corner_edges.add(e)
                #print("add one ")
    return list(bottom_verts),list(corner_edges)
def get_bevel_need_edge(edges):
    edge_set=set()
    for e in edges:
        #print(e.index)
        radius = e.calc_face_angle()*180/math.pi
        if radius >= 45:
            edge_set.add(e)
    return list(edge_set)

def clean_list(array):
    for a in array:
        if not a.is_valid:
            array.remove(a)
    return array

def is_same_level(vert,verts):
    for v in verts:
        for e in v.link_edges:
            if e.other_vert(v) == vert:
                return True
    return False
def clear_select(bm):
    for f in bm.verts:
        f.select = False
    for e in bm.edges:
        e.select = False
    for f in bm.faces:
        f.select = False
def select_items(array,clear_sele=False,bm=None):
    if clear_sele:
        clear_select(bm)
    for a in array:
        a.select = True
def find_faces(verts):
    faces_set = set()
    for v in verts:
        for f in v.link_faces:
            if set(f.verts[:]).issubset(verts):
                faces_set.add(f)
    return list(faces_set)
def find_edges(verts):
    edges_set = set()
    for v in verts:
        for e in v.link_edges:
            if e.other_vert(v) in verts:
                edges_set.add(e)
    return list(edges_set)
def find_edges_from_faces(faces):
    edges_set = set()
    for f in faces:
        edges_set.update(f.edges[:])
    return list(edges_set)
def find_verts_from_edges(edges):
    verts_set = set()
    for e in edges:
        verts_set.add(e.verts[0])
        verts_set.add(e.verts[1])
    return list(verts_set)
def find_edges_loop_from_faces_edges(faces):
    all_edges = find_edges_from_faces(faces)
    faces_set = set(faces)
    edges_set = set()
    for e in all_edges:
        if not set(e.link_faces).issubset(faces_set):
            edges_set.add(e)
    return list(edges_set)
def get_region_loop(verts):
    operate_verts = verts
    operate_verts_set = set(operate_verts)

    all_faces = find_faces(operate_verts)
    all_edges = find_edges(operate_verts)
    all_edges_with_faces = find_edges_from_faces(all_faces)

    all_edges_standalone = list(set(all_edges)-set(all_edges_with_faces))
    all_verts_standalone = find_verts_from_edges(all_edges_standalone)
    all_verts_standalone_set = set(all_verts_standalone)
    all_edges_with_faces_loop = find_edges_loop_from_faces_edges(all_faces)
    all_edges_with_faces_standalone =[]
    for e in all_edges_with_faces_loop:
        if not set(e.verts[:]).issubset(all_verts_standalone_set):
            all_edges_with_faces_standalone.append(e)

            
    all_edges_standalone+=all_edges_with_faces_standalone
    return all_edges_standalone
    
def get_region_loop_no_face(verts):
    edge_loop = []
    for v in verts:
        for e in v.link_edges:
            if e.other_vert(v) in verts:
               edge_loop.append(e) 
    return list(set(edge_loop))
def get_bevle_result(res,segment,top_verts,bottom_verts):
    base_face = None
    other_faces = res['faces'][:]
    '''
    segemnt > 1
        find verts (the most)
    segement = 1
    '''
    if segment > 1:
        for f in res['faces']:
            if len(f.verts) > 4:
               base_face = f
    else:
        print("WORNG FUNCTION!")
        base_face = res['faces'][0]
        
    other_faces.remove(base_face)
    beveled_edges = res['edges']
    
    oneside_on_base=[]
    oneside_on_base_set = set()
    for e in base_face.edges:
        for f in other_faces:
            if e in f.edges:
                oneside_on_base.append(e)
                
    base_verts_set = set(base_face.verts[:])
    all_verts_set = set(res['verts'][:])
    oneside_to_base_verts = all_verts_set-base_verts_set
    oneside_on_base_verts = set()
    for e in set(oneside_on_base):
        oneside_on_base_verts.update(e.verts[:])
    
    if is_same_level(oneside_on_base[0].verts[0],top_verts):
        return oneside_on_base_verts, oneside_to_base_verts
    else :
        return oneside_to_base_verts, oneside_on_base_verts
    
def update_verts(update_edge,verts):
    new_vert_set = set()
    for e in update_edge:
        new_vert_set.add(e.verts[0])
        new_vert_set.add(e.verts[1])
    verts+=list(new_vert_set)
    
def extrude(bm,faces,m_x,m_y,m_z):
    operat_faces=faces
    n = Vector((0,0,0))
    for i in operate_faces:
        #print("face:",i.normal)
        n += i.normal

    r = bmesh.ops.extrude_face_region(bm,geom=operate_faces)

    verts = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    faces = [e for e in r['geom'] if isinstance(e, bmesh.types.BMFace)]
    
    clear_select(bm)
    
    z = mathutils.Vector((0,0,1))
    axis = n.cross(z)
    angle = n.angle(z)
    R = mathutils.Matrix.Rotation(angle,4,axis)
    bmesh.ops.translate(bm, vec = Vector((m_x,m_y,m_z)),space=R,verts = verts )
    bmesh.ops.delete(bm, geom=operate_faces, context=5)
    
    return faces
    
#function area end
bm  = bmesh.from_edit_mesh( bpy.context.object.data)

if True:
    operate_faces = [a for a in bm.select_history]
    extrude_result = extrude(bm,operate_faces,m_x=0,m_y=0,m_z=.1)
if True:
    top_faces = extrude_result
    top_verts=[]
    for f in top_faces:
        top_verts+=f.verts[:]
    top_verts = list(set(top_verts))
    clear_select(bm)
    bottom_verts,corner_edges = from_top_bottom(top_verts)
    edge_need_bevel = get_bevel_need_edge(corner_edges)
    edge_left = list(set(corner_edges)-set(edge_need_bevel))


if True:
    for e in edge_need_bevel:        
        edge_test = e
        geom = [edge_test.verts[0],edge_test.verts[1],edge_test]
        segments=3
        result = bmesh.ops.bevel(bm, geom=geom, offset=0.02,segments=segments, profile=0.5,loop_slide=True)
        clean_list(top_verts)
        clean_list(bottom_verts)
        
        top_verts_update,bottom_verts_update = get_bevle_result(result,segments,top_verts=top_verts,bottom_verts=bottom_verts)
        top_verts += top_verts_update
        bottom_verts += bottom_verts_update
        
    top_edges = get_region_loop(top_verts)
    bottom_edges = get_region_loop_no_face(bottom_verts)
    select_items(top_verts)
    if True:
        all_bottom_verts=set()
        all_top_verts=set()
        for e in top_edges:
            all_top_verts.add(e.verts[0])
            all_top_verts.add(e.verts[1])
        for e in bottom_edges:
            all_bottom_verts.add(e.verts[0])
            all_bottom_verts.add(e.verts[1])
        top_geom = list(all_top_verts)+top_edges
        top_segments = 2
        top_bevel_result = bmesh.ops.bevel(bm, geom=top_geom, offset=0.01,segments=top_segments, profile=0.5,loop_slide=False)        
        bottom_geom = list(all_bottom_verts)+bottom_edges
        bottom_segment = 2
        bottom_bevel_result = bmesh.ops.bevel(bm, geom=bottom_geom, offset=0.01,segments=bottom_segment, profile=0.5,loop_slide=False)
        select_items(top_bevel_result['verts'][:])
        
#bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            

bmesh.update_edit_mesh(bpy.context.object.data)