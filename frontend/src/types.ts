/**
 * @file types.ts
 * @description TypeScript interface definitions for Orto GEC Engine React Studio
 * @module frontend/src
 */

export type ErrantType =
  | 'R:SPELL'
  | 'R:VERB:SVA'
  | 'R:VERB:TENSE'
  | 'R:NOUN:NUM'
  | 'R:PREP'
  | 'M:DET'
  | 'R:WO'
  | 'R:OTHER';

export interface ErrantMeta {
  color: string;
  label: string;
  description: string;
  exampleBad: string;
  exampleGood: string;
}

export interface SpanCoordinate {
  start_char: number;
  end_char: number;
  original_text: string;
}

export interface DiagnosticEdit {
  id?: number;
  span: SpanCoordinate;
  replacement: string;
  errant_type: ErrantType;
  linguistic_rule: string;
  explanation: string;
  counterfactual_example: string;
  confidence: number;
  critic_verified: boolean;
  accepted?: boolean;
}

export interface PipelineTelemetry {
  latency_ms: number;
  input_tokens: number;
  refinement_cycles: number;
  critic_passed: boolean;
}

export interface SvaPair {
  subject: {
    text: string;
    pos: string;
    dep: string;
    number: string;
    start_char: number;
    end_char: number;
  };
  verb: {
    text: string;
    pos: string;
    tag?: string;
    number: string;
    tense: string;
    verb_form: string;
    start_char: number;
    end_char: number;
  };
}

export interface SyntaxPriors {
  sentence_length: number;
  key_dependencies: string[];
  subject_verb_pairs: SvaPair[];
  anomalies: string[];
}

export interface StylometricReport {
  burstiness_score: number;
  mean_sentence_length: number;
  std_sentence_length: number;
  cliche_count: number;
  detected_markers: string[];
  passive_ratio: number;
  nominalization_ratio: number;
  opening_variety_score: number;
  naturalness_grade: 'Natural' | 'Monotonous' | 'Heavily Synthetic';
  sentence_lengths: number[];
  summary: string;
}

export interface StyleRewriteSuggestion {
  span: SpanCoordinate;
  original: string;
  suggestion: string;
  reason: string;
}

export interface StyleAnalysisResult {
  report: StylometricReport;
  suggestions: StyleRewriteSuggestion[];
}

export interface AnalyzeResponse {
  original_text: string;
  corrected_text: string;
  edits: DiagnosticEdit[];
  syntax_priors?: SyntaxPriors;
  stylometry?: StyleAnalysisResult;
  telemetry: PipelineTelemetry;
}

export interface PipelineLog {
  id: string;
  timestampMs: number;
  tag: 'syn' | 'llm' | 'crit' | 'patch';
  message: string;
}

export interface PresetItem {
  id: string;
  label: string;
  text: string;
}

export interface DepToken {
  w: string;
  i: number;
  l: string;
  pos: string;
  head: number;
  label: string;
}
