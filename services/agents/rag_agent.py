from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from services.agents.llm import call_llm

NVIDIA_TECH_KB = """
Tecnologias NVIDIA disponíveis:

1. NVIDIA Inception - Programa para startups: benefícios, crédites em nuvem, suporte técnico, go-to-market. Gratuito para startups early-stage.

2. NVIDIA NIM - Microservices para deploy de modelos de IA otimizados. Suporta LLMs, modelos de visão, voz e embedding. Infere 2-5x mais rápido que APIs genéricas.

3. NVIDIA NeMo - Framework para treinamento, fine-tuning, avaliação e guardrails de modelos generativos. Inclui NeMo Evaluator e NeMo Guardrails.

4. NeMo Guardrails - Controle de comportamento de assistentes e agentes de IA. Previene jailbreaks, alucinações e tópicos indesejados.

5. NVIDIA Triton Inference Server - Serving de modelos em produção com suporte a múltiplos frameworks (PyTorch, TensorFlow, ONNX). Batching dinâmico e concorrência.

6. TensorRT-LLM - Otimização de inferência de LLMs. Compressão de modelos, quantização INT4/INT8/FP8, kernels fused para GPUs NVIDIA.

7. NVIDIA RAPIDS - Aceleração de pipelines de dados com GPU. Inclui cuDF (dataframes GPU), cuML (ML acelerado), cuGraph (grafos).

8. cuDF - Processamento de dataframes em GPU. API compatível com pandas, até 30x mais rápido em GPUs NVIDIA.

9. cuML - Machine learning acelerado em GPU. Algoritmos de ML clássicos (XGBoost, RF, KMeans, PCA, etc.) em GPU.

10. CUDA - Plataforma de programação paralela em GPU. Base para todas as outras tecnologias NVIDIA.

11. NVIDIA Riva - ASR (reconhecimento de fala), TTS (síntese de voz) e NLP em tempo real. Modelos otimizados para português.

12. NVIDIA Omniverse - Plataforma de simulação, gêmeos digitais e colaboração 3D. Baseada em Universal Scene Description (USD).

13. NVIDIA Isaac - Plataforma para robótica, simulação e autonomia. Inclui Isaac Sim, Isaac ROS e Isaac Manipulator.

14. NVIDIA Clara - Plataforma para saúde e ciências da vida. Imagem médica, genômica, descoberta de fármacos com IA.

15. NVIDIA Morpheus - Cybersecurity com IA acelerada. Detecção de ameaças em tempo real, análise de rede com GPU.

16. NVIDIA AI Enterprise - Plataforma empresarial para IA em produção. Suporte enterprise, segurança, estabilidade e certificação.
"""

RAG_SYSTEM_PROMPT = f"""Você é um especialista em tecnologias NVIDIA para startups.
Com base no perfil da startup e nas tecnologias disponíveis, selecione as tecnologias NVIDIA MAIS RELEVANTES.

Base de conhecimento NVIDIA:
{NVIDIA_TECH_KB}

Para cada tecnologia recomendada, explique POR QUE ela é relevante para a startup.
Retorne APENAS um JSON com a lista de recomendações:
{{"relevant_technologies": [
    {{
        "technology": "Nome da tecnologia",
        "relevance": "Explicação curta de por que é relevante",
        "priority": "high/medium/low",
        "use_case": "Caso de uso específico para a startup"
    }}
]}}

Máximo de 5 tecnologias. Se nenhuma for relevante, retorne lista vazia."""


def query_nvidia_kb(
    startup_name: str,
    sector: str | None,
    description: str | None,
    ai_signals: list[str],
    tech_stack: list[str],
    ai_label: str,
) -> list[dict[str, Any]]:
    prompt_parts = [
        f"Startup: {startup_name}",
        f"Setor: {sector or 'N/A'}",
        f"Descrição: {description or 'N/A'}",
        f"Classificação AI: {ai_label}",
        f"Sinais de IA: {', '.join(ai_signals) if ai_signals else 'Nenhum'}",
        f"Stack tecnológica: {', '.join(tech_stack) if tech_stack else 'N/A'}",
    ]
    prompt = "\n".join(prompt_parts)

    result = call_llm(RAG_SYSTEM_PROMPT, prompt, json_mode=True)
    if isinstance(result, dict):
        return result.get("relevant_technologies", [])
    return []
