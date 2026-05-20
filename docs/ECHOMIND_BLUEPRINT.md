# ECHOMIND: Production-Grade Master Blueprint

## Interview Any Expert. Clone Their Reasoning. Preserve Their Genius.

---

## Context

**What this is**: A complete technical and strategic blueprint for ECHOMIND - a system that conducts AI-driven Socratic interviews with human experts, extracts their tacit knowledge into a structured knowledge graph, and creates a digital twin that reasons exactly like them.

**Why this matters**: The $47B expert knowledge loss problem. When a senior engineer retires, a surgeon stops practicing, or a master strategist leaves an organization, their decades of tacit knowledge - the decision heuristics, edge case intuitions, conditional reasoning patterns that exist nowhere in any document - vanish. ECHOMIND captures it all.

**How it works**: Interview an expert for 2 hours. ECHOMIND's Socratic engine generates ~10,000 micro-questions, maps every decision tree, captures every intuition and edge case, builds a knowledge graph of their reasoning, and creates a digital twin that can answer novel questions using the expert's own principles.

---

## SECTION 1: PROBLEM DEFINITION & VISION

### 1.1 The $47B Expert Knowledge Loss Problem

Organizations lose an estimated $47 billion annually from expert knowledge attrition (Panopto Workplace Knowledge and Productivity Report). When a 30-year veteran leaves, they take with them:

- **Procedural knowledge**: How to actually do things vs. how the manual says to do them
- **Conditional heuristics**: "If X happens AND the weather is Y AND the client is type Z, then do W" - chains of conditional reasoning no document captures
- **Experiential pattern recognition**: "This looks like the time in 2014 when..." - pattern matching across decades of experience
- **Intuitive judgments**: "Something feels wrong about this" - gut reactions trained by thousands of prior decisions
- **Edge case libraries**: The mental catalog of "the one time it broke because of..."

### 1.2 What Tacit Knowledge Is and Why It's Impossible to Document Manually

Tacit knowledge (Michael Polanyi, 1966) is knowledge that cannot be fully articulated. A chess grandmaster "sees" the right move before calculating. A diagnostic physician "smells" a rare condition. An experienced pilot "feels" turbulence differently than a new one.

**Why manual documentation fails:**
- Experts don't know what they know - their knowledge is compiled into intuition
- Writing activates different cognitive processes than doing - experts describe what they think they do, not what they actually do
- The space of edge cases is combinatorially large - no static document can enumerate all conditions
- Knowledge is dynamic - it evolves with each new experience
- The most valuable knowledge (intuition, heuristics) is the hardest to verbalize

### 1.3 The "Bus Factor" in Organizations

The bus factor measures how many people need to be "hit by a bus" before a project/team fails. Critical knowledge concentration:

| Scenario | Risk | Cost of Loss |
|----------|------|-------------|
| Solo expert maintains legacy system | Critical | $5-50M in re-engineering |
| Senior surgeon with rare specialty | Critical | Patient outcomes decline for years |
| Lead architect of 10-year platform | High | 6-18 months productivity loss |
| Sales veteran with key client relationships | High | $1-10M revenue at risk |
| Master tradesperson (aviation maintenance) | Critical | FAA compliance and safety risk |

### 1.4 Why Existing Tools Fail

| Tool | What It Captures | What It Misses |
|------|------------------|----------------|
| Confluence/Notion | Documented procedures | Undocumented heuristics, edge cases, intuition |
| SharePoint | File storage | Reasoning chains, decision context |
| Video recordings | Surface-level explanations | The questions no one thought to ask |
| Mentorship | Some tacit transfer | Unsystematic, depends on mentee's questions |
| Exit interviews | High-level overview | No depth, no follow-up, no structure |
| ChatGPT/RAG on docs | What's in the documents | What's in the expert's head but NOT in any document |

### 1.5 Why AI-Driven Socratic Questioning Is the Breakthrough

The key insight: **an AI interviewer can ask the right follow-up questions** - questions that a human interviewer wouldn't know to ask because they lack the domain context to identify knowledge gaps in real-time.

ECHOMIND's Socratic engine:
1. Builds a knowledge graph AS the interview progresses
2. Analyzes the graph for gaps, shallow areas, contradictions, and missing edge cases
3. Generates the next question specifically targeting the biggest knowledge gap
4. Does this ~80 times per interview hour - far faster than any human interviewer

### 1.6 The Digital Immortality Vision

Experts whose knowledge outlives them. A retired surgeon's diagnostic reasoning available to residents. A master engineer's troubleshooting intuition available to junior team members. A grandparent's life wisdom available to future generations. Not a chatbot pretending to be someone - a faithful representation of how they actually think, with calibrated honesty about what it does and doesn't know.

---

## SECTION 2: CORE TECHNICAL ARCHITECTURE

### 2.1 System Architecture Overview

```
[Human Expert]
    |-- voice --> [Browser Mic API]
    |               |
    |               v
    |           [Google Speech-to-Text V2 Streaming]
    |               |
    |               v
    |           [Transcript Buffer Service]
    |               |
    |               v
    |           [Socratic Engine (Gemini 2.0 Flash)]
    |               |
    |               +-- extracts --> [Knowledge Graph Writer (Neo4j)]
    |               +-- generates --> [Next Question]
    |               |
    |               v
    |           [TTS / Text Display to Expert]
    |
    v
[Digital Twin Query Interface]
    |-- user query --> [Subgraph Retrieval Engine]
    |                       |
    |                       v
    |                   [Reasoning Chain Constructor (Gemini 1.5 Pro)]
    |                       |
    |                       v
    |                   [Calibrated Response + Confidence Score]
```

### 2.2 Service Architecture

Five core services, deployable as Cloud Run containers:

**Service 1: `echomind-api` (FastAPI)**
- All REST/WebSocket endpoints
- Orchestrates the interview loop
- Session state via Firebase Firestore
- Connects to Neo4j for graph operations

**Service 2: `echomind-stt-proxy` (lightweight Python)**
- Proxies browser audio to Google Speech-to-Text V2 via gRPC streaming
- Returns interim and final transcripts over WebSocket
- Separated because gRPC streaming requires long-lived connections

**Service 3: `echomind-frontend` (Next.js)**
- Three main views: Interview, Graph Explorer, Clone Chat
- WebSocket for interview, REST for clone queries

**Service 4: Neo4j AuraDB (managed)**
- 50K nodes / 175K relationships on free tier
- Sufficient for 2-hour interview producing ~2,000-3,000 nodes
- Bolt protocol connection from API service

**Service 5: Firebase (managed)**
- Authentication (Google Sign-In)
- Firestore for session metadata, transcripts, progress
- Cloud Storage for audio recordings

**Hackathon simplification**: Collapse services 1 and 2 into single FastAPI process. STT becomes a background task.

