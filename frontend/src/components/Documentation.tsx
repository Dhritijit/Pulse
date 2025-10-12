import React from 'react';
import './Documentation.css';

const Documentation: React.FC = () => {
  return (
    <div className="documentation">
      <h1>Documentation</h1>

      <section className="doc-section">
        <h2>Getting Started</h2>
        <ol>
          <li>Choose Web Scraping or File Upload</li>
          <li>Enter URLs (one per line) or upload CSV/Excel file</li>
          <li>Configure analysis settings in sidebar</li>
          <li>Click Start Analysis</li>
          <li>Monitor real-time progress</li>
          <li>Download Excel report when complete</li>
        </ol>
      </section>

      <section className="doc-section">
        <h2>Supported Review Sites</h2>
        <div className="site-grid">
          <div className="site-card">
            <h3>Trustpilot</h3>
            <code>trustpilot.com/review/company-name</code>
          </div>
          <div className="site-card">
            <h3>Glassdoor</h3>
            <code>glassdoor.com/Reviews/Company-E12345.htm</code>
          </div>
          <div className="site-card">
            <h3>Yelp</h3>
            <code>yelp.com/biz/business-name</code>
          </div>
          <div className="site-card">
            <h3>Google Reviews</h3>
            <code>google.com/maps (place URL)</code>
          </div>
        </div>
      </section>

      <section className="doc-section">
        <h2>File Upload Requirements</h2>
        <ul>
          <li><strong>Format:</strong> CSV, XLSX, or XLS</li>
          <li><strong>Required column:</strong> 'text' or 'review'</li>
          <li><strong>Optional columns:</strong> 'rating', 'date', 'reviewer'</li>
          <li><strong>Max size:</strong> 200MB</li>
        </ul>
      </section>

      <section className="doc-section">
        <h2>Analysis Features</h2>
        <div className="feature-list">
          <div className="feature">
            <h3>Sentiment Analysis</h3>
            <p>AI-powered classification: positive, negative, neutral with confidence scores</p>
          </div>
          <div className="feature">
            <h3>Topic Modeling</h3>
            <p>Automatic extraction of key themes using embeddings and clustering</p>
          </div>
          <div className="feature">
            <h3>Trend Analysis</h3>
            <p>Time-series sentiment and volume trends</p>
          </div>
          <div className="feature">
            <h3>AI Insights</h3>
            <p>Strategic recommendations based on analysis</p>
          </div>
        </div>
      </section>

      <section className="doc-section">
        <h2>Configuration Settings</h2>
        <ul>
          <li><strong>Max Reviews:</strong> Limit reviews per site (100-1000)</li>
          <li><strong>Batch Size:</strong> Reviews processed per API call (10-50)</li>
          <li><strong>Topics:</strong> Number of topics to extract (3-10)</li>
        </ul>
      </section>

      <section className="doc-section">
        <h2>Tips for Best Results</h2>
        <ul>
          <li>Use full URLs including https://</li>
          <li>For files, ensure text column has actual review content</li>
          <li>Analyze 100+ reviews for meaningful trends</li>
          <li>Check OpenAI API key is configured</li>
          <li>Review confidence scores to assess analysis quality</li>
        </ul>
      </section>

      <section className="doc-section">
        <h2>Output</h2>
        <p>Excel report includes:</p>
        <ul>
          <li>Raw data with all reviews</li>
          <li>Sentiment analysis with confidence scores</li>
          <li>Topic assignments and keywords</li>
          <li>Trend charts and statistics</li>
          <li>Executive summary with insights</li>
        </ul>
      </section>
    </div>
  );
};

export default Documentation;