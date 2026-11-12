"""Client Python de l'API MaintAI : ce que fetch faisait dans la page web (TP2), en Python.
 
Usage :
    from maintai.client import MaintaiClient
    api = MaintaiClient("http://localhost:8000", api_key="demo123")
    api.predict({"temperature_c": 72, "vibration_mm_s": 6, "load_pct": 85, "runtime_hours": 15000})
"""
import httpx
 
 
class APIError(Exception):
    """L'API a répondu, mais pas 200 : on garde le code et le message."""
 
    def __init__(self, status_code: int, detail):
        super().__init__(f"Erreur {status_code} : {detail}")
        self.status_code = status_code
        self.detail = detail
 
 
class MaintaiClient:
    def __init__(self, url: str = "http://localhost:8000", api_key: str | None = None,
                 http: httpx.Client | None = None):
        # Les tests passent leur TestClient dans http : même code, sans serveur
        self.http = http or httpx.Client(base_url=url, timeout=5.0)
        self.api_key = api_key
 
    def health(self) -> dict:
        r = self.http.get("/health")
        r.raise_for_status()
        return r.json()
 
    def predict(self, reading: dict) -> dict:
        """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
        # 1. L'en-tête d'authentification, comme headers: {"X-API-Key": ...} dans le fetch du TP2.
        #    On ne l'ajoute que si une clé est donnée : `if self.api_key` écarte à la fois None
        #    et la chaîne vide (champ « Clé API » laissé vide dans Streamlit). Sans en-tête,
        #    l'API répond 401, ce qui est le comportement attendu.
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
 
        # 2. Le POST. On passe par self.http et non par httpx.post : self.http vaut soit un
        #    vrai httpx.Client (base_url = l'URL de l'API), soit le TestClient des tests.
        #    Le chemin est donc relatif ("/v1/predict"), la base_url fait le reste.
        #    json=reading : httpx convertit le dictionnaire en JSON et ajoute
        #    Content-Type: application/json (l'équivalent de JSON.stringify en JS).
        #    Si le serveur est arrêté, cette ligne lève httpx.ConnectError (une httpx.HTTPError) :
        #    on la laisse remonter, c'est à l'interface de l'afficher.
        r = self.http.post("/v1/predict", json=reading, headers=headers)
 
        # 3. L'API a répondu, mais a refusé (401 clé absente/fausse, 422 relevé invalide,
        #    503 modèle non chargé...). FastAPI met toujours l'explication dans "detail".
        #    On lève notre propre exception pour que l'appelant n'ait pas à lire les codes HTTP.
        if r.status_code != 200:
            try:
                detail = r.json().get("detail")
            except ValueError:
                # Corps qui n'est pas du JSON (page d'erreur d'un proxy, par exemple) :
                # on garde le texte brut plutôt que de planter.
                detail = r.text
            raise APIError(r.status_code, detail)
 
        # 4. Succès : le dictionnaire de PredictionOut, par exemple
        #    {"failure_probability": 0.9553, "alert": True, "threshold": 0.3, "model_version": "..."}
        return r.json()
 
