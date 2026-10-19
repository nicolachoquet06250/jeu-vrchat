"""Execute through live Blender MCP; retain original balls, studio and atlas."""
import bpy,runpy,shutil,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent
blend=ROOT/'Billiard_Nocturne.blend'
fbx=PROJECT/'Assets/Billiard_Nocturne/Billiard_Nocturne_Table.fbx'
for path in (blend,fbx):
    backup=ROOT/('Before_Pocket_Fill_'+path.name)
    if not backup.exists(): shutil.copy2(path,backup)
assert Path(bpy.data.filepath)==blend, 'Open the original billiard .blend before running this script'
original=next(s for s in bpy.data.scenes if any(o.name=='Billiard_Nocturne_Table' for o in s.objects))
old=original.objects['Billiard_Nocturne_Table']; oldmat=old.data.materials[0]
module=runpy.run_path(str(ROOT/'build_billiard.py'),run_name='nocturne_table_rebuild')
generated,table=module['build']()
oldmesh=old.data
bpy.data.objects.remove(old,do_unlink=True)
if oldmesh.users==0: bpy.data.meshes.remove(oldmesh)
table.name='Billiard_Nocturne_Table'; table.data.name='Cloth_cut_for_six_pockets'
table.data.materials.clear(); table.data.materials.append(oldmat)
for p in table.data.polygons: p.material_index=0
original.collection.objects.link(table)
for collection in list(table.users_collection):
    if collection!=original.collection: collection.objects.unlink(table)
bpy.context.window.scene=original; bpy.data.scenes.remove(generated)
table['pocket_backing_integrated']=True
bpy.ops.object.select_all(action='DESELECT'); table.select_set(True); bpy.context.view_layer.objects.active=table
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',bake_space_transform=True,apply_scale_options='FBX_SCALE_UNITS',use_tspace=True,bake_anim=False)
for image in bpy.data.images:
    if image.filepath and 'Table_' in image.filepath and not image.packed_file: image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'success':True,'integratedPocketBacks':6,'tableTriangles':len(table.data.polygons),'materials':len(table.data.materials),'blend':str(blend),'fbx':str(fbx)}
(ROOT/'pocket-backing-report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