### 2.3 The Tacit Knowledge Taxonomy

ECHOMIND classifies extracted knowledge into six categories:

| Type | Description | Example | Extraction Difficulty |
|------|------------|---------|----------------------|
| **Procedural** | Step-by-step processes | "First I check X, then Y, then Z" | Low - experts can articulate this |
| **Conditional Heuristic** | If-then rules with context | "If the client is enterprise AND the deal is >$1M, always involve legal" | Medium - triggered by scenarios |
| **Experiential Pattern** | Patterns learned from past events | "This looks like the 2014 outage" | Medium - surfaced by "tell me about a time" |
| **Intuitive Judgment** | Gut reactions, "feel" | "Something about this position feels dangerous" | High - requires rapid-fire probing |
| **Edge Case Knowledge** | Exceptions and unusual situations | "The only time this fails is when..." | Medium-High - requires "what if" questioning |
| **Meta-Knowledge** | Knowledge about knowledge limits | "I'm confident about X but always double-check Y" | Medium - requires calibration probes |

### 2.4 The Decision Tree Builder

Converts free-form answers into formal if-then structures:

```python
# Input: "Well, when I see a patient with chest pain, the first thing I think about
# is their age. If they're over 50, I'm immediately thinking cardiac. But if they're
# young, I want to rule out musculoskeletal first. Unless they have a family history,
# then age doesn't matter as much."

# Output Decision Tree:
{
    "root": "Patient presents with chest pain",
    "branches": [
        {
            "condition": "age > 50",
            "action": "Prioritize cardiac workup",
            "confidence": 0.92
        },
        {
            "condition": "age <= 50 AND no family history",
            "action": "Rule out musculoskeletal first",
            "confidence": 0.85
        },
        {
            "condition": "age <= 50 AND positive family history",
            "action": "Prioritize cardiac workup despite age",
            "confidence": 0.88,
            "note": "Exception - family history overrides age heuristic"
        }
    ]
}
```

### 2.5 The Confidence Calibration System

Every piece of extracted knowledge gets a confidence score based on:
- **Expert certainty signals**: Hedge words ("I think", "maybe") lower confidence
- **Mention frequency**: How often the expert references this knowledge
- **Consistency**: Whether the expert says the same thing when probed from different angles
- **Depth of explanation**: Can the expert explain WHY, or only THAT?
- **Edge case coverage**: How many exceptions have been explored?

### 2.6 The Living Update Loop

Post-interview, the expert can:
1. Review the knowledge graph and correct errors
2. Add missing knowledge nodes
3. Resolve flagged contradictions
4. Rate clone responses on held-out test questions
5. Trigger re-extraction for specific areas

The graph is versioned - every change creates a new graph snapshot, allowing rollback and audit.

---

## SECTION 3: GOOGLE API INTEGRATION PLAN

### 3.1 Gemini 2.0 Flash - Socratic Engine (extraction + question generation)

```python
import google.generativeai as genai

# Knowledge extraction from transcript chunks
extraction_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=EXTRACTION_SYSTEM_PROMPT,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=EXTRACTION_SCHEMA,  # Typed nodes + edges
    )
)

# Question generation
question_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=QUESTION_GENERATION_PROMPT,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=QUESTION_SCHEMA,
    )
)
```

**Why Flash over Pro**: 10x cheaper, 3x faster, native structured JSON output. The Socratic engine makes thousands of extraction calls - Flash's speed/cost ratio is critical. Use Pro only for twin inference where reasoning depth matters.

**Cost estimate**: ~$0.001 per extraction call × ~3,000 calls per 2-hour interview = ~$3/interview.

### 3.2 Google Speech-to-Text V2 - Real-time Interview Capture

```python
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

client = SpeechClient()

config = cloud_speech.RecognitionConfig(
    auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
    language_codes=["en-US"],
    model="long",  # Optimized for long-form speech
    features=cloud_speech.RecognitionFeatures(
        enable_automatic_punctuation=True,
        enable_word_time_offsets=True,  # For transcript alignment
        enable_spoken_punctuation=True,
    ),
)

# Streaming config for real-time transcription
streaming_config = cloud_speech.StreamingRecognitionConfig(
    config=config,
    streaming_features=cloud_speech.StreamingRecognitionFeatures(
        interim_results=True,  # Show partial results as expert speaks
        enable_voice_activity_events=True,  # Detect speech start/stop
    ),
)
```

**Cost**: ~$0.016/minute × 120 minutes = ~$1.92/interview.

### 3.3 Vertex AI / Neo4j - Knowledge Graph

Neo4j AuraDB Free Tier for hackathon (50K nodes, 175K edges). For production, Neo4j AuraDB Professional or self-hosted Neo4j Enterprise on GKE.

Neo4j's native vector index (5.x+) enables embedding-based semantic search directly in the graph - no separate vector DB needed for the twin's subgraph retrieval.

### 3.4 Gemini Embeddings - Semantic Space

```python
from vertexai.language_models import TextEmbeddingModel

model = TextEmbeddingModel.from_pretrained("text-embedding-004")

# Embed knowledge nodes for semantic search during twin inference
embeddings = model.get_embeddings(
    texts=[node.description for node in knowledge_nodes],
    task_type="RETRIEVAL_DOCUMENT",
    output_dimensionality=768,
)
```

Used for: redundancy detection during interview, semantic subgraph retrieval during twin inference.

### 3.5 Google Text-to-Speech - Voice Persona (Optional)

```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()
synthesis_input = texttospeech.SynthesisInput(text=next_question)
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)
```

For the interview: TTS speaks the questions aloud. For the twin: optional voice output. Can be stubbed for hackathon (text display instead).

### 3.6 Firebase - Session Management

- **Firestore**: Session metadata, transcript chunks, interview progress, clone conversation history
- **Auth**: Google Sign-In for expert and querier authentication
- **Storage**: Audio recordings, exported knowledge graphs

### 3.7 Cloud Run - Inference Deployment

```python
CLOUD_RUN_CONFIG = {
    "echomind-api": {
        "cpu": "4", "memory": "8Gi",
        "max_instances": 10, "min_instances": 1,
        "timeout_seconds": 300, "concurrency": 20,
    },
}
```

---

## SECTION 4: THE SOCRATIC ENGINE IN DETAIL

### 4.1 Core Interview Loop

```
WHILE interview_active:
    1. Receive transcript chunk from STT
    2. Extract knowledge elements (nodes + edges) via Gemini
    3. Write to Neo4j (with entity resolution against existing nodes)
    4. Analyze graph for gaps, contradictions, shallow areas
    5. Score exploration frontiers (what to ask about next)
    6. Determine current phase and phase-appropriate question strategy
    7. Generate next question targeting highest-priority gap
    8. Display/speak question to expert
    9. GOTO 1
```

