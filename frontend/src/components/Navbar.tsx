/**
 * @file Navbar.tsx
 * @description Fixed sticky navigation bar with active section scrollspy and scroll progress bar
 * @module frontend/src/components
 */

import React, { useEffect, useState } from 'react';
import { GitBranch, Play } from 'lucide-react';

interface NavbarProps {
  onRunDemoClick?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onRunDemoClick }) => {
  const [isScrolled, setIsScrolled] = useState<boolean>(false);
  const [scrollProgress, setScrollProgress] = useState<number>(0);
  const [activeSection, setActiveSection] = useState<string>('');

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      setIsScrolled(scrollY > 10);

      const h = document.documentElement;
      const total = h.scrollHeight - h.clientHeight;
      setScrollProgress(total > 0 ? scrollY / total : 0);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const sections = ['problem', 'engine', 'demo', 'bench', 'tax', 'stylometry', 'api', 'personas'];
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { rootMargin: '-40% 0px -50% 0px' }
    );

    sections.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <>
      <div id="progress" style={{ transform: `scaleX(${scrollProgress})` }} />
      <nav id="nav" className={isScrolled ? 'scrolled' : ''}>
        <div className="wrap">
          <a className="brand" href="#hero">
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
            ORTO
          </a>

          <div className="navlinks">
            <a href="#problem" className={activeSection === 'problem' ? 'act' : ''}>
              PROBLEM
            </a>
            <a href="#engine" className={activeSection === 'engine' ? 'act' : ''}>
              ENGINE
            </a>
            <a href="#demo" className={activeSection === 'demo' ? 'act' : ''}>
              DEMO
            </a>
            <a href="#bench" className={activeSection === 'bench' ? 'act' : ''}>
              BENCH
            </a>
            <a href="#tax" className={activeSection === 'tax' ? 'act' : ''}>
              TAXONOMY
            </a>
            <a href="#stylometry" className={activeSection === 'stylometry' ? 'act' : ''}>
              STYLOMETRY
            </a>
            <a href="#api" className={activeSection === 'api' ? 'act' : ''}>
              API
            </a>
          </div>

          <div className="navcta">
            <a className="btn btn-ghost" href="#api">
              <GitBranch size={14} />
              Repository
            </a>
            <a
              className="btn btn-primary"
              href="#demo"
              id="navRun"
              onClick={() => onRunDemoClick?.()}
            >
              <Play size={14} fill="currentColor" />
              Run demo
            </a>
          </div>
        </div>
      </nav>
    </>
  );
};
