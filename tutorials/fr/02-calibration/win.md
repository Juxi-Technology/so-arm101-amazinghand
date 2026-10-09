# win

# Phase 2 : Calibration (Windows)

Cette phase consiste à calibrer trois équipements : le bras maître, le bras esclave et la main AmazingHand. La calibration est indispensable à l'exactitude de la téléopération ; **vous devez terminer cette phase avant de passer à la téléopération**.

> **Ordre de calibration** : bras maître → bras esclave \+ main → angles de la main. Chaque étape nécessite une **interaction dans le terminal** (manipulation physique \+ appui sur une touche).

> **⚠️ Rappel général** : les paramètres de port série des commandes de cette page sont des **valeurs de substitution d'exemple** ; vous devez les remplacer par les numéros de COM réels de votre machine (voir les ports série relevés à la phase 1).

---

## Prérequis

- Phase 1 : Configuration de l'environnement terminée

- Environnement conda `lerobot` activé

```Plain Text
# Activer l'environnement
conda activate lerobot

# Se placer dans lerobot
cd ../lerobot
```

- Ports série des trois équipements relevés

- Équipements sous tension, alimentés indépendamment

---

## Étape 1 : Calibrer le bras maître

```PowerShell
lerobot-calibrate --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Remplacez `<leader_arm_com>` par le numéro de COM réel de votre machine (exemple `COM54`).

**Étapes interactives** :

1. Amenez **toutes les articulations du bras maître en position médiane**, puis appuyez sur Entrée

2. Poussez **chaque articulation l'une après l'autre jusqu'à sa butée maximale/minimale**, puis appuyez sur Entrée une fois terminé

**Vérification** : le fichier de calibration est enregistré automatiquement dans
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\teleoperators\so_leader\amazing_hand_leader.json`

> **⚠️ Remarque 1 (la pince doit être calibrée)** : la plage du servomoteur de la pince n° 6 sert de référence de normalisation pour `gripper.pos` (0\~100). La pince doit impérativement être poussée de l'ouverture complète à la fermeture complète et calibrée correctement, sinon le rapport d'ouverture/fermeture de la main sera ensuite faussé.

> **⚠️ Remarque 2 (rotation libre)** : pendant la calibration, le bras doit pouvoir tourner librement ; assurez-vous que les servomoteurs sont à vide.

> **⚠️ Remarque 3 (emplacement du fichier de calibration)** : sous Windows, le chemin se situe dans le répertoire utilisateur `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`.

---

## Étape 2 : Calibrer le bras esclave (avec la main connectée)

```PowerShell
lerobot-calibrate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower
```

> Remplacez `<follower_arm_com>` / `<hand_com>` par les numéros de COM réels (exemple `COM58` / `COM11`).

**Étapes interactives** :

1. Amenez les **5 articulations** du bras esclave (pas de n° 6) en position médiane, puis appuyez sur Entrée

2. Faites parcourir à chaque articulation toute sa course, puis appuyez sur Entrée

**Vérification** : le fichier de calibration est enregistré dans
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\amazing_hand_follower.json`

> **⚠️ Remarque 1 (couple de la main activé automatiquement)** : lors de la connexion, cette commande **active automatiquement le couple des 8 servomoteurs de la main** (le journal affiche `enabling AmazingHand torque`) ; à la fin de la calibration, la main s'ouvre, ce qui est normal.

> **⚠️ Remarque 2 (aucune GUI de la main ne s'ouvre)** : les angles de la main **n'utilisent pas** le `RangeFinderGUI` de lerobot ; la calibration s'arrête à la fin de celle du bras esclave. Les angles de la main se règlent avec l'outil dédié de l'étape 3.

> **⚠️ Remarque 3 (occupation du port série)** : cette étape occupe le port série de la main. **N'exécutez pas** en même temps d'autres processus utilisant ce port série.

---

## Étape 3 : Calibrer les angles de la main \+ la direction de la pince (GUI dédiée)

```PowerShell
lerobot-calibrate-amazing-hand --hand_port <hand-port> --leader_port <leader-port>
```

> Remplacez `<hand_com>` / `<leader_arm_com>` par les numéros de COM réels (exemple `COM11` / `COM54`). `--leader_port` sert à calibrer simultanément la **direction de la pince** (voir ci-dessous).

**Opérations dans la GUI** :

1. Faites glisser les curseurs des 4 doigts (index/middle/ring/thumb) pour **ouvrir complètement** la main, puis cliquez sur **`Save Open`**

2. Faites glisser les curseurs pour **fermer complètement le poing**, puis cliquez sur **`Save Close`**

3. **Ouvrez la pince du bras maître**, puis cliquez sur **`Capture Open`** (la GUI affiche `gripper.pos` en temps réel ; à l'ouverture, la valeur doit être proche de 100)

4. **Pincez la pince du bras maître**, puis cliquez sur **`Capture Close`** (au pincement, la valeur doit être proche de 0)

5. **Enregistrement automatique** : une fois les quatre valeurs ci-dessus définies, une bannière verte `AUTO-SAVED to ...\hand_angles.json` s'affiche en haut de la fenêtre et le terminal affiche le chemin en parallèle

6. Fermez la fenêtre (le couple de la main est automatiquement relâché)

**Vérification** : les angles et le mappage de la pince sont enregistrés dans
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\hand_angles.json`

