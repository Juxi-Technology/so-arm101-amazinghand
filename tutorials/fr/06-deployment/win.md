# win

# Phase 6 : Déploiement et évaluation (Windows)

Cette phase charge la politique entraînée pour que le robot **exécute la tâche de manière autonome** et enregistre une vidéo d'évaluation afin de vérifier le résultat. C'est la conclusion de tout le processus et un moment clé pour valider le fruit de l'entraînement.

---

## Prérequis

- Phase 5 : Entraînement du modèle terminée

- L'entraînement a produit `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`

- Indices des caméras relevés

---

## Étape 1 : Vérifier les fichiers du modèle

```PowerShell
# Vérifier que le répertoire du modèle existe
dir outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model
```

Doit contenir des fichiers de modèle tels que `model.safetensors`.

> **⚠️ Remarque (chemin du modèle)** : `--policy.path` doit pointer vers le répertoire `pretrained_model` (contenant la configuration \+ les poids), et non vers le répertoire racine du checkpoint.

---

## Étape 2 : Déploiement et évaluation

```PowerShell
lerobot-record `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' `
  --policy.path=outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model `
  --dataset.repo_id=soarm_amazing_hand_pick_eval `
  --dataset.root=D:\lerobot_data `
  --dataset.push_to_hub=false `
  --dataset.num_episodes=10 `
  --dataset.single_task="Pick up the cube with the dexterous hand" `
  --display_data=true
```

> Remplacez `<follower_arm_com>` / `<hand_com>` par les numéros de COM réels ; remplacez `index_or_path` des caméras par vos indices de caméra.

> **💡 Explication** : on utilise `lerobot-record` mais **sans ****`--teleop.type`** ; la politique contrôle alors le robot de manière autonome (en remplacement de la téléopération manuelle). Les données sont sauvegardées en tant que jeu d'évaluation. `--dataset.root` / `--dataset.push_to_hub=false` sont identiques à ceux de la phase 4 ; une sauvegarde purement locale ne nécessite aucune connexion HF.

---

## Opérations d'évaluation

1. Réinitialisez le robot \+ la main à la **position de départ**

2. Appuyez sur Entrée pour commencer : la politique exécute la tâche de manière autonome

3. Observez **si la saisie réussit** (appuyez sur Entrée à la fin de chaque épisode pour continuer)

4. Répétez sur `num_episodes` épisodes

**Indicateur d'évaluation** : taux de réussite = nombre d'épisodes réussis / nombre total d'épisodes

> **⚠️ Remarque 1 (cohérence de la réinitialisation)** : commencez chaque épisode à la **même position de départ**, sinon la politique échoue à généraliser et le taux de réussite est artificiellement bas.

> **⚠️ Remarque 2 (sécurité)** : lors de la première exécution autonome, il est recommandé d'observer en **maintenant le robot / à vitesse réduite** pour confirmer que les mouvements de la politique sont raisonnables. La politique peut produire des mouvements inattendus.

> **⚠️ Remarque 3 (taux de réussite attendu)** : ACT atteint généralement 50\-80 % de réussite avec 20 épisodes de données. Si le résultat est inférieur aux attentes, retournez enregistrer des données supplémentaires ou ajustez le nombre de pas d'entraînement.

---

## Optimisation itérative

Si le taux de réussite de l'évaluation n'est pas satisfaisant, ajustez par ordre de priorité :

|Priorité|Élément d'optimisation|Action|
|---|---|---|
|1|Enregistrer des données supplémentaires de haute qualité|Retournez à la phase 4 et enregistrez 20\-30 épisodes de données plus cohérentes|
|2|Augmenter le nombre de pas d'entraînement|Retournez à la phase 5, `--steps=100000`|
|3|Vérifier la cohérence de la position de départ|Réinitialisez strictement à chaque épisode lors de l'évaluation|
|4|Ajuster la description de la tâche|Assurez-vous que `single_task` correspond à la tâche|

---

Vous avez ainsi réalisé la **boucle complète** de SO\-ARM101 \+ AmazingHand : calibration → téléopération → collecte → entraînement → déploiement.

---

## Dépannage

|Symptôme|Cause|Solution|
|---|---|---|
|Échec du chargement du modèle|Chemin erroné / incomplet|Vérifiez que `--policy.path` pointe vers le répertoire `pretrained_model`|
|La politique ne bouge pas|Caméra / observation incorrecte|Vérifiez que les indices des caméras correspondent à ceux de l'entraînement ; vérifiez l'image de `--display_data`|
|La politique s'agite|Position de départ incohérente / données médiocres|Réinitialisez strictement ; enregistrez des données supplémentaires|
|Comportement différent de celui de l'entraînement|Différences d'environnement|Vérifiez que la caméra, l'éclairage et la position des objets sont identiques à ceux de l'enregistrement|

