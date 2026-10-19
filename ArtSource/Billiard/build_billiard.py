"""Run in Blender through MCP. Deterministic, original low-poly asset."""
import bpy, bmesh, numpy as np, math, os, json, struct, zlib
from mathutils import Vector
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(ROOT))
OUT = os.path.join(PROJECT, 'Assets', 'Billiard_Nocturne')
TEX = os.path.join(OUT, 'Textures')
os.makedirs(TEX, exist_ok=True)

def enum(obj, prop, value):
    valid = [i.identifier for i in obj.bl_rna.properties[prop].enum_items]
    if value not in valid: raise ValueError((prop, value, valid))
    setattr(obj, prop, value)

def png(path, arr):
    a = np.uint8(np.clip(arr, 0, 1)*255+.5)[::-1]
    h,w,c = a.shape
    def chunk(tag, data):
        return struct.pack('!I',len(data))+tag+data+struct.pack('!I',zlib.crc32(tag+data)&0xffffffff)
    raw = b''.join(b'\0'+row.tobytes() for row in a)
    with open(path,'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,6 if c==4 else 2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b''))

def textures():
    n=2048; s=n//2
    y,x=np.mgrid[0:s,0:s].astype(np.float32)/s
    rng=np.random.default_rng(19)
    noise=rng.standard_normal((s,s)).astype(np.float32)
    base=np.ones((n,n,3),np.float32); height=np.zeros((n,n),np.float32)
    rough=np.ones((n,n),np.float32)*.5; metal=np.zeros((n,n),np.float32)
    warp=y*85+1.7*np.sin(x*9+y*8)+.65*np.sin(x*31+y*12)
    grain=np.sin(warp*6.283)+.38*np.sin(warp*17.7)+.18*np.sin(warp*41)
    broad=.5*np.sin(y*15+x*2)+.3*np.sin(y*39+np.sin(x*8))
    pores=np.maximum(0,np.sin(warp*33)-.84)*(0.5+0.5*np.sin(x*220))
    tint=1+grain*.105+broad*.16+noise*.014-pores*.30
    base[:s,:s]=np.array([.265,.135,.068])*tint[:,:,None]
    height[:s,:s]=grain*.19+noise*.018-pores*.28
    rough[:s,:s]=np.clip(.30+grain*.024+pores*.25,.24,.48)
    weave=np.sin(x*s*2.094)*np.sin(y*s*2.094)
    nap=.3*np.sin(x*49+y*23)+.18*np.sin(y*67-x*11)
    base[:s,s:]=np.array([.025,.32,.205])*(1+weave[:,:,None]*.032+noise[:,:,None]*.017+nap[:,:,None]*.025)
    height[:s,s:]=weave*.13+noise*.032
    rough[:s,s:]=.89+noise*.013
    pebble=np.sin(x*690+2*np.sin(y*134))*np.sin(y*740+2*np.sin(x*133))
    base[s:,:s]=np.array([.065,.042,.03])*(1+pebble[:,:,None]*.22+noise[:,:,None]*.055)
    height[s:,:s]=pebble*.27+noise*.045
    rough[s:,:s]=.59+pebble*.055
    colors=[(.60,.40,.17),(.04,.048,.052),(.87,.83,.68),(.65,.43,.21)]
    for j,col in enumerate(colors):
        xx=s+(j%2)*512; yy=s+(j//2)*512
        q=np.s_[yy:yy+512,xx:xx+512]
        fine=noise[:512,:512]
        brush=np.sin(y[:512,:512]*11000)*.035
        base[q]=np.array(col)*(1+fine[:,:,None]*.014+brush[:,:,None])
        height[q]=brush*.14
        rough[q]=(.29,.35,.25,.38)[j]+fine*.008
        metal[q]=(.82,.7,0,0)[j]
    dy,dx=np.gradient(height)
    normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    normal=normal*.5+.5
    # Neutral padding stops high-frequency normal seams at atlas region borders.
    for line in (0,1024,2047):
        normal[max(0,line-3):min(n,line+4),:]=(.5,.5,1)
        normal[:,max(0,line-3):min(n,line+4)]=(.5,.5,1)
    png(os.path.join(TEX,'Table_BaseColor.png'),base)
    png(os.path.join(TEX,'Table_Normal.png'),normal)
    png(os.path.join(TEX,'Table_ORM.png'),np.stack([np.ones_like(rough),rough,metal],axis=-1))
    png(os.path.join(TEX,'Table_MetallicSmoothness.png'),np.stack([metal,np.zeros_like(metal),np.zeros_like(metal),1-rough],axis=-1))
    print('Four 2048px PBR atlases written.')

def material():
    m=bpy.data.materials.new('Nocturne_Table_Atlas'); m.diffuse_color=(.12,.20,.12,1)
    nodes=m.node_tree.nodes; links=m.node_tree.links
    bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    for filename,space in [('Table_BaseColor.png','sRGB'),('Table_Normal.png','Non-Color'),('Table_ORM.png','Non-Color')]:
        im=bpy.data.images.load(os.path.join(TEX,filename),check_existing=True)
        im.colorspace_settings.name=space
        node=nodes.new('ShaderNodeTexImage'); node.image=im
        node.label=filename; node.location=(-620,200-220*len([n for n in nodes if n.type=='TEX_IMAGE']))
        if 'BaseColor' in filename: links.new(node.outputs['Color'],bs.inputs['Base Color'])
        elif 'Normal' in filename:
            nm=nodes.new('ShaderNodeNormalMap'); nm.location=(-280,-220)
            links.new(node.outputs['Color'],nm.inputs['Color']); links.new(nm.outputs['Normal'],bs.inputs['Normal'])
        else:
            sep=nodes.new('ShaderNodeSeparateColor'); sep.location=(-280,-450)
            links.new(node.outputs['Color'],sep.inputs['Color'])
            links.new(sep.outputs['Green'],bs.inputs['Roughness']); links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
    return m

REG={'wood':(.008,.008,.484,.484),'cloth':(.508,.008,.484,.484),'leather':(.008,.508,.484,.484),'brass':(.51,.51,.23,.23),'black':(.76,.51,.23,.23),'ivory':(.51,.76,.23,.23),'maple':(.76,.76,.23,.23)}
parts=[]
def mesh(name,verts,faces,region='wood',uvs=None,smooth=False):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); tablecol.objects.link(ob); me.materials.append(MAT)
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(me); bm.free()
    uv=me.uv_layers.new(name='UVMap'); u0,v0,us,vs=REG[region]
    coords=np.array(verts); mins=coords.min(axis=0); size=np.maximum(coords.max(axis=0)-mins,.0001)
    for p in me.polygons:
        p.use_smooth=smooth
        axes=sorted(range(3),key=lambda k:abs(p.normal[k]))[:2]
        axes=sorted(axes,key=lambda k:size[k],reverse=True)
        for li in p.loop_indices:
            vi=me.loops[li].vertex_index
            u,v=uvs[vi] if uvs else ((coords[vi,axes[0]]-mins[axes[0]])/size[axes[0]],(coords[vi,axes[1]]-mins[axes[1]])/size[axes[1]])
            uv.data[li].uv=(u0+u*us,v0+v*vs)
    parts.append(ob); return ob

def box(name,loc,size,region='wood',bevel=0):
    x,y,z=np.array(size)/2
    vs=[(a*x+loc[0],b*y+loc[1],c*z+loc[2]) for c in (-1,1) for b in (-1,1) for a in (-1,1)]
    ob=mesh(name,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],region)
    if bevel:
        bm=bmesh.new(); bm.from_mesh(ob.data)
        bmesh.ops.bevel(bm,geom=list(bm.edges),offset=bevel,segments=1,affect='EDGES')
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(ob.data); bm.free()
    return ob

