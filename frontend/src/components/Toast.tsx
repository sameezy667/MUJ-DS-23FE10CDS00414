/**
 * @file Toast.tsx
 * @description Floating toast notification component for user feedback
 * @module frontend/src/components
 */

import React from 'react';

interface ToastProps {
  message: string | null;
}

export const Toast: React.FC<ToastProps> = ({ message }) => {
  return (
    <div id="toast" className={message ? 'show' : ''}>
      {message}
    </div>
  );
};
