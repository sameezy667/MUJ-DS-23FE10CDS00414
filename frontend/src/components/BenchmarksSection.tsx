/**
 * @file BenchmarksSection.tsx
 * @description Benchmark evaluation results, ablation matrices, and ERRANT category breakdowns
 * @module frontend/src/components
 */

import React, { useEffect, useState } from 'react';

export const BenchmarksSection: React.FC = () => {
  const [inView, setInView] = useState<boolean>(false);

  useEffect(() => {
    const el = document.getElementById('bench');
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section className="sec inkband" id="bench">
      <div className="wrap sec-grid">
        <aside className="rail">
          <span className="r-idx">04</span>
          <div className="r-line" />
          <span className="r-name">Benchmarks</span>
        </aside>

        <div className="sec-body">
          <div className="eyebrow m-eb">
            04 <em>/ benchmarks</em>
          </div>
          <h2 className="sec-title" data-rv="wipe">
            Measured, <span className="serif">not vibes.</span>
          </h2>
          <p className="sec-lede" data-rv style={{ '--d': '0.1s' } as React.CSSProperties}>
            BEA-2019 (W&amp;I-dev) · ERRANT / M² scorer · F₀.₅ weights precision 2× over recall —
            false positives destroy user trust faster than misses.
          </p>

          <div className={`bento ${inView ? 'in' : ''}`} id="kpis">
            <div className="pnl kpi big spot" data-rv>
              <em>TARGET ≥ 68</em>
              <b>69.6</b>
              <span>F₀.₅ · BEA-2019 (W&amp;I-DEV)</span>
              <svg className="spark" viewBox="0 0 160 44">
                <defs>
                  <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0" stopColor="rgba(111,212,168,.2)" />
                    <stop offset="1" stopColor="rgba(111,212,168,0)" />
                  </linearGradient>
                </defs>
                <path
                  d="M0 36 L20 33 L40 34 L60 27 L80 28 L100 19 L120 16 L140 9 L160 5 L160 44 L0 44 Z"
                  fill="url(#sg)"
                />
                <polyline
                  className="spl"
                  points="0,36 20,33 40,34 60,27 80,28 100,19 120,16 140,9 160,5"
                />
                <circle className="spd" cx="160" cy="5" r="3" />
              </svg>
              <div className="spark-cap">ABLATION TRAJECTORY · LAST 8 RUNS</div>
            </div>

            <div
              className="pnl kpi spot"
              data-rv
              style={{ '--d': '0.06s' } as React.CSSProperties}
            >
              <em>&lt; 3.0</em>
              <b>2.1%</b>
              <span>Stylistic drift</span>
            </div>

            <div
              className="pnl kpi spot"
              data-rv
              style={{ '--d': '0.12s' } as React.CSSProperties}
            >
              <em>INVARIANT</em>
              <b>100%</b>
              <span>Span alignment</span>
            </div>

            <div
              className="pnl kpi spot"
              data-rv
              style={{ '--d': '0.18s' } as React.CSSProperties}
            >
              <em>≤ 1.8s</em>
              <b>1.62s</b>
              <span>Latency p95</span>
            </div>

            <div
              className="pnl kpi spot"
              data-rv
              style={{ '--d': '0.24s' } as React.CSSProperties}
            >
              <em>&gt; 92</em>
              <b>94.3%</b>
              <span>Critic catch rate</span>
            </div>
          </div>

          <div className="charts">
            <div className={`pnl chart spot ${inView ? 'in' : ''}`} data-rv id="chart1">
              <div className="pnl-b">
                <div className="chart-title">
                  F₀.₅ BY PIPELINE <span>HIGHER IS BETTER</span>
                </div>
                <div className="crow">
                  <span>Classical rules</span>
                  <div className="track">
                    <i
                      className="fill"
                      style={{ '--w': '45%', '--c': 'var(--ghost)' } as React.CSSProperties}
                    />
                  </div>
                  <b>45.0</b>
                </div>
                <div className="crow">
                  <span>Zero-shot LLM</span>
                  <div className="track">
                    <i
                      className="fill"
                      style={{ '--w': '51%', '--c': 'var(--ghost)' } as React.CSSProperties}
                    />
                  </div>
                  <b>51.0</b>
                </div>
                <div className="crow orto">
                  <span>ORTO HYBRID</span>
                  <div className="track">
                    <i
                      className="fill"
                      style={{ '--w': '69.6%', '--c': '#6fd4a8' } as React.CSSProperties}
                    />
                    <span className="target-line" />
                    <span className="target-tag">68 TARGET</span>
                  </div>
                  <b>69.6</b>
                </div>
              </div>
            </div>

            <div
              className={`pnl chart spot ${inView ? 'in' : ''}`}
              data-rv
              style={{ '--d': '0.08s' } as React.CSSProperties}
              id="chart2"
            >
              <div className="pnl-b">
                <div className="chart-title">
                  STYLISTIC DRIFT <span>LOWER IS BETTER</span>
                </div>
                <div className="crow">
                  <span>Zero-shot LLM</span>
                  <div className="track">
                    <i
                      className="fill"
                      style={{ '--w': '94.5%', '--c': '#e8706f' } as React.CSSProperties}
                    />
                  </div>
                  <b>18.9%</b>
                </div>
                <div className="crow">
                  <span>Classical rules</span>
                  <div className="track">
                    <i
                      className="fill"
                      style={{ '--w': '32%', '--c': 'var(--ghost)' } as React.CSSProperties}
                    />
                  </div>
                  <b>6.4%</b>
                </div>
                <div className="crow orto">
                  <span>ORTO HYBRID</span>
                  <div className="track">
                    <i
                      className="fill"
                      style={{ '--w': '10.5%', '--c': '#6fd4a8' } as React.CSSProperties}
                    />
                  </div>
                  <b>2.1%</b>
                </div>
              </div>
            </div>
          </div>

          <div className={`pnl cats spot ${inView ? 'in' : ''}`} data-rv id="catChart">
            <div className="pnl-b">
              <div className="chart-title">F₀.₅ · PER ERRANT CATEGORY</div>
              <div className="catrow">
                <span style={{ color: '#e8c268' }}>R:SPELL</span>
                <div className="ctrack">
                  <i style={{ '--w': '81.2%', background: '#e8c268' } as React.CSSProperties} />
                </div>
                <b>81.2</b>
              </div>
              <div className="catrow">
                <span style={{ color: '#e8706f' }}>R:VERB:SVA</span>
                <div className="ctrack">
                  <i style={{ '--w': '77.4%', background: '#e8706f' } as React.CSSProperties} />
                </div>
                <b>77.4</b>
              </div>
              <div className="catrow">
                <span style={{ color: '#6fc3cf' }}>R:NOUN:NUM</span>
                <div className="ctrack">
                  <i style={{ '--w': '69.1%', background: '#6fc3cf' } as React.CSSProperties} />
                </div>
                <b>69.1</b>
              </div>
              <div className="catrow">
                <span style={{ color: '#e8935c' }}>R:VERB:TENSE</span>
                <div className="ctrack">
                  <i style={{ '--w': '62.8%', background: '#e8935c' } as React.CSSProperties} />
                </div>
                <b>62.8</b>
              </div>
              <div className="catrow">
                <span style={{ color: '#8fb0e8' }}>R:PREP</span>
                <div className="ctrack">
                  <i style={{ '--w': '58.3%', background: '#8fb0e8' } as React.CSSProperties} />
                </div>
                <b>58.3</b>
              </div>
              <div className="catrow">
                <span style={{ color: '#b9a5f2' }}>M:DET</span>
                <div className="ctrack">
                  <i style={{ '--w': '54.6%', background: '#b9a5f2' } as React.CSSProperties} />
                </div>
                <b>54.6</b>
              </div>
              <div className="catrow">
                <span style={{ color: '#9a958a' }}>R:OTHER</span>
                <div className="ctrack">
                  <i style={{ '--w': '47.2%', background: '#9a958a' } as React.CSSProperties} />
                </div>
                <b>47.2</b>
              </div>
              <div className="catrow">
                <span style={{ color: '#e07ccf' }}>R:WO</span>
                <div className="ctrack">
                  <i style={{ '--w': '41.5%', background: '#e07ccf' } as React.CSSProperties} />
                </div>
                <b>41.5</b>
              </div>
            </div>
          </div>

          <div className="pnl spot" style={{ overflowX: 'auto' }} data-rv>
            <table className="abl">
              <thead>
                <tr>
                  <th>Ablation</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>F₀.₅</th>
                  <th>Drift</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <span className="plab">A · Zero-shot LLM</span>
                    <br />
                    <span
                      style={{
                        fontFamily: 'var(--mono)',
                        fontSize: '9.5px',
                        color: 'var(--dim)',
                      }}
                    >
                      raw rewrite prompt
                    </span>
                  </td>
                  <td>
                    <b>49.2</b>
                  </td>
                  <td>
                    <b>59.8</b>
                  </td>
                  <td>
                    <b>51.0</b>
                  </td>
                  <td>
                    <b>18.9%</b>
                  </td>
                  <td>rewrites whole clauses; no offsets</td>
                </tr>
                <tr>
                  <td>
                    <span className="plab">B · Classical rules</span>
                    <br />
                    <span
                      style={{
                        fontFamily: 'var(--mono)',
                        fontSize: '9.5px',
                        color: 'var(--dim)',
                      }}
                    >
                      SymSpell + UD heuristics
                    </span>
                  </td>
                  <td>
                    <b>55.0</b>
                  </td>
                  <td>
                    <b>26.1</b>
                  </td>
                  <td>
                    <b>45.0</b>
                  </td>
                  <td>
                    <b>6.4%</b>
                  </td>
                  <td>misses long-range dependencies</td>
                </tr>
                <tr className="orto">
                  <td>
                    <span className="plab">C · Orto hybrid</span>
                    <br />
                    <span
                      style={{
                        fontFamily: 'var(--mono)',
                        fontSize: '9.5px',
                        color: 'var(--dim)',
                      }}
                    >
                      priors + constrained LLM + critic
                    </span>
                  </td>
                  <td>
                    <b>72.4</b>
                  </td>
                  <td>
                    <b>60.3</b>
                  </td>
                  <td>
                    <b>69.6</b>
                  </td>
                  <td>
                    <b>2.1%</b>
                  </td>
                  <td>surgical spans · 100% alignment</td>
                </tr>
              </tbody>
            </table>
          </div>

          <p className="bench-foot" data-rv>
            Evaluation run on sample_benchmark.jsonl (W&amp;I-dev slice, n=250). Run the full
            benchmark suite with <span style={{ color: 'var(--mut)' }}>make benchmark</span>.
          </p>
        </div>
      </div>
    </section>
  );
};
