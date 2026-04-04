import zstandard as zstd
import multiprocessing as mp
import psutil
import random
import time

# --- CONFIG i5-9500 ---
BATCH_SIZE = 1000
MAX_WORKERS = 4    # laisse 2 cœurs libres pour Windows
CPU_LIMIT = 75.0   # seuil avant réduction des workers

# --- COMPRESSION ---
def compress_data(data: bytes) -> bytes:
    return zstd.ZstdCompressor().compress(data)

def decompress_data(data: bytes) -> bytes:
    return zstd.ZstdDecompressor().decompress(data)

# --- DATASET ---
def generate_data(n=10000):
    return [random.randint(0, 1000) for _ in range(n)]

def serialize(batch):
    return ",".join(map(str, batch)).encode()

def deserialize(data):
    return list(map(int, data.decode().split(",")))

# --- TRAITEMENT ---
def process_batch(compressed_batch):
    raw = decompress_data(compressed_batch)
    batch = deserialize(raw)
    result = [x ** 4 + x ** 3 - x ** 2 for x in batch]
    time.sleep(0.01)
    return sum(result)

# --- SCHEDULER THERMIQUE ---
def get_optimal_workers():
    cpu = psutil.cpu_percent(interval=0.5)
    if cpu > CPU_LIMIT:
        workers = max(1, MAX_WORKERS // 2)
        print(f"  ⚠️  CPU élevé ({cpu}%) → réduit à {workers} workers")
    else:
        workers = MAX_WORKERS
        print(f"  ✅ CPU normal ({cpu}%) → {workers} workers")
    return workers

# --- PIPELINE ---
def create_batches(data):
    for i in range(0, len(data), BATCH_SIZE):
        yield data[i:i + BATCH_SIZE]

# --- MAIN ---
if __name__ == "__main__":
    print("Génération des données...")
    data = generate_data(200000)

    print("Compression en RAM...")
    compressed_batches = []
    for batch in create_batches(data):
        compressed_batches.append(compress_data(serialize(batch)))
    print(f"{len(compressed_batches)} batches compressés\n")

    print("Analyse CPU...")
    workers = get_optimal_workers()

    print(f"\n⚡ Traitement avec {workers} workers...")
    t1 = time.time()
    with mp.Pool(workers) as pool:
        results = pool.map(process_batch, compressed_batches)
    t2 = time.time()

    print(f"\n📊 Résultats :")
    print(f"  Workers utilisés : {workers}")
    print(f"  Temps            : {t2-t1:.2f}s")
    print(f"  Résultat final   : {sum(results)}")