def ring(name,cx,cy,levels,region='leather',steps=16,cap=False):
    vs=[(cx+r*math.cos(i*2*math.pi/steps),cy+r*math.sin(i*2*math.pi/steps),z) for r,z in levels for i in range(steps)]
    fs=[(k*steps+i,k*steps+(i+1)%steps,(k+1)*steps+(i+1)%steps,(k+1)*steps+i) for k in range(len(levels)-1) for i in range(steps)]
    if cap: fs.append(tuple(range((len(levels)-1)*steps,len(levels)*steps)))
    return mesh(name,vs,fs,region,smooth=True)

def build():
    global tablecol,MAT
    # Preserve the original startup scene in its own scene datablock.
    scene=bpy.data.scenes.new('NOCTURNE | Billiard'); bpy.context.window.scene=scene
    tablecol=bpy.data.collections.new('01_TABLE | one mesh / one material'); scene.collection.children.link(tablecol)
    MAT=material()
    # Bed perimeter has genuine concave openings, no black discs over a solid bed.
    a=1.27; b=.635; r=.105; q=.092
    pts=[]
    def arc(cx,cy,rad,t0,t1,num):
        pts.extend([(cx+rad*math.cos(t),cy+rad*math.sin(t),.80) for t in np.linspace(t0,t1,num)])
    pts.append((-a+r,-b,.8)); arc(0,-b,q,math.pi,0,9)
    arc(a,-b,r,math.pi,math.pi/2,5); arc(a,b,r,-math.pi/2,-math.pi,5)
    arc(0,b,q,0,-math.pi,9); arc(-a,b,r,0,-math.pi/2,5); arc(-a,-b,r,math.pi/2,0,5)
    pts=pts[:-1] # final point equals first
    bed=mesh('Cloth_cut_for_six_pockets',pts,[tuple(range(len(pts)))],'cloth',[( (p[0]+a)/(2*a),(p[1]+b)/(2*b)) for p in pts])
    # A planar open surface must keep its visible side upward for game-engine culling.
    if bed.data.polygons[0].normal.z<0:
        bm=bmesh.new(); bm.from_mesh(bed.data)
        bmesh.ops.reverse_faces(bm,faces=list(bm.faces)); bm.to_mesh(bed.data); bm.free()
    # Six profiled cushions, including angled pocket jaws.
    def cushion(name,length,cx,cy,angle):
        profile=[(0,.811),(0,.828),(.061,.856),(.083,.849),(.083,.80)]
        vs=[]
        for end in (-1,1):
            for depth,z in profile:
                xx=end*(length/2+depth*.45); yy=depth
                vs.append((cx+xx*math.cos(angle)-yy*math.sin(angle),cy+xx*math.sin(angle)+yy*math.cos(angle),z))
        fs=[tuple(range(4,-1,-1)),tuple(range(5,10))]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)]
        mesh(name,vs,fs,'cloth')
    for sy in (-1,1):
        for sx in (-1,1): cushion('Long_cushion',1.08,sx*.635,sy*.635,0 if sy==1 else math.pi)
    cushion('End_cushion_R',1.06,1.27,0,-math.pi/2)
    cushion('End_cushion_L',1.06,-1.27,0,math.pi/2)
    for cx,cy,rad in [(sx*a,sy*b,r) for sx in (-1,1) for sy in (-1,1)]+[(0,sy*b,q) for sy in (-1,1)]:
        # Open leather-lined well: inner wall normals deliberately point inward.
        # Shallow recessed pocket: it must read as a hole without a giant black
        # funnel protruding below the table.
        ob=ring('Pocket_leather_well',cx,cy,[(rad,.802),(rad*.93,.775),(rad*.73,.735)],cap=True)
        bm=bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.reverse_faces(bm,faces=list(bm.faces)); bm.to_mesh(ob.data); bm.free()
        # Upper leather horseshoe only around the outer half/quadrant, clear of bed.
        if cx==0: angles=np.linspace(0,math.pi,9) if cy>0 else np.linspace(math.pi,2*math.pi,9)
        elif cx>0 and cy>0: angles=np.linspace(-math.pi/2,math.pi,13)
        elif cx<0 and cy>0: angles=np.linspace(0,3*math.pi/2,13)
        elif cx>0: angles=np.linspace(math.pi,5*math.pi/2,13)
        else: angles=np.linspace(math.pi/2,2*math.pi,13)
        vs=[(cx+rr*math.cos(t),cy+rr*math.sin(t),zz) for rr,zz in [(rad,.805),(rad*1.17,.855),(rad*1.39,.855)] for t in angles]
        k=len(angles); fs=[(j*k+i,j*k+i+1,(j+1)*k+i+1,(j+1)*k+i) for j in range(2) for i in range(k-1)]
        mesh('Leather_pocket_collar',vs,fs,'leather',smooth=True)
    # Continuous outer wooden frame.  It sits just outside the pocket mouths,
    # leaving every opening fully visible while keeping the outside silhouette
    # straight and connected.
    for sy in (-1,1):
        box(f'Upper_frame_long_{sy}',(0,sy*.80,.70),(3.06,.16,.30),bevel=.004)
        box(f'Upper_frame_inlay_{sy}',(0,sy*.89,.855),(2.80,.004,.008),'brass')
        box(f'Band_outer_fill_{sy}',(0,sy*.735,.815),(2.94,.045,.10),bevel=.002)
    for sx in (-1,1):
        box(f'Upper_frame_end_{sx}',(sx*1.43,0,.70),(.16,1.71,.30),bevel=.004)
        box(f'Upper_frame_end_inlay_{sx}',(sx*1.52,0,.855),(.004,1.48,.008),'brass')
        box(f'Band_outer_fill_end_{sx}',(sx*1.365,0,.815),(.045,1.56,.10),bevel=.002)
    # Heavy apron matching the reference table: deep walnut fascia, inset panels
    # and reinforced corner blocks directly under the rail.
    for sy in (-1,1):
        box(f'Apron_long_{sy}',(0,sy*.70,.52),(2.98,.18,.40),bevel=.018)
        for sx in (-1,1):
            box(f'Apron_panel_{sy}_{sx}',(sx*.70,sy*.797,.53),(1.14,.018,.22),bevel=.008)
            box(f'Apron_panel_inlay_{sy}_{sx}',(sx*.70,sy*.809,.53),(1.00,.004,.008),'brass')
    for sx in (-1,1):
        box(f'Apron_end_{sx}',(sx*1.39,0,.52),(.18,1.42,.40),bevel=.018)
        for sy in (-1,1):
            box(f'Apron_end_panel_{sx}_{sy}',(sx*1.487,sy*.35,.53),(.018,.48,.22),bevel=.008)
            box(f'Apron_end_inlay_{sx}_{sy}',(sx*1.499,sy*.35,.53),(.004,.40,.008),'brass')
    for sx in (-1,1):
        for sy in (-1,1):
            box(f'Apron_corner_block_{sx}_{sy}',(sx*1.40,sy*.70,.69),(.24,.24,.44),bevel=.016)
    # Tapered square legs with just one bevel segment.
    for sx in (-1,1):
        for sy in (-1,1):
            cx=sx*1.04; cy=sy*.49
            vs=[(cx+dx*w,cy+dy*w,z) for w,z in [(.077,.055),(.117,.565)] for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
            mesh('Tapered_walnut_leg',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
            box('Brass_foot',(cx,cy,.063),(.163,.163,.055),'brass',.005)
            box('Rubber_foot',(cx,cy,.018),(.15,.15,.036),'black',.004)
    # Small mother-of-pearl sights: two triangles each.
    for sy in (-1,1):
        for cx in (-.95,-.635,-.32,.32,.635,.95):
            cy=sy*.734; z=.871
            mesh('Rail_diamond',[(cx-.012,cy,z),(cx,cy-.007,z),(cx+.012,cy,z),(cx,cy+.007,z)],[(0,1,2,3)],'ivory')
    for sx in (-1,1):
        for cy in (-.3175,0,.3175):
            cx=sx*1.369; z=.871
            mesh('End_diamond',[(cx-.007,cy,z),(cx,cy-.012,z),(cx+.007,cy,z),(cx,cy+.012,z)],[(0,1,2,3)],'ivory')
    for cx in (-.635,.635):
        rad=.004
        mesh('Cloth_spot',[(cx+rad*math.cos(t),rad*math.sin(t),.8002) for t in np.linspace(0,2*math.pi,12,endpoint=False)],[tuple(range(12))],'ivory')
    # Join the table into one renderer / submesh; triangulate explicitly for export.
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts: ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join()
    table=bpy.context.object; table.name='Billiard_Nocturne_Table'
    bm=bmesh.new(); bm.from_mesh(table.data); bmesh.ops.triangulate(bm,faces=list(bm.faces)); bm.to_mesh(table.data); bm.free()
    table['design']='Original Nocturne 9-foot American pool table'
    table['texture_resolution']=2048
    table['pocket_count']=6
    table['gameplay']='Visual asset. Add colliders and gameplay in Unity.'
    print(json.dumps({'table_triangles':len(table.data.polygons),'table_vertices':len(table.data.vertices),'material_slots':len(table.data.materials)}))
    return scene,table

if __name__=='__main__':
    textures()
    build()





















