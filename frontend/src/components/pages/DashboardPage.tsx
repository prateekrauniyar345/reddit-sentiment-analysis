import React, { useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Remove,
  Assessment,
  Forum,
  Schedule,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAnalysis } from '../../contexts/AnalysisContext';
// import SentimentTimelineChart from '../charts/SentimentTimelineChart';
// import SentimentDistributionChart from '../charts/SentimentDistributionChart';
// import EngagementScatterChart from '../charts/EngagementScatterChart';
// import SubredditSentimentChart from '../charts/SubredditSentimentChart';
import SentimentTimelineChart from '../charts/SentimentTimelineChart';
import SentimentDistributionChart from '../charts/SentimentDistributionChart';
import EngagementScatterChart from '../charts/EngagementScatterChart';
import SubredditSentimentChart from '../charts/SubredditSentimentChart';

const DashboardPage: React.FC = () => {
  const { state, getHistory } = useAnalysis();
  const { currentAnalysis, isLoading, error } = state;

  useEffect(() => {
    getHistory();
  }, [getHistory]);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!currentAnalysis) {
    return (
      <Box textAlign="center" py={8}>
        <Assessment sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h4" color="text.secondary" gutterBottom>
          No Analysis Available
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Start a new analysis to see comprehensive insights and visualizations.
        </Typography>
      </Box>
    );
  }

  const analytics = currentAnalysis.analytics;
  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.1) return <TrendingUp color="success" />;
    if (sentiment < -0.1) return <TrendingDown color="error" />;
    return <Remove color="warning" />;
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.1) return 'success';
    if (sentiment < -0.1) return 'error';
    return 'warning';
  };

  return (
    <Box>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Analysis Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Query: "{currentAnalysis.query}" • {currentAnalysis.total_posts} posts • {currentAnalysis.total_comments} comments
        </Typography>
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Overall Sentiment
                    </Typography>
                    <Typography variant="h4">
                      {analytics.sentiment_analysis.overall_sentiment_score.toFixed(3)}
                    </Typography>
                  </Box>
                  {getSentimentIcon(analytics.sentiment_analysis.overall_sentiment_score)}
                </Box>
                <Chip
                  label={analytics.sentiment_analysis.overall_sentiment_score > 0.1 ? 'Positive' : 
                         analytics.sentiment_analysis.overall_sentiment_score < -0.1 ? 'Negative' : 'Neutral'}
                  color={getSentimentColor(analytics.sentiment_analysis.overall_sentiment_score) as any}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Engagement Score
                    </Typography>
                    <Typography variant="h4">
                      {analytics.engagement_analysis.average_engagement.toFixed(3)}
                    </Typography>
                  </Box>
                  <Assessment color="primary" />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Avg engagement level
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Active Subreddits
                    </Typography>
                    <Typography variant="h4">
                      {analytics.subreddit_analysis.total_subreddits}
                    </Typography>
                  </Box>
                  <Forum color="secondary" />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Communities analyzed
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.4 }}
          >
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Analysis Time
                    </Typography>
                    <Typography variant="h4">
                      {Math.round(currentAnalysis.analysis_duration)}s
                    </Typography>
                  </Box>
                  <Schedule color="info" />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Processing duration
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Charts Grid */}
      <Grid container spacing={3}>
        {/* Sentiment Timeline */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.5 }}
          >
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                Sentiment Over Time
              </Typography>
              <SentimentTimelineChart data={analytics.visualizations.sentiment_timeline} />
            </Paper>
          </motion.div>
        </Grid>

        {/* Sentiment Distribution */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.6 }}
          >
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                Sentiment Distribution
              </Typography>
              <SentimentDistributionChart data={analytics.sentiment_analysis.sentiment_distribution} />
            </Paper>
          </motion.div>
        </Grid>

        {/* Engagement vs Sentiment Scatter */}
        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.7 }}
          >
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                Engagement vs Sentiment
              </Typography>
              <EngagementScatterChart data={analytics.visualizations.engagement_sentiment_scatter} />
            </Paper>
          </motion.div>
        </Grid>

        {/* Subreddit Sentiment */}
        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.8 }}
          >
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                Subreddit Sentiment Analysis
              </Typography>
              <SubredditSentimentChart data={analytics.visualizations.subreddit_sentiment} />
            </Paper>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;