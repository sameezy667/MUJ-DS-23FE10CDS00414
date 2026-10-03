/**
 * @file HeroSection.tsx
 * @description Hero section featuring animated manuscript annotation loop and interactive performance metrics
 * @module frontend/src/components
 */

import React, { useEffect, useRef, useState } from 'react';
import { Play, Network, ShieldCheck, Terminal } from 'lucide-react';

interface HeroSectionProps {
  onRunDemoClick?: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onRunDemoClick }) => {
  const [bgOffset, setBgOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [stage, setStage] = useState<number>(-1);
  const [errText, setErrText] = useState<string>('were');
  const [isFixed, setIsFixed] = useState<boolean>(false);
  const [isScanned, setIsScanned] = useState<boolean>(false);
  const [isMarked, setIsMarked] = useState<boolean>(false);
  const [isDone, setIsDone] = useState<boolean>(false);
  const [isFlash, setIsFlash] = useState<boolean>(false);
  const [isFade, setIsFade] = useState<boolean>(false);
  const [showSeal, setShowSeal] = useState<boolean>(false);
  const [showDiff, setShowDiff] = useState<boolean>(false);
  const [assertText, setAssertText] = useState<string>('');
  const [showAssert, setShowAssert] = useState<boolean>(false);

  const [countF05, setCountF05] = useState<number>(0);
  const [countDrift, setCountDrift] = useState<number>(0);
  const [countAlign, setCountAlign] = useState<number>(0);
  const [countLat, setCountLat] = useState<number>(0);

  const manuscriptRef = useRef<HTMLDivElement>(null);
  const errRef = useRef<HTMLSpanElement>(null);
  const fixRef = useRef<HTMLSpanElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Parallax on mouse move
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 22;
      const y = (e.clientY / window.innerHeight - 0.5) * 16;
      setBgOffset({ x, y });
    };
    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Animate Count-up Stats
  useEffect(() => {
    const timer = setTimeout(() => {
      const duration = 1300;
      const t0 = performance.now();
      const step = (now: number) => {
        const p = Math.min(1, (now - t0) / duration);
        const ease = 1 - Math.pow(1 - p, 4);
        setCountF05(parseFloat((69.6 * ease).toFixed(1)));
        setCountDrift(parseFloat((2.1 * ease).toFixed(1)));
        setCountAlign(Math.round(100 * ease));
        setCountLat(parseFloat((1.62 * ease).toFixed(2)));
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, 800);
    return () => clearTimeout(timer);
  }, []);

  // Position Red Pen Annotation Over the Target Word
  const updateAnnotation = () => {
    if (!manuscriptRef.current || !errRef.current || !fixRef.current || !svgRef.current) return;
    const mr = manuscriptRef.current.getBoundingClientRect();
    const er = errRef.current.getBoundingClientRect();
    const cx = er.left - mr.left + er.width / 2;
    const cy = er.top - mr.top + er.height / 2;
    const rx = er.width / 2 + 6;
    const ry = er.height / 2 + 3;

    fixRef.current.style.left = `${Math.round(cx - fixRef.current.offsetWidth / 2)}px`;
    fixRef.current.style.top = `${Math.round(er.top - mr.top - er.height - 6)}px`;

    svgRef.current.setAttribute('width', `${Math.max(manuscriptRef.current.clientWidth, cx + rx + 20)}`);
    svgRef.current.setAttribute('height', `${manuscriptRef.current.clientHeight}`);
    svgRef.current.innerHTML = `
      <ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="none" stroke="#d92c35" stroke-width="2.2" pathLength="1" class="anno-e" transform="rotate(-2 ${cx} ${cy})" style="--ad:0s"/>
      <path d="M ${cx - rx + 3} ${cy + 3} Q ${cx} ${cy + 7}, ${cx + rx - 3} ${cy + 3}" fill="none" stroke="#d92c35" stroke-width="2.6" stroke-linecap="round" pathLength="1" class="anno-e" style="--ad:.5s"/>
      <path d="M ${cx - 9} ${cy - ry - 9} L ${cx} ${cy - ry + 3} L ${cx + 9} ${cy - ry - 9}" fill="none" stroke="#d92c35" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" pathLength="1" class="anno-e" style="--ad:.8s"/>
    `;
  };

  // Automated Hero Simulation Loop
  useEffect(() => {
    let isCancelled = false;
    let typeTimer: any = null;

    const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

    const typeAssert = async (fullStr: string) => {
      setShowAssert(true);
      for (let i = 1; i <= fullStr.length; i++) {
        if (isCancelled) return;
        setAssertText(fullStr.slice(0, i));
        await wait(14);
      }
    };

    const runLoop = async () => {
      while (!isCancelled) {
        setStage(-1);
        setErrText('were');
        setIsFixed(false);
        setIsScanned(false);
        setIsMarked(false);
        setIsDone(false);
        setShowSeal(false);
        setShowDiff(false);
        setShowAssert(false);
        setAssertText('');
        setIsFlash(false);
        setIsFade(false);

        await wait(600);
        if (isCancelled) break;
        setStage(0);
        setIsScanned(true);

        await wait(1150);
        if (isCancelled) break;
        setStage(1);
        updateAnnotation();
        setIsMarked(true);

        await wait(1700);
        if (isCancelled) break;
        setStage(2);
        await typeAssert('critic · Number(box)=Sing ≡ Number(was)=Sing — verified');

        await wait(1700);
        if (isCancelled) break;
        setIsDone(true);
        setErrText('was');
        setIsFixed(true);
        setIsFlash(true);
        setTimeout(() => setIsFlash(false), 800);

        await wait(900);
        if (isCancelled) break;
        setStage(3);
        setShowSeal(true);
        setShowDiff(true);

        await wait(3100);
        if (isCancelled) break;
        setIsFade(true);
        await wait(500);
        setIsFade(false);
      }
    };

    runLoop();

    return () => {
      isCancelled = true;
      if (typeTimer) clearInterval(typeTimer);
    };
  }, []);

  return (
    <section id="hero">
      <div
        className="bg-arcs"
        id="bgArcs"
        style={{
          marginLeft: `${bgOffset.x}px`,
          marginTop: `${bgOffset.y}px`,
        }}
      >
        <svg viewBox="0 0 1200 640" preserveAspectRatio="xMidYMid slice">
          <g fill="none" stroke="rgba(25,24,19,.06)" strokeWidth="1.1">
            <path d="M40 470 Q 300 90 620 430" />
            <path d="M240 520 Q 520 170 900 420" />
            <path d="M-40 300 Q 360 40 780 300" />
            <path d="M420 560 Q 700 260 1080 480" />
            <path d="M120 200 Q 500 -40 940 240" />
          </g>
          <g fill="none" stroke="rgba(217,44,53,.12)" strokeWidth="1.4">
            <path d="M160 500 Q 480 130 840 460" />
            <path d="M640 540 Q 860 300 1160 400" />
          </g>
          <g fill="rgba(217,44,53,.35)">
            <circle cx="40" cy="470" r="2.5" />
            <circle cx="620" cy="430" r="2.5" />
            <circle cx="940" cy="240" r="2.5" />
          </g>
          <g fill="rgba(25,24,19,.15)">
            <circle cx="300" cy="90" r="2" />
            <circle cx="700" cy="260" r="2" />
            <circle cx="860" cy="300" r="2" />
          </g>
        </svg>
      </div>

      <div className="wrap hero-grid">
        <div>
          <div className="eyebrow">
            Neurosymbolic GEC Engine <em>// open-source release</em>
          </div>
          <h1 className="hero-h">
            <span className="hw" style={{ '--d': '0.05s' } as React.CSSProperties}>
              <span>Grammar</span>
            </span>{' '}
            <span className="hw" style={{ '--d': '0.11s' } as React.CSSProperties}>
              <span>correction,</span>
            </span>
            <br />
            <span className="hw" style={{ '--d': '0.18s' } as React.CSSProperties}>
              <span>down</span>
            </span>{' '}
            <span className="hw" style={{ '--d': '0.24s' } as React.CSSProperties}>
              <span>to</span>
            </span>{' '}
            <span className="hw" style={{ '--d': '0.30s' } as React.CSSProperties}>
              <span>the</span>
            </span>{' '}
            <span className="word-anno">
              <span className="hw" style={{ '--d': '0.38s' } as React.CSSProperties}>
                <span>
                  <span className="serif">character.</span>
                </span>
              </span>
              <svg className="squig" viewBox="0 0 180 14" preserveAspectRatio="none">
                <path d="M2 10 C 30 4, 55 12, 82 8 S 132 3, 178 8" />
              </svg>
            </span>
          </h1>

          <p className="hero-lede">
            Orto fuses <b>Universal Dependency parsing</b>, <b>constrained LLM decoding</b>, and a{' '}
            <b>symbolic critic</b> — minimal edits confined to the error span, exact character
            offsets, cited rules, counterfactual feedback, and zero parser regressions.
          </p>

          <div className="hero-ctas">
            <a
              className="btn btn-primary"
              href="#demo"
              id="heroRun"
              onClick={() => onRunDemoClick?.()}
            >
              <Play size={16} fill="currentColor" />
              Run the live demo
            </a>
            <a className="btn btn-ghost" href="#engine">
              <Network size={16} />
              Read the architecture
            </a>
          </div>

          <div className="spec-strip">
            <div className="spec">
              <b>{countF05}</b>
              <span>F₀.₅ · BEA-2019</span>
            </div>
            <div className="spec">
              <b>{countDrift}%</b>
              <span>Stylistic drift</span>
            </div>
            <div className="spec">
              <b>{countAlign}%</b>
              <span>Span alignment</span>
            </div>
            <div className="spec">
              <b>{countLat}s</b>
              <span>Latency p95</span>
            </div>
          </div>
        </div>

        <div style={{ position: 'relative' }}>
          <div
            id="heroPanel"
            className={`an ${isFlash ? 'flash' : ''} ${isFade ? 'fade' : ''}`}
          >
            <i className="ct ct-tl" />
            <i className="ct ct-tr" />
            <i className="ct ct-bl" />
            <i className="ct ct-br" />

            <div className="float-chip fc1">
              <b>642ms</b> · latency · p95 1.62s
            </div>
            <div className="float-chip fc2">
              <b>0</b> parser regressions · critic <b>94.3%</b>
            </div>

            <div className="hd-head">
              <Terminal size={14} style={{ stroke: 'var(--dim)' }} />
              orto / pipeline.preview
              <span className="live">LIVE</span>
            </div>

            <div id="hdStages">
              <div
                className={`hstage ${stage === 0 ? 'on' : stage > 0 ? 'done' : ''}`}
                style={{ '--sc': '#1a6f8a' } as React.CSSProperties}
              >
                01 Feature Engine
              </div>
              <div
                className={`hstage ${stage === 1 ? 'on' : stage > 1 ? 'done' : ''}`}
                style={{ '--sc': '#6a4fa3' } as React.CSSProperties}
              >
                02 LLM Diagnostics
              </div>
              <div
                className={`hstage ${stage === 2 ? 'on' : stage > 2 ? 'done' : ''}`}
                style={{ '--sc': '#177a4e' } as React.CSSProperties}
              >
                03 Symbolic Critic
              </div>
              <div
                className={`hstage ${stage === 3 ? 'on' : stage > 3 ? 'done' : ''}`}
                style={{ '--sc': '#191813' } as React.CSSProperties}
              >
                04 Verified Payload
              </div>
            </div>

            <div
              id="manuscript"
              ref={manuscriptRef}
              className={`${isScanned ? 'scan' : ''} ${isMarked ? 'marked' : ''} ${
                isDone ? 'done' : ''
              }`}
            >
              <p className="ms-text">
                The box of old vintage vinyl records{' '}
                <span className={`ms-err ${isFixed ? 'fixed' : ''}`} id="msErr" ref={errRef}>
                  {errText}
                </span>{' '}
                dropped by the movers.
              </p>
              <svg id="msAnno" ref={svgRef} />
              <span id="msFix" ref={fixRef}>
                was
              </span>
              <span id="msNote">
                box is singular — the verb agrees with the head, not the modifier
              </span>
            </div>

            <div id="hdAssert" className={showAssert ? 'show' : ''}>
              {assertText}
            </div>

            <div className="hd-bottom">
              <span id="hdSeal" className={showSeal ? 'show' : ''}>
                <ShieldCheck size={14} />
                CRITIC VERIFIED
              </span>
              <span id="hdDiff" className={showDiff ? 'show' : ''}>
                <s>− were</s>&nbsp;&nbsp;<b>+ was</b>&nbsp;&nbsp;
                <span style={{ color: 'var(--dim)' }}>· span [37,41]</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="scroll-hint">SCROLL</div>
    </section>
  );
};
