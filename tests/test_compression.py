import zstandard as zstd

# Données simulées (comme un dataset IA)
data = b"exemple de donnees IA " * 1000

# Compression
compressor = zstd.ZstdCompressor()
compressed = compressor.compress(data)

# Décompression
decompressor = zstd.ZstdDecompressor()
original = decompressor.decompress(compressed)

# Résultats
print(f"Taille originale  : {len(data)} octets")
print(f"Taille compressée : {len(compressed)} octets")
print(f"Gain mémoire      : {round((1 - len(compressed)/len(data)) * 100)}%")
print(f"Décompression OK  : {data == original}")
