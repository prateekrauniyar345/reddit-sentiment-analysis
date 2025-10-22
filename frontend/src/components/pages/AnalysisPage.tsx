import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Typography,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Alert,
  Paper,
} from '@mui/material';
import { Search as SearchIcon, PlayArrow as PlayIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAnalysis } from '../../contexts/AnalysisContext';
import { AnalysisRequest } from '../../types';

const AnalysisPage: React.FC = () => {
  const { state, startAnalysis } = useAnalysis();
  const { analysisStatus, isLoading, error } = state;

  const [formData, setFormData] = useState<AnalysisRequest>({
    query: '',
    limit: 100,
    subreddits: [],
    time_filter: 'week',
    sort_type: 'relevance',
  });

  const [subredditInput, setSubredditInput] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.query.trim()) return;

    try {
      await startAnalysis(formData);
    } catch (error) {
      console.error('Failed to start analysis:', error);
    }
  };

  const handleAddSubreddit = () => {
    if (subredditInput.trim() && !formData.subreddits?.includes(subredditInput.trim())) {
      setFormData(prev => ({
        ...prev,
        subreddits: [...(prev.subreddits || []), subredditInput.trim()]
      }));
      setSubredditInput('');
    }
  };

  const handleRemoveSubreddit = (subreddit: string) => {
    setFormData(prev => ({
      ...prev,
      subreddits: prev.subreddits?.filter(s => s !== subreddit) || []
    }));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        New Reddit Analysis
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Configure your Reddit sentiment analysis parameters below. You can analyze up to 1000 posts with advanced sentiment analysis and engagement metrics.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardContent>
                <form onSubmit={handleSubmit}>
                  <Grid container spacing={3}>
                    {/* Search Query */}
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Search Query"
                        value={formData.query}
                        onChange={(e) => setFormData(prev => ({ ...prev, query: e.target.value }))}
                        placeholder="e.g., artificial intelligence, climate change, cryptocurrency"
                        required
                        InputProps={{
                          startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                        }}
                      />
                    </Grid>

                    {/* Limit */}
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Number of Posts"
                        type="number"
                        value={formData.limit}
                        onChange={(e) => setFormData(prev => ({ ...prev, limit: parseInt(e.target.value) || 100 }))}
                        inputProps={{ min: 10, max: 1000 }}
                        helperText="Maximum 1000 posts"
                      />
                    </Grid>

                    {/* Time Filter */}
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Time Filter</InputLabel>
                        <Select
                          value={formData.time_filter}
                          onChange={(e) => setFormData(prev => ({ ...prev, time_filter: e.target.value as any }))}
                          label="Time Filter"
                        >
                          <MenuItem value="day">Past Day</MenuItem>
                          <MenuItem value="week">Past Week</MenuItem>
                          <MenuItem value="month">Past Month</MenuItem>
                          <MenuItem value="year">Past Year</MenuItem>
                          <MenuItem value="all">All Time</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    {/* Sort Type */}
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Sort By</InputLabel>
                        <Select
                          value={formData.sort_type}
                          onChange={(e) => setFormData(prev => ({ ...prev, sort_type: e.target.value as any }))}
                          label="Sort By"
                        >
                          <MenuItem value="relevance">Relevance</MenuItem>
                          <MenuItem value="hot">Hot</MenuItem>
                          <MenuItem value="top">Top</MenuItem>
                          <MenuItem value="new">New</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    {/* Subreddit Filter */}
                    <Grid item xs={12}>
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Specific Subreddits (Optional)
                        </Typography>
                        <Box display="flex" gap={1} mb={2}>
                          <TextField
                            value={subredditInput}
                            onChange={(e) => setSubredditInput(e.target.value)}
                            placeholder="e.g., technology, worldnews"
                            size="small"
                            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSubreddit())}
                          />
                          <Button
                            variant="outlined"
                            onClick={handleAddSubreddit}
                            disabled={!subredditInput.trim()}
                          >
                            Add
                          </Button>
                        </Box>
                        <Box display="flex" flexWrap="wrap" gap={1}>
                          {formData.subreddits?.map((subreddit) => (
                            <Chip
                              key={subreddit}
                              label={`r/${subreddit}`}
                              onDelete={() => handleRemoveSubreddit(subreddit)}
                              color="primary"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                        {(formData.subreddits?.length || 0) === 0 && (
                          <Typography variant="body2" color="text.secondary">
                            Leave empty to search across all subreddits
                          </Typography>
                        )}
                      </Box>
                    </Grid>

                    {/* Submit Button */}
                    <Grid item xs={12}>
                      <Button
                        type="submit"
                        variant="contained"
                        size="large"
                        startIcon={<PlayIcon />}
                        disabled={isLoading || !formData.query.trim()}
                        fullWidth
                      >
                        {isLoading ? 'Starting Analysis...' : 'Start Analysis'}
                      </Button>
                    </Grid>
                  </Grid>
                </form>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Status Panel */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Analysis Status
              </Typography>
              
              {analysisStatus ? (
                <Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2">Progress</Typography>
                    <Typography variant="body2">{analysisStatus.progress}%</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={analysisStatus.progress} 
                    sx={{ mb: 2 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    Status: {analysisStatus.status}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {analysisStatus.message}
                  </Typography>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No active analysis
                </Typography>
              )}
            </Paper>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalysisPage;