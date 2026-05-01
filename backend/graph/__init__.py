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
    "Neo4jClient",
    "neo4j_client",
    "GraphOperations",
    "graph_ops",
    "QUERIES",
    "SCHEMA_INIT_QUERIES",
    "NODE_TYPES",
    "EMBEDDING_NODE_TYPES",
    "EMBEDDING_DIM",
    "embed_text",
    "embed_texts",
    "cosine_similarity",
]
