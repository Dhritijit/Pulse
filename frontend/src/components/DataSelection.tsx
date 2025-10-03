import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './DataSelection.css';

const API_BASE = 'http://localhost:8000';

interface Props {
  onAnalysisComplete: (jobId: string, results: any) => void;
  maxReviews: number;
}

type InputMethod = 'webscraping' | 'upload';

const DataSelection: React.FC<Props> = ({ onAnalysisComplete, maxReviews }) => {
  const [inputMethod, setInputMethod] = useState<InputMethod>('webscraping');
  const [urls, setUrls] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    return () => {
      // Cleanup WebSocket on unmount
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

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
    const ws = new WebSocket(`ws://localhost:8000/ws/${jobId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.progress);
      setStatusMessage(data.message);

      if (data.status === 'completed') {
        pollJobStatus(jobId);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };
  };

  const pollJobStatus = async (jobId: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/jobs/${jobId}`);
      const job = response.data;

      if (job.status === 'completed' && job.results) {
        setIsAnalyzing(false);
        setProgress(100);
        setStatusMessage('Analysis completed!');
        onAnalysisComplete(jobId, job.results);
      } else if (job.status === 'failed') {
        setIsAnalyzing(false);
        setStatusMessage(`Error: ${job.error}`);
        alert(`Analysis failed: ${job.error}`);
      }
    } catch (error) {
      console.error('Error polling job status:', error);
    }
  };

  const handleStartAnalysis = async () => {
    if (inputMethod === 'webscraping') {
      // Web scraping analysis
      const urlList = urls.split('\n').filter(url => url.trim());
      
      if (urlList.length === 0) {
        alert('Please enter at least one URL');
        return;
      }

      try {
        setIsAnalyzing(true);
        setProgress(0);
        setStatusMessage('Starting analysis...');

        const response = await axios.post(`${API_BASE}/api/analyze/urls`, {
          urls: urlList,
          max_reviews: maxReviews,
          num_topics: 5
        });

        const jobId = response.data.job_id;
        setCurrentJobId(jobId);
        connectWebSocket(jobId);

      } catch (error: any) {
        setIsAnalyzing(false);
        const errorMsg = error.response?.data?.detail || 'Analysis failed';
        alert(errorMsg);
      }
    } else {
      // File upload analysis
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

        const response = await axios.post(`${API_BASE}/api/analyze/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        const jobId = response.data.job_id;
        setCurrentJobId(jobId);
        connectWebSocket(jobId);

      } catch (error: any) {
        setIsAnalyzing(false);
        const errorMsg = error.response?.data?.detail || 'File upload failed';
        alert(errorMsg);
      }
    }
  };

  const handleStopAnalysis = async () => {
    if (currentJobId) {
      try {
        await axios.delete(`${API_BASE}/api/jobs/${currentJobId}`);
        setIsAnalyzing(false);
        setProgress(0);
        setStatusMessage('Analysis cancelled');
        if (wsRef.current) {
          wsRef.current.close();
        }
      } catch (error) {
        console.error('Error cancelling job:', error);
      }
    }
  };

  return (
    <div className="data-selection">
      <div className="section-card">
        <h2 className="section-title">
          Data Selection
          <span className="section-subtitle">(Choose your data input method)</span>
        </h2>

        <div className="input-methods">
          <label className="radio-option">
            <input
              type="radio"
              name="inputMethod"
              checked={inputMethod === 'webscraping'}
              onChange={() => setInputMethod('webscraping')}
              disabled={isAnalyzing}
            />
            <span className="radio-label">Web Scraping (URLs)</span>
          </label>

          <label className="radio-option">
            <input
              type="radio"
              name="inputMethod"
              checked={inputMethod === 'upload'}
              onChange={() => setInputMethod('upload')}
              disabled={isAnalyzing}
            />
            <span className="radio-label">Upload File (Excel/CSV)</span>
          </label>
        </div>

        {inputMethod === 'webscraping' ? (
          <div className="url-input-section">
            <h3 className="subsection-title">Enter URLs</h3>
            <textarea
              className="url-textarea"
              placeholder="https://www.trustpilot.com/review/company-name.com&#10;https://www.glassdoor.com/Reviews/Company-Reviews-E123456.htm&#10;https://www.yelp.com/biz/restaurant-name"
              value={urls}
              onChange={(e) => setUrls(e.target.value)}
              disabled={isAnalyzing}
              rows={6}
            />
          </div>
        ) : (
          <div className="file-upload-section">
            <h3 className="subsection-title">
              File Upload
              <span className="subsection-subtitle">
                (Upload Excel or CSV file containing customer reviews)
              </span>
            </h3>

            <div className="file-select-label">Select File</div>
            
            <div
              className="file-drop-zone"
              onDrop={handleFileDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="file-drop-content">
                <div className="upload-icon">☁️</div>
                <div className="file-drop-text">
                  {selectedFile ? selectedFile.name : 'Drag and drop file here'}
                </div>
                <div className="file-drop-subtext">
                  Limit 200MB per file • CSV, XLSX, XLS
                </div>
                <button className="browse-button" onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}>
                  Browse files
                </button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                disabled={isAnalyzing}
              />
            </div>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {isAnalyzing && (
        <div className="progress-section">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
          <div className="progress-text">{statusMessage}</div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="action-buttons">
        <button
          className="btn btn-start"
          onClick={handleStartAnalysis}
          disabled={isAnalyzing}
        >
          Start Analysis
        </button>
        <button
          className="btn btn-stop"
          onClick={handleStopAnalysis}
          disabled={!isAnalyzing}
        >
          Stop Analysis
        </button>
      </div>
    </div>
  );
};

export default DataSelection;