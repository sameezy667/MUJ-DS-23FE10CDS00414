/**
 * @file Header.tsx
 * @description Top navigation bar for Orto React Studio
 * @module frontend/src/components
 */

import React from 'react';
import { Layers, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  enableCritic: boolean;
  onToggleCritic: (val: boolean) => void;
  apiStatus: 'ready' | 'loading' | 'error';
}

export const Header: React.FC<HeaderProps> = ({
  enableCritic,
  onToggleCritic,
  apiStatus,
}) => {
  return (
    <header className="app-header">
      <div className="brand-container">
        <div className="brand-logo">
          <Layers size={24} strokeWidth={2.5} />
        </div>
        <div>
          <div className="brand-title">
            <span className="brand-gradient">Orto</span>
            <span className="version-pill">v0.1.0</span>
          </div>
          <div className="brand-subtitle">
            Neurosymbolic GEC &amp; Linguistic Diagnostic Studio
          </div>
        </div>
      </div>

      <div className="header-controls">
        <div className="status-badge">
          <span className="status-pulse"></span>
          <span>{apiStatus === 'loading' ? 'Processing...' : 'Engine Ready'}</span>
        </div>

        <div className="toggle-group">
          <label className="switch-control" title="Enforces Subject-Verb Agreement and tree connectivity checks">
            <input
              type="checkbox"
              checked={enableCritic}
              onChange={(e) => onToggleCritic(e.target.checked)}
            />
            <span className="switch-track"></span>
          </label>
          <span className="toggle-text" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <ShieldCheck size={16} color={enableCritic ? '#34D399' : '#94A3B8'} />
            Symbolic Critic
          </span>
        </div>
      </div>
    </header>
  );
};
