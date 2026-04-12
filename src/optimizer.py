import psutil
import multiprocessing as mp
import zstandard as zstd
import torch
import torch.nn as nn
import random
import time
import struct
import itertools

# ==============================
# MODÈLE
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

# ==============================
# PIPELINE PARAMÉTRABLE
# ==============================
def process_batch(args):
    compressed_batch, sleep_time = args
    raw    = decompress(compressed_batch)
    batch  = deserialize(raw)
    tensor = torch.tensor(batch, dtype=torch.float32).unsqueeze(1)
    with torch.no_grad():
        output = model(tensor)
    time.sleep(sleep_time)
    return output.sum().item()

def run_pipeline(batch_size, workers, sleep_time, n_data=10000):
    """Lance le pipeline avec des paramètres donnés et mesure le temps"""
    # Génère et compresse les données
    data = [random.uniform(0, 1) for _ in range(n_data)]
    batches = []
    for i in range(0, len(data), batch_size):
        chunk = data[i:i + batch_size]
        batches.append(compress(serialize(chunk)))

    # Lance avec les paramètres
    args = [(b, sleep_time) for b in batches]
    t1 = time.time()
    with mp.Pool(workers) as pool:
        results = pool.map(process_batch, args)
    t2 = time.time()

    return {
        "batch_size"  : batch_size,
        "workers"     : workers,
        "sleep_time"  : sleep_time,
        "temps"       : round(t2 - t1, 3),
        "score"       : round(sum(results), 2),
        "n_batches"   : len(batches),
    }

# ==============================
# GRID SEARCH
# ==============================
def grid_search():
    """Teste toutes les combinaisons de paramètres"""

    # Grille des paramètres à tester
    grille = {
        "batch_size"  : [256, 512, 1024],
        "workers"     : [2, 3, 4],
        "sleep_time"  : [0.0, 0.01, 0.02],
    }

    combinaisons = list(itertools.product(
        grille["batch_size"],
        grille["workers"],
        grille["sleep_time"]
    ))

    print("="*60)
    print("  OPTIMISEUR — Grid Search")
    print("="*60)
    print(f"  Combinaisons à tester : {len(combinaisons)}")
    print(f"  CPU actuel            : {psutil.cpu_percent(interval=0.5):.1f}%")
    print("="*60 + "\n")

    resultats = []

    for i, (batch_size, workers, sleep_time) in enumerate(combinaisons):
        print(f"Test {i+1:2}/{len(combinaisons)} | "
              f"batch={batch_size:4} | "
              f"workers={workers} | "
              f"sleep={sleep_time:.2f}s", end=" → ")

        perf = run_pipeline(batch_size, workers, sleep_time)
        resultats.append(perf)
        print(f"temps={perf['temps']}s")

    return resultats

# ==============================
# ANALYSE DES RÉSULTATS
# ==============================
def analyser(resultats):
    print("\n" + "="*60)
    print("  RAPPORT D'OPTIMISATION")
    print("="*60)

    # Meilleur temps
    meilleur = min(resultats, key=lambda x: x["temps"])
    pire     = max(resultats, key=lambda x: x["temps"])

    print(f"\n  Meilleure config :")
    print(f"    batch_size  : {meilleur['batch_size']}")
    print(f"    workers     : {meilleur['workers']}")
    print(f"    sleep_time  : {meilleur['sleep_time']}s")
    print(f"    temps       : {meilleur['temps']}s  ← OPTIMAL")

    print(f"\n  Pire config :")
    print(f"    batch_size  : {pire['batch_size']}")
    print(f"    workers     : {pire['workers']}")
    print(f"    sleep_time  : {pire['sleep_time']}s")
    print(f"    temps       : {pire['temps']}s")

    gain = round((pire["temps"] - meilleur["temps"]) / pire["temps"] * 100, 1)
    print(f"\n  Gain d'optimisation : {gain}%")

    # Classement top 5
    print(f"\n  Top 5 configurations :")
    top5 = sorted(resultats, key=lambda x: x["temps"])[:5]
    for i, r in enumerate(top5):
        print(f"    {i+1}. batch={r['batch_size']:4} | "
              f"workers={r['workers']} | "
              f"sleep={r['sleep_time']:.2f}s | "
              f"temps={r['temps']}s")

    print("\n" + "="*60)
    return meilleur

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    resultats = grid_search()
    meilleur  = analyser(resultats)
    print(f"\n  Config optimale trouvée automatiquement !")
    print(f"  Utilise batch_size={meilleur['batch_size']} "
          f"et workers={meilleur['workers']} dans ton pipeline.")
