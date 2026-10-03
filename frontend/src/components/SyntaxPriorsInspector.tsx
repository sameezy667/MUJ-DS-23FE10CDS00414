/**
 * @file SyntaxPriorsInspector.tsx
 * @description Inspector view for spaCy Universal Dependency graph edges and morphological priors
 * @module frontend/src/components
 */

import React from 'react';
import type { SyntaxPriors } from '../types';
import { GitFork, Network } from 'lucide-react';

interface SyntaxPriorsInspectorProps {
  syntaxPriors?: SyntaxPriors;
}

export const SyntaxPriorsInspector: React.FC<SyntaxPriorsInspectorProps> = ({
  syntaxPriors,
}) => {
  if (!syntaxPriors) {
    return (
      <div className="empty-state-view">
        <p>No syntactic dependency priors available.</p>
      </div>
    );
  }

  const { key_dependencies = [], subject_verb_pairs = [] } = syntaxPriors;

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <GitFork size={15} />
          Universal Dependency Edges
        </h3>
        <div style={{ maxHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          {key_dependencies.length > 0 ? (
            key_dependencies.map((dep, idx) => (
              <div key={idx} className="syntax-edge-card">
                {dep}
              </div>
            ))
          ) : (
            <div className="syntax-edge-card">No key dependencies found.</div>
          )}
        </div>
      </div>

      <div>
        <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Network size={15} />
          Subject-Verb Agreement Clauses
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          {subject_verb_pairs.length > 0 ? (
            subject_verb_pairs.map((pair, idx) => (
              <div
                key={idx}
                className="syntax-edge-card"
                style={{ borderLeft: '3px solid #EF4444' }}
              >
                <strong style={{ color: '#F87171' }}>Subject:</strong> {pair.subject.text} (Number: {pair.subject.number})
                &nbsp;➔&nbsp;
                <strong style={{ color: '#38BDF8' }}>Verb:</strong> {pair.verb.text} (Number: {pair.verb.number}, Form: {pair.verb.verb_form})
              </div>
            ))
          ) : (
            <div className="syntax-edge-card">No explicit SVA clauses detected.</div>
          )}
        </div>
      </div>
    </div>
  );
};
