import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface SentimentDistribution {
  positive: number;
  negative: number;
  neutral: number;
  positive_percentage: number;
  negative_percentage: number;
  neutral_percentage: number;
}

interface SentimentDistributionChartProps {
  data: SentimentDistribution;
}

const SentimentDistributionChart: React.FC<SentimentDistributionChartProps> = ({ data }) => {
  const chartData = [
    {
      name: 'Positive',
      value: data.positive,
      percentage: data.positive_percentage,
      color: '#4caf50'
    },
    {
      name: 'Neutral',
      value: data.neutral,
      percentage: data.neutral_percentage,
      color: '#ff9800'
    },
    {
      name: 'Negative',
      value: data.negative,
      percentage: data.negative_percentage,
      color: '#f44336'
    }
  ];

  const CustomTooltip = ({ active, payload }: any) => {
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
          <p style={{ margin: '0 0 5px 0', fontWeight: 'bold', color: data.color }}>
            {data.name}
          </p>
          <p style={{ margin: '0 0 5px 0' }}>
            Count: {data.value}
          </p>
          <p style={{ margin: 0 }}>
            Percentage: {data.percentage.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height="90%">
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          outerRadius={80}
          dataKey="value"
          label={({ name, percentage }) => `${name} (${percentage.toFixed(1)}%)`}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default SentimentDistributionChart;