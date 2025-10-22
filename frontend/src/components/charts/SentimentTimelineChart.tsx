import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

interface TimelineDataPoint {
  date: string;
  sentiment: number;
  title: string;
}

interface SentimentTimelineChartProps {
  data: TimelineDataPoint[];
}

const SentimentTimelineChart: React.FC<SentimentTimelineChartProps> = ({ data }) => {
  // Transform data for recharts
  const chartData = data.map(point => ({
    ...point,
    date: format(new Date(point.date), 'MMM dd'),
    formattedSentiment: Number(point.sentiment.toFixed(3))
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>{label}</p>
          <p style={{ margin: '0 0 5px 0', color: '#8884d8' }}>
            Sentiment: {data.formattedSentiment}
          </p>
          <p style={{ margin: 0, fontSize: '12px', color: '#666' }}>
            {data.title}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height="90%">
      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis domain={[-1, 1]} />
        <Tooltip content={<CustomTooltip />} />
        <Line 
          type="monotone" 
          dataKey="formattedSentiment" 
          stroke="#1976d2" 
          strokeWidth={2}
          dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default SentimentTimelineChart;