from app.config import settings
from app.observability import trace
import time
from functools import lru_cache
import logging
from pinecone import Pinecone,ServerlessSpec

log = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def index():
    """Return an initialized pinecone index.
       This is used to store and retrieve embeddings for the vector search.
       It is also used to store and retrieve the metadata for the embeddings.
       Repeate requests in one process are safe and will return the same index object.
    """
    s = settings()
    if not s.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is missing from .env")
    if not s.pinecone_index_name:
        raise RuntimeError("PINECONE_INDEX_NAME is missing from .env")

    pc = Pinecone(api_key=s.pinecone_api_key)
    name = s.pinecone_index_name

    # Describe rather than list: avoids listing every index and works for existing indexes.
    try:
        info = pc.describe_index(name)
    except Exception as exc:
        # Only create on an actual 404; never hide auth/network failures.
        if getattr(exc, 'status', None) != 404:
            raise
        log.info('Creating Pinecone index %s (dimension=%d, metric=cosine)', name, s.embed_dim)
        try:
            pc.create_index(name=name, dimension=s.embed_dim, metric='cosine',
                spec=ServerlessSpec(cloud=s.pinecone_cloud, region=s.pinecone_region))
        except Exception as create_exc:
            # Another process may have created the index concurrently.
            if getattr(create_exc, 'status', None) != 409:
                raise
        info = pc.describe_index(name)
    if int(info.dimension) != s.embed_dim:
        raise ValueError(f'Pinecone index {name} dimension={info.dimension}, expected {s.embed_dim}. '
                         'Use a different index name or matching EMBED_DIM.')
    if str(info.metric).lower() != 'cosine':
        raise ValueError(f'Pinecone index {name} must use cosine metric, got {info.metric}')
    while not pc.describe_index(name).status['ready']:
        if time.monotonic() >= time.monotonic() + s.pinecone_ready_timeout:
            raise TimeoutError(f'Pinecone index {name} was not ready within {s.pinecone_ready_timeout}s')
        time.sleep(3)
    log.info('Pinecone index %s ready', name)
    return pc.Index(name)

def namespace(tenant):
    return 'tenant-' + tenant

@trace("upsert")
def upsert(tenant, records):
    """Upsert records into the pinecone index for the given tenant."""
    return index().upsert(vectors=records, namespace=namespace(tenant))

@trace("search")
def search(tenant, vector, groups, owner, limit=5): 
    """Search the pinecone index for the given tenant."""
    acl = {'$or': [{'allowed_groups': {'$in': list(groups)}},
                   {'owner': owner}]}
    return index().query(vector=vector, top_k=limit, include_metadata=True,
                         filter=acl, namespace=namespace(tenant))

def delete(tenant, ids):
    """Delete records from the pinecone index for the given tenant."""
    return index().delete(ids=ids, namespace=namespace(tenant))