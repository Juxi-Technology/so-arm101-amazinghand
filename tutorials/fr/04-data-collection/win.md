# win

# Phase 4 : Collecte de données (Windows)

Cette phase consiste à enregistrer un jeu de données de téléopération : collecter des échantillons « angles d'articulation \+ images de caméra » sous contrôle humain, en vue de l'entraînement ultérieur. La qualité du jeu de données détermine directement l'efficacité de la politique ; **les opérations doivent être standardisées et cohérentes**. Cette phase se fait **entièrement en enregistrement local, sans connexion HF**.

---

## Prérequis

- Phase 3 : Téléopération terminée et directions vérifiées correctes

- Caméras connectées et indices relevés (`lerobot-find-cameras`)

- Chemin de stockage local du jeu de données défini (dans ce document, l'exemple utilise `D:\lerobot_data`, personnalisable)

---

## Étape 1 : Vérifier les indices des caméras

```PowerShell
lerobot-find-cameras
```

Relevez le numéro des caméras. Par exemple :

- N° 0 : caméra du poignet (wrist)

- N° 1 : caméra du dessus (top)

> **⚠️ Remarque (indices des caméras)** : `index_or_path` est l'indice de la caméra (0/1/2\.\.\.) ou le chemin d'un flux vidéo. Les numéros diffèrent d'un ordinateur à l'autre ; vérifiez-les impérativement au préalable.

---

## Étape 2 : Enregistrer le jeu de données (sauvegarde locale, sans connexion)

```PowerShell
lerobot-record --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data --dataset.push_to_hub=false --dataset.num_episodes=20 --dataset.single_task="Pick up the cube with the dexterous hand" --display_data=true
```

> Remplacez `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>` par les numéros de COM réels ; remplacez `index_or_path` des caméras par vos indices de caméra.

> **💡 Explication** :

- `--dataset.root=D:\lerobot_data` : le jeu de données est enregistré dans un **chemin local** spécifié, **sans connexion HF** (si ce paramètre est omis, il est stocké par défaut dans `%USERPROFILE%\.cache\huggingface\lerobot\datasets\...`).

- `--dataset.push_to_hub=false` : **désactive l'envoi** (par défaut, une tentative d'envoi vers HF est effectuée, ce qui nécessite une connexion). Ne le passez à `true` que si vous devez partager le jeu de données.

- `--dataset.repo_id=soarm_amazing_hand_pick` : nom du jeu de données ; utilisez le **même nom** lors de l'entraînement.

- `--display_data=true` nécessite rerun (si non installé : `pip install "rerun-sdk>=0.24.0,<0.34.0"`), ou supprimez ce paramètre (l'enregistrement n'est pas affecté).

---

## Description des paramètres

|Paramètre|Description|
|---|---|
|`--robot.cameras`|Configuration des caméras. `index_or_path` est l'indice de la caméra, `width/height/fps` sont **obligatoires**|
|`--dataset.repo_id`|Nom du jeu de données (pour l'identification locale)|
|`--dataset.root`|Chemin de stockage local du jeu de données. **Obligatoire pour un enregistrement purement local**, afin d'éviter un chemin par défaut non maîtrisé|
|`--dataset.push_to_hub`|`false` = local uniquement (recommandé par défaut) ; `true` = envoi vers HF (nécessite une connexion)|
|`--dataset.num_episodes`|Nombre d'épisodes à enregistrer (episode)|
|`--dataset.episode_time_s`|**Durée maximale en secondes par épisode** (60 par défaut). Si la tâche se termine plus tôt, appuyez sur Entrée pour terminer par anticipation ; au-delà, l'épisode se termine automatiquement|
|`--dataset.single_task`|Description de la tâche, écrite dans les métadonnées du jeu de données|
|`--display_data=true`|Affichage en temps réel des images enregistrées (facultatif)|

---

## Règles de manipulation pour l'enregistrement

**Déroulement de chaque épisode (episode)** :

1. Réinitialisez le bras \+ la main à la **position de départ**

2. Appuyez sur Entrée dans le terminal pour commencer l'enregistrement

3. Manipulez le bras maître pour exécuter la tâche (par exemple saisir un cube) ; **les gestes doivent être lents et cohérents**

4. Une fois la tâche terminée, appuyez sur Entrée pour terminer l'épisode (**sinon l'enregistrement dure au maximum 60 secondes**, contrôlé par `--dataset.episode_time_s`, et se termine automatiquement)