> **⚠️ Remarque 1 (calibration obligatoire)** : **cette étape doit être effectuée pour chaque nouvel ordinateur / chaque main**. Les angles du config sont les valeurs par défaut génériques officielles d'AmazingHand et ne servent que de secours ; si `hand_angles.json` existe, vos valeurs mesurées sont chargées en priorité. Ne pas calibrer peut entraîner des erreurs de direction/plage d'ouverture-fermeture.

> **⚠️ Remarque 2 (chargement automatique)** : à chaque démarrage, le robot lit `hand_angles.json` (contenant `gripper_open_pos`/`gripper_close_pos`) et écrase les valeurs par défaut du config, **sans modification du code**. La direction de la pince varie selon le bras maître ; une seule calibration suffit.

> **⚠️ Remarque 3 (sémantique des curseurs)** : déplacer le curseur vers `+` fait aller le m1 de ce doigt vers `+angle` et le m2 vers `-angle` (symétrie). Jugez l'ouverture/fermeture d'après la **posture réelle de la main**, sans vous soucier des valeurs d'angle.

> **⚠️ Remarque 4 (calibration précise)** : lors de la calibration de la « pleine ouverture », n'allez pas trop loin (doigts de travers/écartés) ; pour le « poing fermé », ne serrez pas excessivement (les servomoteurs resteraient sous contrainte). Sinon, l'ouverture/fermeture sera excessive lors de la téléopération.

> **⚠️ Remarque 5 (ordre des Capture)** : `Capture Open` / `Capture Close` correspondent à l'ouverture/fermeture de la **pince du bras maître**, et non aux doigts de la main. Si la direction d'ouverture de la main est inversée, c'est probablement une inversion ici ou dans les angles de la main ; recalibrez.

> **⚠️ Remarque 6 (la GUI ne s'ouvre pas)** : vérifiez que `pygame` est installé (inclus dans l'extra `amazinghand`). Si elle ne s'ouvre toujours pas, vérifiez la présence d'un environnement de bureau graphique.

---

## Recalibration

Pour ne recalibrer qu'une partie :

- **Recalibrer uniquement la main** → exécuter seulement l'étape 3

- **Recalibrer uniquement le bras esclave** → exécuter seulement l'étape 2 (le couple de la main sera également activé au passage)

- **Tout recalibrer** → étapes 1 → 2 → 3

> **⚠️ Remarque** : les étapes 2 et 3 **ne peuvent pas être exécutées simultanément** (toutes deux occupent le port série de la main).

---

Une fois cette phase terminée, passez à la phase 3 : Téléopération.

---

## Dépannage

|Symptôme|Cause|Solution|
|---|---|---|
|Erreur de modèle 2307 lors de la calibration du bras maître|Bus du bras pollué / conflit de port série<br>|Vérifiez que le port série de la main n'est pas connecté en même temps ; dans ce projet, la main passe par rustypot, ce qui l'évite|
|Aucune GUI ne s'affiche pour la calibration de la main|Commande erronée utilisée|Vous devez utiliser `lerobot-calibrate-amazing-hand` (et non `lerobot-calibrate`)|
|Le pilote de la main signale `Operation timed out`|Port série occupé / temporisation|Vérifiez que le port série de la main n'est pas occupé, puis réessayez|
|Fichier de calibration introuvable|Chemin incorrect<br>|Vérifiez `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`|
|Le port série ne s'ouvre pas|Numéro de COM incorrect|Revérifiez avec `lerobot-find-port`|