### 4.2 The Five Interview Phases

**Phase 1: Domain Mapping (Minutes 0-20)**
- **Goal**: Discover the major concepts, their hierarchy, the expert's vocabulary
- **Question style**: Broad, open-ended - "What are the main areas of X you think about?" "How would you categorize different types of Y?"
- **Transition trigger**: >15 top-level Concept nodes AND average CONTAINS depth ≥ 2

**Phase 2: Decision Tree Extraction (Minutes 20-50)**
- **Goal**: For each major concept, extract decision points, conditions, outcomes
- **Question style**: "When you encounter X, what's your thought process?" "What factors do you consider when deciding between A and B?"
- **Transition trigger**: 70% of high-confidence Concept nodes have ≥2 connected Decision nodes

**Phase 3: Edge Case Mining (Minutes 50-80)**
- **Goal**: Find boundaries, exceptions, unusual situations
- **Question style**: "What's the weirdest case of X?" "When does rule Y NOT apply?" "What's the most common mistake with Z?"
- **Key technique**: Propose incorrect applications of stated rules to provoke corrections
- **Transition trigger**: EXCEPTION_TO edge count > 20% of Rule node count

**Phase 4: Contradiction Probing (Minutes 80-100)**
- **Goal**: Surface and resolve internal contradictions
- **Question style**: "Earlier you said A, but also B. How do you reconcile those?"
- **Detection algorithm**: Cypher query for rules with overlapping scope but unlinkled nodes, then Gemini assessment of actual contradiction
- **Transition trigger**: All detected contradictions have resolution fields populated

**Phase 5: Intuition Surfacing (Minutes 100-120)**
- **Goal**: Extract deeply tacit knowledge the expert can't easily articulate
- **Question style**: Rapid-fire pattern recognition - "Quick: I describe X, what's your gut reaction?" Then: "Why did you say that?"
- **Key technique**: Present simplified scenarios, ask for instant reactions, then retrospectively analyze reasoning
- **Generates**: Heuristic and Pattern nodes with `tacit_level: "deeply_tacit"`

### 4.3 The Question Generation Algorithm

```python
QUESTION_GENERATION_PROMPT = """You are the Socratic questioning engine for ECHOMIND.

CURRENT INTERVIEW STATE:
- Phase: {current_phase} ({phase_description})
- Questions asked: {question_count}
- Minutes elapsed: {elapsed_minutes}
- Domain: {domain}

KNOWLEDGE GRAPH SUMMARY:
- Total nodes: {total_nodes} (Concepts: {c}, Decisions: {d}, Rules: {r}, Heuristics: {h}, Experiences: {e}, Patterns: {p})
- Total edges: {total_edges}
- Low-confidence nodes: {low_confidence_nodes}
- High-mention but underconnected nodes: {underconnected_nodes}
- Potential contradictions: {contradictions}

TOP EXPLORATION FRONTIERS (highest priority):
{frontier_list}

LAST 5 Q&A PAIRS:
{recent_qa_pairs}

RULES:
1. Ask exactly ONE question - conversational, natural, not robotic
2. Phase 1-2: Open "how" and "why" questions
3. Phase 3: "What if" and "have you ever seen" questions
4. Phase 4: Present contradictions gently: "I noticed you mentioned X and also Y..."
5. Phase 5: Rapid pattern-matching: "Quick reaction: [scenario]. First thought?"
6. Include follow_up_if_brief for short answers
7. Never repeat a semantically similar question
"""
```

### 4.4 Knowledge Gap Detection

```python
def score_frontier(node, graph_stats):
    """Score a knowledge node for exploration priority."""
    depth_need = (1.0 - node.confidence) * 3.0
    connectivity_gap = node.mention_count / max(node.edge_count, 1)
    recency = 1.0 / (minutes_since_discovery + 1)
    centrality = graph_stats.pagerank(node.id)
    phase_weight = get_phase_weight(current_phase, node.type)

    return (depth_need * 0.3 +
            connectivity_gap * 0.25 +
            recency * 0.15 +
            centrality * 0.2 +
            phase_weight * 0.1)
```

Goes **deeper** when top frontier has connections but low confidence. Goes **broader** when top frontier is high-centrality with few explored neighbors.

### 4.5 Redundancy Detection

```python
def is_redundant(candidate_question, asked_questions, graph):
    # 1. Embedding similarity against last 50 questions
    candidate_emb = get_embedding(candidate_question)
    for prev_q in asked_questions[-50:]:
        if cosine_similarity(candidate_emb, prev_q.embedding) > 0.85:
            return True
    # 2. Has the target knowledge area been sufficiently filled?
    target_nodes = identify_target_nodes(candidate_question, graph)
    if mean([n.confidence for n in target_nodes]) > 0.8:
        return True
    return False
```

### 4.6 The 10,000 Micro-Questions Explained

Not 10,000 questions asked verbally. The breakdown:
- **Questions asked to expert**: ~200-300 (one every 25-40 seconds, accounting for response time)
- **Internal gap-analysis micro-questions** probing the knowledge graph: ~3,000-5,000
- **Sub-questions derived** from decomposing each expert response: ~5,000-7,000

Each response is decomposed into multiple micro-knowledge-elements, each generating implicit micro-questions that are either answered by the response or queued.

---

## SECTION 5: THE KNOWLEDGE GRAPH ARCHITECTURE

### 5.1 Database Choice: Neo4j AuraDB

**Why Neo4j over alternatives:**
- **vs. local Docker**: AuraDB eliminates DevOps. One-minute setup, no port mapping
- **vs. Amazon Neptune**: No free tier, requires VPC configuration
- **vs. NetworkX (in-memory)**: Lacks Cypher, persistence, and visualization (Bloom)
- **vs. ArangoDB/Dgraph**: Neo4j has best Python driver ecosystem and largest community
- Neo4j 5.x native vector indexes enable semantic search without a separate vector DB

### 5.2 Node Types

