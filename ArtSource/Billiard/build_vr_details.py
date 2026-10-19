"""Additive VR-only pocket housings and a cue marker. Run through live Blender MCP."""
import bpy,bmesh,math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent
OUT=PROJECT/'Assets/NocturneGame/VR/Models'; OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.data.scenes.new('NOCTURNE | VR details'); bpy.context.window.scene=scene
mat=bpy.data.materials.new('VR_Pocket_Walnut'); mat.use_nodes=True
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
for suffix,socket in [('BaseColor','Base Color'),('Normal','Normal')]:
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(PROJECT/'Assets/Billiard_Nocturne/Textures'/('Table_'+suffix+'.png')),check_existing=True)
    if suffix=='Normal':
        tex.image.colorspace_settings.name='Non-Color'; normal=mat.node_tree.nodes.new('ShaderNodeNormalMap'); mat.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']); mat.node_tree.links.new(normal.outputs['Normal'],bs.inputs[socket])
    else: mat.node_tree.links.new(tex.outputs['Color'],bs.inputs[socket])
bs.inputs['Roughness'].default_value=.4
verts=[];faces=[]
for cx,cy,r in [(sx*1.27,sy*.635,.105) for sx in(-1,1) for sy in(-1,1)]+[(0,sy*.635,.092) for sy in(-1,1)]:
    if cx==0: start,end=(0,math.pi) if cy>0 else (math.pi,math.tau)
    elif cx>0 and cy>0: start,end=-math.pi/2,math.pi
    elif cx<0 and cy>0: start,end=0,math.pi*1.5
    elif cx>0: start,end=math.pi,math.pi*2.5
    else: start,end=math.pi/2,math.tau
    steps=24 if cx else 16; base=len(verts)
    for zz,rr in[(.51,r*1.40),(.51,r*2.0),(.871,r*1.40),(.871,r*2.0)]:
        for i in range(steps+1):
            t=start+(end-start)*i/steps; verts.append((cx+rr*math.cos(t),cy+rr*math.sin(t),zz))
    k=steps+1
    for i in range(steps):
        for a,b in[(0,1),(1,3),(3,2),(2,0)]: faces.append(tuple(base+j for j in(a*k+i,a*k+i+1,b*k+i+1,b*k+i)))
    faces.extend([(base,base+k,base+3*k,base+2*k),(base+steps,base+2*k+steps,base+3*k+steps,base+k+steps)])
mesh=bpy.data.meshes.new('VR_Pocket_Housings'); mesh.from_pydata(verts,[],faces); mesh.update()
uv=mesh.uv_layers.new(name='UVMap')
for p in mesh.polygons:
    for i in p.loop_indices:
        v=mesh.vertices[mesh.loops[i].vertex_index].co
        uv.data[i].uv=(.02+((v.x+v.y)*2%1)*.45,.02+(v.z*2%1)*.45)
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bmesh.ops.triangulate(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()
wood=bpy.data.objects.new('VR_Pocket_Housings',mesh); scene.collection.objects.link(wood); mesh.materials.append(mat)
def export(obj,name):
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',bake_space_transform=True,apply_scale_options='FBX_SCALE_UNITS',use_tspace=True,bake_anim=False)
export(wood,'VR_Pocket_Housings')
# A thick, two-sided downward arrow: broad silhouette readable at a glance.
outline=[(-.045,.36),(.045,.36),(.045,.16),(.12,.16),(0,0),(-.12,.16),(-.045,.16)]
vs=[(x,y,z) for y in(-.02,.02) for x,z in outline]; n=len(outline)
fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
me=bpy.data.meshes.new('Yellow_Cue_Arrow'); me.from_pydata(vs,[],fs); me.update()
bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bmesh.ops.triangulate(bm,faces=list(bm.faces)); bm.to_mesh(me); bm.free()
arrow=bpy.data.objects.new('VR_Yellow_Cue_Arrow',me); scene.collection.objects.link(arrow)
yellow=bpy.data.materials.new('VR_Yellow'); yellow.diffuse_color=(1,.75,.01,1); me.materials.append(yellow)
export(arrow,'VR_Yellow_Cue_Arrow')
for image in bpy.data.images:
    if image.filepath and 'Table_' in image.filepath and not image.packed_file: image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Nocturne_VR_Details.blend'),compress=True)
print(json.dumps({'housings_triangles':len(mesh.polygons),'arrow_triangles':len(me.polygons),'holes':'6 open entrances; wood outside the leather collars'}))
