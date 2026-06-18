from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="La consulta del usuario sobre la documentación técnica.")
    filters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Filtros opcionales para refinar la búsqueda en Qdrant (ej. {'project_id': 'AD4086'})."
    )

class SourceNode(BaseModel):
    id: str = Field(..., description="ID único del chunk padre.")
    document: str = Field(..., description="Nombre del documento del que procede la información.")
    heading: Optional[str] = Field(None, description="Encabezado o sección específica dentro del documento.")
    content_snippet: str = Field(..., description="Fragmento del contenido del chunk.")
    compressed: bool = Field(..., description="Indica si se aplicó compresión contextual semántica.")

class PipelineTrace(BaseModel):
    retrieved_chunks: int = Field(..., description="Número de chunks recuperados.")
    use_hyde: bool = Field(..., description="Indica si se utilizó HyDE (Hypothetical Document Embeddings).")
    use_multiquery: bool = Field(..., description="Indica si se utilizó Multi-Query Expansion.")
    compression_applied: bool = Field(..., description="Indica si se aplicó compresión contextual.")
    cache_hit: bool = Field(..., description="Indica si la respuesta proviene de la caché semántica.")
    cache_similarity: Optional[float] = Field(None, description="Similitud semántica calculada para el cache hit.")

class QueryResponse(BaseModel):
    query: str = Field(..., description="La consulta original.")
    category: str = Field(..., description="Categoría asignada por el router inteligente.")
    answer: str = Field(..., description="Respuesta final generada por el LLM.")
    sources: List[SourceNode] = Field(..., description="Fuentes utilizadas para responder.")
    pipeline_trace: PipelineTrace = Field(..., description="Detalles de la traza de ejecución del RAG.")

class IngestRequest(BaseModel):
    file_path: str = Field(..., description="Ruta absoluta o relativa al archivo en el servidor.")
    project_id: Optional[str] = Field(None, description="ID del proyecto asociado (ej. 'AD4086').")
    doc_type: Optional[str] = Field(None, description="Tipo de documento (ej. 'datasheet', 'manual').")
    confidentiality: Optional[str] = Field(None, description="Nivel de confidencialidad.")

class IngestResponse(BaseModel):
    file_path: str = Field(..., description="Archivo procesado.")
    n_parents: int = Field(..., description="Número de chunks padre guardados.")
    n_children: int = Field(..., description="Número de chunks hijo indexados en Qdrant.")
    duration_seconds: float = Field(..., description="Tiempo total de la ingesta en segundos.")
    status: str = Field(..., description="Resultado del procesamiento (ok, error, etc.).")

class HealthResponse(BaseModel):
    status: str = Field("ok", description="Estado general de la API.")
    qdrant_connected: bool = Field(..., description="Conectividad con Qdrant.")
    collection_name: str = Field(..., description="Nombre de la colección activa.")
    vector_count: int = Field(..., description="Número total de vectores en la colección.")
