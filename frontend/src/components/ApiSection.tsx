/**
 * @file ApiSection.tsx
 * @description Interactive API contract explorer with syntax highlighting and Python SDK examples
 * @module frontend/src/components
 */

import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface ApiSectionProps {
  onShowToast: (msg: string) => void;
}

export const ApiSection: React.FC<ApiSectionProps> = ({ onShowToast }) => {
  const [activeTab, setActiveTab] = useState<'req' | 'res' | 'py' | 'sc'>('req');
  const [copied, setCopied] = useState<boolean>(false);

  const snippets = {
    req: {
      head: 'POST /api/v1/analyze  ·  Authorization: Bearer <API_KEY>  ·  Content-Type: application/json',
      code: `{
  "text": "The box of old vintage vinyl records were dropped by the movers.",
  "options": {
    "enable_critic": true,
    "max_refinements": 1,
    "model": "gpt-4o-mini",
    "include_style": true
  }
}`,
    },
    res: {
      head: 'HTTP/1.1 200 OK  ·  content-type: application/json',
      code: `{
  "original_text": "The box of old vintage vinyl records were dropped by the movers.",
  "corrected_text": "The box of old vintage vinyl records was dropped by the movers.",
  "edits": [
    {
      "span": { "start_char": 37, "end_char": 41, "original_text": "were" },
      "replacement": "was",
      "errant_type": "R:VERB:SVA",
      "linguistic_rule": "Subject-Verb Agreement with Intervening Prepositional Phrase",
      "explanation": "The grammatical subject head is 'box' (singular), separated by the prepositional phrase 'of old vintage vinyl records'. The verb must take the singular form.",
      "counterfactual_example": "The records were dropped by the movers.",
      "confidence": 0.98,
      "critic_verified": true
    }
  ],
  "telemetry": { "latency_ms": 642, "input_tokens": 12, "refinement_cycles": 0, "critic_passed": true }
}`,
    },
    py: {
      head: '// typed python client — orto.pipeline.OrtoEngine adapter (OpenAI / Anthropic / LiteLLM / vLLM)',
      code: `from orto import OrtoEngine

engine = OrtoEngine(model="gpt-4o-mini", enable_critic=True)

analysis = engine.analyze(
    "The box of old vintage vinyl records were dropped by the movers."
)

for edit in analysis.edits:
    print(edit.errant_type, edit.span.start_char, edit.replacement)
    # -> R:VERB:SVA 37 "was"

print(analysis.corrected_text)
# -> The box of old vintage vinyl records was dropped ...

assert analysis.edits[0].critic_verified is True`,
    },
    sc: {
      head: '// orto/llm/schemas.py — strict structured outputs, enforced at client boundary',
      code: `class SpanCoordinate(BaseModel):
    start_char: int      # 0-indexed offset in original text
    end_char: int
    original_text: str   # must equal input_text[start:end]

class DiagnosticEdit(BaseModel):
    span: SpanCoordinate
    replacement: str
    errant_type: Literal[
        "R:SPELL", "R:VERB:SVA", "R:VERB:TENSE", "R:NOUN:NUM",
        "R:PREP", "M:DET", "R:WO", "R:OTHER" ]
    linguistic_rule: str
    explanation: str
    counterfactual_example: str
    confidence: float = Field(ge=0.0, le=1.0)
    critic_verified: bool = True

class OrtoAnalysis(BaseModel):
    edits: List[DiagnosticEdit] = []`,
    },
  };

  const current = snippets[activeTab];

  const handleCopyCode = () => {
    navigator.clipboard.writeText(current.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    onShowToast('Snippet copied to clipboard');
  };

  const handleCopyInstall = () => {
    navigator.clipboard.writeText('pip install -e .');
    onShowToast('Install command copied');
  };

  return (
    <section className="sec" id="api">
      <div className="wrap sec-grid">
        <aside className="rail">
          <span className="r-idx">07</span>
          <div className="r-line" />
          <span className="r-name">API Contract</span>
        </aside>

        <div className="sec-body">
          <div className="eyebrow m-eb">
            07 <em>/ api contract</em>
          </div>
          <h2 className="sec-title" data-rv="wipe">
            Deterministic spans,
            <br />
            <span className="serif">straight to your editor.</span>
          </h2>
          <p className="sec-lede" data-rv style={{ '--d': '0.1s' } as React.CSSProperties}>
            A typed Python library and a REST contract that emits character-exact intervals —
            designed to drive web editors, browser extensions, and automated grading pipelines.
          </p>

          <div className="api-grid">
            <div className="code-panel" data-rv>
              <div className="code-tabs">
                <button
                  className={`ctab ${activeTab === 'req' ? 'on' : ''}`}
                  onClick={() => setActiveTab('req')}
                >
                  REQUEST
                </button>
                <button
                  className={`ctab ${activeTab === 'res' ? 'on' : ''}`}
                  onClick={() => setActiveTab('res')}
                >
                  RESPONSE
                </button>
                <button
                  className={`ctab ${activeTab === 'py' ? 'on' : ''}`}
                  onClick={() => setActiveTab('py')}
                >
                  PYTHON
                </button>
                <button
                  className={`ctab ${activeTab === 'sc' ? 'on' : ''}`}
                  onClick={() => setActiveTab('sc')}
                >
                  SCHEMA
                </button>
              </div>

              <div className="code-body">
                <button
                  className="sbtn copy-btn"
                  id="apiCopy"
                  aria-label="Copy snippet"
                  onClick={handleCopyCode}
                >
                  {copied ? <Check size={11} stroke="#6fd4a8" /> : <Copy size={11} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
                <div className="code-head" id="codeHead">
                  {current.head}
                </div>
                <pre id="codePre">
                  <code>{current.code}</code>
                </pre>
              </div>
            </div>

            <div
              className="pnl api-side spot"
              data-rv
              style={{ '--d': '0.1s' } as React.CSSProperties}
            >
              <h4>ENDPOINT</h4>
              <div className="ep">
                <b>POST</b>/api/v1/analyze
              </div>

              <h4 style={{ marginTop: '26px' }}>GUARANTEES</h4>
              <ul>
                <li>
                  <span style={{ color: 'var(--tx)' }}>text[start:end] == original_text</span> —
                  100% programmatic check
                </li>
                <li>Temperature 0.0 · seed 42 · reproducible spans</li>
                <li>Exponential backoff, classical fallback on rate limits</li>
                <li>Typed Pydantic models, mypy strict, ≥ 85% coverage</li>
              </ul>

              <h4 style={{ marginTop: '26px' }}>INSTALL</h4>
              <div className="install" id="installCmd" onClick={handleCopyInstall}>
                pip install -e .
                <Copy size={13} style={{ stroke: 'var(--dim)' }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
