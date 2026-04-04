import struct
import random
import time
import zstandard as zstd

# --- DÉTECTION GPU ---
try:
    import torch
    import torch.nn as nn
    if torch.cuda.is_available():
        DEVICE = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        vram     = torch.cuda.get_device_properties(0).total_memory // 1024**2
        print(f"✅ GPU détecté : {gpu_name}")
        print(f"✅ VRAM        : {vram} Mo")
    else:
        DEVICE = "cpu"
        print("⚠️  Aucun GPU NVIDIA détecté → CPU utilisé")
        print("   (Le script est prêt pour quand tu auras un GPU)")
except ImportError:
    print("❌ PyTorch non installé")
    exit()

# --- CONFIG ---
BATCH_SIZE  = 512 if DEVICE == "cpu" else 2048  # plus gros batches sur GPU
NUM_WORKERS = 1                                  # GPU gère seul

# --- MODÈLE PLUS PUISSANT (exploite le GPU) ---
class FullModel(nn.Module):
    """
    Réseau plus profond que MiniModel
    CPU  : trop lent pour ce modèle
    GPU  : parfait, calculs en parallèle massif
    """
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.layers(x)

model = FullModel().to(DEVICE)
print(f"\n📐 Modèle : FullModel ({sum(p.numel() for p in model.parameters())} paramètres)")
print(f"📍 Dispositif : {DEVICE.upper()}\n")

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

# --- TRAITEMENT GPU ---
def process_batch(compressed_batch):
    raw    = decompress_data(compressed_batch)
    batch  = deserialize(raw)

    # Envoi automatique sur GPU ou CPU
    tensor = torch.tensor(batch, dtype=torch.float32).unsqueeze(1).to(DEVICE)

    with torch.no_grad():
        output = model(tensor)

    return output.sum().item()

# --- PIPELINE ---
def create_batches(data):
    for i in range(0, len(data), BATCH_SIZE):
        yield data[i:i + BATCH_SIZE]

# --- MAIN ---
if __name__ == "__main__":
    n_data = 50000 if DEVICE == "cpu" else 500000  # plus de données sur GPU

    print(f"Génération de {n_data} données...")
    data = generate_data(n_data)

    print("Compression en RAM...")
    compressed_batches = []
    for batch in create_batches(data):
        compressed_batches.append(compress_data(serialize(batch)))
    print(f"{len(compressed_batches)} batches compressés")

    print(f"\n⚡ Inférence IA sur {DEVICE.upper()}...")
    t1 = time.time()
    results = [process_batch(b) for b in compressed_batches]
    t2 = time.time()

    print(f"\n📊 Résultats :")
    print(f"  Modèle    : FullModel ({DEVICE.upper()})")
    print(f"  Données   : {n_data}")
    print(f"  Batches   : {len(compressed_batches)}")
    print(f"  Temps     : {t2-t1:.2f}s")
    print(f"  Résultat  : {sum(results):.4f}")

    # Infos VRAM si GPU
    if DEVICE == "cuda":
        vram_used = torch.cuda.memory_allocated() // 1024**2
        vram_total = torch.cuda.get_device_properties(0).total_memory // 1024**2
        print(f"\n💾 VRAM utilisée : {vram_used} Mo / {vram_total} Mo")
        print(f"   Libre         : {vram_total - vram_used} Mo")
