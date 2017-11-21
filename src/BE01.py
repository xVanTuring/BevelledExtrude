import bpy, bmesh
import math
#utils
print()
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
def select_item(array,clear_sele=False,bm=None):
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
                print("add one ")
    return list(bottom_verts),list(corner_edges)
def get_bevel_need_edge(edges):
    edge_set=set()
    for e in edges:
        radius = e.calc_face_angle(e)*180/math.pi
        if radius >= 45:
            edge_set.add(e)
    return list(edge_set)        


#function area end
bm  = bmesh.from_edit_mesh( bpy.context.object.data )
verts = [a for a in bm.select_history]
clear_select(bm)

print("verts selected: ",len(verts))
if False:
    bottom_verts,corner_edges = from_top_bottom(verts)
    edge_need_bevel = get_bevel_need_edge(corner_edges)

    edge_left = list(set(corner_edges)-set(edge_need_bevel))



if True:
    edge_test = bm.edges[870]
    geom = [edge_test.verts[0],edge_test.verts[1],edge_test]

    result = bmesh.ops.bevel(bm, geom=geom, offset=0.05,segments=2, profile=0.5,loop_slide=True)
    print(result)


bmesh.update_edit_mesh(bpy.context.object.data)