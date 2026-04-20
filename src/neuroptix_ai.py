import threading
import ollama
import psutil
import multiprocessing as mp
import zstandard as zstd
import torch
import torch.nn as nn
import random
import time
import struct

# ==============================
# MODÈLE PYTORCH
# ==============================
class MiniModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1, 16), nn.ReLU(), nn.Linear(16, 1)
        )
    def forward(self, x):
        return self.layers(x)

model = MiniModel()

# ==============================
# COMPRESSION
# ==============================
def compress(data):
    return zstd.ZstdCompressor().compress(data)

def decompress(data):
    return zstd.ZstdDecompressor().decompress(data)

def serialize(batch):
    return struct.pack(f"{len(batch)}f", *batch)

def deserialize(data):
    return list(struct.unpack(f"{len(data)//4}f", data))

def process_batch(compressed_batch):
    raw    = decompress(compressed_batch)
    batch  = deserialize(raw)
    tensor = torch.tensor(batch, dtype=torch.float32).unsqueeze(1)
    with torch.no_grad():
        output = model(tensor)
    time.sleep(0.01)
    return output.sum().item()

# ==============================
# CERVEAU IA LOCALE (Ollama)
# ==============================
def analyser_avec_ia(historique):
    """Envoie les résultats du pipeline à Phi3 pour analyse"""

    # Prépare le contexte pour l'IA
    contexte = "CPU:" + str(int(psutil.cpu_percent(interval=0.5))) + "% RAM:" + str(int(psutil.virtual_memory().percent)) + "% | " + " | ".join(["t=" + str(h['temps']) + "s s=" + str(int(h['score'])) for h in historique]) + "\nReponds en francais en 1 phrase courte: systeme optimise? que faire?"

    print("\n  Analyse IA en cours...", end=" ", flush=True)
    try:
        response = ollama.chat(
            model="phi3:mini",
            messages=[{"role": "user", "content": contexte}]
        )
        conseil = response["message"]["content"].strip()
        print("✓\n")
        return conseil
    except Exception as e:
        return f"Erreur IA : {e}"

# ==============================
# PIPELINE
# ==============================
def run_cycle(workers, batch_size=512):
    data = [random.uniform(0, 1) for _ in range(10000)]
    batches = []
    for i in range(0, len(data), batch_size):
        chunk = data[i:i + batch_size]
        batches.append(compress(serialize(chunk)))

    t1 = time.time()
    with mp.Pool(workers) as pool:
        results = pool.map(process_batch, batches)
    t2 = time.time()

    return {
        "workers" : workers,
        "temps"   : round(t2 - t1, 2),
        "score"   : round(sum(results), 2),
    }

# ==============================
# MAIN
# ==============================
# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    print("="*60)
    print("  NeurOptix — Pipeline IA + Analyse par Phi3")
    print("="*60)
    historique = []
    resultat_ia = [None]

    def lancer_analyse_ia(data):
        """Tourne en arrière-plan pendant les cycles"""
        resultat_ia[0] = analyser_avec_ia(data)

    # Lance 3 cycles
    for cycle in range(1, 4):
        cpu = psutil.cpu_percent(interval=0.5)
        workers = 4 if cpu < 75 else 2
        print(f"\n--- CYCLE {cycle}/3 ---")
        print(f"  CPU : {cpu:.1f}% · workers : {workers}")
        perf = run_cycle(workers)
        historique.append(perf)
        print(f"  Temps : {perf['temps']}s · Score : {perf['score']:.2f}")

        # Lance l'IA en arrière-plan après le 1er cycle
        if cycle == 1:
            t = threading.Thread(target=lancer_analyse_ia, args=(historique,))
            t.daemon = True
            t.start()

        time.sleep(1)

    # Récupère le résultat IA (attend max 5s)
    print("\n" + "="*60)
    print("  ANALYSE PAR L'IA LOCALE (Phi3:mini)")
    print("="*60)
    t.join(timeout=40)
    conseil = resultat_ia[0] or "⚠️ IA trop lente — aucun conseil disponible"
    print(f"  {conseil}")
    print("="*60)
