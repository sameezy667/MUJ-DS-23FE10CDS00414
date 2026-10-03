/**
 * @file App.tsx
 * @description Root application controller assembling the editorial neurosymbolic GEC showcase and interactive studio
 * @module frontend/src
 */

import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { HeroSection } from './components/HeroSection';
import { Ticker } from './components/Ticker';
import { ProblemSection } from './components/ProblemSection';
import { ArchitectureSection } from './components/ArchitectureSection';
import { LiveConsole } from './components/LiveConsole';
import { BenchmarksSection } from './components/BenchmarksSection';
import { TaxonomySection } from './components/TaxonomySection';
import { StylometrySection } from './components/StylometrySection';
import { ApiSection } from './components/ApiSection';
import { PersonasSection } from './components/PersonasSection';
import { Footer } from './components/Footer';
import { Toast } from './components/Toast';

export const App: React.FC = () => {
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 2400);
  };

  const handleRunDemo = () => {
    const demoEl = document.getElementById('demo');
    if (demoEl) {
      demoEl.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Reset scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Setup reveal IntersectionObserver for animated components
  useEffect(() => {
    const rvElements = document.querySelectorAll('[data-rv]');
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('in');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );

    rvElements.forEach((el) => observer.observe(el));

    // Dynamic spot-light mouse move handling
    const isFinePointer = window.matchMedia('(pointer: fine)').matches;
    const handleMouseMove = (e: MouseEvent) => {
      if (!isFinePointer) return;
      const target = (e.target as HTMLElement).closest('.spot') as HTMLElement;
      if (target) {
        const rect = target.getBoundingClientRect();
        target.style.setProperty('--mx', `${e.clientX - rect.left}px`);
        target.style.setProperty('--my', `${e.clientY - rect.top}px`);
      }
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });

    return () => {
      observer.disconnect();
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div className="app-container">
      <Navbar onRunDemoClick={handleRunDemo} />
      <HeroSection onRunDemoClick={handleRunDemo} />
      <Ticker />
      <ProblemSection />
      <ArchitectureSection />
      <LiveConsole onShowToast={showToast} />
      <BenchmarksSection />
      <TaxonomySection />
      <StylometrySection />
      <ApiSection onShowToast={showToast} />
      <PersonasSection />
      <Footer />
      <Toast message={toastMessage} />
    </div>
  );
};

export default App;
