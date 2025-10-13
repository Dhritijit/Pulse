import React, { useState, useEffect } from 'react';
import './App.css';
import DataSelection from './components/DataSelection';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import Documentation from './components/Documentation';
import { VscSettings } from "react-icons/vsc";
import { MdCategory } from "react-icons/md";
import { IoMdAnalytics } from "react-icons/io";
import { FaChartSimple, FaSun, FaMoon } from "react-icons/fa6";
import { IoDocumentText, IoLogOut } from "react-icons/io5";

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
  const [maxPages, setMaxPages] = useState<number>(10);
  const [apiKeyStatus, setApiKeyStatus] = useState<string>('Checking...');
  
  // Company name state
  const [companyName, setCompanyName] = useState<string>('');
  
  // Dark mode state
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);
  
  // User info (hardcoded for now, will be dynamic with login)
  const userName = "Dhritijit Sengupta";

  // Check API key status on mount
  useEffect(() => {
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => {
        setApiKeyStatus(data.openai_configured ? '✅ Configured' : '❌ Missing');
      })
      .catch(() => setApiKeyStatus('❌ Backend Offline'));
  }, []);
  
  // Apply dark/light mode to body
  useEffect(() => {
    document.body.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);
  
  // Extract company name from URL
  const extractCompanyName = (url: string): string => {
    try {
      const urlObj = new URL(url);
      const hostname = urlObj.hostname;
      
      // Remove www. if present
      let domain = hostname.replace('www.', '');
      
      // For review sites, try to extract the company being reviewed
      if (domain.includes('trustpilot.com')) {
        // Extract from path: /review/company-name
        const pathParts = urlObj.pathname.split('/');
        const companyIndex = pathParts.indexOf('review');
        if (companyIndex !== -1 && pathParts[companyIndex + 1]) {
          return formatCompanyName(pathParts[companyIndex + 1]);
        }
      } else if (domain.includes('glassdoor.com')) {
        // Extract from path: /Reviews/Company-Name
        const pathParts = urlObj.pathname.split('/');
        if (pathParts.length > 2) {
          return formatCompanyName(pathParts[2]);
        }
      } else if (domain.includes('yelp.com')) {
        // Extract from path: /biz/company-name
        const pathParts = urlObj.pathname.split('/');
        const bizIndex = pathParts.indexOf('biz');
        if (bizIndex !== -1 && pathParts[bizIndex + 1]) {
          return formatCompanyName(pathParts[bizIndex + 1]);
        }
      }
      
      // Default: use the main domain name
      const parts = domain.split('.');
      return formatCompanyName(parts[0]);
    } catch (e) {
      return 'Unknown Company';
    }
  };
  
  // Format company name (convert kebab-case or domain to Title Case)
  const formatCompanyName = (name: string): string => {
    return name
      .replace(/-/g, ' ')
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };
  
  // NEW ADDITION: Function to get logo based on theme
  const getLogo = () => {
    return isDarkMode ? '/LogoDarkTheme.png' : '/LogoLightTheme.png';
  };
  
  // Toggle dark/light mode
  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };
  
  // Handle logout (placeholder for now)
  const handleLogout = () => {
    // TODO: Implement actual logout logic when authentication is added
    alert('Logout functionality will be implemented with authentication');
  };

  // Refresh function to reset everything
  const handleRefresh = () => {
    setResults(null);
    setJobId(null);
    setCompanyName('');
    setMaxReviews(500);
    setBatchSize(20);
    setMaxPages(10);
    setCurrentView('analysis');
  };

  // Updated to accept company name from user input
  const handleAnalysisComplete = (jobId: string, analysisResults: AnalysisResults, inputCompanyName: string) => {
    setJobId(jobId);
    setResults(analysisResults);
    
    // Use the company name from user input
    if (inputCompanyName && inputCompanyName.trim()) {
      setCompanyName(inputCompanyName);
    } else {
      // Fallback: Extract from first review's source URL
      if (analysisResults.reviews && analysisResults.reviews.length > 0) {
        const firstReview = analysisResults.reviews[0];
        if (firstReview.source_url) {
          const extractedName = extractCompanyName(firstReview.source_url);
          setCompanyName(extractedName);
        }
      }
    }
    
    setCurrentView('dashboard');
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        {/* UPDATED: Dynamic logo based on theme */}
        <div className="logo">
          <img src={getLogo()} alt="Pulse.ai" className="logo-image" />
        </div>

        <div className="sidebar-section">
          <h3 className="sidebar-title">
            <VscSettings style={{ marginRight: '8px' }} />
            Configuration
          </h3>
          
          <div className="config-item">
            <label className="config-label">📋 Prerequisites</label>
            <div className="status-badge">
              OpenAI API: {apiKeyStatus}
            </div>
          </div>

          <div className="config-item">
            <label className="config-label">
              <VscSettings style={{ marginRight: '5px', fontSize: '14px' }} />
              Analysis Settings
            </label>
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
              <label>Max pages per site: {maxPages}</label>
              <input 
                type="range" 
                min="1" 
                max="25" 
                step="1"
                value={maxPages}
                onChange={(e) => setMaxPages(Number(e.target.value))}
                className="slider"
              />
            </div>
          </div>
        </div>

        <div className="sidebar-section">
          <h3 className="sidebar-title">
            <MdCategory style={{ marginRight: '8px' }} />
            Taxonomy
          </h3>
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
          {/* LEFT: Company Name */}
          <div className="top-nav-left">
            {companyName && (
              <div className="company-name-display">
                <span className="company-icon">🏢</span>
                <span className="company-text">{companyName}</span>
              </div>
            )}
          </div>
          
          {/* CENTER: Navigation Buttons */}
          <div className="nav-buttons-group">
            <button
              className={`nav-button ${currentView === 'analysis' ? 'active' : ''}`}
              onClick={() => setCurrentView('analysis')}
            >
              <IoMdAnalytics style={{ marginRight: '8px', fontSize: '18px' }} />
              Analysis
            </button>
            <button
              className={`nav-button ${currentView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentView('dashboard')}
              disabled={!results}
              title={results ? 'View dashboard' : 'Complete an analysis first'}
            >
              <FaChartSimple style={{ marginRight: '8px', fontSize: '16px' }} />
              Dashboard {results && <span style={{ color: '#4ade80' }}>✅</span>}
            </button>
            <button
              className={`nav-button ${currentView === 'documentation' ? 'active' : ''}`}
              onClick={() => setCurrentView('documentation')}
            >
              <IoDocumentText style={{ marginRight: '8px', fontSize: '18px' }} />
              Documentation
            </button>

            {/* Refresh Button - only show when results exist and on analysis view */}
            {results && currentView === 'analysis' && (
              <button
                className="nav-button"
                onClick={handleRefresh}
                title="Reset to default"
                style={{
                  background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                  color: '#ffffff',
                  marginLeft: 'auto'
                }}
              >
                🔄 Refresh
              </button>
            )}
          </div>
          
          {/* RIGHT: Theme Toggle + User Info + Logout */}
          <div className="top-nav-right">
            {/* Theme Toggle */}
            <button className="theme-toggle" onClick={toggleTheme} title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
              {isDarkMode ? <FaSun size={18} /> : <FaMoon size={18} />}
            </button>
            
            {/* User Greeting */}
            <div className="user-greeting">
              <span className="greeting-text">Hello, {userName}</span>
            </div>
            
            {/* Logout Button */}
            <button className="logout-button" onClick={handleLogout} title="Logout">
              <IoLogOut size={18} />
              <span>Logout</span>
            </button>
          </div>
        </nav>

        {/* Content Area */}
        <div className="content-area">
          {currentView === 'analysis' && (
            <DataSelection 
              onAnalysisComplete={handleAnalysisComplete} 
              maxReviews={maxReviews}
              batchSize={batchSize}
              maxPages={maxPages}
            />
          )}
          {currentView === 'dashboard' && results && (
            <AnalyticsDashboard results={results} jobId={jobId} companyName={companyName} />
          )}
          {currentView === 'documentation' && <Documentation />}
        </div>
      </div>
    </div>
  );
}

export default App;

// LINES OF CODE: 329 lines
// CHANGES MADE:
// Line 113-116: ADDED getLogo() function
// Line 170: UPDATED to use getLogo() instead of static /logo.png