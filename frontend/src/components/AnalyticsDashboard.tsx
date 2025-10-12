import React, { useState } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './AnalyticsDashboard.css';

interface Props {
  results: any;
  jobId: string | null;
  companyName?: string;
}

interface Review {
  text: string;
  sentiment: string;
  source_url: string;
  rating?: number;
  date?: string;
}

const AnalyticsDashboard: React.FC<Props> = ({ results, jobId, companyName }) => {
  const [selectedLevel1, setSelectedLevel1] = useState<string | null>(null);
  
  // CHANGE #8: Review audit modal state
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [selectedReviews, setSelectedReviews] = useState<Review[]>([]);
  const [selectedTopicName, setSelectedTopicName] = useState<string>('');

  // Calculate sentiment statistics
  const totalReviews = results.total_reviews || 0;
  const sentimentCounts = {
    positive: results.sentiment_results?.filter((r: any) => r.sentiment === 'positive').length || 0,
    negative: results.sentiment_results?.filter((r: any) => r.sentiment === 'negative').length || 0,
    neutral: results.sentiment_results?.filter((r: any) => r.sentiment === 'neutral').length || 0,
  };

  const positivePercentage = totalReviews > 0 ? ((sentimentCounts.positive / totalReviews) * 100).toFixed(1) : '0.0';
  const negativePercentage = totalReviews > 0 ? ((sentimentCounts.negative / totalReviews) * 100).toFixed(1) : '0.0';
  const neutralPercentage = totalReviews > 0 ? ((sentimentCounts.neutral / totalReviews) * 100).toFixed(1) : '0.0';

  // CHANGE #6: Sentiment data for pie chart with better labels
  const sentimentData = [
    { name: 'Positive', value: sentimentCounts.positive, color: '#4ade80' },
    { name: 'Negative', value: sentimentCounts.negative, color: '#f87171' },
    { name: 'Neutral', value: sentimentCounts.neutral, color: '#94a3b8' },
  ].filter(item => item.value > 0);

  // Get hierarchical stats
  const hierarchicalStats = results.hierarchical_stats || [];

  // Prepare Level 1 bar chart data
  const level1ChartData = hierarchicalStats.map((stat: any) => ({
    name: stat.level1_name,
    value: stat.level1_percentage,
    count: stat.level1_count,
    id: stat.level1_id
  }));

  // Get Level 2 data for selected Level 1
  const getLevel2Data = () => {
    if (!selectedLevel1) return [];
    
    const level1Stat = hierarchicalStats.find((stat: any) => stat.level1_id === selectedLevel1);
    if (!level1Stat) return [];

    return level1Stat.level2_topics.map((topic: any) => ({
      name: topic.name,
      value: topic.percentage,
      count: topic.count
    }));
  };

  const level2ChartData = getLevel2Data();

  // CHANGE #8: Handle review audit
  const handleReviewAudit = (level1Id: string, level2Name?: string) => {
    const level1Stat = hierarchicalStats.find((stat: any) => stat.level1_id === level1Id);
    if (!level1Stat) return;

    // Filter reviews based on topic
    const filteredReviews = results.reviews.filter((review: any, index: number) => {
      const assignment = results.topic_assignments?.[index];
      if (!assignment) return false;
      
      if (level2Name) {
        return assignment.level1_id === level1Id && assignment.level2_topic === level2Name;
      } else {
        return assignment.level1_id === level1Id;
      }
    }).map((review: any, index: number) => {
      const sentimentResult = results.sentiment_results?.find((s: any, i: number) => 
        results.reviews[i] === review
      );
      
      return {
        text: review.text || review.review_text || 'No review text',
        sentiment: sentimentResult?.sentiment || 'unknown',
        source_url: review.source_url || review.url || 'Unknown source',
        rating: review.rating,
        date: review.date
      };
    });

    setSelectedReviews(filteredReviews);
    setSelectedTopicName(level2Name ? `${level1Stat.level1_name} → ${level2Name}` : level1Stat.level1_name);
    setShowReviewModal(true);
  };

  // CHANGE #7: Custom X-Axis tick with wrapped text
  const CustomXAxisTick = (props: any) => {
    const { x, y, payload } = props;
    const words = payload.value.split(' ');
    const maxWidth = 15;
    const lines: string[] = [];
    let currentLine = '';

    words.forEach((word: string) => {
      if ((currentLine + word).length <= maxWidth) {
        currentLine += (currentLine ? ' ' : '') + word;
      } else {
        if (currentLine) lines.push(currentLine);
        currentLine = word;
      }
    });
    if (currentLine) lines.push(currentLine);

    return (
      <g transform={`translate(${x},${y})`}>
        {lines.map((line, index) => (
          <text
            key={index}
            x={0}
            y={index * 12 + 10}
            textAnchor="middle"
            fill="#8b9dc3"
            fontSize={11}
          >
            {line}
          </text>
        ))}
      </g>
    );
  };

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: '#1e3a5f',
          border: '1px solid #4a90e2',
          padding: '10px',
          borderRadius: '8px'
        }}>
          <p style={{ color: '#ffffff', margin: 0, fontWeight: 600 }}>{payload[0].payload.name}</p>
          <p style={{ color: '#4ade80', margin: '5px 0 0 0' }}>
            {payload[0].value.toFixed(1)}% ({payload[0].payload.count} reviews)
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="analytics-dashboard">
      {/* Top Metric Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            📊
          </div>
          <div className="metric-content">
            <div className="metric-label">Total Reviews</div>
            <div className="metric-value">{totalReviews.toLocaleString()}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)' }}>
            😊
          </div>
          <div className="metric-content">
            <div className="metric-label">Positive</div>
            <div className="metric-value">{positivePercentage}%</div>
            <div className="metric-subtext">{sentimentCounts.positive} reviews</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #f87171 0%, #ef4444 100%)' }}>
            😞
          </div>
          <div className="metric-content">
            <div className="metric-label">Negative</div>
            <div className="metric-value">{negativePercentage}%</div>
            <div className="metric-subtext">{sentimentCounts.negative} reviews</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)' }}>
            😐
          </div>
          <div className="metric-content">
            <div className="metric-label">Neutral</div>
            <div className="metric-value">{neutralPercentage}%</div>
            <div className="metric-subtext">{sentimentCounts.neutral} reviews</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        {/* CHANGE #6: Sentiment Distribution Pie Chart with fixed labels */}
        <div className="chart-card">
          <h3 className="chart-title">Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
                label={(entry) => `${entry.name} ${((entry.value / totalReviews) * 100).toFixed(1)}%`}
                labelLine={false}
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* CHANGE #7: Level 1 Topics Bar Chart with wrapped text */}
        <div className="chart-card chart-card-wide">
          <h3 className="chart-title">Topic Distribution (Level 1)</h3>
          <p className="chart-subtitle">Click a bar to view Level 2 subcategories</p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={level1ChartData} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d5a7b" />
              <XAxis 
                dataKey="name" 
                tick={<CustomXAxisTick />}
                interval={0}
                height={100}
              />
              <YAxis 
                stroke="#8b9dc3"
                tick={{ fill: '#8b9dc3' }}
                label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft', fill: '#8b9dc3' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="value" 
                fill="#4a90e2"
                radius={[8, 8, 0, 0]}
                onClick={(data: any) => {
                  setSelectedLevel1(data.id);
                }}
                cursor="pointer"
              >
                {level1ChartData.map((entry: any, index: number) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={selectedLevel1 === entry.id ? '#4ade80' : '#4a90e2'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Level 2 Topics - Drill Down */}
      {selectedLevel1 && level2ChartData.length > 0 && (
        <div className="chart-card chart-card-full">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h3 className="chart-title">Level 2 Subcategories</h3>
              <p className="chart-subtitle">
                Breakdown for: <strong>{hierarchicalStats.find((s: any) => s.level1_id === selectedLevel1)?.level1_name}</strong>
                {' '}(Percentages relative to this Level 1 category)
              </p>
            </div>
            <button
              onClick={() => setSelectedLevel1(null)}
              style={{
                padding: '8px 16px',
                background: '#2d5a7b',
                border: 'none',
                borderRadius: '6px',
                color: '#ffffff',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              ← Back to Level 1
            </button>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={level2ChartData} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d5a7b" />
              <XAxis 
                dataKey="name" 
                tick={<CustomXAxisTick />}
                interval={0}
                height={100}
              />
              <YAxis 
                stroke="#8b9dc3"
                tick={{ fill: '#8b9dc3' }}
                label={{ value: '% of Level 1 Category', angle: -90, position: 'insideLeft', fill: '#8b9dc3' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="value" 
                fill="#22c55e"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* CHANGE #8: Topic Hierarchy Table with Review Audit buttons */}
      <div className="chart-card chart-card-full">
        <h3 className="chart-title">Complete Topic Hierarchy</h3>
        <div className="hierarchy-table-container">
          <table className="hierarchy-table">
            <thead>
              <tr>
                <th>Level 1 Category</th>
                <th>Count</th>
                <th>% of Total</th>
                <th>Level 2 Subcategories</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {hierarchicalStats.map((level1: any, index: number) => (
                <React.Fragment key={index}>
                  <tr className="level1-row" onClick={() => setSelectedLevel1(level1.level1_id)}>
                    <td className="level1-name">
                      <span className="expand-icon">▶</span>
                      {level1.level1_name}
                    </td>
                    <td>{level1.level1_count}</td>
                    <td>
                      <div className="percentage-bar">
                        <div 
                          className="percentage-fill" 
                          style={{ width: `${level1.level1_percentage}%` }}
                        />
                        <span className="percentage-text">{level1.level1_percentage}%</span>
                      </div>
                    </td>
                    <td>{level1.level2_topics.length} subcategories</td>
                    <td>
                      <button
                        className="review-audit-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleReviewAudit(level1.level1_id);
                        }}
                      >
                        👁️ Review
                      </button>
                    </td>
                  </tr>
                  {level1.level2_topics.map((level2: any, idx: number) => (
                    <tr key={`${index}-${idx}`} className="level2-row">
                      <td className="level2-name">└─ {level2.name}</td>
                      <td>{level2.count}</td>
                      <td>
                        <div className="percentage-bar level2-bar">
                          <div 
                            className="percentage-fill level2-fill" 
                            style={{ width: `${level2.percentage}%` }}
                          />
                          <span className="percentage-text">
                            {level2.percentage}% <span className="percentage-subtext">(of {level1.level1_name})</span>
                          </span>
                        </div>
                      </td>
                      <td className="level2-detail">{level2.percentage_of_total}% of total</td>
                      <td>
                        <button
                          className="review-audit-btn-small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleReviewAudit(level1.level1_id, level2.name);
                          }}
                        >
                          👁️
                        </button>
                      </td>
                    </tr>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Insights Section */}
      <div className="chart-card chart-card-full">
        <h3 className="chart-title">💡 AI-Generated Insights</h3>
        <div className="insights-content">
          {results.insights ? (
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8', color: '#e2e8f0' }}>
              {results.insights}
            </div>
          ) : (
            <p style={{ color: '#8b9dc3', fontStyle: 'italic' }}>No insights available</p>
          )}
        </div>
      </div>

      {/* Download Section */}
      <div className="download-section">
        <button
          onClick={() => window.open(`http://localhost:8000/api/download/${results.filename}`, '_blank')}
          className="download-button"
        >
          📥 Download Complete Excel Report
        </button>
      </div>

      {/* CHANGE #8: Review Audit Modal */}
      {showReviewModal && (
        <div className="modal-overlay" onClick={() => setShowReviewModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Review Audit: {selectedTopicName}</h2>
              <button className="modal-close" onClick={() => setShowReviewModal(false)}>✕</button>
            </div>
            
            <div className="modal-body">
              <div className="review-count-header">
                Total Reviews: <strong>{selectedReviews.length}</strong>
              </div>
              
              {selectedReviews.length === 0 ? (
                <div className="no-reviews">No reviews found for this topic.</div>
              ) : (
                <div className="reviews-list">
                  {selectedReviews.map((review, index) => (
                    <div key={index} className="review-item">
                      <div className="review-header">
                        <span className={`sentiment-badge sentiment-${review.sentiment}`}>
                          {review.sentiment.toUpperCase()}
                        </span>
                        <span className="review-index">Review #{index + 1}</span>
                      </div>
                      
                      <div className="review-text">{review.text}</div>
                      
                      <div className="review-metadata">
                        <div className="metadata-item">
                          <strong>Source:</strong> 
                          <a href={review.source_url} target="_blank" rel="noopener noreferrer" className="source-link">
                            {review.source_url.length > 60 ? review.source_url.substring(0, 60) + '...' : review.source_url}
                          </a>
                        </div>
                        {review.rating && (
                          <div className="metadata-item">
                            <strong>Rating:</strong> {review.rating} / 5
                          </div>
                        )}
                        {review.date && (
                          <div className="metadata-item">
                            <strong>Date:</strong> {review.date}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className="modal-footer">
              <button className="modal-btn-close" onClick={() => setShowReviewModal(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;