```cypher
// 1. CONCEPT - A domain topic or entity
(:Concept {
  id: String,           // UUID
  name: String,         // "Sicilian Defense"
  domain: String,       // "chess.openings"
  description: String,  // Expert's own words
  confidence: Float,    // 0.0-1.0, exploration thoroughness
  mention_count: Int,   // Times referenced
  phase_discovered: Int,// Interview phase (1-5)
  embedding: List<Float>, // 768-dim vector
  created_at: DateTime
})

// 2. DECISION - A choice point in reasoning
(:Decision {
  id: String,
  question: String,     // "Should I trade queens here?"
  context: String,      // Situational description
  outcome: String,      // Expert's typical choice
  reasoning: String,    // Why they choose this
  frequency: String,    // "always"|"usually"|"sometimes"|"rarely"
  conditions: List<String>,
  confidence: Float
})

// 3. RULE - An explicit, stated principle
(:Rule {
  id: String,
  statement: String,    // "Never move the same piece twice in opening"
  scope: String,        // "opening"|"middlegame"|"endgame"|"universal"
  strength: String,     // "absolute"|"strong"|"moderate"|"weak"
  source: String,       // "personal"|"classical"|"modern_theory"
  exceptions_count: Int,
  confidence: Float
})

// 4. HEURISTIC - A tacit rule of thumb
(:Heuristic {
  id: String,
  statement: String,    // "When opponent castles queenside, attack kingside"
  trigger_condition: String,
  reliability: Float,   // Expert's self-assessed reliability
  tacit_level: String,  // "explicit"|"semi-tacit"|"deeply_tacit"
  extraction_method: String, // "direct"|"inferred"|"contradiction_resolution"
  confidence: Float
})

// 5. EXPERIENCE - A specific episode or memory
(:Experience {
  id: String,
  description: String,  // "In my game against Magnus at the 2019 tournament..."
  outcome: String,
  lesson: String,
  emotional_valence: String, // "positive"|"negative"|"neutral"
  vividness: Float,
  confidence: Float
})

// 6. PATTERN - A recurring structure the expert recognizes
(:Pattern {
  id: String,
  name: String,         // "Weak back rank"
  description: String,
  indicators: List<String>, // Observable signs
  response: String,     // What to do when detected
  domain_context: String,
  confidence: Float
})
```

### 5.3 Edge Types

```cypher
-[:DEPENDS_ON {weight, description}]->           // "Understanding X requires Y"
-[:CONTAINS {weight}]->                           // Hierarchical containment
-[:TRIGGERS {weight, condition, probability}]->   // Seeing X leads to doing Y
-[:CONTRADICTS {weight, resolution, context_a, context_b}]-> // Tension between two elements
-[:REFINES {weight, description}]->               // X adds nuance to Y
-[:EXCEPTION_TO {weight, condition, frequency}]-> // X is exception to general rule Y
-[:LEARNED_FROM {weight, description}]->          // Knowledge from experience
-[:APPLIES_WHEN {weight, condition}]->            // Conditional application
-[:SIMILAR_TO {weight, description}]->            // Analogical relationship
```

### 5.4 Graph Statistics (2-Hour Chess Interview Estimate)

| Node Type | Count | Edge Type | Count |
|-----------|-------|-----------|-------|
| Concept | 400-600 | DEPENDS_ON | 500-800 |
| Decision | 300-500 | TRIGGERS | 300-500 |
| Rule | 150-250 | CONTRADICTS | 50-100 |
| Heuristic | 200-400 | REFINES | 200-400 |
| Experience | 100-200 | EXCEPTION_TO | 100-200 |
| Pattern | 150-300 | Other edges | 800-1500 |
| **Total** | **1,300-2,250** | **Total** | **3,000-6,000** |

Fits within AuraDB Free (50K/175K limits).

### 5.5 Query Patterns for Twin Inference

```cypher
// Find all knowledge relevant to a query concept + 2-hop neighborhood
MATCH (n) WHERE n.name IN $concept_names OR n.description CONTAINS $search_term
WITH n
MATCH path = (n)-[*1..2]-(connected)
RETURN n, relationships(path), nodes(path)
LIMIT 200

// Semantic vector search (Neo4j 5.x vector index)
CALL db.index.vector.queryNodes('node_embeddings', 20, $query_embedding)
YIELD node, score WHERE score > 0.7
WITH node
MATCH path = (node)-[*1..2]-(connected)
RETURN node, relationships(path), nodes(path), score
ORDER BY score DESC LIMIT 150

// Find contradictions for probing
MATCH (r1:Rule), (r2:Rule)
WHERE r1.scope = r2.scope AND r1.id <> r2.id
  AND NOT (r1)-[:CONTRADICTS]-(r2) AND NOT (r1)-[:REFINES]-(r2)
RETURN r1, r2 LIMIT 10
```

### 5.6 Versioning and Conflict Resolution

- Every graph mutation creates a timestamped changelog entry in Firestore
- Contradictions are stored explicitly as CONTRADICTS edges with resolution fields
- Expert review sessions can override confidence scores and add resolution notes
- Graph snapshots (Neo4j database dumps) taken after each interview session

---

## SECTION 6: THE DIGITAL TWIN INFERENCE ENGINE

### 6.1 Query Pipeline

```
[User Query]
  → [1. Query Analysis & Decomposition]
  → [2. Subgraph Retrieval (multi-strategy)]
  → [3. Reasoning Chain Construction (Gemini)]
  → [4. Confidence Calibration]
  → [5. Response Generation]
```

### 6.2 Query Analysis

```python
async def analyze_query(query: str, graph_summary: dict) -> QueryAnalysis:
    """Decompose user query into graph-searchable components."""
    # Returns:
    # - core_concepts: ["Sicilian Defense", "opening choice"]
    # - decision_sought: "which opening to play"
    # - context_conditions: ["against 1.e4", "as Black"]
    # - query_type: "procedural" | "factual" | "evaluative" | "comparative" | "hypothetical" | "metacognitive"
    # - requires_experience: bool
    # - requires_intuition: bool
```

### 6.3 Subgraph Retrieval (Three Strategies)

1. **Direct concept match + 2-hop neighborhood**: Cypher query matching concept names
2. **Embedding-based semantic search**: Neo4j vector index for semantically similar nodes
3. **Decision-specific retrieval**: For procedural queries, find Decision nodes by context

Results are combined, deduplicated, and ranked by relevance.

### 6.4 Reasoning Chain Construction

```python
TWIN_REASONING_PROMPT = """You are the digital twin of {expert_name}, a {domain} expert.
You must reason EXACTLY as they would, based on their extracted knowledge graph.

RULES:
1. You are NOT a general {domain} AI. You are a specific person's clone.
2. ONLY use knowledge from the provided subgraph. No general knowledge.
3. If the subgraph contains a relevant Rule, state it as the expert would.
4. Weight Heuristics by expert's stated reliability scores.
5. If an Experience is relevant, reference it naturally.
6. Follow Decision preferences from the graph.
7. Acknowledge CONTRADICTS edges - use stored resolutions.
8. NEVER fabricate knowledge not in the subgraph.
9. Speak in first person as the expert.

RETRIEVED KNOWLEDGE SUBGRAPH:
{subgraph_json}

USER QUESTION: {query}

Provide response as the expert. Include reasoning chain.
Return JSON with: answer, reasoning_chain, knowledge_sources_used,
confidence (0-1), uncertainty_type, calibration level.
"""
```

### 6.5 Confidence Calibration

