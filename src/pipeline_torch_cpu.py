import torch
import torch.nn as nn
import zstandard as zstd
import random
import time
import struct

# --- CONFIG ---
BATCH_SIZE  = 512
DEVICE      = "cpu"

print(f"Dispositif utilisé : {DEVICE}")

# --- MODÈLE IA SIMPLE ---
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

model = MiniModel().to(DEVICE)

# --- COMPRESSION ---
def compress_data(data: bytes) -> bytes:
    return zstd.ZstdCompressor().compress(data)

def decompress_data(data: bytes) -> bytes:
    return zstd.ZstdDecompressor().decompress(data)

# --- DATASET ---
def generate_data(n=10000):
    return [random.uniform(0, 1) for _ in range(n)]

def serialize(batch):
    return struct.pack(f"{len(batch)}f", *batch)

def deserialize(data):
    n = len(data) // 4
    return list(struct.unpack(f"{n}f", data))

# --- TRAITEMENT AVEC MODÈLE IA ---
def process_batch(compressed_batch):
    raw    = decompress_data(compressed_batch)
    batch  = deserialize(raw)
    tensor = torch.tensor(batch, dtype=torch.float32).unsqueeze(1)
    with torch.no_grad():
        output = model(tensor)
    time.sleep(0.01)
    return output.sum().item()

# --- PIPELINE ---
def create_batches(data):
    for i in range(0, len(data), BATCH_SIZE):
        yield data[i:i + BATCH_SIZE]

# --- MAIN ---
if __name__ == "__main__":
    print("Génération des données...")
    data = generate_data(20000)

    print("Compression en RAM...")
    compressed_batches = []
    for batch in create_batches(data):
        compressed_batches.append(compress_data(serialize(batch)))
    print(f"{len(compressed_batches)} batches compressés")

    print(f"\n⚡ Inférence IA sur {DEVICE}...")
    t1 = time.time()
    results = [process_batch(b) for b in compressed_batches]
    t2 = time.time()

    print(f"\n📊 Résultats :")
    print(f"  Modèle   : MiniModel (CPU)")
    print(f"  Batches  : {len(compressed_batches)}")
    print(f"  Temps    : {t2-t1:.2f}s")
    print(f"  Résultat : {sum(results):.4f}")
