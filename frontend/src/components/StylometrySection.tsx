/**
 * @file StylometrySection.tsx
 * @description Interactive AI Humanizer, stylometric cadence analyzer, and synthetic cliché marker detector
 * @module frontend/src/components
 */

import React, { useState } from 'react';
import { ShieldAlert, Wand2 } from 'lucide-react';
import type { StyleAnalysisResult } from '../types';

export const StylometrySection: React.FC = () => {
  const [inputText, setInputText] = useState<string>(
    'Delving deep into the rich tapestry of artificial intelligence serves as a testament to human ingenuity and plays a pivotal role in seamless innovation.'
  );
  const [humanizedResult, setHumanizedResult] = useState<string>('');
  const [styleReport, setStyleReport] = useState<StyleAnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const samplePresets = [
    {
      label: 'AI Cliché Cluster',
      text: 'Delving deep into the rich tapestry of artificial intelligence serves as a testament to human ingenuity and plays a pivotal role in seamless innovation.',
    },
    {
      label: 'Monotonous 8-Word Sentences',
      text: 'The model analyzes text with great precision. The parser extracts syntax relationships very reliably. The critic verifies subject verb agreement quickly.',
    },
    {
      label: 'Natural Human Flow',
      text: 'We shipped the engine in two weeks. It is fast, minimal, and never rewrites your sentences without proof.',
    },
  ];

  const handleRunHumanizer = async (textToRun?: string) => {
    const text = (textToRun !== undefined ? textToRun : inputText).trim();
    if (!text) return;

    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/style/humanize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (res.ok) {
        const data = await res.json();
        setHumanizedResult(data.humanized_text);
        setStyleReport(data.stylometry);
      } else {
        // Fallback local rule de-clichéing
        const decliched = text
          .replace(/\bdelving deep into\b/gi, 'exploring')
          .replace(/\brich tapestry of\b/gi, 'landscape of')
          .replace(/\bserves as a testament to\b/gi, 'demonstrates')
          .replace(/\bplays a pivotal role in\b/gi, 'is essential for')
          .replace(/\bseamless\b/gi, 'smooth');
        setHumanizedResult(decliched);
      }
    } catch {
      const decliched = text
        .replace(/\bdelving deep into\b/gi, 'exploring')
        .replace(/\brich tapestry of\b/gi, 'landscape of')
        .replace(/\bserves as a testament to\b/gi, 'demonstrates')
        .replace(/\bplays a pivotal role in\b/gi, 'is essential for')
        .replace(/\bseamless\b/gi, 'smooth');
      setHumanizedResult(decliched);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="sec inkband" id="stylometry">
      <div className="wrap sec-grid">
        <aside className="rail">
          <span className="r-idx">06</span>
          <div className="r-line" />
          <span className="r-name">AI Humanizer</span>
        </aside>

        <div className="sec-body">
          <div className="eyebrow m-eb">
            06 <em>/ stylometry &amp; ai humanizer</em>
          </div>
          <h2 className="sec-title" data-rv="wipe">
            Detecting synthetic cadence.
            <br />
            <span className="serif">Restoring human rhythm.</span>
          </h2>
          <p className="sec-lede" data-rv style={{ '--d': '0.1s' } as React.CSSProperties}>
            Beyond grammatical mechanics, Orto evaluates stylometric naturalness — quantifying
            sentence length burstiness $B = \sigma / \mu$, flagging synthetic cliché clusters, and
            surgically re-rhythming text without altering meaning.
          </p>

          <div className="chips" style={{ marginBottom: '18px' }}>
            {samplePresets.map((preset, idx) => (
              <button
                key={idx}
                className="chip"
                onClick={() => {
                  setInputText(preset.text);
                  handleRunHumanizer(preset.text);
                }}
              >
                {preset.label}
              </button>
            ))}
          </div>

          <div className="pnl spot" style={{ padding: '24px', marginBottom: '24px' }}>
            <div className="io-row" style={{ marginBottom: '16px' }}>
              <textarea
                id="ta"
                style={{
                  minHeight: '84px',
                  background: 'var(--sur2)',
                  color: 'var(--tx)',
                }}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
              <button
                className={`btn btn-primary ${isLoading ? 'busy' : ''}`}
                style={{ background: 'var(--green)', alignSelf: 'flex-start' }}
                disabled={isLoading}
                onClick={() => handleRunHumanizer()}
              >
                <Wand2 size={14} />
                Humanize Cadence
              </button>
            </div>

            {humanizedResult && (
              <div
                style={{
                  padding: '16px 18px',
                  background: 'rgba(23,122,78,0.06)',
                  border: '1px solid rgba(23,122,78,0.3)',
                  borderRadius: '9px',
                  marginBottom: '18px',
                }}
              >
                <span
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: '9px',
                    letterSpacing: '0.16em',
                    color: 'var(--green)',
                    display: 'block',
                    marginBottom: '6px',
                  }}
                >
                  RE-RHYTHMED HUMANIZED OUTPUT
                </span>
                <p
                  style={{
                    fontFamily: 'var(--disp)',
                    fontSize: '17.5px',
                    lineHeight: '1.9',
                    color: 'var(--tx)',
                  }}
                >
                  {humanizedResult}
                </p>
              </div>
            )}

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '16px',
                paddingTop: '16px',
                borderTop: '1px solid var(--line)',
              }}
            >
              <div>
                <span
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: '9px',
                    letterSpacing: '0.16em',
                    color: 'var(--dim)',
                    display: 'block',
                    textTransform: 'uppercase',
                  }}
                >
                  Burstiness ($B = \sigma / \mu$)
                </span>
                <b
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: '22px',
                    color:
                      (styleReport?.report.burstiness_score || 0.15) > 0.4
                        ? 'var(--green)'
                        : 'var(--red)',
                  }}
                >
                  {styleReport
                    ? styleReport.report.burstiness_score.toFixed(2)
                    : '0.18'}
                </b>
              </div>

              <div>
                <span
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: '9px',
                    letterSpacing: '0.16em',
                    color: 'var(--dim)',
                    display: 'block',
                    textTransform: 'uppercase',
                  }}
                >
                  Naturalness Grade
                </span>
                <b
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: '18px',
                    color:
                      styleReport?.report.naturalness_grade === 'Natural'
                        ? 'var(--green)'
                        : 'var(--red)',
                  }}
                >
                  {styleReport?.report.naturalness_grade || 'Monotonous / Synthetic'}
                </b>
              </div>

              <div>
                <span
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: '9px',
                    letterSpacing: '0.16em',
                    color: 'var(--dim)',
                    display: 'block',
                    textTransform: 'uppercase',
                  }}
                >
                  Passive Voice Density
                </span>
                <b
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: '18px',
                    color: 'var(--tx)',
                  }}
                >
                  {styleReport
                    ? `${Math.round(styleReport.report.passive_ratio * 100)}%`
                    : '20%'}
                </b>
              </div>

              <div>
                <span
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: '9px',
                    letterSpacing: '0.16em',
                    color: 'var(--dim)',
                    display: 'block',
                    textTransform: 'uppercase',
                  }}
                >
                  Detected Cliché Markers
                </span>
                <b
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: '18px',
                    color:
                      (styleReport?.report.cliche_count || 0) > 0 ? '#e8706f' : '#6fd4a8',
                  }}
                >
                  {styleReport?.report.cliche_count || 0} markers
                </b>
              </div>
            </div>

            {styleReport?.report.detected_markers &&
              styleReport.report.detected_markers.length > 0 && (
                <div style={{ marginTop: '18px' }}>
                  <span
                    style={{
                      fontFamily: 'var(--mono)',
                      fontSize: '9.5px',
                      color: 'var(--dim)',
                      display: 'block',
                      marginBottom: '8px',
                    }}
                  >
                    SYNTHETIC MARKERS DETECTED:
                  </span>
                  {styleReport.report.detected_markers.map((c) => (
                    <span className="cliche-badge" key={c}>
                      <ShieldAlert size={11} /> {c}
                    </span>
                  ))}
                </div>
              )}
          </div>

          <div className="pnl equation spot" data-rv>
            <code>Burstiness B = StandardDeviation(SentenceLengths) / Mean(SentenceLengths)</code>
            <p>
              Natural human writing exhibits high variance in sentence length — rapid punchy
              sentences mixed with periodic structures ($B &gt; 0.5$). Synthetic LLM text
              clusters unnaturally around uniform lengths ($B &lt; 0.25$).
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
