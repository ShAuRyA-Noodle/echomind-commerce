"""Echomind Commerce - graph package (Neo4j client + ops + queries + schema)."""

from .embeddings import cosine_similarity, embed_text, embed_texts
from .neo4j_client import Neo4jClient, neo4j_client
from .operations import GraphOperations, graph_ops
from .queries import QUERIES
from .schema import (
    EMBEDDING_DIM,
    EMBEDDING_NODE_TYPES,
    NODE_TYPES,
    SCHEMA_INIT_QUERIES,
)

__all__ = [
    "EMBEDDING_DIM",
    "EMBEDDING_NODE_TYPES",
    "NODE_TYPES",
    "QUERIES",
    "SCHEMA_INIT_QUERIES",
    "GraphOperations",
    "Neo4jClient",
    "cosine_similarity",
    "embed_text",
    "embed_texts",
    "graph_ops",
    "neo4j_client",
]
