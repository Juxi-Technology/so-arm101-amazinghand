# win

# Phase 3 : Téléopération (Windows)

Cette phase met en route la boucle de téléopération : le bras maître commande les mouvements du bras esclave, et la pince commande l'ouverture/fermeture de l'AmazingHand. C'est une phase clé pour vérifier si l'ensemble du système fonctionne correctement.

---

## Prérequis

- Phase 1 : Configuration de l'environnement et Phase 2 : Calibration terminées

- Les trois équipements sont sous tension et leurs ports série sont relevés

---

## Lancer la téléopération

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Remplacez `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>` par les numéros de COM réels de votre machine (exemple `COM58` / `COM11` / `COM54`).

**Effet attendu** :

- Les 5 articulations du bras maître → le bras esclave suit

- La pince du bras maître → ouverture/fermeture de l'AmazingHand (suivi proportionnel : à moitié pincée = à moitié fermée)

> **💡 Description des paramètres** :

- `--robot.type=so101_amazing_hand` : robot combiné bras esclave \+ main

- `--robot.port` : port série du bras esclave

- `--robot.hand_port` : port série de la main

- `--teleop.type=so101_leader` : téléopérateur du bras maître

- `--teleop.port` : port série du bras maître

---

## À faire impérativement au premier lancement : vérification des directions

Après le démarrage, effectuez d'abord un **test de direction** pour confirmer que les deux points suivants sont corrects :

|Test|Opération|Phénomène correct|
|---|---|---|
|Suivi du bras|Faire tourner chaque articulation du bras maître|Le bras esclave suit dans le même sens|
|Ouverture/fermeture de la main|Ouvrir/pincer la pince du bras maître|Pince ouverte → main ouverte ; pince pincée → main fermée|

> **⚠️ Remarque (que faire si la direction est inversée)** :

- **Direction d'ouverture/fermeture de la main inversée** (la main se ferme alors que la pince s'ouvre) : cela signifie que les angles de la main sont mal calibrés ; réexécutez l'outil de calibration (y compris la calibration de la direction de la pince), l'effet sera automatique après l'enregistrement, **sans modification manuelle des fichiers**. Voir Phase 2 : Calibration.

- **Direction du mappage de la pince inversée** (la main se ferme alors que la pince s'ouvre) : idem ; lors de la calibration, cliquez sur `[Capture Open]` quand la pince du bras maître est **ouverte** et sur `[Capture Close]` quand elle est **pincée** ; l'outil enregistre automatiquement `gripper_open_pos`/`gripper_close_pos` et les charge au démarrage.

> Après modification, **relancez la téléopération** pour vérifier.

---

## Vérification du suivi proportionnel

Une fois les directions correctes, vérifiez la finesse du suivi proportionnel :

1. Ouvrez **lentement** la pince → la main doit s'ouvrir **de façon fluide** (sans saut)

2. Arrêtez la pince à **mi-course** → la main doit également s'arrêter à mi-course

3. Ouvrez/fermez rapidement → la main réagit rapidement, sans à-coup

> **⚠️ Remarque (problème historique d'ouverture/fermeture excessive de la main)** : si la main se ferme alors que la pince est à moitié ouverte, c'est le plus souvent que les positions « ouverte/poing fermé » sont imprécises lors de la calibration des angles de la main. Réexécutez l'étape 3 de calibration (GUI des angles de la main) pour calibrer des positions d'ouverture/fermeture plus précises.

---

## Facultatif : visualisation avec caméra

Ajoutez `--robot.cameras` pour connecter une caméra et `--display_data=true` pour ouvrir la fenêtre de visualisation Rerun (affichage en temps réel des images de la caméra \+ de l'état des articulations) :

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --display_data=true
```

> **💡 Explication** :

- `index_or_path` est l'indice de la caméra ; confirmez-le d'abord avec `lerobot-find-cameras` (les numéros diffèrent d'une machine à l'autre).

- `fourcc: "MJPG"` est facultatif ; il réduit nettement la bande passante occupée par la caméra USB (passage à la compression MJPEG) et peut être ajouté en cas de saccades.

- Si une seule caméra est nécessaire, supprimez la ligne correspondante (par exemple `top`).

> **⚠️ Remarque (dépendance rerun)** : `--display_data=true` nécessite le paquet de visualisation rerun ; s'il n'est pas installé, exécutez :

```PowerShell
pip install "rerun-sdk>=0.24.0,<0.34.0"
```

> Nécessite l'exécutable Rerun Viewer. Sous Windows, si l'erreur `Failed to find Rerun Viewer executable` apparaît, cela signifie que le visualiseur GUI est absent. Cela **n'affecte pas la téléopération** : supprimez simplement `--display_data=true`.

---

## Quitter

Appuyez sur `Ctrl+C` pour arrêter. Le programme effectue automatiquement :

1. Relâche le couple des 8 servomoteurs de la main

2. Déconnecte les ports série du bras esclave/du bras maître

3. Déconnecte la caméra (le cas échéant)

> **⚠️ Remarque** : avant une sortie normale, **ne fermez pas directement le terminal**, sinon une occupation résiduelle du port série peut subsister. Si le port série est occupé après une sortie anormale, rebranchez l'USB ou redémarrez le processus du terminal.

---

## Dépannage

|Symptôme|Cause|Solution|
|---|---|---|
|Direction de la main inversée|Angles de la main ou mappage de la pince inversés|Voir « Vérification des directions » ci-dessus ; échangez les angles ou ajustez le mappage|
|Ouverture/fermeture de la main excessive/insuffisante|Angles de la main mal calibrés|Recalibrer la GUI des angles de la main|
|Le bras ne suit pas|Calibration manquante / port série incorrect|Vérifiez que le bras esclave est calibré et que `--robot.port` est correct|
|Erreur rerun|Dépendance de visualisation manquante|Supprimez `--display_data=true`|
|Port série occupé|Sortie anormale précédente|Fermez le processus qui l'occupe ou rebranchez l'USB|

