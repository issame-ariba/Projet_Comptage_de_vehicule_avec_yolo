# Ticket de sortie · Séance 7

**Nom :** KENZA ELAIATI — CHAIMAA HADDAD  
**Groupe :** Binôme  

1. **Qu’est-ce que le MLOps ajoute au DevOps ?**
   Le DevOps gère un seul élément qui évolue : le **code**. Le MLOps ajoute la gestion et le suivi de deux autres éléments qui changent : les **données** (qui peuvent dériver) et le **modèle** (avec ses paramètres, ses métriques et ses dépendances).

2. **Que versionnent Git, DVC et MLflow ?**
   - **Git** : le code source, la documentation et les petits fichiers `.dvc` (reçus de 4–5 lignes).
   - **DVC** : les fichiers de données (stockés hors Git dans un cache local et un stockage distant).
   - **MLflow** : chaque entraînement (« run ») avec ses paramètres, l’empreinte `data_md5` des données, ses métriques, le modèle et les versions exactes des bibliothèques (`requirements.txt`).

3. **Pourquoi `data/sensors.csv` n’est-il pas dans Git ?**
   Parce qu’un fichier de données peut être très volumineux et changer fréquemment ; Git gère mal les gros fichiers binaires ou de données et conserverait chaque version dans tout l’historique. On ne met dans Git que le léger reçu `data/sensors.csv.dvc`.

4. **À partir d’un run MLflow, comment retrouver ses données ?**
   On lit le paramètre `data_md5` du run dans MLflow, puis on retrouve le commit Git où `data/sensors.csv.dvc` contient ce même `md5`, et on exécute `git checkout <commit> -- data/sensors.csv.dvc` suivi de `dvc checkout` (ou `dvc pull`) pour restaurer exactement le fichier de données correspondant.

5. **Qu’est-ce qui reste flou pour vous ?**
   Rien de bloquant ; le lien entre Git, DVC et MLflow est compris.
