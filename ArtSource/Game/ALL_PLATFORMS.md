# Fonctionnalités communes — 19 septembre 2026

La dernière demande remplace la restriction « VR uniquement ». Les corrections
décrites dans `VR_CORRECTIONS.md` s'appliquent désormais au PC flat, au PC VR,
à la VR autonome et au mobile Android/iOS.

- Boules visuellement doublées pour tous (85,4 mm), textures et normales
  conservées. Le choix précédent d'une physique commune de 42,7 mm est conservé.
- Les six barrières invisibles de bande restent actives sur tous les clients et
  pour tous les coups. Elles ne touchent que les boules et laissent les trous libres.
- Caches en bois, flèche jaune et étiquettes locales sur tous les appareils.
  En écran plat, le champ de vision et la position viennent de la caméra affichée,
  pour respecter aussi le format portrait et la caméra mobile.
- Repositionnement depuis les deux grands panneaux : mêmes conditions de départ
  ou de proximité d'une bande, même ligne imposée, même validation réseau.
- Tir en arrière interdit sur la ligne de départ, sur tous les appareils.
- Nouvelle partie disponible à tout moment, même pendant un coup.
- Hauteur fixe de 1,65 m en partie, 9,9 m pour regarder ; taille d'origine au lobby.
  Redimensionnement manuel désactivé, saut et correction de vitesse latérale actifs.
- Point de saisie des trois putters placé sous le sommet de la poignée pour tous.
  Les orientations restent adaptées aux axes de saisie différents du SDK en VR
  et sur écran plat.

## Commandes selon l'appareil

Sur PC flat et mobile, le panneau flottant près de la blanche est supprimé et
remplacé par un HUD à l'écran : verrouillage, réglage fin de direction, puissance
et bouton Tirer. Le bouton requiert un verrouillage explicite. Sur PC, maintenir
Tab libère le curseur pour cliquer ; E verrouille et F charge/tire au clavier.
La notification locale « À VOUS DE JOUER » occupe le bandeau du HUD pendant
15 secondes. Le HUD disparaît au lobby, en mode spectateur et en VR.

En VR, le geste du putter et la gâchette restent les commandes de tir et de
verrouillage ; la notification reste placée dans la vue du casque.

Références : [Screen Canvas VRChat](https://creators.vrchat.com/worlds/examples/screen-canvas/)
et [caméra affichée](https://creators.vrchat.com/worlds/udon/vrc-graphics/vrc-camera-settings/).

La scène d'avant généralisation est sauvegardée dans `Before_All_Platforms.unity`.
La scène jouable est `Assets/Scenes/Nocturne_MiniGolf.unity`, avec son
`VRCSceneDescriptor` et l'identifiant du monde existant conservés.

Les noms de certains composants et RPC contiennent encore « VR » pour conserver
les références sérialisées ; ces noms ne limitent plus leur utilisation en jeu.
Les rapports `vr-test-report.json`, `playtest-report.json` et
`multiplayer-test-report.json` vérifient les nouvelles règles communes dans
ClientSim. Une validation avec de vrais clients PC, mobile et casque reste
nécessaire pour confirmer les entrées natives et le transport réseau réel.

Résultat : **252 contrôles réussis**, sans erreur d'exécution (95 fonctions
communes/VR, 85 commandes PC/tactiles/spectateur et 72 règles multijoueurs).
Rapport consolidé : `all-platforms-test-report.json`.

## Lisibilité et maillage des poches — 19 septembre

Les chiffres sont maintenant en gras et environ quatre fois plus grands à
distance. La taille suit la profondeur dans la vue, sans l'ancien plafonnement
qui rendait les numéros minuscules à l'autre bout de la table. Lorsque les boules
sont regroupées, leurs étiquettes sont espacées dans la vue locale et reliées par
des traits fins à leur boule. Capture de contrôle : `Numbers_From_Cue.png`.

Le bois derrière les six poches est désormais fusionné au maillage principal du
billard dans Blender. Les caches séparés ont été retirés de la scène et du
générateur. Le `.blend`, le FBX et le GLB du billard sont actualisés ; la table
compte 3 424 triangles et conserve un seul matériau avec ses textures détaillées.
Les contrôles de rayons dans Unity en mode jeu vérifient les six remplissages et
les six ouvertures : `pocket-native-validation.json`. Captures :
`Integrated_Pocket_Corner.png`, `Integrated_Pocket_Middle.png`.
