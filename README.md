# 🟢 NVIDIA Startup AI Radar

> Plataforma inteligente e multi-agente para mapeamento de startups brasileiras, qualificação de maturidade técnica em IA e recomendação personalizada do ecossistema de hardware e software NVIDIA.

---

## 📖 Sumário
1. [Contextualização e Problema](#-contextualização-e-problema)
2. [Objetivos do Projeto](#-objetivos-do-projeto)
3. [Arquitetura do Sistema](#-arquitetura-do-sistema)
4. [Mapeamento e Pipeline de Ingestão (Scraping)](#-mapeamento-e-pipeline-de-ingestão-scraping)
5. [Tecnologias NVIDIA Mapeadas](#-tecnologias-nvidia-mapeadas)
6. [Estrutura do Projeto](#-estrutura-do-projeto)
7. [Como Configurar e Executar](#-como-configurar-e-executar)
   - [Requisitos](#requisitos)
   - [Variáveis de Ambiente](#variáveis-de-ambiente)
   - [Configurando o Backend](#configurando-o-backend)
   - [Configurando o Frontend](#configurando-o-frontend)

---

## 🔍 Contextualização e Problema

O mercado de inteligência artificial vive uma transição estrutural. Gigantes de tecnologia e provedores de modelos fundacionais (OpenAI, Google, Meta, Anthropic) estão subindo na cadeia de valor, integrando memórias nativas, voz, automações e agentes avançados aos seus ecossistemas. 

Nesse novo cenário, **startups simples que atuam apenas como "wrappers de LLM" (interfaces gráficas sobre APIs externas) enfrentam sérias ameaças de desintermediação**.

Para prosperar, as startups precisam se diferenciar evoluindo para **AI-Native Services** — combinando workflows profundos, dados proprietários e serviços especializados de ponta a ponta. 

### A Oportunidade com a NVIDIA
A stack tecnológica da NVIDIA (hardware, SDKs, otimizações e microsserviços de inferência) é o caminho ideal para que startups superem barreiras de:
* **Custos operacionais elevados** com APIs externas em escala.
* **Latência de inferência** em modelos de produção.
* **Governança de dados, segurança e soberania**.
* **Escalabilidade de processamento** em pipelines de dados complexos.

O **NVIDIA Startup AI Radar** atua como uma ferramenta estratégica de inteligência e qualificação para o time de **Startups & VCs da NVIDIA na América Latina**, facilitando a identificação de empresas com grande potencial tecnológico para ingresso no programa **NVIDIA Inception**.

---

## 🎯 Objetivos do Projeto

- **Mapear** o ecossistema brasileiro de startups ativas através de múltiplas fontes abertas.
- **Estruturar** dados brutos e públicos de páginas institucionais, blogs, notícias e portfólios em perfis técnicos padronizados.
- **Classificar** startups em termos de maturidade de IA: *AI-Native*, *AI-Enabled* ou *Non-AI*.
- **Identificar Gaps** técnicos na stack computacional das startups.
- **Gerar Recomendações** precisas utilizando inteligência de RAG enriquecida com documentações oficiais da NVIDIA.
- **Gerar Briefings Executivos** automatizados no formato Markdown para apoiar a abordagem técnica e comercial.

---

## 🤖 Arquitetura do Sistema

A orquestração do sistema de qualificação é gerenciada de forma reativa e baseada em estado utilizando o **LangGraph**. A pipeline executa múltiplos agentes especializados no processamento de dados e na inferência:

```mermaid
graph TD
    START --> load_startup["Carregar Dados (Load Startup Node)"]
    load_startup --> classify["Classificar Maturidade (Classifier Agent)"]
    classify --> route{Classificação Válida?}
    route -- Sim --> validate["Validar Evidências (Validator Agent)"]
    route -- Erro/Não --> END
    validate --> query_nvidia["Consultar Base RAG (RAG Agent)"]
    query_nvidia --> recommend["Gerar Recomendações (Recommendation Agent)"]
    recommend --> brief["Gerar Briefing (Briefer Agent)"]
    brief --> END
```

### Detalhamento dos Agentes (LangGraph Nodes)
1. **Load Startup Node**: Carrega as informações básicas e os metadados do banco de dados estruturado PostgreSQL.
2. **Classifier Agent**: Classifica e avalia o nível de uso de IA na startup com base nos sinais e menções públicas de stack.
3. **Evidence Validator Agent**: Realiza o cross-checking das afirmações e valida se a startup possui embasamento público ou se requer atenção para falsas promessas de tecnologia.
4. **NVIDIA RAG Agent**: Faz buscas híbridas enriquecidas com reranking na base de conhecimento sobre SDKs e hardware NVIDIA.
5. **Recommendation Agent**: Cruza os gaps e as necessidades de infraestrutura da startup com a biblioteca de soluções NVIDIA para criar o plano técnico e de negócios.
6. **Briefer Agent**: Compila o briefing executivo final no formato Markdown, adicionando justificativas técnicas e prioridades de atendimento.

---

## 📥 Mapeamento e Pipeline de Ingestão (Scraping)

O pipeline de dados opera em duas fases principais e processa **16 fontes brasileiras** importantes para o ecossistema de startups:

### Fase 1: Fontes Rápidas (BS4 & Planilhas)
Extração baseada em padrões de BeautifulSoup e importações diretas:
* Planilha **InovAtiva Brasil**
* Portfólio **ACE Ventures**
* Portfólio **WOW Aceleradora**

### Fase 2: Crawling Avançado com LLM (Trafilatura + Groq)
Mineração de conteúdo dinâmico e processamento de linguagem natural usando **Llama 3.1 8B via Groq** para transformar texto não estruturado em JSON:
* Distrito Blog, Cubo Itaú, Latitud, Abstartups, Liga Ventures, Endeavor Brasil, StartSe, Startups.com.br, Brazil Journal, NeoFeed, Exame Startups, PEGN, Mobile Time.

---

## 🟢 Tecnologias NVIDIA Mapeadas

O motor de RAG e recomendação do projeto cobre todo o ecossistema de software empresarial da NVIDIA, agrupando-os por caso de uso:

* **Otimização de Inferência & Deploy**: NVIDIA NIM, Triton Inference Server, TensorRT-LLM, CUDA Toolkit.
* **Customização & Governança de LLMs**: NVIDIA NeMo, NeMo Guardrails.
* **Engenharia & Ciência de Dados**: NVIDIA RAPIDS (cuDF, cuML, cuGraph).
* **Voz e Processamento de Áudio**: NVIDIA Riva (ASR/TTS).
* **Robótica e Simulação Física**: NVIDIA Isaac, NVIDIA Omniverse.
* **Setores Especializados**: NVIDIA Clara (Saúde), NVIDIA Morpheus (Cybersecurity).
* **Apoio ao Negócio**: Benefícios e créditos do programa global **NVIDIA Inception**.

---

## 📂 Estrutura do Projeto

O repositório é dividido entre o backend em Python (Django + LangGraph) e o frontend (Next.js + Tailwind v4):

```bash
├── api/                  # Endpoints REST e serializadores Django
├── config/               # Configurações do servidor Django
├── db/                   # Gerenciamento de conexões PostgreSQL/psycopg2 e repositórios
├── ingestion/            # Scripts de execução do crawler e ingestão RAG
├── services/
│   ├── agents/           # Fluxo de agentes LangGraph (Graph, Classifier, Recommender, etc.)
│   ├── rag/              # Mecanismo RAG (ChromaDB, Hybrid Search, Embeddings)
│   └── scraping/         # Crawlers especializados para as 16 fontes de startups
├── frontend/
│   ├── app/              # Estrutura Next.js App Router (Dashboard, Analytics, Startups)
│   ├── components/       # Componentes globais e UI (Globe canvas, Sidebar, Toasts)
│   ├── lib/              # Configurações de chamada de API e utilitários
│   └── tailwind.config.ts
└── manage.py             # Script de gerenciamento Django
```

---

## 🚀 Como Configurar e Executar

### Requisitos
* Python 3.10+
* Node.js 18+
* Banco de dados PostgreSQL (ex: Supabase)

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto (e também em `frontend/.env.local` se necessário):

```env
DATABASE_URL=postgresql://usuario:senha@host:port/database
GROQ_API_KEY=sua-chave-groq
COHERE_API_KEY=sua-chave-cohere (opcional para reranking RAG)
```

---

### Configurando o Backend

1. **Instale as dependências do Python**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Execute as Migrações do Banco**:
   ```bash
   python manage.py migrate
   python -m db.migrate
   ```

3. **Inicie o Pipeline de Ingestão de Startups (Crawler)**:
   ```bash
   python -m ingestion.run_full_pipeline
   ```

4. **Inicie o Servidor Django**:
   ```bash
   python manage.py runserver
   ```

---

### Configurando o Frontend

1. **Navegue até a pasta frontend**:
   ```bash
   cd frontend
   ```

2. **Instale as dependências**:
   ```bash
   npm install
   ```

3. **Inicie o Servidor de Desenvolvimento**:
   ```bash
   npm run dev
   ```

4. **Gere a Build de Produção**:
   ```bash
   npm run build
   ```

---

*Desenvolvido como ferramenta de Inteligência de Ecossistemas para o NVIDIA Inception Brasil.*
