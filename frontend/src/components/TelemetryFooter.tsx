/**
 * @file TelemetryFooter.tsx
 * @description Bottom footer displaying real-time execution telemetry and verification metrics
 * @module frontend/src/components
 */

import React from 'react';
import type { PipelineTelemetry } from '../types';
import { Clock, RefreshCw, Cpu } from 'lucide-react';

interface TelemetryFooterProps {
  telemetry?: PipelineTelemetry;
}

export const TelemetryFooter: React.FC<TelemetryFooterProps> = ({
  telemetry,
}) => {
  return (
    <footer className="app-footer">
      <div className="telemetry-items">
        <div className="telemetry-stat">
          <Clock size={14} color="#64748B" />
          <span className="tel-label">Latency:</span>
          <span className="stat-val">{telemetry ? `${telemetry.latency_ms.toFixed(1)} ms` : '0.0 ms'}</span>
        </div>

        <div className="telemetry-stat">
          <RefreshCw size={14} color="#64748B" />
          <span className="tel-label">Refinements:</span>
          <span className="stat-val">{telemetry ? telemetry.refinement_cycles : 0}</span>
        </div>

        <div className="telemetry-stat">
          <Cpu size={14} color="#64748B" />
          <span className="tel-label">Critic Status:</span>
          {telemetry?.critic_passed ? (
            <span className="badge-passed">PASSED</span>
          ) : (
            <span className="badge-passed" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#F87171' }}>
              FLAGGED
            </span>
          )}
        </div>
      </div>

      <div style={{ color: '#64748B', fontSize: '0.8rem' }}>
        Orto Neurosymbolic Pipeline • Minimal Reverse-Offset String Patcher
      </div>
    </footer>
  );
};