```python
def calibrate_response(confidence, uncertainty_type, subgraph_coverage, node_count):
    evidence_factor = min(1.0, node_count / 10.0)
    coverage_factor = subgraph_coverage
    adjusted = confidence * 0.4 + evidence_factor * 0.3 + coverage_factor * 0.3

    if adjusted >= 0.8:   return "certain"      # No hedge
    elif adjusted >= 0.6: return "confident"     # "Based on my experience..."
    elif adjusted >= 0.35: return "uncertain"    # "I'm not entirely sure, but..."
    elif adjusted >= 0.15: return "low_confidence" # "This is outside my strongest area..."
    else:                  return "dont_know"    # "I honestly don't know enough about that."
```

**Critical distinction**: "I don't know" = graph has essentially no relevant nodes (coverage < 0.15). "I'm uncertain" = relevant nodes exist but are low-confidence, contradictory, or sparse.

### 6.6 The "Expert Reasoning Trace"

Every clone response includes an expandable reasoning trace showing:
1. Which graph nodes were activated
2. Which rules/heuristics were applied
3. How conflicts were resolved
4. Why this confidence level was assigned

This is the key trust mechanism - users can audit the clone's reasoning.

### 6.7 Calibration Dashboard

Compare clone answers to expert answers on held-out test questions:
- Accuracy rate by domain sub-area
- Average confidence calibration (does 80% confidence mean ~80% accuracy?)
- Blind spots (areas where coverage < 30%)
- Strongest areas (coverage > 80%)

---

## SECTION 7: FRONTEND ARCHITECTURE

### 7.1 Interview Interface (`/interview`)

Three-column layout:

**Left (30%): Live Transcript**
- Real-time transcript with speaker labels (Interviewer / Expert)
- Highlighted segments that were extracted as knowledge nodes (clickable)
- Auto-scroll with manual scroll-lock

**Center (40%): Question Display**
- Large, readable current question
- Phase indicator bar (5 segments, current highlighted)
- Timer (elapsed + phase time remaining)
- Audio controls: mute/unmute, volume meter, speech detection
- Text input fallback

**Right (30%): Mini Graph Preview**
- Force-directed graph updating in real-time
- New nodes animate in with pulse effect
- Color-coded by type:
  - Concept: blue `#3B82F6`
  - Decision: amber `#F59E0B`
  - Rule: green `#10B981`
  - Heuristic: purple `#8B5CF6`
  - Experience: rose `#F43F5E`
  - Pattern: cyan `#06B6D4`
- Counters: "Nodes: 342 | Edges: 890 | Coverage: 65%"

### 7.2 Knowledge Graph Visualization (`/graph/[sessionId]`)

Full-page force-directed graph using `react-force-graph-2d`:
- Node size proportional to mention_count
- Node opacity proportional to confidence
- Edge thickness proportional to weight
- Edge color by relationship type
- Click node → detail panel with full properties and connections
- Sidebar: filter by type, minimum confidence, phase, search by name
- Coverage heatmap: treemap of domain areas colored by confidence (green/yellow/red)

### 7.3 Clone Chat Interface (`/clone/[sessionId]`)

**Left (65%): Chat Thread**
- Message thread with the clone
- Each response includes:
  - Answer text (first person as expert)
  - Confidence badge (green/yellow/orange/red pill)
  - Expandable "Reasoning Chain" accordion
  - Expandable "Source Nodes" (clickable → graph view)
- Suggested questions (generated from graph analysis)

**Right (35%): Confidence Dashboard**
- Radar chart of confidence across domain sub-areas
- Overall accuracy estimate
- "Strong areas" and "Weak areas" lists
- "Ask the expert directly" suggestions (where clone confidence is too low)

### 7.4 Comparison Dashboard

Side-by-side view:
- Left: clone's answer to a test question
- Right: expert's actual answer (from validation session)
- Difference highlighting
- Aggregate metrics across test set

---

## SECTION 8: COMPLETE FILE & FOLDER STRUCTURE

```
echomind/
├── README.md
├── docker-compose.yml
├── .env.example
├── Makefile
│
├── backend/
│   ├── main.py                         # FastAPI entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                 # Pydantic Settings (env vars, API keys)
│   │   └── prompts.py                  # ALL Gemini system prompts (centralized)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py                   # Main API router
│   │   ├── endpoints/
│   │   │   ├── interview.py            # POST /interview/start, WS /interview/ws/{id}
│   │   │   ├── clone.py                # POST /clone/query, GET /clone/capabilities
│   │   │   ├── graph.py                # GET /graph/{id}, GET /graph/{id}/stats
│   │   │   └── auth.py                 # POST /auth/verify-token
│   │   └── schemas/
│   │       ├── interview.py            # InterviewStart, TranscriptChunk
│   │       ├── clone.py                # CloneQuery, CloneResponse, ConfidenceData
│   │       ├── graph.py                # GraphNode, GraphEdge, GraphStats
│   │       └── common.py               # SessionInfo, ErrorResponse
│   │
│   ├── core/                           # SOCRATIC ENGINE
│   │   ├── __init__.py
│   │   ├── socratic_engine.py          # Main interview loop orchestrator
│   │   ├── knowledge_extractor.py      # Gemini → nodes + edges from transcript
│   │   ├── question_generator.py       # Gemini → next question from graph gaps
│   │   ├── phase_manager.py            # Phase transitions and state
│   │   ├── gap_analyzer.py             # Knowledge graph gap detection
│   │   ├── contradiction_detector.py   # Cross-reference rules for contradictions
│   │   ├── redundancy_checker.py       # Embedding-based question dedup
│   │   └── frontier_scorer.py          # Priority queue for exploration frontiers
│   │
│   ├── twin/                           # DIGITAL TWIN ENGINE
│   │   ├── __init__.py
│   │   ├── inference_engine.py         # Main twin query pipeline
│   │   ├── query_analyzer.py           # Decompose user queries
│   │   ├── subgraph_retriever.py       # Neo4j multi-strategy retrieval
│   │   ├── reasoning_chain.py          # Build reasoning from subgraph + Gemini
│   │   └── confidence_calibrator.py    # Confidence scoring and calibration
│   │
│   ├── graph/                          # NEO4J OPERATIONS
│   │   ├── __init__.py
│   │   ├── neo4j_client.py             # Driver wrapper, connection pool
│   │   ├── operations.py               # CRUD for nodes/edges (Cypher)
│   │   ├── queries.py                  # Complex Cypher (gaps, stats, subgraph)
│   │   ├── embeddings.py               # Gemini embedding + vector index ops
│   │   └── schema.py                   # Constraints, indexes (run at startup)
│   │
│   ├── services/                       # EXTERNAL SERVICE WRAPPERS
│   │   ├── __init__.py
│   │   ├── stt_service.py              # Google STT V2 streaming
│   │   ├── gemini_service.py           # Centralized Gemini client (retry, rate limit)
│   │   ├── firebase_service.py         # Firestore R/W, auth verification
│   │   └── audio_service.py            # Audio chunk processing, VAD
│   │
│   └── tests/
│       ├── test_socratic_engine.py
│       ├── test_knowledge_extractor.py
│       ├── test_twin_inference.py
│       ├── test_graph_operations.py
│       └── conftest.py                 # Fixtures: mock Neo4j, mock Gemini
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── Dockerfile
│   │
│   ├── public/
│   │   ├── logo.svg
│   │   └── sounds/                     # Interview notification sounds
│   │
│   └── src/
│       ├── app/
│       │   ├── layout.tsx              # Root layout with providers
│       │   ├── page.tsx                # Landing / dashboard
│       │   ├── globals.css
│       │   ├── interview/
│       │   │   └── page.tsx            # Interview session
│       │   ├── graph/
│       │   │   └── [sessionId]/
│       │   │       └── page.tsx        # Session graph explorer
│       │   ├── clone/
│       │   │   └── [sessionId]/
│       │   │       └── page.tsx        # Clone chat
│       │   └── api/
│       │       └── auth/route.ts       # Next.js auth proxy
│       │
│       ├── components/
│       │   ├── ui/                     # shadcn/ui base components
│       │   ├── interview/
│       │   │   ├── InterviewPanel.tsx
│       │   │   ├── TranscriptView.tsx
│       │   │   ├── QuestionDisplay.tsx
│       │   │   ├── AudioControls.tsx
│       │   │   ├── PhaseIndicator.tsx
│       │   │   ├── InterviewTimer.tsx
│       │   │   └── MiniGraphPreview.tsx
│       │   ├── graph/
│       │   │   ├── ForceGraph.tsx
│       │   │   ├── NodeDetail.tsx
│       │   │   ├── GraphControls.tsx
│       │   │   ├── GraphLegend.tsx
│       │   │   ├── CoverageHeatmap.tsx
│       │   │   └── GraphStats.tsx
│       │   ├── clone/
│       │   │   ├── ChatInterface.tsx
│       │   │   ├── CloneMessage.tsx
│       │   │   ├── ConfidenceBadge.tsx
│       │   │   ├── ReasoningChain.tsx
│       │   │   └── SourceNodes.tsx
│       │   └── dashboard/
│       │       ├── SessionList.tsx
│       │       ├── DomainCoverage.tsx
│       │       └── ConfidenceDashboard.tsx
│       │
│       ├── hooks/
│       │   ├── useWebSocket.ts
│       │   ├── useAudioStream.ts
│       │   ├── useInterviewState.ts
│       │   ├── useGraphData.ts
│       │   └── useAuth.ts
│       │
│       ├── lib/
│       │   ├── api.ts
│       │   ├── firebase.ts
│       │   ├── graphUtils.ts
│       │   ├── types.ts
│       │   └── constants.ts
│       │
│       └── providers/
│           ├── AuthProvider.tsx
│           └── SocketProvider.tsx
```

