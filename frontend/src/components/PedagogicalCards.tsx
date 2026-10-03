/**
 * @file PedagogicalCards.tsx
 * @description Pedagogical diagnostic cards with counterfactual pairs and individual accept/reject toggles
 * @module frontend/src/components
 */

import React from 'react';
import type { DiagnosticEdit, ErrantType } from '../types';
import { ShieldCheck, Sparkles } from 'lucide-react';

interface PedagogicalCardsProps {
  edits: DiagnosticEdit[];
  acceptedIndices: Set<number>;
  onToggleEdit: (index: number, accepted: boolean) => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
}

const CATEGORY_CLASS_MAP: Record<ErrantType, string> = {
  'R:SPELL': 'badge-spell',
  'R:VERB:SVA': 'badge-sva',
  'R:VERB:TENSE': 'badge-tense',
  'R:NOUN:NUM': 'badge-noun',
  'R:PREP': 'badge-prep',
  'M:DET': 'badge-det',
  'R:WO': 'badge-wo',
  'R:OTHER': 'badge-other',
};

export const PedagogicalCards: React.FC<PedagogicalCardsProps> = ({
  edits,
  acceptedIndices,
  onToggleEdit,
  onSelectAll,
  onDeselectAll,
}) => {
  if (!edits || edits.length === 0) {
    return (
      <div className="empty-state-view">
        <p>No pedagogical diagnostic issues to display.</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#94A3B8' }}>
          {edits.length} Diagnostic Issue{edits.length > 1 ? 's' : ''}
        </div>
        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
          <button className="btn-link-action" onClick={onSelectAll}>
            Select All
          </button>
          <span style={{ color: '#475569' }}>•</span>
          <button className="btn-link-action" onClick={onDeselectAll}>
            Deselect All
          </button>
        </div>
      </div>

      <div className="cards-scroll-container">
        {edits.map((edit, idx) => {
          const isAccepted = acceptedIndices.has(idx);
          const badgeCls = CATEGORY_CLASS_MAP[edit.errant_type] || 'badge-other';

          return (
            <div key={idx} className="pedagogical-card">
              <div className="pedagogical-card-top">
                <div className="rule-group-header">
                  <span className={`errant-pill ${badgeCls}`}>{edit.errant_type}</span>
                  <span className="rule-title-text">{edit.linguistic_rule}</span>
                  {edit.critic_verified && (
                    <span className="critic-verified-pill">
                      <ShieldCheck size={13} />
                      Critic Verified
                    </span>
                  )}
                </div>

                <label className="switch-control" title={isAccepted ? 'Accepted' : 'Rejected'}>
                  <input
                    type="checkbox"
                    checked={isAccepted}
                    onChange={(e) => onToggleEdit(idx, e.target.checked)}
                  />
                  <span className="switch-track"></span>
                </label>
              </div>

              <div className="edit-mutation-row">
                <span className="orig-strikethrough">{edit.span.original_text}</span>
                <span className="mutation-arrow">➔</span>
                <span className="rep-highlight">{edit.replacement || '[DELETED]'}</span>
              </div>

              <p className="explanation-paragraph">{edit.explanation}</p>

              <div className="counterfactual-container">
                <span className="counterfactual-title" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Sparkles size={14} />
                  Minimal Counterfactual Pair:
                </span>
                <span className="counterfactual-quote">"{edit.counterfactual_example}"</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
