/**
 * @file ArchitectureSection.tsx
 * @description Technical architecture breakdown of Orto's 4-stage neurosymbolic cascade
 * @module frontend/src/components
 */

import React from 'react';
import { GitBranch, Sparkles, ShieldCheck, ArrowRight } from 'lucide-react';

export const ArchitectureSection: React.FC = () => {
  return (
    <section className="sec inkband" id="engine">
      <div className="wrap sec-grid">
        <aside className="rail">
          <span className="r-idx">02</span>
          <div className="r-line" />
          <span className="r-name">Architecture</span>
        </aside>

        <div className="sec-body">
          <div className="eyebrow m-eb">
            02 <em>/ architecture</em>
          </div>
          <h2 className="sec-title" data-rv="wipe">
            A neurosymbolic <span className="serif">cascade.</span>
          </h2>
          <p className="sec-lede" data-rv style={{ '--d': '0.1s' } as React.CSSProperties}>
            Three decoupled layers, one invariant: the original string is never rewritten — only
            patched, re-parsed, asserted, then rendered.
          </p>

          <div className="arch">
            <span className="pulse" />
            <span className="pulse p2" />
            <span className="pulse p3" />

            <div
              className="scard"
              style={{ '--sc': '#6fc3cf' } as React.CSSProperties}
              data-rv
            >
              <span className="snum">S1</span>
              <div className="sicon">
                <GitBranch size={19} />
              </div>
              <h3>Feature Engine</h3>
              <span className="stag">CLASSICAL · SPACY UD</span>
              <ul>
                <li>
                  <b>Offset-preserving tokenization</b> — whitespace &amp; punctuation never mutated (FR-1.1).
                </li>
                <li>
                  Directed UD edges: <b>nsubj · ROOT · dobj · prep · pobj</b> (FR-1.2).
                </li>
                <li>
                  Morphological bundles: <b>Number · Person · Tense · VerbForm</b>.
                </li>
                <li>Priors serialized into the LLM system prompt (FR-1.3).</li>
              </ul>
              <div className="sfoot">orto/core/syntax_engine.py · en_core_web_sm · ≤ 2 GB RAM</div>
            </div>

            <div
              className="scard"
              style={{ '--sc': '#b9a5f2', '--d': '0.07s' } as React.CSSProperties}
              data-rv
            >
              <span className="snum">S2</span>
              <div className="sicon">
                <Sparkles size={19} />
              </div>
              <h3>LLM Diagnostics</h3>
              <span className="stag">NEURAL · CONSTRAINED DECODE</span>
              <ul>
                <li>
                  <b>Strict schema decoding</b> — Pydantic-validated, wrappers rejected (FR-2.1).
                </li>
                <li>
                  <b>Surgical locality</b>: minimal sub-phrase replacement only (FR-2.2).
                </li>
                <li>
                  Exactly one <b>ERRANT class</b> per edit, from the official taxonomy (FR-2.3).
                </li>
                <li>
                  Rule citation + explanation + <b>counterfactual pair</b> (FR-2.4).
                </li>
              </ul>
              <div className="sfoot">
                orto/llm/ · schemas.py + prompts.py · temp=0.00 · seed=42
              </div>
            </div>

            <div
              className="scard"
              style={{ '--sc': '#6fd4a8', '--d': '0.14s' } as React.CSSProperties}
              data-rv
            >
              <span className="snum">S3</span>
              <div className="sicon">
                <ShieldCheck size={19} />
              </div>
              <h3>Symbolic Critic</h3>
              <span className="stag">SYMBOLIC · IN-MEMORY CHECK</span>
              <ul>
                <li>
                  <b>Reverse-offset virtual patching</b> — zero index drift (FR-3.1).
                </li>
                <li>
                  Subject–verb agreement asserted on <b>re-parse</b> (FR-3.2).
                </li>
                <li>
                  <b>Orphan-token</b> &amp; tree-connectivity assertions (FR-3.3).
                </li>
                <li>
                  One targeted <b>refinement retry</b> with the parser trace (FR-3.4).
                </li>
              </ul>
              <div className="sfoot">
                orto/critic/verifier.py · catch rate 94.3% on induced flaws
              </div>
            </div>

            <div
              className="scard"
              style={{ '--sc': '#e8b45f', '--d': '0.21s' } as React.CSSProperties}
              data-rv
            >
              <span className="snum">S4</span>
              <div className="sicon">
                <ArrowRight size={19} />
              </div>
              <h3>Verified Payload</h3>
              <span className="stag">RENDER · CONSUME</span>
              <ul>
                <li>
                  <b>Character-exact diffs</b> for web editors &amp; diff UIs.
                </li>
                <li>
                  Color-coded <b>ERRANT badges</b>, per category.
                </li>
                <li>JSON / REST / Web-UI consumption, one contract.</li>
                <li>
                  End-to-end <b>≤ 1.8 s p95</b> per standard paragraph.
                </li>
              </ul>
              <div className="sfoot">orto/pipeline.py · assert text[s:e] == original_text</div>
            </div>
          </div>

          <div className="loopback">
            <div className="lb" />
            <span>CRITIC FAIL → 1× TARGETED LLM REFINEMENT</span>
          </div>

          <div className="pnl equation spot" data-rv>
            <code>Number(SubjectHead) ≡ Number(PatchedVerb)</code>
            <p>
              Every edit flagged{' '}
              <span style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: '#e8706f' }}>
                R:VERB:SVA
              </span>{' '}
              is re-parsed through spaCy and asserted against this invariant before it is ever
              rendered. If the patched sentence breaks agreement, the edit is rejected — or refined
              exactly once.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
