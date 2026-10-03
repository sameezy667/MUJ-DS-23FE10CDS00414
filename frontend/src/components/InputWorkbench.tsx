/**
 * @file InputWorkbench.tsx
 * @description Input workbench panel with character counts, presets, and diagnostic triggers
 * @module frontend/src/components
 */

import React from 'react';
import { Edit3, Trash2, Zap, Loader2 } from 'lucide-react';

export interface PresetItem {
  id: string;
  label: string;
  text: string;
}

export const PRESET_OPTIONS: PresetItem[] = [
  {
    id: 'sva_prep',
    label: 'SVA Across Preposition',
    text: 'The box of old vintage vinyl records were dropped by the movers.',
  },
  {
    id: 'spelling',
    label: 'Spelling & Doubling',
    text: 'She will definately recieve the package untill Friday.',
  },
  {
    id: 'article_sva',
    label: 'Article & Agreement',
    text: 'A increase in temperature affect on the final chemical reaction.',
  },
  {
    id: 'mass_noun',
    label: 'Uncountable Noun',
    text: 'The goverment provides many informations to the public.',
  },
  {
    id: 'homophone',
    label: 'Homophone (Their/There)',
    text: 'Their is no doubt that the committee will approve the budget.',
  },
  {
    id: 'cliche_synthetic',
    label: 'AI Cliché & Monotony',
    text: 'Moreover, let us delve into the rich tapestry of modern innovations. It is crucial to foster a beacon of collaboration that underscores our vital role.',
  },
];

interface InputWorkbenchProps {
  inputText: string;
  onChangeText: (val: string) => void;
  onAnalyze: () => void;
  onClear: () => void;
  isLoading: boolean;
  activePreset: string;
  onSelectPreset: (preset: PresetItem) => void;
}

export const InputWorkbench: React.FC<InputWorkbenchProps> = ({
  inputText,
  onChangeText,
  onAnalyze,
  onClear,
  isLoading,
  activePreset,
  onSelectPreset,
}) => {
  const charCount = inputText.length;
  const wordCount = inputText.trim() ? inputText.trim().split(/\s+/).length : 0;

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      onAnalyze();
    }
  };

  return (
    <section className="studio-card">
      <div className="studio-card-header">
        <div className="card-title-group">
          <Edit3 size={18} color="#6366F1" />
          <h2>Raw Input Text</h2>
        </div>
        <div className="card-meta-counts">
          <span>{charCount} chars</span>
          <span className="meta-sep">•</span>
          <span>{wordCount} words</span>
        </div>
      </div>

      <div className="presets-bar">
        <span className="presets-tag">Presets:</span>
        {PRESET_OPTIONS.map((p) => (
          <button
            key={p.id}
            className={`preset-btn ${activePreset === p.id ? 'active' : ''}`}
            onClick={() => onSelectPreset(p)}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="editor-wrapper">
        <textarea
          className="orto-textarea"
          value={inputText}
          onChange={(e) => onChangeText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter text to analyze and diagnose with Orto..."
          rows={7}
        />
      </div>

      <div className="action-controls">
        <button className="btn-secondary" onClick={onClear} disabled={isLoading}>
          <Trash2 size={15} />
          Clear
        </button>
        <button
          className="btn-primary"
          onClick={onAnalyze}
          disabled={isLoading || !inputText.trim()}
        >
          {isLoading ? (
            <>
              <Loader2 size={16} className="spinner-icon" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Zap size={16} />
              <span>Diagnose &amp; Correct</span>
              <span className="shortcut-key">Ctrl + Enter</span>
            </>
          )}
        </button>
      </div>
    </section>
  );
};
