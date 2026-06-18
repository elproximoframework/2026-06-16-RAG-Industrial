import time
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.api.schemas import (
    QueryRequest, QueryResponse, 
    IngestRequest, IngestResponse, 
    HealthResponse, SourceNode, PipelineTrace
)
from app.api.dependencies import get_rag_pipeline, get_ingestion_pipeline
from app.retrieval.agentic_pipeline import AgenticRAGPipeline
from app.ingestion.pipeline import IngestionPipeline

router = APIRouter()

@router.post(
    "/query", 
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar el motor de RAG Agéntico",
    description="Procesa una pregunta utilizando enrutamiento inteligente, recuperación híbrida y generación con citas estrictas."
)
async def query_rag(
    request: QueryRequest,
    rag: AgenticRAGPipeline = Depends(get_rag_pipeline)
):
    try:
        # Ejecutar consulta a través del orquestador agéntico
        result = rag.query(request.query, filters=request.filters)
        
        # Mapear las fuentes a la estructura de SourceNode de Pydantic
        sources = [
            SourceNode(
                id=s["id"],
                document=s["document"],
                heading=s.get("heading"),
                content_snippet=s["content_snippet"],
                compressed=s["compressed"]
            )
            for s in result.get("sources", [])
        ]
        
        # Mapear la traza de ejecución
        trace = PipelineTrace(
            retrieved_chunks=result["pipeline_trace"]["retrieved_chunks"],
            use_hyde=result["pipeline_trace"]["use_hyde"],
            use_multiquery=result["pipeline_trace"]["use_multiquery"],
            compression_applied=result["pipeline_trace"]["compression_applied"]
        )
        
        return QueryResponse(
            query=result["query"],
            category=result["category"],
            answer=result["answer"],
            sources=sources,
            pipeline_trace=trace
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en el RAG Pipeline: {str(e)}"
        )

@router.post(
    "/ingest/sync",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingestar un nuevo documento en caliente",
    description="Procesa, segmenta y vectoriza un archivo local (.pdf, .docx) en la base de datos vectorial de manera síncrona."
)
async def ingest_file(
    request: IngestRequest,
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline)
):
    try:
        # Construir metadatos a partir del request
        base_metadata = {}
        if request.project_id:
            base_metadata["project_id"] = request.project_id
        if request.doc_type:
            base_metadata["doc_type"] = request.doc_type
        if request.confidentiality:
            base_metadata["confidentiality"] = request.confidentiality
            
        # Ejecutar la ingesta
        result = pipeline.process_file(request.file_path, base_metadata=base_metadata)
        
        if result.get("status") != "ok":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fallo en la ingesta del archivo: {result.get('status')}"
            )
            
        return IngestResponse(
            file_path=result["file_path"],
            n_parents=result["n_parents"],
            n_children=result["n_children"],
            duration_seconds=result["duration_seconds"],
            status=result["status"]
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error crítico en el proceso de ingesta: {str(e)}"
        )

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Chequeo de salud del sistema",
    description="Verifica la conectividad de la base de datos Qdrant y la cantidad de vectores indexados."
)
async def health_check(
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline)
):
    qdrant_connected = False
    vector_count = 0
    collection_name = pipeline.vector_store.collection_name
    
    try:
        # Comprobar estado de la colección
        info = pipeline.get_collection_info()
        if info:
            qdrant_connected = True
            vector_count = info.get("points_count", 0)
    except Exception:
        # No levantamos excepción HTTP aquí para que el JSON de respuesta contenga el estado detallado
        pass
        
    return HealthResponse(
        status="ok" if qdrant_connected else "degraded",
        qdrant_connected=qdrant_connected,
        collection_name=collection_name,
        vector_count=vector_count
    )
