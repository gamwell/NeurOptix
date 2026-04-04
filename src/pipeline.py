import zstandard as zstd
import random
import time

# --- CONFIG ---
BATCH_SIZE = 1000

# --- COMPRESSION ---
compressor = zstd.ZstdCompressor()
decompressor = zstd.ZstdDecompressor()

def compress_data(data: bytes) -> bytes:
    return compressor.compress(data)

def decompress_data(data: bytes) -> bytes:
    return decompressor.decompress(data)

# --- DATASET ---
def generate_data(n=10000):
    print(f"Génération de {n} nombres aléatoires...")
    return [random.randint(0, 1000) for _ in range(n)]

def serialize(batch):
    """Convertit une liste en bytes"""
    return ",".join(map(str, batch)).encode()

def deserialize(data):
    """Convertit des bytes en liste"""
    return list(map(int, data.decode().split(",")))

# --- PIPELINE ---
def create_batches(data):
    """Découpe les données en morceaux"""
    for i in range(0, len(data), BATCH_SIZE):
        yield data[i:i + BATCH_SIZE]

def process_batch(compressed_batch):
    """Décompresse + traite un batch"""
    raw = decompress_data(compressed_batch)
    batch = deserialize(raw)
    result = [x * x for x in batch]  # simulation calcul IA
    time.sleep(0.01)                  # limite la chauffe
    return sum(result)

# --- MAIN ---
if __name__ == "__main__":
    # 1. Générer les données
    data = generate_data(20000)

    # 2. Compresser en RAM par batches
    print("Compression en RAM...")
    compressed_batches = []
    for batch in create_batches(data):
        raw = serialize(batch)
        compressed = compress_data(raw)
        compressed_batches.append(compressed)
    print(f"{len(compressed_batches)} batches compressés")

    # 3. Traiter chaque batch
    print("Traitement des batches...")
    results = []
    for i, batch in enumerate(compressed_batches):
        result = process_batch(batch)
        results.append(result)
        print(f"  Batch {i+1}/{len(compressed_batches)} → {result}")

    print(f"\nRésultat final : {sum(results)}")
