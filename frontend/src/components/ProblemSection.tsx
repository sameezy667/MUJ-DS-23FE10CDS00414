/**
 * @file ProblemSection.tsx
 * @description Educational comparison section analyzing the failure modes of pure rules vs raw LLM rewrites
 * @module frontend/src/components
 */

import React from 'react';
import { Check, X } from 'lucide-react';

export const ProblemSection: React.FC = () => {
  return (
    <section className="sec" id="problem">
      <div className="wrap sec-grid">
        <aside className="rail">
          <span className="r-idx">01</span>
          <div className="r-line" />
          <span className="r-name">The Problem</span>
        </aside>

        <div className="sec-body">
          <div className="eyebrow m-eb">
            01 <em>/ the problem</em>
          </div>
          <h2 className="sec-title" data-rv="wipe">
            Writing assistants fail
            <br />
            in <span className="serif">two directions.</span>
          </h2>
          <p className="sec-lede" data-rv style={{ '--d': '0.1s' } as React.CSSProperties}>
            Both extremes are unusable for real correction work — one is too brittle to see the
            error, the other too confident to admit which span it touched.
          </p>

          <div className="polar">
            <div className="pnl pcard spot" data-rv>
              <h3>Rule-based engines</h3>
              <span className="ptag">DETERMINISTIC · FRAGILE</span>
              <ul>
                <li className="good">
                  <Check className="ic" stroke="#177a4e" />
                  <span>
                    <b>Microsecond latency</b>, zero output variance across runs.
                  </span>
                </li>
                <li className="bad">
                  <X className="ic" stroke="#d92c35" />
                  <span>
                    Blind to <b>long-range agreement</b> — “the box … <b>were</b>”.
                  </span>
                </li>
                <li className="bad">
                  <X className="ic" stroke="#d92c35" />
                  <span>
                    Real-word confusables slip through — <b>affect / effect</b>.
                  </span>
                </li>
                <li className="bad">
                  <X className="ic" stroke="#d92c35" />
                  <span>
                    No model of <b>structural syntactic ambiguity</b>.
                  </span>
                </li>
              </ul>
            </div>

            <div className="pnl pcard spot" data-rv style={{ '--d': '0.1s' } as React.CSSProperties}>
              <h3>End-to-end LLM rewrites</h3>
              <span className="ptag">FLUENT · UNACCOUNTABLE</span>
              <ul>
                <li className="good">
                  <Check className="ic" stroke="#177a4e" />
                  <span>
                    <b>Fluid surface corrections</b> from a single prompt.
                  </span>
                </li>
                <li className="bad">
                  <X className="ic" stroke="#d92c35" />
                  <span>
                    <b>Stylistic drift</b> — your voice rewritten without asking.
                  </span>
                </li>
                <li className="bad">
                  <X className="ic" stroke="#d92c35" />
                  <span>
                    No <b>character offsets</b> for diff UIs — guesswork rendering.
                  </span>
                </li>
                <li className="bad">
                  <X className="ic" stroke="#d92c35" />
                  <span>
                    <b>Hallucinated grammatical justifications</b> for edits it can’t defend.
                  </span>
                </li>
              </ul>
            </div>
          </div>

          <div className="pnl gap-band spot" data-rv>
            <div>
              <h4>The GEC diagnostic gap</h4>
              <p>
                Sequence taggers (GECToR-class) emit corrected token streams — with no
                human-interpretable rule, no cited taxonomy, and no counterfactual for the learner
                who wants to know <i>why</i>.
              </p>
            </div>
            <span className="gap-orto">
              Orto: span + rule + reason + counterfactual — verified before render.
            </span>
          </div>

          <div className="drift" data-rv>
            <div className="drift-title">THE SAME SENTENCE · TWO PHILOSOPHIES</div>
            <div className="drow">
              <span className="dlab src">INPUT</span>
              <p className="dtext">
                Me and my sister <mark>goes</mark> to the lake every summer, and we catch{' '}
                <mark>fishes</mark>.
              </p>
              <span />
            </div>
            <div className="drow">
              <span className="dlab llm">LLM</span>
              <p className="dtext">
                <span className="u">My sister and I</span> <span className="u">go</span> to the lake
                every summer, and we catch <span className="u">fish</span> <span className="u">there</span>.
              </p>
              <span className="dstat red">12 TOKENS REWRITTEN · VOICE LOST</span>
            </div>
            <div className="drow">
              <span className="dlab orto">ORTO</span>
              <p className="dtext">
                Me and my sister <del>goes</del>{' '}
                <b style={{ color: 'var(--green)', fontWeight: 600 }}>go</b> to the lake every
                summer, and we catch <del>fishes</del>{' '}
                <b style={{ color: 'var(--green)', fontWeight: 600 }}>fish</b>.
              </p>
              <span className="dstat grn">2 TOKENS ALTERED · 0 STYLE EDITS</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
