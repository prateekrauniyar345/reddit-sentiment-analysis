import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface SubredditSentimentData {
  subreddit: string;
  sentiment: number;
  post_count: number;
}

interface SubredditSentimentChartProps {
  data: SubredditSentimentData[];
}

const SubredditSentimentChart: React.FC<SubredditSentimentChartProps> = ({ data }) => {
  // Take only top 10 subreddits for better visualization
  const chartData = data.slice(0, 10).map(item => ({
    ...item,
    subreddit: item.subreddit.replace('r/', ''),
    sentiment: Number(item.sentiment.toFixed(3))
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
          <p style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>
            r/{label}
          </p>
          <p style={{ margin: '0 0 5px 0', color: data.sentiment > 0 ? '#4caf50' : data.sentiment < 0 ? '#f44336' : '#ff9800' }}>
            Sentiment: {data.sentiment}
          </p>
          <p style={{ margin: 0 }}>
            Posts: {data.post_count}
          </p>
        </div>
      );
    }
    return null;
  };

  const getBarColor = (sentiment: number) => {
    if (sentiment > 0.1) return '#4caf50'; // Green for positive
    if (sentiment < -0.1) return '#f44336'; // Red for negative
    return '#ff9800'; // Orange for neutral
  };

  const CustomBar = (props: any) => {
    const { payload, ...rest } = props;
    return (
      <rect 
        {...rest} 
        fill={getBarColor(payload.sentiment)} 
      />
    );
  };

  return (
    <ResponsiveContainer width="100%" height="90%">
      <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="subreddit" 
          angle={-45}
          textAnchor="end"
          height={80}
          interval={0}
        />
        <YAxis domain={[-1, 1]} />
        <Tooltip content={<CustomTooltip />} />
        <Bar 
          dataKey="sentiment" 
          shape={<CustomBar />}
        />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default SubredditSentimentChart;