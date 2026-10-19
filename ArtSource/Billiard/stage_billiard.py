import bpy, math, os, json
from mathutils import Vector
ns=bpy.app.driver_namespace['nocturne_builder']
enum=ns['enum']; OUT=ns['OUT']; ROOT=ns['ROOT']; TEX=ns['TEX']
scene=bpy.context.scene

def linkobj(name,data,col):
    ob=bpy.data.objects.new(name,data); col.objects.link(ob); return ob

def accessories():
    col=bpy.data.collections.new('02_BALLS | optional separate objects'); scene.collection.children.link(col)
    mat=bpy.data.materials.new('Nocturne_Balls_Atlas')
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value=.19
    bs.inputs['Coat Weight'].default_value=.28
    bs.inputs['Coat Roughness'].default_value=.16
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(os.path.join(TEX,'Balls_BaseColor.png'))
    mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    positions=[(-.635,0)]
    for row in range(5):
        for j in range(row+1): positions.append((.45+row*.0500,(j-row/2)*.0580))
    order=[0,1,9,2,3,8,10,11,4,12,5,6,13,7,14,15]
    for index,(x,y) in enumerate(positions):
        number=order[index]; verts=[]; faces=[]; coords=[]
        lon=16; lat=8; radius=.028575
        # Duplicate seam and pole vertices preserve correct atlas UV interpolation.
        for j in range(lat+1):
            theta=math.pi*j/lat
            for k in range(lon+1):
                phi=2*math.pi*k/lon
                verts.append((radius*math.sin(theta)*math.cos(phi),radius*math.sin(theta)*math.sin(phi),radius*math.cos(theta)))
                coords.append(((number%4+(k/lon)*.984+.008)/4,(3-number//4+(1-j/lat)*.984+.008)/4))
        for j in range(lat):
            for k in range(lon):
                a=j*(lon+1)+k; b=a+1; c=b+lon+1; d=a+lon+1
                if j==0: faces.append((a,d,c))
                elif j==lat-1: faces.append((a,d,b))
                else: faces.extend([(a,d,c),(a,c,b)])
        me=bpy.data.meshes.new('Ball_%02d_Mesh'%number); me.from_pydata(verts,[],faces); me.update()
        uv=me.uv_layers.new(name='UVMap')
        for p in me.polygons:
            p.use_smooth=True
            for li in p.loop_indices: uv.data[li].uv=coords[me.loops[li].vertex_index]
        ob=linkobj('Ball_%02d'%number,me,col); ob.location=(x,y,.8+radius); me.materials.append(mat)
        ob.rotation_euler=(.35,-.6,.3+number*.62)
        ob['diameter_m']=radius*2; ob['ball_number']=number
    print('16 independent balls, 224 triangles each, one shared atlas/material')

def studio():
    col=bpy.data.collections.new('90_STUDIO | excluded from game export'); scene.collection.children.link(col)
    me=bpy.data.meshes.new('Studio_floor_mesh'); me.from_pydata([(-200,-200,0),(200,-200,0),(200,200,0),(-200,200,0)],[],[(0,1,2,3)])
    floor=linkobj('Studio_floor',me,col)
    mat=bpy.data.materials.new('Studio_charcoal'); bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bs.inputs['Base Color'].default_value=(.026,.032,.038,1); bs.inputs['Roughness'].default_value=.76; me.materials.append(mat)
    for name,loc,power,color,size in [('Key_softbox',(0,-2.5,4.5),650,(1,.90,.76),4),('Cool_fill',(-3,1,2.8),450,(.65,.8,1),3),('Rim',(2,2,3),800,(1,.87,.65),2.4)]:
        light=bpy.data.lights.new(name,'AREA'); light.energy=power; light.color=color; light.shape='DISK' if 'DISK' in [i.identifier for i in light.bl_rna.properties['shape'].enum_items] else light.shape; light.size=size
        ob=linkobj(name,light,col); ob.location=loc; ob.rotation_euler=(Vector((0,0,.45))-ob.location).to_track_quat('-Z','Y').to_euler()
    world=bpy.data.worlds.new('Nocturne_Studio_World'); scene.world=world
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs['Color'].default_value=(.10,.12,.16,1); bg.inputs['Strength'].default_value=.35
    cam=bpy.data.cameras.new('Product_camera'); enum(cam,'type','ORTHO'); cam.ortho_scale=3.95
    ob=linkobj('Product_camera',cam,col); ob.location=(3.25,-4.3,3.65); ob.rotation_euler=(Vector((0,0,.4))-ob.location).to_track_quat('-Z','Y').to_euler(); scene.camera=ob
    scene.render.resolution_x=1440; scene.render.resolution_y=1080; scene.render.resolution_percentage=100
    enum(scene.render.image_settings,'file_format','PNG'); scene.render.filepath=os.path.join(ROOT,'Nocturne_Preview.png')
    print('studio ready',scene.render.engine)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active; space.lens=50
                enum(space.region_3d,'view_perspective','CAMERA')
                space.region_3d.view_camera_zoom=0
                space.overlay.show_overlays=False
    return col

accessories()
studio()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Billiard_Nocturne.blend'))
print('Blend saved')
