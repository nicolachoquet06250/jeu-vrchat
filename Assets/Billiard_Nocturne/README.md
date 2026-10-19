# Billard Nocturne

Billard américain original à six poches, noyer sombre, tapis vert, cuir et incrustations métalliques. Créé dans Blender 5.2.1 via MCP.

## Fichiers et budget

| Élément | Géométrie | Matériaux |
| --- | ---: | ---: |
| `Billiard_Nocturne_Table.fbx` | 3 424 triangles, 1 mesh | 1 |
| `Billiard_Nocturne_Balls.fbx` | 16 billes indépendantes, 224 triangles chacune | 1 partagé |
| Ensemble | 7 008 triangles, 17 meshes | 2 |

- Dimensions extérieures : 2,94 × 1,67 m ; dessus des rails à environ 0,872 m.
- Surface du tapis : 2,54 × 1,27 m, altitude 0,80 m.
- Billes : diamètre 57,15 mm ; pivots au centre de chaque bille.
- Géométrie triangulée, UV et tangentes exportées, biseaux à un segment, aucun modificateur coûteux à exécuter.
- Six véritables ouvertures dans le tapis et le caisson, avec puits en cuir à fond fermé à 0,54 m.
- Un mesh et un matériau pour toute la table. Les 16 billes restent séparées pour permettre leur animation ; deux matériaux ne signifient donc pas deux draw calls pour l'ensemble.

## Textures

Atlas original partagé de 2 048 × 2 048 pixels pour la table. Les zones bois, tapis et cuir occupent chacune un quadrant ; les petits éléments partagent le dernier quadrant. Les détails sont procéduraux, sans textures externes.

| Texture | Usage |
| --- | --- |
| `Table_BaseColor.png` | Couleur, sRGB |
| `Table_Normal.png` | Normal map tangentielle, +Y/OpenGL ; import Unity en **Normal map** |
| `Table_MetallicSmoothness.png` | Unity Standard : rouge = métal, alpha = lissage ; données linéaires |
| `Table_ORM.png` | glTF/Blender : rouge = 1, vert = rugosité, bleu = métal ; données linéaires |
| `Balls_BaseColor.png` | Atlas de 1 024 × 1 024 pixels pour les 16 billes numérotées |

La normal map provient des gradients des mêmes motifs de hauteur que le veinage, le tissage et le grain du cuir : elle correspond aux détails de couleur. Il ne s'agit pas d'un bake depuis un modèle high-poly. Le canal rouge ORM est neutre : aucune occlusion ambiante n'est précalculée.

## Unity

Les deux matériaux Standard sont dans `Materials`. Les fichiers `.meta` relient les FBX à leurs matériaux et règlent l'import des textures : mipmaps, compression, normal map et espaces colorimétriques. Conserver ces `.meta` avec les fichiers.

Glisser `Billiard_Nocturne_Table.fbx` dans la scène. Ajouter `Billiard_Nocturne_Balls.fbx` à la même origine pour retrouver la disposition du rendu. Échelle d'import : 1 ; les unités du fichier sont prises en compte. Pour un billard géant, appliquer le même facteur d'échelle à la table et aux billes.

Les matériaux utilisent le shader Standard du pipeline intégré du projet. Ils ne constituent pas une configuration mobile Quest validée. Les collisions, les rigidbodies, la synchronisation et les règles de jeu ne sont pas inclus dans cet asset visuel.

Références Unity : [import des normal maps](https://docs.unity.cn/Manual/StandardShaderMaterialParameterNormalMapImport.html), [lissage dans le canal alpha](https://docs.unity.cn/Manual/StandardShaderMaterialParameterSmoothness.html).

## Sources et vérifications

Dans `ArtSource/Billiard` à la racine du projet :

- `Billiard_Nocturne.blend` : source modifiable avec textures embarquées, studio et caméra ; la scène de démarrage initiale est conservée séparément.
- `Billiard_Nocturne.glb` : table + billes, matériaux PBR et images embarquées ; studio exclu.
- `Nocturne_Preview.png` : rendu de contrôle.
- Scripts de construction, génération des textures et préparation des fichiers Unity.
- `validation.json` et `fbx_validation.json` : contrôles des fichiers exportés.

Contrôles effectués : inspection visuelle dans Blender, réimport des deux FBX pour vérifier triangles et dimensions, analyse du GLB (17 meshes, 2 matériaux, 4 images embarquées, UV et tangentes), absence de triangles dégénérés sur la table et rayons de contrôle atteignant le fond des six poches.

Import effectué dans **Unity 2022.3.22f1** : matériaux et normal map reliés, dimensions et triangles vérifiés. L'orientation du tapis a été corrigée dans le `.blend` et les exports pour l'affichage avec culling dans Unity. Les prefabs sont dans `Prefabs` et la scène de présentation est `Assets/Scenes/Nocturne_Models.unity`. Le rapport et le rendu Unity sont dans `ArtSource/Unity`.
