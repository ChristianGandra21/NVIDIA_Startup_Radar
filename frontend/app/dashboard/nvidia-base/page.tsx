"use client";

const technologies = [
  {
    name: "NVIDIA Inception",
    description: "Programa para startups com benefícios, créditos em nuvem, suporte técnico e go-to-market. Gratuito para startups early-stage.",
    category: "Programas",
  },
  {
    name: "NVIDIA NIM",
    description: "Microservices para deploy de modelos de IA otimizados. Suporta LLMs, visão, voz e embedding. Inferência 2-5x mais rápida.",
    category: "Inferência",
  },
  {
    name: "NVIDIA NeMo",
    description: "Framework para treinamento, fine-tuning e guardrails de modelos generativos. Inclui NeMo Evaluator e NeMo Guardrails.",
    category: "Modelos",
  },
  {
    name: "NeMo Guardrails",
    description: "Controle de comportamento de assistentes e agentes de IA. Previne jailbreaks, alucinações e tópicos indesejados.",
    category: "Segurança",
  },
  {
    name: "Triton Inference Server",
    description: "Serving de modelos em produção com suporte a múltiplos frameworks (PyTorch, TensorFlow, ONNX). Batching dinâmico.",
    category: "Inferência",
  },
  {
    name: "TensorRT-LLM",
    description: "Otimização de inferência de LLMs. Compressão, quantização INT4/INT8/FP8 e kernels fused para GPUs NVIDIA.",
    category: "Inferência",
  },
  {
    name: "NVIDIA RAPIDS",
    description: "Aceleração de pipelines de dados com GPU. Inclui cuDF (dataframes), cuML (ML), cuGraph (grafos).",
    category: "Data Science",
  },
  {
    name: "CUDA Toolkit",
    description: "Plataforma de programação paralela em GPU. Base para todas as tecnologias NVIDIA.",
    category: "Infraestrutura",
  },
  {
    name: "NVIDIA Riva",
    description: "ASR (reconhecimento de fala), TTS (síntese de voz) e NLP em tempo real. Modelos otimizados para português.",
    category: "Voz & NLP",
  },
  {
    name: "NVIDIA Omniverse",
    description: "Plataforma de simulação, gêmeos digitais e colaboração 3D. Baseada em Universal Scene Description (USD).",
    category: "Simulação",
  },
  {
    name: "NVIDIA Isaac",
    description: "Plataforma para robótica, simulação e autonomia. Inclui Isaac Sim, Isaac ROS e Isaac Manipulator.",
    category: "Robótica",
  },
  {
    name: "NVIDIA Clara",
    description: "Plataforma para saúde e ciências da vida. Imagem médica, genômica e descoberta de fármacos com IA.",
    category: "Saúde",
  },
  {
    name: "NVIDIA Morpheus",
    description: "Cybersecurity com IA acelerada. Detecção de ameaças em tempo real, análise de rede com GPU.",
    category: "Segurança",
  },
  {
    name: "NVIDIA AI Enterprise",
    description: "Plataforma empresarial para IA em produção. Suporte enterprise, segurança e certificação.",
    category: "Infraestrutura",
  },
];

const categories = [...new Set(technologies.map((t) => t.category))];

export default function NvidiaBasePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Base NVIDIA</h1>
        <p className="text-sm text-gray-500 mt-1">
          Catálogo de tecnologias NVIDIA disponíveis para recomendação
        </p>
      </div>

      {categories.map((category) => (
        <div key={category}>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            {category}
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {technologies
              .filter((t) => t.category === category)
              .map((tech) => (
                <div
                  key={tech.name}
                  className="p-5 bg-white rounded-xl border border-gray-200 card-shadow hover:card-shadow-hover transition-all duration-200"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-2 h-2 rounded-full bg-nvidia" />
                    <h3 className="text-sm font-semibold">{tech.name}</h3>
                  </div>
                  <p className="text-xs text-gray-500 leading-relaxed">
                    {tech.description}
                  </p>
                </div>
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}