---

## SECTION 9: THE HACKATHON DEMO PLAN

### 9.1 The Chess Expert Demo

**Setup**: Pre-populate a knowledge graph (~800 nodes) from a text-based chess interview conducted during build hours 15-17. Graph covers openings (Sicilian, Queen's Gambit, King's Indian), middlegame strategy, some endgame basics. Critically, the graph does NOT contain discussion of the specific position used for the "aha moment."

### 9.2 Demo Flow (8 Minutes)

**[0:00-1:00] Introduction**
"ECHOMIND turns human experts into digital twins. We interview them using AI-driven Socratic questioning, build a knowledge graph of their expertise, and create a clone that reasons like they do."

**[1:00-3:00] Live Interview Snippet**
Show 2-3 exchanges with the chess "expert":
- System asks about the Najdorf variation
- Expert responds about ...a6, flexibility, counterattacking chances
- Graph lights up with new nodes in real-time
- System generates intelligent follow-up about timing counterattacks

**[3:00-4:00] Knowledge Graph Tour**
Switch to graph visualization. Show 800+ nodes. Zoom into clusters. Click "King Safety" - show connections to Pawn Structure, Castling Decision. Show coverage heatmap: openings deep green, endgames yellow.

**[4:00-5:00] Clone: Easy Question**
Ask: "What opening should I play against 1.e4?"
Clone responds naturally in first person as the expert, recommending the Sicilian Najdorf with reasoning. Confidence badge: green (0.91).

**[5:00-7:00] THE AHA MOMENT: Novel Reasoning**
Ask: "My opponent played an early h4 in the Najdorf before castling. What should I think about?"

This was NEVER discussed in the interview. The clone synthesizes:
- Rule: "When opponent's king is in center, open the position" → suggests ...d5 break
- Heuristic: "Uncastled king + pawn advance = tactical opportunity"
- Pattern: "Counterattacking setup" from Najdorf discussion
- Decision: "Choose castling side based on opponent's pawn structure"

Shows reasoning chain: 5 knowledge elements combined that were never directly connected.

"The clone has NEVER been told about h4 in the Najdorf. But it combined the expert's own principles to construct novel, coherent analysis. This is expert reasoning, not pattern matching."

**[7:00-8:00] Calibration Demo**
Ask about the Catalan Opening (area with minimal coverage).
Clone: "I honestly don't have strong opinions about the Catalan. You'd be better off consulting someone who specializes in 1.d4 systems as White."
Confidence badge: red (0.22). "The clone knows what it doesn't know."

### 9.3 The Extrapolation Test

The demo's power moment: asking about something NOT covered in the interview. The clone must:
1. Identify relevant-but-not-directly-applicable knowledge nodes
2. Combine them via the expert's stated principles
3. Generate a novel answer that SOUNDS like the expert
4. Assign appropriate uncertainty (confident, not certain)

This proves ECHOMIND captures reasoning patterns, not just facts.

---

## SECTION 10: 24-HOUR BUILD SPRINT PLAN

### Hours 0-1: Foundation
| Task | Details |
|------|---------|
| Create repo, install deps | `create-next-app`, FastAPI scaffold, `pip install` |
| API keys | Google Cloud project, enable Gemini/STT/Firestore APIs |
| Neo4j AuraDB | Create free instance, note Bolt URI + credentials |
| Firebase | Enable Auth (Google), create Firestore DB |
| `.env` config | All credentials, Pydantic settings |

**Deliverable**: All services connect. FastAPI returns `{"status": "ok"}`.

### Hours 1-3: Knowledge Graph + Extraction
| Task | Details |
|------|---------|
| `neo4j_client.py` + `operations.py` | CRUD for all 6 node types, 9 edge types |
| `schema.py` | Constraints and indexes |
| `knowledge_extractor.py` | Gemini structured output for nodes/edges from text |
| `gemini_service.py` | Centralized client with retry + rate limiting |
| `prompts.py` | All system prompts in one file |

