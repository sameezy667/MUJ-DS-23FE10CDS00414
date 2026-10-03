/**
 * @file Footer.tsx
 * @description Editorial footer displaying repository hierarchy, quick links, and system specs
 * @module frontend/src/components
 */

import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="inkband">
      <div className="wrap">
        <div className="fgrid">
          <div data-rv>
            <h5>REPOSITORY LAYOUT</h5>
            <pre className="ftree">
              orto/{'\n'}
              <span className="d">├──</span> <span className="f">orto/</span>{'\n'}
              <span className="d">│   ├──</span> <span className="f">core/</span>{'       '}<span className="x">tokenizer · syntax_engine · patcher</span>{'\n'}
              <span className="d">│   ├──</span> <span className="f">llm/</span>{'        '}<span className="x">client · schemas · prompts</span>{'\n'}
              <span className="d">│   ├──</span> <span className="f">critic/</span>{'     '}<span className="x">verifier (symbolic SVA)</span>{'\n'}
              <span className="d">│   ├──</span> <span className="f">style/</span>{'      '}<span className="x">analyzer · naturalizer · metrics</span>{'\n'}
              <span className="d">│   └──</span> <b>pipeline.py</b>{'  '}<span className="x">end-to-end orchestrator</span>{'\n'}
              <span className="d">├──</span> <span className="f">backend/</span>{'     '}<span className="x">server.py (FastAPI REST server)</span>{'\n'}
              <span className="d">├──</span> <span className="f">frontend/</span>{'    '}<span className="x">React 19 + TypeScript Vite Studio</span>{'\n'}
              <span className="d">├──</span> <span className="f">benchmarks/</span>{'   '}<span className="x">evaluate.py · run_ablations.py</span>{'\n'}
              <span className="d">├──</span> <span className="f">data/</span>{'         '}<span className="x">sample_benchmark.jsonl · confusion_sets</span>{'\n'}
              <span className="d">└──</span> <span className="f">tests/</span>{'        '}<span className="x">36/36 tests passing (pytest)</span>
            </pre>
          </div>

          <div className="fcol" data-rv style={{ '--d': '0.08s' } as React.CSSProperties}>
            <h5>ENGINE</h5>
            <p>
              Neurosymbolic GEC &amp; diagnostic engine. Universal Dependency priors, constrained LLM
              decoding, and a symbolic critic that refuses to render a regressive fix.
            </p>
            <ul className="flinks">
              <li>
                <a href="#engine">Architecture cascade</a>
              </li>
              <li>
                <a href="#demo">Live console</a>
              </li>
              <li>
                <a href="#bench">Benchmark suite</a>
              </li>
              <li>
                <a href="#tax">ERRANT taxonomy</a>
              </li>
              <li>
                <a href="#stylometry">Stylometry &amp; naturalness</a>
              </li>
              <li>
                <a href="#api">REST contract</a>
              </li>
            </ul>
          </div>

          <div data-rv style={{ '--d': '0.16s' } as React.CSSProperties}>
            <h5>RELEASE</h5>
            <div className="fmark">
              <svg className="ic logo-mark" viewBox="0 0 32 32">
                <path
                  d="M9 8l7 7 7-7"
                  stroke="#d92c35"
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <circle cx="16" cy="21.5" r="6" stroke="#191813" strokeWidth="3" fill="none" />
              </svg>
              <b
                style={{
                  fontFamily: 'var(--disp)',
                  letterSpacing: '0.1em',
                  fontOpticalSizing: 'auto',
                }}
              >
                ORTO
              </b>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--mut)' }}>
              v1.0.0 — academic benchmark &amp; open-source production release. MIT licensed. PEP 8,
              mypy strict, ≥ 85% core coverage.
            </p>
          </div>
        </div>

        <div className="fbottom">
          <span>ORTO · SURGICAL GRAMMAR CORRECTION, DOWN TO THE CHARACTER.</span>
          <span>MIT · pip install -e . · make run-server</span>
        </div>
      </div>
    </footer>
  );
};
