/**
 * @file SurgicalSpansViewer.tsx
 * @description Interactive visualizer highlighting surgical error spans with ERRANT badges
 * @module frontend/src/components
 */

import React from 'react';
import type { DiagnosticEdit, ErrantType } from '../types';
import { CheckCircle2 } from 'lucide-react';

interface SurgicalSpansViewerProps {
  originalText: string;
  edits: DiagnosticEdit[];
  onSelectEdit?: (edit: DiagnosticEdit) => void;
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

export const SurgicalSpansViewer: React.FC<SurgicalSpansViewerProps> = ({
  originalText,
  edits,
}) => {
  if (!edits || edits.length === 0) {
    return (
      <div className="empty-state-view">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
          <CheckCircle2 size={32} color="#34D399" />
          <p style={{ fontSize: '1.05rem', fontWeight: 600, color: '#F8FAFC' }}>
            No grammatical errors detected!
          </p>
          <span style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
            The input sentence conforms to standard Universal Dependency morphosyntax.
          </span>
        </div>
      </div>
    );
  }

  // Segment original text into non-error and error chunks
  const sortedEdits = [...edits].sort((a, b) => a.span.start_char - b.span.start_char);
  const segments: React.ReactNode[] = [];
  let lastIdx = 0;

  sortedEdits.forEach((edit, idx) => {
    const start = edit.span.start_char;
    const end = edit.span.end_char;
    const badgeCls = CATEGORY_CLASS_MAP[edit.errant_type] || 'badge-other';

    // Plain text before error span
    if (start > lastIdx) {
      segments.push(
        <span key={`plain-${idx}`}>{originalText.slice(lastIdx, start)}</span>
      );
    }

    // Highlighted interactive span
    segments.push(
      <span
        key={`span-${idx}`}
        className={`interactive-span ${badgeCls}`}
        title={`${edit.errant_type}: ${edit.explanation}`}
      >
        {edit.span.original_text} ➔ <strong>{edit.replacement || '[DELETE]'}</strong>
      </span>
    );

    lastIdx = end;
  });

  // Trailing plain text
  if (lastIdx < originalText.length) {
    segments.push(
      <span key="plain-tail">{originalText.slice(lastIdx)}</span>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1rem' }}>
        <span className="errant-pill badge-sva">R:VERB:SVA</span>
        <span className="errant-pill badge-spell">R:SPELL</span>
        <span className="errant-pill badge-tense">R:VERB:TENSE</span>
        <span className="errant-pill badge-noun">R:NOUN:NUM</span>
        <span className="errant-pill badge-prep">R:PREP</span>
        <span className="errant-pill badge-det">M:DET</span>
      </div>

      <div className="spans-display-box">{segments}</div>
    </div>
  );
};
