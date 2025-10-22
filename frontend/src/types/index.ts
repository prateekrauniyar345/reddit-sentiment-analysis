// Core data types for Reddit Sentiment Analysis

export interface Comment {
  id: string;
  author: string;
  body: string;
  score: number;
  created_utc: number;
  sentiment_score: number;
  sentiment_label: 'positive' | 'negative' | 'neutral';
  permalink?: string;
}

export interface Post {
  id: string;
  title: string;
  selftext: string;
  author: string;
  subreddit: string;
  score: number;
  upvote_ratio: number;
  num_comments: number;
  created_utc: number;
  url: string;
  is_video: boolean;
  over_18: boolean;
  permalink?: string;
  comments: Comment[];
  post_sentiment_score: number;
  post_sentiment_label: 'positive' | 'negative' | 'neutral';
  overall_sentiment: number;
  sentiment_label: 'positive' | 'negative' | 'neutral';
  engagement_score: number;
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

export interface AnalysisRequest {
  query: string;
  limit: number;
  subreddits?: string[];
  time_filter?: 'all' | 'day' | 'week' | 'month' | 'year';
  sort_type?: 'relevance' | 'hot' | 'top' | 'new';
}

export interface AnalysisStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
}

export interface BasicStats {
  total_posts: number;
  total_comments: number;
  average_comments_per_post: number;
  average_post_score: number;
  median_post_score: number;
  max_post_score: number;
  min_post_score: number;
  average_engagement: number;
  posts_with_comments: number;
  nsfw_posts: number;
}

export interface SentimentAnalytics {
  overall_sentiment_score: number;
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
    positive_percentage: number;
    negative_percentage: number;
    neutral_percentage: number;
  };
  sentiment_volatility: number;
  most_positive_sentiment: number;
  most_negative_sentiment: number;
  comment_sentiment_avg: number;
  posts_above_threshold: {
    very_positive: number;
    very_negative: number;
  };
}

export interface TemporalAnalytics {
  time_range: {
    start: string;
    end: string;
    span_hours: number;
  };
  posting_patterns: {
    peak_hour: number;
    peak_day: string;
    hourly_distribution: Record<string, number>;
    daily_distribution: Record<string, number>;
  };
  activity_metrics: {
    posts_per_hour: number;
    most_active_hour_count: number;
    least_active_hour_count: number;
  };
}

export interface EngagementAnalytics {
  average_engagement: number;
  engagement_distribution: {
    high: number;
    medium: number;
    low: number;
  };
  upvote_metrics: {
    average_ratio: number;
    highly_upvoted: number;
  };
  comment_engagement: {
    average_comments: number;
    max_comments: number;
    posts_with_many_comments: number;
  };
  score_metrics: {
    average_score: number;
    viral_posts: number;
    controversial_posts: number;
  };
}

export interface ContentAnalytics {
  text_metrics: {
    average_title_length: number;
    average_selftext_length: number;
    longest_title: number;
    longest_selftext: number;
  };
  content_types: {
    text_posts: number;
    link_posts: number;
    text_post_percentage: number;
  };
  keywords: {
    top_title_words: Record<string, number>;
    top_comment_words: Record<string, number>;
    unique_title_words: number;
    unique_comment_words: number;
  };
}

export interface SubredditAnalytics {
  subreddit_distribution: Record<string, number>;
  total_subreddits: number;
  top_subreddit: [string, number];
  subreddit_sentiment: Record<string, number>;
  most_positive_subreddit: [string, number];
  most_negative_subreddit: [string, number];
}

export interface UserBehaviorAnalytics {
  active_users: {
    total_post_authors: number;
    total_comment_authors: number;
    top_posters: Record<string, number>;
    top_commenters: Record<string, number>;
  };
  user_participation: {
    users_with_multiple_posts: number;
    average_posts_per_user: number;
    most_active_poster: [string, number];
  };
}

export interface TopicModelingAnalytics {
  top_keywords: Record<string, number>;
  total_unique_words: number;
  most_common_word: [string, number];
  word_diversity: number;
}

export interface CorrelationAnalytics {
  correlations: Record<string, number>;
  strongest_positive_correlation: [string, number];
  strongest_negative_correlation: [string, number];
}

export interface TrendAnalytics {
  sentiment_trend: 'increasing' | 'decreasing';
  sentiment_change: number;
  trend_strength: number;
  data_points: number;
}

export interface VisualizationData {
  sentiment_timeline: Array<{
    date: string;
    sentiment: number;
    title: string;
  }>;
  subreddit_sentiment: Array<{
    subreddit: string;
    sentiment: number;
    post_count: number;
  }>;
  engagement_sentiment_scatter: Array<{
    x: number;
    y: number;
    size: number;
    title: string;
    subreddit: string;
  }>;
  hourly_activity: Array<{
    hour: number;
    count: number;
  }>;
}

export interface Analytics {
  basic_stats: BasicStats;
  sentiment_analysis: SentimentAnalytics;
  temporal_analysis: TemporalAnalytics;
  engagement_analysis: EngagementAnalytics;
  content_analysis: ContentAnalytics;
  subreddit_analysis: SubredditAnalytics;
  user_behavior: UserBehaviorAnalytics;
  topic_modeling: TopicModelingAnalytics;
  correlation_analysis: CorrelationAnalytics;
  trend_analysis: TrendAnalytics;
  visualizations: VisualizationData;
}

export interface AnalysisResult {
  task_id: string;
  query: string;
  total_posts: number;
  total_comments: number;
  analysis_duration: number;
  created_at: string;
  posts: Post[];
  analytics: Analytics;
}

export interface AnalysisHistory {
  task_id: string;
  query: string;
  total_posts: number;
  total_comments: number;
  analysis_duration: number;
  created_at: string;
}

// Chart data types
export interface ChartDataPoint {
  x: number | string;
  y: number;
  label?: string;
  color?: string;
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface PieChartData {
  name: string;
  value: number;
  color?: string;
}

export interface ScatterPlotDataPoint {
  x: number;
  y: number;
  size?: number;
  label?: string;
  category?: string;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}