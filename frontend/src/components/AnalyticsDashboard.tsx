import React from 'react';

interface Props {
  results: any;
  jobId: string | null;
}

const AnalyticsDashboard: React.FC<Props> = ({ results, jobId }) => {
  return (
    <div style={{ color: '#fff', padding: '20px' }}>
      <h1>Analytics Dashboard</h1>
      <div style={{ background: '#0a1929', padding: '20px', borderRadius: '8px', marginTop: '20px' }}>
        <h2>Analysis Results</h2>
        <p>Total Reviews: {results.total_reviews}</p>
        <p>Job ID: {jobId}</p>
        {results.filename && (
          <a 
            href={`http://localhost:8000/api/download/${results.filename}`}
            download
            style={{ color: '#4ade80', textDecoration: 'underline' }}
          >
            📥 Download Excel Report
          </a>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;