import subprocess
import sys

# Grille 1 : Régression logistique (5 valeurs de C x 3 seuils = 15 runs)
c_values = [0.001, 0.01, 0.1, 1.0, 10.0]
thresholds = [0.15, 0.2, 0.25]

# Grille 2 : Forêt aléatoire (5 valeurs de C/réglages x 3 seuils = 15 runs)
# Note : selon les options de maintai/train.py, on fait varier --threshold et --model
models_configs = []

for c in c_values:
    for th in thresholds:
        models_configs.append(["--model", "logreg", "--C", str(c), "--threshold", str(th)])

# Ajout de 15 configurations supplémentaires (total = 30 runs max)
more_c = [0.005, 0.05, 0.5, 2.0, 5.0]
more_th = [0.18, 0.22, 0.3]

for c in more_c:
    for th in more_th:
        models_configs.append(["--model", "logreg", "--C", str(c), "--threshold", str(th)])

# Sécurité : limiter strictement à 30 runs maximum
configs_to_run = models_configs[:30]

print(f"Démarrage du Grid Search : {len(configs_to_run)} runs prévus...")

for i, args in enumerate(configs_to_run, start=1):
    cmd = [sys.executable, "-m", "maintai.train"] + args
    print(f"\n[{i}/{len(configs_to_run)}] Exécution : {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

print("\nGrid Search terminé ! Ouvre MLflow UI (http://localhost:5000) pour trier par 'recall'.")