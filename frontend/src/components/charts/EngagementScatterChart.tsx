import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ScatterDataPoint {
  x: number;
  y: number;
  size: number;
  title: string;
  subreddit: string;
}

interface EngagementScatterChartProps {
  data: ScatterDataPoint[];
}

const EngagementScatterChart: React.FC<EngagementScatterChartProps> = ({ data }) => {
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          maxWidth: '300px'
        }}>
          <p style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>
            {data.title}
          </p>
          <p style={{ margin: '0 0 5px 0' }}>
            Subreddit: r/{data.subreddit}
          </p>
          <p style={{ margin: '0 0 5px 0' }}>
            Engagement: {data.x.toFixed(3)}
          </p>
          <p style={{ margin: 0 }}>
            Sentiment: {data.y.toFixed(3)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height="90%">
      <ScatterChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          type="number" 
          dataKey="x" 
          domain={[0, 1]} 
          name="Engagement"
          label={{ value: 'Engagement Score', position: 'insideBottom', offset: -5 }}
        />
        <YAxis 
          type="number" 
          dataKey="y" 
          domain={[-1, 1]} 
          name="Sentiment"
          label={{ value: 'Sentiment Score', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Scatter name="Posts" dataKey="y" fill="#1976d2" />
      </ScatterChart>
    </ResponsiveContainer>
  );
};

export default EngagementScatterChart;