**Deliverable**: Feed text → see nodes in Neo4j.

### Hours 3-5: Socratic Engine
| Task | Details |
|------|---------|
| `socratic_engine.py` | Main loop: text → extract → gaps → question |
| `question_generator.py` | Gemini question generation from graph state |
| `phase_manager.py` | Phase transitions with configurable thresholds |
| `gap_analyzer.py` | Cypher queries for low-confidence, disconnected nodes |
| `frontier_scorer.py` | Priority scoring function |

**Deliverable**: Simulate text interview - feed answers, get intelligent questions, watch graph grow.

### Hours 5-7: Speech Pipeline + WebSocket
| Task | Details |
|------|---------|
| `stt_service.py` | Google STT V2 streaming |
| `interview.py` endpoints | WebSocket: STT → Socratic Engine |
| `audio_service.py` | Audio chunk handling |
| End-to-end test | Speak → transcript → question |

**Deliverable**: Voice conversation with the Socratic engine.

### Hours 7-9: Digital Twin Inference
| Task | Details |
|------|---------|
| `query_analyzer.py` | Gemini query decomposition |
| `subgraph_retriever.py` | Multi-strategy Neo4j retrieval |
| `reasoning_chain.py` | Gemini + subgraph → twin response |
| `confidence_calibrator.py` | Calibration logic |
| `clone.py` endpoints | REST endpoint for clone queries |

**Deliverable**: Ask clone questions, get calibrated responses with reasoning chains.

### Hours 9-12: Frontend Core
| Task | Details |
|------|---------|
| Layout + routing | App shell, navigation, 3 pages |
| `InterviewPanel.tsx` | WebSocket, audio streaming, transcript |
| `AudioControls.tsx` + `useAudioStream.ts` | Browser mic API |
| `ForceGraph.tsx` | react-force-graph-2d with type colors |
| `ChatInterface.tsx` | Clone chat with message history |

**Deliverable**: All three pages render with real data.

### Hours 12-15: Frontend Polish
| Task | Details |
|------|---------|
| `MiniGraphPreview.tsx` | Real-time graph during interview |
| `ConfidenceBadge.tsx` + `ReasoningChain.tsx` | Clone response details |
| `NodeDetail.tsx` + `GraphControls.tsx` | Graph interaction |
| `CoverageHeatmap.tsx` | Domain coverage treemap |
| Firebase Auth | Google Sign-In flow |

### Hours 15-17: Chess Demo Content
| Task | Details |
|------|---------|
| Chess interview script | Openings, middlegame, endgame, tactics |
| Pre-load seed knowledge | Text-based interview → populate graph |
| Test clone | Verify reasonable chess answers |
| Identify "aha moment" | Find novel-reasoning test queries |

**Deliverable**: Pre-populated chess graph with 800+ nodes.

### Hours 17-19: Hardening
Error handling, WebSocket reconnection, Gemini rate limiting, loading states, contradiction detector.

### Hours 19-21: Integration Testing
Full interview simulation, clone stress test (20 queries), graph at scale, mobile responsiveness.

### Hours 21-23: Demo Preparation
Rehearse 3 times, pre-warm services, prepare video backup, polish landing page.

### Hours 23-24: Final Polish
Slides, README, clean debug output, final end-to-end run.

### What to Stub for Hackathon
1. **Embedding search**: Simple string matching in Cypher instead of vector indexes
2. **Audio recording**: Skip - focus on live transcription only
3. **Redundancy checker**: Simple set of recent question strings instead of embedding similarity
4. **Phase 4 contradictions**: Simplified version checking rules with same scope
5. **TTS output**: Text display instead of speech for questions

---

