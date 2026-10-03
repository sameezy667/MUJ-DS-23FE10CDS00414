/**
 * @file PatchedOutputViewer.tsx
 * @description Real-time dynamically patched output viewer with copy actions
 * @module frontend/src/components
 */

import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface PatchedOutputViewerProps {
  patchedText: string;
  appliedCount: number;
  totalCount: number;
}

export const PatchedOutputViewer: React.FC<PatchedOutputViewerProps> = ({
  patchedText,
  appliedCount,
  totalCount,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!patchedText) return;
    await navigator.clipboard.writeText(patchedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.82rem', color: '#34D399', fontWeight: 600 }}>
          {appliedCount === totalCount
            ? `All ${totalCount} verified edits applied`
            : `${appliedCount} of ${totalCount} edits applied`}
        </span>

        <button className="btn-secondary btn-sm" onClick={handleCopy}>
          {copied ? (
            <>
              <Check size={14} color="#34D399" />
              <span style={{ color: '#34D399' }}>Copied!</span>
            </>
          ) : (
            <>
              <Copy size={14} />
              <span>Copy Text</span>
            </>
          )}
        </button>
      </div>

      <div className="patched-box">
        {patchedText || (
          <span style={{ color: '#64748B', fontStyle: 'italic' }}>
            No output generated yet. Run analysis above.
          </span>
        )}
      </div>
    </div>
  );
};
