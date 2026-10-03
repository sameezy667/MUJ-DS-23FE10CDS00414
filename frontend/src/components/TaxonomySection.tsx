/**
 * @file TaxonomySection.tsx
 * @description ERRANT taxonomy reference matrix detailing the formal grammatical error categories
 * @module frontend/src/components
 */

import React from 'react';
import { CATS } from '../utils/engine';
import type { ErrantType } from '../types';

export const TaxonomySection: React.FC = () => {
  const categories: Array<{ id: ErrantType; num: string; delay?: string }> = [
    { id: 'R:SPELL', num: '01' },
    { id: 'R:VERB:SVA', num: '02', delay: '0.06s' },
    { id: 'R:VERB:TENSE', num: '03', delay: '0.12s' },
    { id: 'R:NOUN:NUM', num: '04', delay: '0.18s' },
    { id: 'R:PREP', num: '05' },
    { id: 'M:DET', num: '06', delay: '0.06s' },
    { id: 'R:WO', num: '07', delay: '0.12s' },
    { id: 'R:OTHER', num: '08', delay: '0.18s' },
  ];

  return (
    <section className="sec" id="tax">
      <div className="wrap sec-grid">
        <aside className="rail">
          <span className="r-idx">05</span>
          <div className="r-line" />
          <span className="r-name">ERRANT Taxonomy</span>
        </aside>

        <div className="sec-body">
          <div className="eyebrow m-eb">
            05 <em>/ errant taxonomy</em>
          </div>
          <h2 className="sec-title" data-rv="wipe">
            Every edit carries
            <br />
            a <span className="serif">formal class.</span>
          </h2>
          <p className="sec-lede" data-rv style={{ '--d': '0.1s' } as React.CSSProperties}>
            Eight official ERRANT categories. One badge per edit, machine-checkable,
            benchmark-comparable — never a vague “grammar suggestion”.
          </p>

          <div className="taxgrid">
            {categories.map((cat) => {
              const meta = CATS[cat.id];
              return (
                <div
                  key={cat.id}
                  className="pnl ttile spot"
                  style={
                    {
                      '--tc': meta.c,
                      '--d': cat.delay || '0s',
                    } as React.CSSProperties
                  }
                  data-rv
                >
                  <span className="tnum">{cat.num}</span>
                  <span className="dot" />
                  <code>{cat.id}</code>
                  <h4>{meta.label}</h4>
                  <p>{meta.desc}</p>
                  <div className="tex">
                    <s>{meta.bad}</s>
                    <i>→</i>
                    <b>{meta.good}</b>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};
