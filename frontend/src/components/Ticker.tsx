/**
 * @file Ticker.tsx
 * @description Infinite scrolling telemetry marquee ticker component
 * @module frontend/src/components
 */

import React from 'react';

export const Ticker: React.FC = () => {
  const items = [
    { num: '69.6', label: 'F₀.₅', note: '· BEA-2019 W&I-DEV' },
    { num: '100%', label: 'SPAN ALIGNMENT', note: '· CHAR-EXACT' },
    { num: '2.1%', label: 'STYLISTIC DRIFT', note: '· NON-ERRONEOUS TOKENS' },
    { num: '8', label: 'ERRANT CLASSES', note: '· R:* / M:*' },
    { num: '94.3%', label: 'CRITIC CATCH', note: '· INDUCED FLAWS' },
    { num: 'TEMP 0.00', label: '· SEED 42', note: '· REPRODUCIBLE' },
    { num: '1.62s', label: 'P95', note: '· PER PARAGRAPH' },
    { num: 'MIT', label: 'OPEN SOURCE', note: '· pip install -e .' },
  ];

  return (
    <div className="ticker">
      <div className="tk-track" id="tickTrack">
        <div className="tk-g">
          {items.concat(items).map((it, idx) => (
            <span className="tk" key={idx}>
              <b>{it.num}</b> {it.label} <i>{it.note}</i>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
