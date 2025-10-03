import React, { useState } from 'react';
import './App.css';
import DataSelection from './components/DataSelection';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import Documentation from './components/Documentation';

type View = 'analysis' | 'dashboard' | 'documentation';

interface AnalysisResults {
  reviews: any[];
  sentiment_results: any[];
  topics: any;
  topic_assignments: any[];
  trends: any;
  insights: string;
  filename: string;
  total_reviews: number;
}

function App() {
  const [currentView, setCurrentView] = useState<View>('analysis');
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  
  // Settings state
  const [maxReviews, setMaxReviews] = useState<number>(500);
  const [batchSize, setBatchSize] = useState<number>(20);
  const [numTopics, setNumTopics] = useState<number>(5);
  const [apiKeyStatus, setApiKeyStatus] = useState<string>('Checking...');

  // Check API key status on mount
  React.useEffect(() => {
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => {
        setApiKeyStatus(data.openai_configured ? '✅ Configured' : '❌ Missing');
      })
      .catch(() => setApiKeyStatus('❌ Backend Offline'));
  }, []);

  const handleAnalysisComplete = (jobId: string, analysisResults: AnalysisResults) => {
    setJobId(jobId);
    setResults(analysisResults);
    setCurrentView('dashboard');
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="logo">
          <img src="/logo.png" alt="Pulse.ai" className="logo-image" />
          </div>

        <div className="sidebar-section">
          <h3 className="sidebar-title">⚙️ Configuration</h3>
          
          <div className="config-item">
            <label className="config-label">📋 Prerequisites</label>
            <div className="status-badge">
              OpenAI API: {apiKeyStatus}
            </div>
          </div>

          <div className="config-item">
            <label className="config-label">🎛️ Analysis Settings</label>
            <div className="slider-container">
              <label>Max reviews per site: {maxReviews}</label>
              <input 
                type="range" 
                min="50" 
                max="2000" 
                step="50"
                value={maxReviews}
                onChange={(e) => setMaxReviews(Number(e.target.value))}
                className="slider"
              />
            </div>
          </div>

          <div className="config-item">
            <label className="config-label">🔧 Advanced Settings</label>
            <div className="slider-container">
              <label>Batch size: {batchSize}</label>
              <input 
                type="range" 
                min="10" 
                max="50" 
                step="5"
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                className="slider"
              />
            </div>
            <div className="slider-container">
              <label>Topics to extract: {numTopics}</label>
              <input 
                type="range" 
                min="3" 
                max="10" 
                step="1"
                value={numTopics}
                onChange={(e) => setNumTopics(Number(e.target.value))}
                className="slider"
              />
            </div>
          </div>
        </div>

        <div className="sidebar-section">
          <h3 className="sidebar-title">🏷️ Taxonomy</h3>
          <div className="config-item">
            <label className="config-label">Upload Taxonomy File</label>
            <div className="upload-section">
              <input type="file" accept=".json,.csv" className="file-input" />
              <button className="upload-btn">Browse</button>
            </div>
            <div className="taxonomy-status">
              No taxonomy file loaded
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Top Navigation */}
        <nav className="top-nav">
          <button
            className={`nav-button ${currentView === 'analysis' ? 'active' : ''}`}
            onClick={() => setCurrentView('analysis')}
          >
            🔍 Analysis
          </button>
          <button
            className={`nav-button ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
            disabled={!results}
          >
            📊 Dashboard
          </button>
          <button
            className={`nav-button ${currentView === 'documentation' ? 'active' : ''}`}
            onClick={() => setCurrentView('documentation')}
          >
            📚 Documentation
          </button>
        </nav>

        {/* Content Area */}
        <div className="content-area">
          {currentView === 'analysis' && (
            <DataSelection onAnalysisComplete={handleAnalysisComplete} maxReviews={maxReviews} />
          )}
          {currentView === 'dashboard' && results && (
            <AnalyticsDashboard results={results} jobId={jobId} />
          )}
          {currentView === 'documentation' && <Documentation />}
        </div>
      </div>
    </div>
  );
}

export default App;