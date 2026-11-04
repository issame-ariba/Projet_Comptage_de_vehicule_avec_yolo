# ADR 003 : Sécurisation de l'API (Clé et CORS)

Date : 04/11/2026 · Auteurs : Abderrahmane Sbaii

## Contexte
L'API MaintAI doit restreindre son accès aux seuls clients autorisés sans exposer de secrets dans le code ou sur GitHub[cite: 6]. De plus, elle doit autoriser les requêtes provenant d'une page web locale spécifique (localhost:5500) tout en bloquant les autres origines pour protéger les utilisateurs[cite: 5, 6]. 

## Options étudiées

**Pour la transmission de la clé API :**
1. Clé dans l'URL : Facile à implémenter, mais dangereux car la clé finit enregistrée partout (historiques de navigation, journaux du serveur)[cite: 4].
2. Clé dans l'en-tête (Header `X-API-Key`) : Plus discret, n'apparaît pas dans les logs des serveurs ni dans les URL, et correspond aux standards web[cite: 4].

**Pour la configuration des origines CORS :**
1. Origines écrites en dur dans le code (`main.py`) : Simple, mais les valeurs finissent sur GitHub pour toujours et on ne peut pas les modifier en production sans changer le code[cite: 5].
2. Origines lues depuis le fichier `.env` : Le fichier n'est pas versionné par Git (grâce au `.gitignore`), ce qui permet d'avoir une configuration différente par machine (développement vs production) sans toucher au code source[cite: 5].

## Décision
Nous transmettons la clé API via l'en-tête HTTP `X-API-Key`[cite: 4]. Nous gérons la liste des origines CORS autorisées via le fichier `.env` (exclu de Git)[cite: 5].

## Conséquences
Ces décisions renforcent la sécurité. Cependant, elles obligent chaque développeur à créer son propre fichier `.env` à partir du `.env.example` pour faire fonctionner l'API[cite: 5]. De plus, tous les clients (JavaScript `fetch`, requêtes `curl`) doivent être explicitement codés pour inclure l'en-tête `X-API-Key`[cite: 4, 8].