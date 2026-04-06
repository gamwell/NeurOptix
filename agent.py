import psutil
import multiprocessing as mp
import zstandard as zstd
import torch
import torch.nn as nn
import random
import time
import struct

# ==============================
# CONFIG DE L'AGENT
# ==============================
CONFIG = {
    "cpu_limit"    : 75.0,   # seuil % CPU avant réduction
    "max_workers"  : 4,      # workers max (i5-9500)
    "batch_size"   : 512,    # taille d'un batch
    "cycles"       : 5,      # nombre de cycles autonomes
    "sleep_cycle"  : 2.0,    # pause entre cycles (secondes)
}

# ==============================
# MODÈLE IA
# ==============================
class MiniModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )
    def forward(self, x):
        return self.layers(x)

model = MiniModel()

# ==============================
# COMPRESSION
# ==============================
def compress(data: bytes) -> bytes:
    return zstd.ZstdCompressor().compress(data)

def decompress(data: bytes) -> bytes:
    return zstd.ZstdDecompressor().decompress(data)

def serialize(batch):
    return struct.pack(f"{len(batch)}f", *batch)

def deserialize(data):
    return list(struct.unpack(f"{len(data)//4}f", data))

# ==============================
# TRAITEMENT
# ==============================
def process_batch(compressed_batch):
    raw    = decompress(compressed_batch)
    batch  = deserialize(raw)
    tensor = torch.tensor(batch, dtype=torch.float32).unsqueeze(1)
    with torch.no_grad():
        output = model(tensor)
    time.sleep(0.01)
    return output.sum().item()

def create_compressed_batches(n=10000):
    data = [random.uniform(0, 1) for _ in range(n)]
    batches = []
    for i in range(0, len(data), CONFIG["batch_size"]):
        chunk = data[i:i + CONFIG["batch_size"]]
        batches.append(compress(serialize(chunk)))
    return batches

# ==============================
# CERVEAU DE L'AGENT
# ==============================
class Agent:
    def __init__(self):
        self.cycle        = 0
        self.historique   = []   # résultats des cycles passés
        self.workers      = CONFIG["max_workers"]
        self.total_result = 0

    def observer(self):
        """Lit l'état du système"""
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        return {
            "cpu"     : cpu,
            "ram_pct" : ram.percent,
            "ram_libre": ram.available // 1024**2,
        }

    def decider(self, etat):
        """Choisit les paramètres optimaux selon l'état"""
        cpu = etat["cpu"]

        if cpu > CONFIG["cpu_limit"]:
            self.workers = max(1, self.workers - 1)
            decision = f"CPU élevé ({cpu:.1f}%) → réduit à {self.workers} workers"
        elif cpu < 30 and self.workers < CONFIG["max_workers"]:
            self.workers = min(CONFIG["max_workers"], self.workers + 1)
            decision = f"CPU bas ({cpu:.1f}%) → augmente à {self.workers} workers"
        else:
            decision = f"CPU stable ({cpu:.1f}%) → maintient {self.workers} workers"

        return decision

    def agir(self):
        """Lance le pipeline avec les paramètres actuels"""
        batches = create_compressed_batches(10000)
        t1 = time.time()
        with mp.Pool(self.workers) as pool:
            results = pool.map(process_batch, batches)
        t2 = time.time()
        return {
            "resultat" : sum(results),
            "temps"    : round(t2 - t1, 2),
            "workers"  : self.workers,
            "batches"  : len(batches),
        }

    def apprendre(self, perf):
        """Mémorise les performances pour s'améliorer"""
        self.historique.append(perf)
        self.total_result += perf["resultat"]

        # Détecte si la dernière décision était bonne
        if len(self.historique) >= 2:
            prev = self.historique[-2]["temps"]
            curr = self.historique[-1]["temps"]
            if curr < prev:
                return f"Amélioration : {prev:.2f}s → {curr:.2f}s"
            else:
                return f"Régression   : {prev:.2f}s → {curr:.2f}s"
        return "Premier cycle — pas encore de comparaison"

    def rapport(self):
        """Affiche un bilan final"""
        print("\n" + "="*50)
        print("  RAPPORT FINAL DE L'AGENT")
        print("="*50)
        print(f"  Cycles effectués : {self.cycle}")
        print(f"  Résultat cumulé  : {self.total_result:.2f}")
        print(f"\n  Détail par cycle :")
        for i, h in enumerate(self.historique):
            print(f"    Cycle {i+1} : {h['workers']} workers · "
                  f"{h['temps']}s · résultat {h['resultat']:.2f}")
        meilleur = min(self.historique, key=lambda x: x["temps"])
        print(f"\n  Meilleur cycle : {meilleur['temps']}s "
              f"avec {meilleur['workers']} workers")
        print("="*50)

# ==============================
# BOUCLE PRINCIPALE DE L'AGENT
# ==============================
if __name__ == "__main__":
    print("="*50)
    print("  AGENT IA AUTONOME — OptiCPU-RAM")
    print("="*50)
    print(f"  Cycles prévus  : {CONFIG['cycles']}")
    print(f"  Workers max    : {CONFIG['max_workers']}")
    print(f"  Seuil CPU      : {CONFIG['cpu_limit']}%")
    print("="*50 + "\n")

    agent = Agent()

    for cycle in range(1, CONFIG["cycles"] + 1):
        agent.cycle = cycle
        print(f"--- CYCLE {cycle}/{CONFIG['cycles']} ---")

        # 1. Observer
        etat = agent.observer()
        print(f"  Observe  : CPU {etat['cpu']:.1f}% · "
              f"RAM {etat['ram_pct']:.1f}% · "
              f"{etat['ram_libre']} Mo libres")

        # 2. Décider
        decision = agent.decider(etat)
        print(f"  Décide   : {decision}")

        # 3. Agir
        print(f"  Agit     : lance le pipeline...")
        perf = agent.agir()
        print(f"  Résultat : {perf['temps']}s · "
              f"{perf['batches']} batches · "
              f"score {perf['resultat']:.2f}")

        # 4. Apprendre
        apprentissage = agent.apprendre(perf)
        print(f"  Apprend  : {apprentissage}")

        print()
        time.sleep(CONFIG["sleep_cycle"])

    # Rapport final
    agent.rapport()
