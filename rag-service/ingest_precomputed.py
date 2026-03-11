"""
One-time ingestion for precomputed embeddings + metadata into a persisted FAISS vector store.
"""

import argparse
import json
from pathlib import Path

import faiss
import numpy as np


def load_metadata(path: Path):
    with path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if not isinstance(metadata, list):
        raise ValueError("metadata.json must be a list")

    for idx, item in enumerate(metadata[:5]):
        if not isinstance(item, dict):
            raise ValueError(f"metadata item at index {idx} is not an object")
        if "text" not in item:
            raise ValueError("each metadata item must contain a 'text' field")

    return metadata


def build_store(embeddings_path: Path, metadata_path: Path, store_dir: Path) -> None:
    embeddings = np.load(embeddings_path).astype(np.float32)
    metadata = load_metadata(metadata_path)

    if embeddings.ndim != 2:
        raise ValueError("embeddings.npy must be a 2D array")

    if embeddings.shape[0] != len(metadata):
        raise ValueError(
            f"row mismatch: embeddings has {embeddings.shape[0]} rows, metadata has {len(metadata)} entries"
        )

    faiss.normalize_L2(embeddings)
    dim = embeddings.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    store_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(store_dir / "index.faiss"))
    np.save(store_dir / "embeddings.npy", embeddings)

    with (store_dir / "metadata.json").open("w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False)

    print("Vector store created successfully")
    print(f"store_dir: {store_dir}")
    print(f"vectors: {index.ntotal}")
    print(f"dimension: {dim}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--embeddings", required=True, help="Path to embeddings.npy")
    parser.add_argument("--metadata", required=True, help="Path to metadata.json")
    parser.add_argument(
        "--store-dir",
        default=str(Path(__file__).resolve().parent / "data" / "vector_store"),
        help="Directory to write index.faiss, metadata.json, embeddings.npy",
    )
    args = parser.parse_args()

    build_store(Path(args.embeddings), Path(args.metadata), Path(args.store_dir))


if __name__ == "__main__":
    main()
