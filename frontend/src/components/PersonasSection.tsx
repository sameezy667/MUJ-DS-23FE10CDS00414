/**
 * @file PersonasSection.tsx
 * @description Target persona showcase for researchers, language learners, and platform engineers
 * @module frontend/src/components
 */

import React from 'react';
import { BarChart2, MessageSquare, Code2 } from 'lucide-react';

export const PersonasSection: React.FC = () => {
  return (
    <section className="sec" id="personas">
      <div className="wrap sec-grid">
        <aside className="rail">
          <span className="r-idx">08</span>
          <div className="r-line" />
          <span className="r-name">Built For</span>
        </aside>

        <div className="sec-body">
          <div className="eyebrow m-eb">
            08 <em>/ built for</em>
          </div>
          <h2 className="sec-title" data-rv="wipe">
            Three readers, <span className="serif">one engine.</span>
          </h2>

          <div className="pgrid" style={{ marginTop: '48px' }}>
            <div
              className="pnl pcard2 spot"
              style={{ '--pc': '#1a6f8a' } as React.CSSProperties}
              data-rv
            >
              <div className="pav">
                <BarChart2 size={20} />
              </div>
              <h3>The Researcher</h3>
              <span className="prole">NLP · Academic evaluator</span>
              <p>
                Reproducible ablations against BEA-2019 &amp; CoNLL-2014, category-level ERRANT
                scoring, and a one-command benchmark runner. No magic — every number
                reconstructable.
              </p>
              <blockquote>
                “Finally an engine where I can ablate the critic and watch F₀.₅ move — per error
                class.”
                <footer>— A/B ablation matrix, benchmarks/run_ablations.py</footer>
              </blockquote>
            </div>

            <div
              className="pnl pcard2 spot"
              style={{ '--pc': '#177a4e', '--d': '0.08s' } as React.CSSProperties}
              data-rv
            >
              <div className="pav">
                <MessageSquare size={20} />
              </div>
              <h3>The Language Learner</h3>
              <span className="prole">Second-language writer</span>
              <p>
                Minimal corrections that keep your voice — each with the formal rule, the
                plain-language reason, and a counterfactual pair showing when your original word
                would be right.
              </p>
              <blockquote>
                “It fixed one word, told me why, and showed me a sentence where my word was the
                correct one.”
                <footer>— counterfactual pedagogy, FR-2.4</footer>
              </blockquote>
            </div>

            <div
              className="pnl pcard2 spot"
              style={{ '--pc': '#6a4fa3', '--d': '0.16s' } as React.CSSProperties}
              data-rv
            >
              <div className="pav">
                <Code2 size={20} />
              </div>
              <h3>The Developer</h3>
              <span className="prole">Product · Platform engineer</span>
              <p>
                A typed library and a REST contract emitting deterministic character spans — drop
                it into an editor, an extension, or a grading pipeline and render diffs without
                guesswork.
              </p>
              <blockquote>
                “Spans that survive an assert. I can build an entire review UI on this.”
                <footer>— POST /api/v1/analyze · span[37,41]</footer>
              </blockquote>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
