import React from 'react';
import './SuccessMessage.css';

const SuccessMessage = ({ message, onClose }) => {
  if (!message) return null;

  return (
    <div className="success-message">
      <div className="success-content">
        <span className="success-icon">✓</span>
        <span className="success-text">{message}</span>
        {onClose && (
          <button className="success-close" onClick={onClose} aria-label="Close success message">
            ×
          </button>
        )}
      </div>
    </div>
  );
};

export default SuccessMessage;
