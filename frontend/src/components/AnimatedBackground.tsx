import React from 'react';
import './AnimatedBackground.css';

const AnimatedBackground: React.FC = () => {
  return (
    <div className="animated-background">
      <div className="gradient-orb orb-1"></div>
      <div className="gradient-orb orb-2"></div>
      <div className="gradient-orb orb-3"></div>
    </div>
  );
};

export default AnimatedBackground;