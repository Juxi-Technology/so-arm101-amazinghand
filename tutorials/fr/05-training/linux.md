# linux

# Phase 5 : Entraînement du modèle (Linux)

Cette phase utilise le jeu de données collecté pour entraîner une politique (ACT, etc.) et produire un modèle déployable. **Linux est le meilleur environnement pour l'entraînement sur GPU** — les dépendances CUDA torch sont résolues automatiquement, sans configuration manuelle.

---

## Prérequis

- Phase 4 : Collecte de données terminée

- GPU NVIDIA (recommandé), pilote CUDA (vérifiable avec `nvidia-smi`)

- Jeu de données enregistré (visible dans le cache local)

---

## Étape 1 : Vérifier l'environnement GPU

```Bash
# Vérifier le pilote CUDA
nvidia-smi

# Vérifier si torch peut utiliser CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Sortie attendue** : `CUDA: True | GPU: <your_gpu_name>`

> **⚠️ Remarque (CUDA torch)** : si `CUDA: False`, cela signifie que la version CPU de torch est installée. Réinstallez la version CUDA :

```Bash
# Source officielle (réseaux hors de Chine)
pip install torch --index-url https://download.pytorch.org/whl/cu128

# Pour les réseaux en Chine continentale, privilégier le miroir Alibaba Cloud
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> Ou bien entraînez sur CPU (`--policy.device=cpu`, mais beaucoup plus lent).

> **💡 Astuce** : `pip install -e ".[amazinghand]"` résout généralement déjà la version GPU de torch sous Linux (si un environnement CUDA est détecté). Sinon, réinstallez avec les commandes ci-dessus.

---

## Étape 2 : Entraînement

```Bash
lerobot-train \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --policy.type=act \
  --output_dir=outputs/train/soarm_amazing_hand_pick \
  --job_name=soarm_amazing_hand_pick \
  --policy.device=cuda \
  --wandb.enable=false \
  --policy.push_to_hub=false \
  --steps=60000
```

> **💡 Explication** : `--dataset.repo_id` et `--dataset.root` doivent être **parfaitement identiques** à ceux de l'enregistrement de la phase 4 (`repo_id=soarm_amazing_hand_pick`, `root=~/lerobot_data`) pour pouvoir lire le jeu de données local, sans connexion HF.

---

## Description des paramètres

|Paramètre|Description|
|---|---|
|`--dataset.repo_id`|Nom du jeu de données (identique à celui de l'enregistrement)|
|`--dataset.root`|Chemin local du jeu de données (identique à celui de l'enregistrement)|
|`--policy.type`|Type de politique ; `act` est un choix courant|
|`--output_dir`|Répertoire de sortie de l'entraînement (checkpoints, journaux)|
|`--job_name`|Nom de la tâche (pour distinguer les journaux)|
|`--policy.device`|`cuda` (GPU) ou `cpu`|
|`--wandb.enable`|Journalisation des poids ; `false` la désactive (aucun compte wandb requis)|
|`--policy.push_to_hub`|Indique s'il faut envoyer le modèle vers HF ; `false` = local uniquement|
|`--steps`|Nombre de pas d'entraînement|

---

## Explication du processus d'entraînement

- **checkpoints** : enregistrés automatiquement à chaque pas dans `outputs/train/soarm_amazing_hand_pick/checkpoints/`

- **Journaux** : le terminal affiche en temps réel des indicateurs tels que la loss

- **Durée** : 60000 pas prennent généralement plusieurs heures sur un GPU grand public (cela dépend de la carte graphique)

> **⚠️ Remarque 1 (ajustement du nombre de pas)** : `--steps=60000` est une valeur typique pour ACT. Pour une tâche simple, vous pouvez réduire à 30000 ; pour une tâche complexe, augmenter à 100000\+. Observez la convergence de la loss.

> **⚠️ Remarque 2 (reprise après interruption)** : après une interruption, relancer la **commande avec les mêmes paramètres** reprendra à partir du dernier checkpoint.

> **⚠️ Remarque 3 (wandb)** : si vous souhaitez visualiser la courbe de loss, activez `--wandb.enable=true` (nécessite `wandb login`). Désactivé par défaut.

> **⚠️ Remarque 4 (serveur sans écran)** : si vous entraînez sur un serveur en SSH / sans écran, veillez à ne pas dépendre d'une GUI (l'entraînement lui-même n'a pas besoin d'affichage). Si vous utilisez des paramètres liés à `--display_data`, un serveur d'affichage est nécessaire.

> **⚠️ Remarque 5 (entraînement en arrière-plan)** : pour un entraînement long, il est recommandé d'utiliser `nohup ... &` ou `tmux` pour maintenir le processus, afin d'éviter une interruption lors d'une déconnexion SSH :

```Bash
tmux new -s train
lerobot-train --dataset.repo_id=...
# Ctrl+B puis D pour se détacher ; tmux attach -t train pour revenir
```

---

Une fois cette phase terminée, passez à la phase 6 : Déploiement et évaluation.

---

## Dépannage

|Symptôme|Cause|Solution|
|---|---|---|
|`CUDA: False`|Version CPU de torch|Réinstaller la version CUDA de torch|
|Mémoire GPU insuffisante (OOM)|Taille de lot trop grande|`--policy.batch_size=8` ou moins|
|Jeu de données introuvable|repo\_id/root incohérents|Vérifiez que `--dataset.repo_id` et `--dataset.root` sont parfaitement identiques à ceux de l'enregistrement|
|Coupure SSH en cours d'entraînement|Processus tué|Entraînez en arrière-plan avec `tmux`/`nohup`|
|Erreur `wandb`|Non connecté|`--wandb.enable=false` ou `wandb login`|