## SECTION 11: TECHNICAL RISKS & MITIGATIONS

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Interview quality variance** - expert gives terse, unhelpful answers | HIGH | `follow_up_if_brief` in every question. Phase-aware escalation: if answers get short, switch to scenario-based questions. Pre-interview coaching guide. |
| **Knowledge graph inconsistencies** - extraction creates duplicate/conflicting nodes | HIGH | Entity resolution via embedding similarity against existing nodes. Gemini receives current node names for disambiguation. Periodic graph cleanup pass. |
| **Clone overconfidence** - twin confidently states things the expert didn't say | CRITICAL | Strict subgraph-only prompting. Calibration system with evidence factor. "I don't know" threshold. Post-hoc expert validation. |
| **Voice persona uncanny valley** - TTS sounds weird | LOW | Stub TTS for hackathon (text only). For production, use custom voice cloning with expert consent. |
| **Expert cooperation** - expert gets frustrated with questioning style | MEDIUM | Phase transitions provide variety. "Skip question" button. Real-time feedback on graph growth motivates engagement. |
| **Gemini rate limits during hackathon** | HIGH | Pre-cache demo responses. Batch extraction calls. Request quota increase. Video backup. |
| **Neo4j AuraDB free tier limits** | LOW | 50K nodes is 20x what a single interview produces. Only a risk if running many interviews. |
| **STT accuracy in noisy environment** | MEDIUM | Text input fallback always available. Pre-test audio setup. |
| **Knowledge extraction quality** - Gemini misinterprets expert statements | HIGH | Expert review loop post-interview. Confidence signals from hedge words. Multiple extraction passes from overlapping transcript windows. |
| **Latency** - real-time interview loop too slow | HIGH | Gemini Flash is fast enough (<1s for extraction + question). Async extraction (don't block on graph write). Batch writes to Neo4j. |

---

## SECTION 12: BUSINESS MODEL

### 12.1 Target Markets

| Market | Use Case | Value Proposition | Deal Size |
|--------|----------|-------------------|-----------|
| **Enterprise knowledge preservation** | Retiring experts, departing employees | Capture 30 years of knowledge in 2 hours | $50-500K/year |
| **Professional services** | Law firms, consulting, accounting | Clone senior partners for junior team augmentation | $100-300K/year |
| **Aviation / Manufacturing** | Maintenance experts, safety knowledge | FAA/regulatory compliance, reduce error rates | $200K-1M/year |
| **Medical** | Senior diagnosticians, rare disease specialists | Preserve diagnostic reasoning for training | $100-500K/year |
| **Legal** | Retiring judges, senior litigators | Capture precedent reasoning and case strategy | $100-300K/year |
| **Succession planning** | Family businesses, specialized roles | Knowledge transfer during leadership transitions | $25-100K |

### 12.2 Pricing

| Tier | Price | Includes |
|------|-------|---------|
| **Starter** | $2,000/interview | Single 2-hour interview, knowledge graph, clone access for 1 year |
| **Professional** | $10,000/expert | 4 interview sessions (8 hours total), iterative graph refinement, expert validation, unlimited clone queries |
| **Enterprise** | Custom ($50K+/year) | Unlimited interviews, SSO, private deployment, API access, analytics, dedicated support |

### 12.3 Revenue Model

Per-interview revenue + recurring clone access fees:
- Year 1 target: 500 interviews × $5K avg = $2.5M ARR
- COGS per interview: ~$5 (Gemini) + $2 (STT) + $1 (compute) = ~$8
- Gross margin: >99% per interview (value is in the IP, not compute)
- Recurring: $500/year per active clone for query access

---

## SECTION 13: JUDGING CRITERIA & PITCH STRUCTURE

### 13.1 Judging Criteria Strategy

| Criterion | Weight | How ECHOMIND Wins |
|-----------|--------|-------------------|
| **Innovation** | 25% | No product does AI-driven Socratic interviews → knowledge graph → reasoning digital twin. The combination is novel. |
| **Technical Complexity** | 25% | Five-phase Socratic engine, typed knowledge graph, multi-strategy subgraph retrieval, calibrated confidence, real-time speech pipeline. Not a wrapper. |
| **Impact** | 25% | $47B knowledge loss problem. Universal: aviation, medicine, law, engineering, any domain where expertise matters. |
| **Completeness** | 15% | Working end-to-end: speak into mic → watch graph build → chat with clone that reasons about novel situations. |
| **Presentation** | 10% | The "aha moment" when the clone reasons about h4 in the Najdorf using principles it was never directly taught. |

### 13.2 Pitch Structure (5 Minutes)

```
00:00-00:30  HOOK: "When a 30-year expert walks out the door, $47 billion in
             knowledge walks with them every year. What if you could clone their brain?"
00:30-01:30  PROBLEM: Show bus factor. Show why documents, videos, mentorship fail.
01:30-02:00  SOLUTION: "ECHOMIND: AI Socratic interviews → knowledge graph → digital twin"
02:00-03:30  LIVE DEMO: Quick interview exchange → graph building → clone answering
03:30-04:30  AHA MOMENT: Clone reasons about novel question using combined principles
04:30-04:45  CALIBRATION: Clone says "I don't know" where it should
04:45-05:00  CLOSE: "Expert knowledge shouldn't die when experts retire.
             ECHOMIND makes expertise immortal."
```

### 13.3 Handling Judge Questions

- **"How accurate is the clone?"** → "Every response includes a calibrated confidence score. The clone knows what it doesn't know - it says 'I don't know' when knowledge is missing, not make things up."
- **"What about privacy?"** → "The expert controls everything. They review the graph, approve the clone, and can delete it anytime. Data stays in their organization's cloud."
- **"Why not just record a video?"** → "A video answers the questions someone thought to ask. ECHOMIND asks the 10,000 questions nobody thought to ask - including the edge cases and contradictions the expert doesn't realize they know."
- **"What's the moat?"** → "Three things: the five-phase Socratic extraction algorithm, the typed knowledge graph with contradiction resolution, and the calibrated inference engine that says 'I don't know' instead of hallucinating."

---

## SECTION 14: APPENDICES

### 14.1 API Endpoints

```
POST   /api/interview/start
  Body: { expert_name, domain, planned_duration_minutes }
  → { session_id, ws_url }

WS     /api/interview/ws/{session_id}
  Client→Server: { type: "audio_chunk"|"control"|"text_input", ... }
  Server→Client: { type: "transcript"|"question"|"extraction"|"phase_change"|"graph_update"|"progress", ... }

GET    /api/interview/{session_id}/status → { phase, questions_asked, nodes, edges, elapsed }
POST   /api/interview/{session_id}/end → { summary }

POST   /api/clone/{session_id}/query
  Body: { question, include_reasoning }
  → { answer, confidence, calibration, reasoning_chain, source_nodes, uncertainty_type }

GET    /api/clone/{session_id}/capabilities → { strong_areas, weak_areas, total_nodes, coverage }

GET    /api/graph/{session_id} → { nodes, edges, stats }
GET    /api/graph/{session_id}/stats → { node_counts, edge_counts, avg_confidence, coverage_by_domain }
GET    /api/graph/{session_id}/node/{node_id} → { node, connections }
GET    /api/graph/{session_id}/search?q=term → { results }
```

### 14.2 Environment Variables

```bash
# Google Cloud
GCP_PROJECT_ID=echomind-prod
GCP_REGION=us-central1

# Gemini
GEMINI_FLASH_MODEL=gemini-2.0-flash
GEMINI_PRO_MODEL=gemini-1.5-pro-002
GEMINI_EMBEDDING_MODEL=text-embedding-004

# Neo4j
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=xxxxx

# Firebase
FIREBASE_PROJECT_ID=echomind-prod
FIREBASE_API_KEY=xxxxx

# Google STT
GOOGLE_STT_PROJECT=echomind-prod

# API Config
API_PORT=8080
```

### 14.3 Key Dependencies

**Backend (Python 3.11+)**:
```
fastapi==0.115.0
uvicorn==0.30.0
websockets==13.0
google-generativeai==0.8.0
google-cloud-speech==2.27.0
google-cloud-firestore==2.19.0
google-cloud-storage==2.18.0
firebase-admin==6.6.0
neo4j==5.25.0
pydantic==2.9.0
httpx==0.27.0
numpy==1.26.0
```

**Frontend (Node 20+)**:
```
next@14.2
react@18.3
react-force-graph-2d@1.25
firebase@10.14
tailwindcss@3.4
shadcn/ui
@tanstack/react-query@5.50
```

### 14.4 Critical Implementation Files (Priority Order)

1. **`backend/config/prompts.py`** - Every Gemini prompt in one file. 60% of debugging is prompt tuning. Centralization is the highest-leverage organizational decision.
2. **`backend/core/socratic_engine.py`** - Central orchestrator connecting STT, extraction, gap analysis, question generation. Everything flows through here.
3. **`backend/core/knowledge_extractor.py`** - Gemini structured output converting transcript → typed nodes + edges. Extraction quality determines everything downstream.
4. **`backend/twin/inference_engine.py`** - The twin query pipeline: analysis → subgraph → reasoning → calibration. This is where the "aha moment" happens.
5. **`backend/graph/operations.py`** - All Cypher queries. The graph is the system's memory; this file defines how it reads and writes.

### 14.5 Verification Plan

1. **Unit tests**: Mock Gemini responses, test extraction produces correct node/edge types, test confidence calibration thresholds
2. **Integration test**: Text-based interview simulation (no audio) - feed 20 scripted answers, verify graph has expected structure
3. **Clone accuracy test**: 10 held-out chess questions answered by both clone and "expert" - compare
4. **Latency test**: Interview loop completes in <2s per cycle (extract + gap analysis + question generation)
5. **End-to-end demo rehearsal**: Full audio interview → graph → clone query, 3 times minimum before presentation
