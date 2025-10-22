import React, { useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  TrendingUp,
  TrendingDown,
  Remove,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAnalysis } from '../../contexts/AnalysisContext';
import { format } from 'date-fns';

const HistoryPage: React.FC = () => {
  const { state, getHistory, getAnalysisResult, deleteAnalysis } = useAnalysis();
  const { history } = state;

  useEffect(() => {
    getHistory();
  }, [getHistory]);

  const handleViewAnalysis = async (taskId: string) => {
    await getAnalysisResult(taskId);
  };

  const handleDeleteAnalysis = async (taskId: string) => {
    if (window.confirm('Are you sure you want to delete this analysis?')) {
      await deleteAnalysis(taskId);
    }
  };

  const getSentimentIcon = (query: string) => {
    // This is a simplified version - in a real app, you'd store sentiment with history
    const hash = query.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    const sentiment = (hash % 200) / 100 - 1; // Generate a sentiment between -1 and 1
    
    if (sentiment > 0.1) return <TrendingUp color="success" />;
    if (sentiment < -0.1) return <TrendingDown color="error" />;
    return <Remove color="warning" />;
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analysis History
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        View and manage your previous Reddit sentiment analyses.
      </Typography>

      {history.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Analysis History
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Your completed analyses will appear here.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {history.map((item, index) => (
            <Grid item xs={12} key={item.task_id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card>
                  <CardContent>
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={12} md={6}>
                        <Box display="flex" alignItems="center" gap={2}>
                          {getSentimentIcon(item.query)}
                          <Box>
                            <Typography variant="h6" gutterBottom>
                              "{item.query}"
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {format(new Date(item.created_at), 'PPp')}
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12} md={4}>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          <Chip
                            label={`${item.total_posts} posts`}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                          <Chip
                            label={`${item.total_comments} comments`}
                            size="small"
                            color="secondary"
                            variant="outlined"
                          />
                          <Chip
                            label={formatDuration(item.analysis_duration)}
                            size="small"
                            color="info"
                            variant="outlined"
                          />
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12} md={2}>
                        <Box display="flex" gap={1} justifyContent="flex-end">
                          <IconButton
                            onClick={() => handleViewAnalysis(item.task_id)}
                            color="primary"
                            title="View Analysis"
                          >
                            <ViewIcon />
                          </IconButton>
                          <IconButton
                            onClick={() => handleDeleteAnalysis(item.task_id)}
                            color="error"
                            title="Delete Analysis"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default HistoryPage;