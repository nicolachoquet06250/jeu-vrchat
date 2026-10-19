"""Write native Unity material/import metadata using the project's own templates."""
from pathlib import Path
import re, uuid, struct, json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/Billiard_Nocturne'
TEX=OUT/'Textures'
MATS=OUT/'Materials'
MATS.mkdir(exist_ok=True)

def guid(name): return uuid.uuid5(uuid.NAMESPACE_URL,'nocturne-billiard-original/'+name).hex
def write(path,text): path.write_text(text,encoding='utf-8')

texture_template=(ROOT/'Packages/vrchat.jordo.easyquestswitch/Runtime/Resources/EQS_Logo_Crop.png.meta').read_text()
for path in TEX.glob('*.png'):
    normal='Normal' in path.name
    color='BaseColor' in path.name
    text=re.sub(r'guid: \w+',f'guid: {guid(path.name)}',texture_template,count=1)
    for key,value in {'enableMipMap':1,'sRGBTexture':int(color),'linearTexture':int(not color),'externalNormalMap':int(normal),'streamingMipmaps':1,'filterMode':2,'aniso':4,'spriteMode':0,'alphaIsTransparency':0,'textureType':int(normal),'maxTextureSize':1024 if path.name.startswith('Balls') else 2048,'compressionQuality':100}.items():
        text=re.sub(rf'(?m)^(\s*{key}:) .+$',rf'\g<1> {value}',text)
    write(path.with_suffix('.png.meta'),text)

mat_template=(ROOT/'Packages/com.vrchat.worlds/Samples/GraphicsBlitExampleScene/SampleSceneAssets/Sample Material.mat').read_text()
for name,maps in [('Nocturne_Table_Atlas',{'_MainTex':'Table_BaseColor.png','_BumpMap':'Table_Normal.png','_MetallicGlossMap':'Table_MetallicSmoothness.png'}),('Nocturne_Balls_Atlas',{'_MainTex':'Balls_BaseColor.png'})]:
    text=mat_template.replace('m_Name: Sample Material',f'm_Name: {name}')
    text=text.replace('m_ShaderKeywords: _METALLICGLOSSMAP','m_ShaderKeywords: _METALLICGLOSSMAP _NORMALMAP' if 'Table' in name else 'm_ShaderKeywords:')
    text=text.replace('m_DoubleSidedGI: 1','m_DoubleSidedGI: 0')
    for key in ['_MainTex','_BumpMap','_MetallicGlossMap']:
        ref=f'{{fileID: 2800000, guid: {guid(maps[key])}, type: 3}}' if key in maps else '{fileID: 0}'
        text=re.sub(rf'(- {key}:\n\s*m_Texture:) [^\n]+',rf'\g<1> {ref}',text)
    if 'Balls' in name: text=text.replace('_Glossiness: 0.5','_Glossiness: 0.81')
    write(MATS/(name+'.mat'),text)
    write(MATS/(name+'.mat.meta'),f'fileFormatVersion: 2\nguid: {guid(name)}\nNativeFormatImporter:\n  externalObjects: {{}}\n  mainObjectFileID: 2100000\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')

model_template=(ROOT/'Packages/com.vrchat.worlds/Integrations/ClientSim/Runtime/Resources/ClientSim/Avatars/VRC_Utility_FullBody/Avatar_Utility.fbx.meta').read_text()
version=re.search(r'ModelImporter:\n  serializedVersion: (\d+)',model_template)[1]
mesh_settings='  meshes:'+model_template.split('  meshes:',1)[1].split('  referencedClips:',1)[0]
mesh_settings=mesh_settings.replace('importBlendShapes: 1','importBlendShapes: 0')
for part in ['Table','Balls']:
    name='Billiard_Nocturne_'+part+'.fbx'; material='Nocturne_'+part+'_Atlas'
    write(OUT/(name+'.meta'),f'''fileFormatVersion: 2
guid: {guid(name)}
ModelImporter:
  serializedVersion: {version}
  internalIDToNameTable: []
  externalObjects:
  - first:
      type: UnityEngine:Material
      assembly: UnityEngine.CoreModule
      name: {material}
    second: {{fileID: 2100000, guid: {guid(material)}, type: 2}}
  materials:
    materialImportMode: 1
    materialName: 0
    materialSearch: 0
    materialLocation: 1
  animations:
    isReadable: 0
{mesh_settings}  referencedClips: []
  importAnimation: 0
  animationType: 0
  userData: Nocturne original low-poly billiard visual asset
  assetBundleName: 
  assetBundleVariant: 
''')

# Check the actual exported GLB, not just in-memory Blender counts.
data=(ROOT/'ArtSource/Billiard/Billiard_Nocturne.glb').read_bytes()
magic,version,total=struct.unpack_from('<3I',data)
assert magic==0x46546c67 and version==2 and total==len(data)
length,kind=struct.unpack_from('<2I',data,12)
doc=json.loads(data[20:20+length])
assert len(doc['meshes'])==17 and len(doc['materials'])==2
assert len(doc['scenes'])==1
assert not any(n.get('name')=='Cube' for n in doc['nodes'])
triangles=0; table_triangles=0
for mesh in doc['meshes']:
    for p in mesh['primitives']:
        assert 'TANGENT' in p['attributes'] and 'TEXCOORD_0' in p['attributes']
        count=doc['accessors'][p['indices']]['count']//3
        triangles+=count
        if mesh['name']=='Cloth_cut_for_six_pockets': table_triangles+=count
table_mat=next(m for m in doc['materials'] if m['name']=='Nocturne_Table_Atlas')
assert 'normalTexture' in table_mat and 'metallicRoughnessTexture' in table_mat['pbrMetallicRoughness']
assert all('bufferView' in image for image in doc['images'])
report={'table_triangles':table_triangles,'all_triangles':triangles,'mesh_count':len(doc['meshes']),'materials':len(doc['materials']),'embedded_images':len(doc['images']),'uv_and_tangents':True,'studio_excluded':True,'glb_bytes':len(data),'unity_editor_validation':'Not run; Unity was closed.'}
write(ROOT/'ArtSource/Billiard/validation.json',json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