5. Répétez jusqu'à atteindre `num_episodes`

> **⚠️ Remarque 1 (cohérence de la position de départ)** : commencez chaque épisode à la **même position de départ** pour éviter une distribution de données désordonnée. Il est recommandé de fixer une posture de réinitialisation.

> **⚠️ Remarque 2 (cohérence des gestes)** : pour une même tâche, utilisez des trajectoires de manipulation similaires (angle d'approche, position de saisie, vitesse) ; la politique apprendra plus vite et plus stablement.

> **⚠️ Remarque 3 (qualité de l'enregistrement)** : mieux vaut enregistrer moins d'épisodes de haute qualité que beaucoup d'échantillons désordonnés. 20 épisodes constituent le point de départ pour ACT ; pour les tâches complexes, 30\-50 épisodes sont recommandés.

> **⚠️ Remarque 4 (temps réel des caméras)** : pendant l'enregistrement, évitez d'obstruer les caméras et les variations de forte lumière ; la cohérence des images affecte la généralisation.

---

## Stockage des données

- **Enregistrement local** : les données sont sauvegardées dans le répertoire spécifié par `--dataset.root` (exemple `D:\lerobot_data\soarm_amazing_hand_pick`).

- **Référence à l'entraînement** : lors de l'entraînement, utilisez le **même ****`--dataset.repo_id`**** \+ ****`--dataset.root`**, sans déplacer les fichiers manuellement :

```PowerShell
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data ...
```

- **Cas d'une connexion HF** (facultatif) : si vous devez partager le jeu de données dans le cloud, passez à `--dataset.push_to_hub=true` (nécessite `huggingface-cli login`). Pour un entraînement purement local, cela **n'est pas nécessaire**.

> **⚠️ Remarque (local vs cloud)** : par défaut, le tutoriel est entièrement local ; `--dataset.push_to_hub=false` garantit qu'aucune connexion HF n'est déclenchée. N'ajoutez `true` que si vous voulez partager le jeu de données.

---

## Étape 3 : Vérification par relecture (facultative mais recommandée)

Une fois l'enregistrement terminé, vous pouvez utiliser `lerobot-replay` pour relire les données d'un épisode et vérifier la **qualité des données \+ l'exactitude de l'enregistrement des mouvements du robot**. Lors de la relecture, le robot rejoue automatiquement les mouvements de cet épisode (y compris l'ouverture/fermeture de la main).

```PowerShell
lerobot-replay `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --dataset.repo_id=soarm_amazing_hand_pick `
  --dataset.root=D:\lerobot_data `
  --dataset.episode=0
```

> Remplacez `<follower_arm_com>` / `<hand_com>` par les numéros de COM réels ; `--dataset.episode` est le numéro de l'épisode à relire (**commence à 0** ; par exemple, si 20 épisodes ont été enregistrés, `0`\~`19`).

> **💡 Explication** : avant la relecture, **ramenez le bras esclave \+ la main à la position de départ** pour éviter les conflits de mouvement ; pendant la relecture, le robot se déplace tout seul, **n'intervenez pas manuellement**. Si les mouvements relus diffèrent nettement de ceux de l'enregistrement, la qualité des données pose problème ; il est recommandé de réenregistrer cet épisode.

---

Une fois cette phase terminée, passez à la phase 5 : Entraînement du modèle.

---

## Dépannage

|Symptôme|Cause|Solution|
|---|---|---|
|Caméra introuvable|Indice erroné / pilote manquant|Confirmez avec `lerobot-find-cameras` ; installez OpenCV / le pilote de la caméra|
|Enregistrement interrompu|Expiration du délai du port série|Vérifiez que les ports série des trois équipements ne sont pas occupés, puis réessayez|
|Image entièrement noire / brouillée|Configuration de caméra erronée|Vérifiez `index_or_path`/`fps`|
|Jeu de données vide|Enregistrement incorrect|Vérifiez que vous appuyez bien sur Entrée pour commencer/terminer chaque épisode|

