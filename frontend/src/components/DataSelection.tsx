import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './DataSelection.css';

// Import React Icons
import { PiSelectionPlus } from "react-icons/pi";
import { FaGlobe } from "react-icons/fa";
import { PiFolderSimplePlusFill } from "react-icons/pi";
import { IoMdRocket } from "react-icons/io";
import { AiFillStop } from "react-icons/ai";

const API_BASE = 'http://localhost:8000';

// CHANGE #2: Updated Props to accept company name parameter
interface Props {
  onAnalysisComplete: (jobId: string, results: any, companyName: string) => void;
  maxReviews: number;
  batchSize: number;
  maxPages: number;
}

type InputMethod = 'webscraping' | 'upload';

const DataSelection: React.FC<Props> = ({ 
  onAnalysisComplete, 
  maxReviews,
  batchSize,
  maxPages
}) => {
  const [inputMethod, setInputMethod] = useState<InputMethod>('webscraping');
  const [urls, setUrls] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  
  // CHANGE #2: Add company name state
  const [companyName, setCompanyName] = useState<string>('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const hasCompletedRef = useRef(false);

  useEffect(() => {
    return () => {
      cleanup();
    };
  }, []);

  const cleanup = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
      setSelectedFile(file);
    } else {
      alert('Please upload a CSV or Excel file');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const connectWebSocket = (jobId: string) => {
    console.log(`🔌 Connecting WebSocket for job: ${jobId}`);
    
    try {
      const ws = new WebSocket(`ws://localhost:8000/ws/${jobId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📡 Progress update:', data.progress + '%', data.message);
          
          setProgress(data.progress || 0);
          setStatusMessage(data.message || '');

          if (data.status === 'completed' && !hasCompletedRef.current) {
            hasCompletedRef.current = true;
            console.log('🎉 Analysis completed!');
            setTimeout(() => fetchAndCompleteAnalysis(jobId), 500);
          } else if (data.status === 'failed') {
            cleanup();
            setIsAnalyzing(false);
            alert(`Analysis failed: ${data.message}`);
          }
        } catch (e) {
          console.error('❌ Error parsing WebSocket message:', e);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        console.log('🔄 Falling back to polling...');
        startPolling(jobId);
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket closed');
      };
    } catch (error) {
      console.error('❌ Error creating WebSocket:', error);
      startPolling(jobId);
    }
  };

  const startPolling = (jobId: string) => {
    console.log('🔄 Starting status polling');
    
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    pollingIntervalRef.current = setInterval(() => {
      if (!hasCompletedRef.current) {
        pollJobStatus(jobId);
      }
    }, 2000);
  };

  const pollJobStatus = async (jobId: string) => {
    if (hasCompletedRef.current) {
      return;
    }

    try {
      const response = await axios.get(`${API_BASE}/api/jobs/${jobId}`);
      const job = response.data;

      setProgress(job.progress || 0);
      setStatusMessage(job.message || '');

      if (job.status === 'completed' && job.results && !hasCompletedRef.current) {
        hasCompletedRef.current = true;
        console.log('✅ Analysis complete via polling!');
        
        cleanup();
        
        setProgress(100);
        setStatusMessage('🎉 Analysis completed successfully!');
        
        setTimeout(() => {
          setIsAnalyzing(false);
          // CHANGE #2: Pass company name to callback
          onAnalysisComplete(jobId, job.results, companyName);
        }, 1000);
        
      } else if (job.status === 'failed') {
        console.error('❌ Analysis failed:', job.error);
        cleanup();
        setIsAnalyzing(false);
        alert(`Analysis failed: ${job.error}`);
      }
    } catch (error: any) {
      console.error('❌ Error polling:', error);
      
      if (error.response?.status === 404) {
        cleanup();
        setIsAnalyzing(false);
        alert('Job not found');
      }
    }
  };

  const fetchAndCompleteAnalysis = async (jobId: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/jobs/${jobId}`);
      const job = response.data;

      if (job.status === 'completed' && job.results) {
        cleanup();
        
        setProgress(100);
        setStatusMessage('🎉 Analysis completed successfully!');
        
        setTimeout(() => {
          setIsAnalyzing(false);
          // CHANGE #2: Pass company name to callback
          onAnalysisComplete(jobId, job.results, companyName);
        }, 1000);
      }
    } catch (error) {
      console.error('❌ Error fetching final results:', error);
    }
  };

  const handleStartAnalysis = async () => {
    hasCompletedRef.current = false;

    // CHANGE #2: Validate company name first
    if (!companyName.trim()) {
      alert('Please enter a company name');
      return;
    }

    if (inputMethod === 'webscraping') {
      const urlList = urls.split('\n').filter(url => url.trim());
      
      if (urlList.length === 0) {
        alert('Please enter at least one URL');
        return;
      }

      try {
        setIsAnalyzing(true);
        setProgress(0);
        setStatusMessage('Starting analysis...');

        console.log('🚀 Starting analysis with URLs:', urlList);

        const response = await axios.post(`${API_BASE}/api/analyze/urls`, {
          urls: urlList,
          max_reviews: maxReviews,
          batch_size: batchSize,
          max_pages: maxPages
        });

        const jobId = response.data.job_id;
        console.log('✅ Job created:', jobId);
        
        setCurrentJobId(jobId);
        
        connectWebSocket(jobId);
        
        setTimeout(() => {
          if (!hasCompletedRef.current) {
            startPolling(jobId);
          }
        }, 3000);

      } catch (error: any) {
        console.error('❌ Error starting analysis:', error);
        setIsAnalyzing(false);
        const errorMsg = error.response?.data?.detail || error.message || 'Failed to start';
        alert(errorMsg);
      }
    } else {
      if (!selectedFile) {
        alert('Please select a file');
        return;
      }

      try {
        setIsAnalyzing(true);
        setProgress(0);
        setStatusMessage('Uploading file...');

        const formData = new FormData();
        formData.append('file', selectedFile);

        console.log('📤 Uploading:', selectedFile.name);

        const response = await axios.post(`${API_BASE}/api/analyze/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        const jobId = response.data.job_id;
        console.log('✅ Upload job created:', jobId);
        
        setCurrentJobId(jobId);
        connectWebSocket(jobId);
        startPolling(jobId);

      } catch (error: any) {
        console.error('❌ Upload error:', error);
        setIsAnalyzing(false);
        const errorMsg = error.response?.data?.detail || error.message || 'Upload failed';
        alert(errorMsg);
      }
    }
  };

  const handleStopAnalysis = async () => {
    if (currentJobId) {
      try {
        await axios.delete(`${API_BASE}/api/jobs/${currentJobId}`);
        cleanup();
        setIsAnalyzing(false);
        setProgress(0);
        setStatusMessage('Analysis cancelled');
        hasCompletedRef.current = false;
      } catch (error) {
        console.error('❌ Error cancelling:', error);
      }
    }
  };

  return (
    <div className="data-selection">
      <div className="section-card">
        <h2 className="section-title">
          <PiSelectionPlus style={{ marginRight: '10px', fontSize: '28px' }} />
          Data Selection & Analysis
        </h2>

        {/* CHANGE #2: Company Name Input Section */}
        <div style={{ marginBottom: '30px', paddingBottom: '30px', borderBottom: '1px solid #1e3a5f' }}>
          <h3 className="subsection-title">
            🏢 Company Information
          </h3>
          <input
            type="text"
            placeholder="Enter company name (e.g., Airtel, Amazon, Flipkart)"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            disabled={isAnalyzing}
            style={{
              width: '100%',
              padding: '14px 18px',
              background: '#021526',
              border: '2px solid #2d5a7b',
              borderRadius: '8px',
              color: '#ffffff',
              fontSize: '16px',
              fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
              transition: 'border-color 0.3s ease'
            }}
            onFocus={(e) => e.target.style.borderColor = '#4ade80'}
            onBlur={(e) => e.target.style.borderColor = '#2d5a7b'}
          />
          <div style={{ 
            color: '#8b9dc3', 
            fontSize: '13px', 
            fontStyle: 'italic', 
            marginTop: '8px' 
          }}>
            This name will be displayed in the dashboard instead of URLs
          </div>
        </div>

        {/* Input Method Selection */}
        <div className="input-methods">
          <label className="radio-option">
            <input
              type="radio"
              checked={inputMethod === 'webscraping'}
              onChange={() => setInputMethod('webscraping')}
              disabled={isAnalyzing}
            />
            <span className="radio-label">
              <FaGlobe style={{ marginRight: '8px', fontSize: '16px', verticalAlign: 'middle' }} />
              Scrape from URLs
            </span>
          </label>
          <label className="radio-option">
            <input
              type="radio"
              checked={inputMethod === 'upload'}
              onChange={() => setInputMethod('upload')}
              disabled={isAnalyzing}
            />
            <span className="radio-label">
              <PiFolderSimplePlusFill style={{ marginRight: '8px', fontSize: '16px', verticalAlign: 'middle' }} />
              Upload File (CSV/Excel)
            </span>
          </label>
        </div>

        {/* URL Input Section */}
        {inputMethod === 'webscraping' && (
          <div className="url-input-section">
            <h3 className="subsection-title">
              Enter URLs <span className="subsection-subtitle">(one per line)</span>
            </h3>
            <textarea
              className="url-textarea"
              value={urls}
              onChange={(e) => setUrls(e.target.value)}
              placeholder="https://www.trustpilot.com/review/example.com&#10;https://www.glassdoor.com/Reviews/company.htm"
              disabled={isAnalyzing}
            />
          </div>
        )}

        {/* File Upload Section */}
        {inputMethod === 'upload' && (
          <div className="file-upload-section">
            <h3 className="file-select-label">Select Review File</h3>
            <div
              className="file-drop-zone"
              onDrop={handleFileDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="file-drop-content">
                {selectedFile ? (
                  <>
                    <div className="upload-icon">✅</div>
                    <div className="file-drop-text">{selectedFile.name}</div>
                    <div className="file-drop-subtext">Click to change file</div>
                  </>
                ) : (
                  <>
                    <div className="upload-icon">📁</div>
                    <div className="file-drop-text">Drop file here or click to browse</div>
                    <div className="file-drop-subtext">Supports CSV, XLSX, XLS files</div>
                  </>
                )}
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
          </div>
        )}

        {/* Progress Section */}
        {isAnalyzing && (
          <div className="progress-section">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="progress-text">
              <span style={{ fontWeight: 600 }}>{progress}%</span> - {statusMessage}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-buttons">
          {!isAnalyzing ? (
            <button
              className="btn btn-start"
              onClick={handleStartAnalysis}
            >
              <IoMdRocket style={{ marginRight: '8px', fontSize: '18px' }} />
              Start Analysis
            </button>
          ) : (
            <button
              className="btn btn-stop"
              onClick={handleStopAnalysis}
            >
              <AiFillStop style={{ marginRight: '8px', fontSize: '18px' }} />
              Stop Analysis
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataSelection;