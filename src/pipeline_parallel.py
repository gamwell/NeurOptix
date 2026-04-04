import zstandard as zstd
import multiprocessing as mp
import random
import time

# --- CONFIG ---
BATCH_SIZE = 1000
NUM_WORKERS = 2  # limite pour éviter la chauffe

# --- COMPRESSION ---
def compress_data(data: bytes) -> bytes:
    c = zstd.ZstdCompressor()
    return c.compress(data)

def decompress_data(data: bytes) -> bytes:
    d = zstd.ZstdDecompressor()
    return d.decompress(data)

# --- DATASET ---
def generate_data(n=10000):
    return [random.randint(0, 1000) for _ in range(n)]

def serialize(batch):
    return ",".join(map(str, batch)).encode()

def deserialize(data):
    return list(map(int, data.decode().split(",")))

# --- PIPELINE ---
def create_batches(data):
    for i in range(0, len(data), BATCH_SIZE):
        yield data[i:i + BATCH_SIZE]

def process_batch(compressed_batch):
    raw = decompress_data(compressed_batch)
    batch = deserialize(raw)
    result = [x ** 4 + x ** 3 - x ** 2 for x in batch]
    time.sleep(0.01)  # limite la chauffe
    return sum(result)

# --- MAIN ---
if __name__ == "__main__":
    print("Génération des données...")
    data = generate_data(200000)

    print("Compression en RAM...")
    compressed_batches = []
    for batch in create_batches(data):
        compressed_batches.append(compress_data(serialize(batch)))
    print(f"{len(compressed_batches)} batches compressés")

    # Mesure du temps séquentiel
    print("\n⏱ Traitement séquentiel...")
    t1 = time.time()
    results_seq = [process_batch(b) for b in compressed_batches]
    t2 = time.time()
    print(f"Temps séquentiel : {t2-t1:.2f}s → résultat : {sum(results_seq)}")

    # Mesure du temps parallèle
    print(f"\n⚡ Traitement parallèle ({NUM_WORKERS} workers)...")
    t3 = time.time()
    with mp.Pool(NUM_WORKERS) as pool:
        results_par = pool.map(process_batch, compressed_batches)
    t4 = time.time()
    print(f"Temps parallèle  : {t4-t3:.2f}s → résultat : {sum(results_par)}")

    print(f"\n🚀 Gain de vitesse : x{(t2-t1)/(t4-t3):.1f}")
