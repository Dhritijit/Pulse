import React from 'react';

const Documentation: React.FC = () => {
  return (
    <div style={{ color: '#fff', padding: '20px' }}>
      <h1>📚 Documentation</h1>
      <div style={{ background: '#0a1929', padding: '20px', borderRadius: '8px', marginTop: '20px' }}>
        <h2>How to Use</h2>
        <ol style={{ lineHeight: '2' }}>
          <li>Choose <strong>Web Scraping</strong> or <strong>File Upload</strong></li>
          <li>Enter URLs or upload your CSV/Excel file</li>
          <li>Click <strong>Start Analysis</strong></li>
          <li>Monitor real-time progress</li>
          <li>View results in Analytics Dashboard</li>
        </ol>
        
        <h2 style={{ marginTop: '30px' }}>Supported Sites</h2>
        <ul style={{ lineHeight: '2' }}>
          <li>✅ Trustpilot</li>
          <li>✅ Glassdoor</li>
          <li>✅ Yelp</li>
          <li>✅ Google Reviews</li>
        </ul>
      </div>
    </div>
  );
};

export default Documentation;