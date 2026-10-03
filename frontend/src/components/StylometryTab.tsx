/**
 * @file StylometryTab.tsx
 * @description Stylometry, sentence burstiness, and AI-marker detection visualizer component
 * @module frontend/src/components
 */

import React, { useState } from 'react';
import type { StyleAnalysisResult } from '../types';
import { AlertTriangle, CheckCircle, Copy, Check, Sparkles, Sliders } from 'lucide-react';

interface StylometryTabProps {
  stylometry?: StyleAnalysisResult;
  originalText: string;
}

export const StylometryTab: React.FC<StylometryTabProps> = ({
  stylometry,
  originalText,
}) => {
  const [copied, setCopied] = useState(false);

  if (!stylometry) {
    return (
      <div className="empty-state-view">
        <p>No stylometric analysis available. Run analysis above.</p>
      </div>
    );
  }

  const { report, suggestions = [] } = stylometry;

  // Compute naturalized text by substituting detected clichés
  let naturalizedText = originalText;
  const sortedSuggestions = [...suggestions].sort(
    (a, b) => b.span.start_char - a.span.start_char
  );
  for (const s of sortedSuggestions) {
    const { start_char, end_char } = s.span;
    if (start_char >= 0 && end_char <= naturalizedText.length) {
      naturalizedText =
        naturalizedText.slice(0, start_char) +
        s.suggestion +
        naturalizedText.slice(end_char);
    }
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(naturalizedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getGradeBadge = (grade: string) => {
    switch (grade) {
      case 'Natural':
        return { color: '#34D399', bg: 'rgba(16, 185, 129, 0.15)', icon: <CheckCircle size={15} /> };
      case 'Monotonous':
        return { color: '#FBBF24', bg: 'rgba(245, 158, 11, 0.15)', icon: <Sliders size={15} /> };
      default:
        return { color: '#F87171', bg: 'rgba(239, 68, 68, 0.15)', icon: <AlertTriangle size={15} /> };
    }
  };

  const gradeInfo = getGradeBadge(report.naturalness_grade);

  return (
    <div>
      {/* Metric Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', padding: '0.85rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>
            Burstiness (B)
          </div>
          <div style={{ fontSize: '1.35rem', fontWeight: 800, color: report.burstiness_score >= 0.35 ? '#34D399' : '#FBBF24', fontFamily: 'JetBrains Mono' }}>
            {report.burstiness_score.toFixed(2)}
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748B' }}>
            {report.burstiness_score >= 0.35 ? 'Natural Cadence' : 'Uniform / Monotonous'}
          </div>
        </div>

        <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', padding: '0.85rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>
            Naturalness
          </div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.2rem', padding: '0.2rem 0.6rem', borderRadius: '9999px', background: gradeInfo.bg, color: gradeInfo.color, fontWeight: 700, fontSize: '0.85rem' }}>
            {gradeInfo.icon}
            {report.naturalness_grade}
          </div>
        </div>

        <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', padding: '0.85rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>
            AI Markers
          </div>
          <div style={{ fontSize: '1.35rem', fontWeight: 800, color: report.cliche_count > 0 ? '#EF4444' : '#34D399', fontFamily: 'JetBrains Mono' }}>
            {report.cliche_count}
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748B' }}>
            {report.cliche_count > 0 ? 'Cliché Tropes' : 'Zero Clichés'}
          </div>
        </div>

        <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', padding: '0.85rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 600 }}>
            Passive Voice
          </div>
          <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#38BDF8', fontFamily: 'JetBrains Mono' }}>
            {(report.passive_ratio * 100).toFixed(0)}%
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748B' }}>
            Verb Density
          </div>
        </div>
      </div>

      {/* Summary Banner */}
      <div style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.3)', borderRadius: '8px', padding: '0.75rem 1rem', marginBottom: '1.25rem', fontSize: '0.9rem', color: '#CBD5E1' }}>
        <strong style={{ color: '#818CF8' }}>Diagnosis: </strong>
        {report.summary}
      </div>

      {/* Two Column Section: Clichés & Naturalized Preview */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        <div>
          <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <AlertTriangle size={15} color="#EF4444" />
            Detected AI Markers ({suggestions.length})
          </h4>
          <div style={{ maxHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {suggestions.length > 0 ? (
              suggestions.map((s, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    borderLeft: '3px solid #EF4444',
                    borderRadius: '6px',
                    padding: '0.5rem 0.75rem',
                    fontSize: '0.85rem',
                  }}
                >
                  <span style={{ color: '#EF4444', textDecoration: 'line-through', fontWeight: 600 }}>
                    {s.original}
                  </span>
                  &nbsp;➔&nbsp;
                  <span style={{ color: '#10B981', fontWeight: 700 }}>{s.suggestion}</span>
                  <div style={{ color: '#94A3B8', fontSize: '0.75rem', marginTop: '0.2rem' }}>
                    {s.reason}
                  </div>
                </div>
              ))
            ) : (
              <div style={{ color: '#34D399', fontSize: '0.85rem', padding: '0.5rem 0' }}>
                ✓ No synthetic cliché markers detected.
              </div>
            )}
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
            <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Sparkles size={15} color="#818CF8" />
              De-Clichéd Naturalized Text
            </h4>
            <button className="btn-secondary btn-sm" onClick={handleCopy}>
              {copied ? (
                <>
                  <Check size={13} color="#34D399" />
                  <span style={{ color: '#34D399' }}>Copied</span>
                </>
              ) : (
                <>
                  <Copy size={13} />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
          <div
            style={{
              background: 'rgba(11, 15, 25, 0.8)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '8px',
              padding: '0.85rem',
              fontSize: '0.95rem',
              lineHeight: 1.6,
              color: '#F8FAFC',
              minHeight: '140px',
            }}
          >
            {naturalizedText}
          </div>
        </div>
      </div>
    </div>
  );
};
