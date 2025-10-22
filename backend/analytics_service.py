"""
Advanced Analytics Service
Provides comprehensive analysis and insights from Reddit data
"""

import asyncio
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import re
from textblob import TextBlob
import logging
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        """Initialize analytics service"""
        pass
    
    async def generate_analytics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analytics from analyzed posts"""
        logger.info(f"Generating analytics for {len(posts)} posts")
        
        if not posts:
            return {}
        
        try:
            analytics = {
                'basic_stats': self._get_basic_statistics(posts),
                'sentiment_analysis': self._get_sentiment_analytics(posts),
                'temporal_analysis': self._get_temporal_analytics(posts),
                'engagement_analysis': self._get_engagement_analytics(posts),
                'content_analysis': self._get_content_analytics(posts),
                'subreddit_analysis': self._get_subreddit_analytics(posts),
                'user_behavior': self._get_user_behavior_analytics(posts),
                'topic_modeling': await self._get_topic_modeling(posts),
                'correlation_analysis': self._get_correlation_analysis(posts),
                'trend_analysis': self._get_trend_analysis(posts)
            }
            
            # Generate visualization data
            analytics['visualizations'] = self._generate_visualization_data(posts, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return {}
    
    def _get_basic_statistics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic statistics"""
        try:
            total_posts = len(posts)
            total_comments = sum(len(post.get('comments', [])) for post in posts)
            
            scores = [post.get('score', 0) for post in posts]
            engagement_scores = [post.get('engagement_score', 0) for post in posts]
            
            return {
                'total_posts': total_posts,
                'total_comments': total_comments,
                'average_comments_per_post': total_comments / total_posts if total_posts > 0 else 0,
                'average_post_score': np.mean(scores) if scores else 0,
                'median_post_score': np.median(scores) if scores else 0,
                'max_post_score': max(scores) if scores else 0,
                'min_post_score': min(scores) if scores else 0,
                'average_engagement': np.mean(engagement_scores) if engagement_scores else 0,
                'posts_with_comments': len([p for p in posts if len(p.get('comments', [])) > 0]),
                'nsfw_posts': len([p for p in posts if p.get('over_18', False)])
            }
        except Exception as e:
            logger.error(f"Error in _get_basic_statistics: {e}")
            return {}
    
    def _get_sentiment_analytics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment patterns"""
        try:
            sentiments = [post.get('overall_sentiment', 0) for post in posts]
            
            # Sentiment distribution
            positive = len([s for s in sentiments if s > 0.3])
            negative = len([s for s in sentiments if s < -0.3])
            neutral = len(sentiments) - positive - negative
            
            # Comment sentiment analysis
            all_comment_sentiments = []
            for post in posts:
                for comment in post.get('comments', []):
                    all_comment_sentiments.append(comment.get('sentiment_score', 0))
            
            # Sentiment volatility (standard deviation)
            sentiment_volatility = np.std(sentiments) if sentiments else 0
            
            return {
                'overall_sentiment_score': np.mean(sentiments) if sentiments else 0,
                'sentiment_distribution': {
                    'positive': positive,
                    'negative': negative,
                    'neutral': neutral,
                    'positive_percentage': (positive / len(sentiments) * 100) if sentiments else 0,
                    'negative_percentage': (negative / len(sentiments) * 100) if sentiments else 0,
                    'neutral_percentage': (neutral / len(sentiments) * 100) if sentiments else 0
                },
                'sentiment_volatility': sentiment_volatility,
                'most_positive_sentiment': max(sentiments) if sentiments else 0,
                'most_negative_sentiment': min(sentiments) if sentiments else 0,
                'comment_sentiment_avg': np.mean(all_comment_sentiments) if all_comment_sentiments else 0,
                'posts_above_threshold': {
                    'very_positive': len([s for s in sentiments if s > 0.7]),
                    'very_negative': len([s for s in sentiments if s < -0.7])
                }
            }
        except Exception as e:
            logger.error(f"Error in _get_sentiment_analytics: {e}")
            return {}
    
    def _get_temporal_analytics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns"""
        try:
            # Convert timestamps
            timestamps = []
            for post in posts:
                try:
                    timestamp = post.get('created_utc', 0)
                    if timestamp:
                        timestamps.append(datetime.utcfromtimestamp(timestamp))
                except:
                    continue
            
            if not timestamps:
                return {}
            
            # Sort timestamps
            timestamps.sort()
            
            # Analyze posting patterns
            hours = [t.hour for t in timestamps]
            days = [t.weekday() for t in timestamps]  # 0=Monday, 6=Sunday
            
            hour_counts = Counter(hours)
            day_counts = Counter(days)
            
            # Find peak activity times
            peak_hour = max(hour_counts, key=hour_counts.get) if hour_counts else 0
            peak_day = max(day_counts, key=day_counts.get) if day_counts else 0
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Time range analysis
            time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600  # hours
            
            return {
                'time_range': {
                    'start': timestamps[0].isoformat() if timestamps else None,
                    'end': timestamps[-1].isoformat() if timestamps else None,
                    'span_hours': time_span
                },
                'posting_patterns': {
                    'peak_hour': peak_hour,
                    'peak_day': day_names[peak_day] if 0 <= peak_day < 7 else 'Unknown',
                    'hourly_distribution': dict(hour_counts),
                    'daily_distribution': {day_names[k]: v for k, v in day_counts.items() if 0 <= k < 7}
                },
                'activity_metrics': {
                    'posts_per_hour': len(posts) / max(time_span, 1),
                    'most_active_hour_count': max(hour_counts.values()) if hour_counts else 0,
                    'least_active_hour_count': min(hour_counts.values()) if hour_counts else 0
                }
            }
        except Exception as e:
            logger.error(f"Error in _get_temporal_analytics: {e}")
            return {}
    
    def _get_engagement_analytics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        try:
            engagement_scores = [post.get('engagement_score', 0) for post in posts]
            upvote_ratios = [post.get('upvote_ratio', 0.5) for post in posts]
            comment_counts = [len(post.get('comments', [])) for post in posts]
            scores = [post.get('score', 0) for post in posts]
            
            # Engagement tiers
            high_engagement = len([e for e in engagement_scores if e > 0.7])
            medium_engagement = len([e for e in engagement_scores if 0.3 < e <= 0.7])
            low_engagement = len([e for e in engagement_scores if e <= 0.3])
            
            return {
                'average_engagement': np.mean(engagement_scores) if engagement_scores else 0,
                'engagement_distribution': {
                    'high': high_engagement,
                    'medium': medium_engagement,
                    'low': low_engagement
                },
                'upvote_metrics': {
                    'average_ratio': np.mean(upvote_ratios) if upvote_ratios else 0,
                    'highly_upvoted': len([r for r in upvote_ratios if r > 0.9])
                },
                'comment_engagement': {
                    'average_comments': np.mean(comment_counts) if comment_counts else 0,
                    'max_comments': max(comment_counts) if comment_counts else 0,
                    'posts_with_many_comments': len([c for c in comment_counts if c > 50])
                },
                'score_metrics': {
                    'average_score': np.mean(scores) if scores else 0,
                    'viral_posts': len([s for s in scores if s > 1000]),
                    'controversial_posts': len([post for post in posts if post.get('upvote_ratio', 1) < 0.6])
                }
            }
        except Exception as e:
            logger.error(f"Error in _get_engagement_analytics: {e}")
            return {}
    
    def _get_content_analytics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content characteristics"""
        try:
            # Text length analysis
            title_lengths = [len(post.get('title', '')) for post in posts]
            selftext_lengths = [len(post.get('selftext', '')) for post in posts]
            
            # Content type analysis
            text_posts = len([p for p in posts if p.get('selftext', '').strip()])
            link_posts = len([p for p in posts if not p.get('selftext', '').strip() and p.get('url')])
            
            # Extract keywords from titles
            all_titles = ' '.join([post.get('title', '') for post in posts])
            title_words = re.findall(r'\b\w+\b', all_titles.lower())
            title_word_freq = Counter([word for word in title_words if len(word) > 3])
            
            # Extract keywords from comments
            all_comments = []
            for post in posts:
                for comment in post.get('comments', []):
                    all_comments.append(comment.get('body', ''))
            
            comment_text = ' '.join(all_comments)
            comment_words = re.findall(r'\b\w+\b', comment_text.lower())
            comment_word_freq = Counter([word for word in comment_words if len(word) > 3])
            
            return {
                'text_metrics': {
                    'average_title_length': np.mean(title_lengths) if title_lengths else 0,
                    'average_selftext_length': np.mean(selftext_lengths) if selftext_lengths else 0,
                    'longest_title': max(title_lengths) if title_lengths else 0,
                    'longest_selftext': max(selftext_lengths) if selftext_lengths else 0
                },
                'content_types': {
                    'text_posts': text_posts,
                    'link_posts': link_posts,
                    'text_post_percentage': (text_posts / len(posts) * 100) if posts else 0
                },
                'keywords': {
                    'top_title_words': dict(title_word_freq.most_common(20)),
                    'top_comment_words': dict(comment_word_freq.most_common(20)),
                    'unique_title_words': len(title_word_freq),
                    'unique_comment_words': len(comment_word_freq)
                }
            }
        except Exception as e:
            logger.error(f"Error in _get_content_analytics: {e}")
            return {}
    
    def _get_subreddit_analytics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze subreddit distribution and characteristics"""
        try:
            subreddits = [post.get('subreddit', '') for post in posts]
            subreddit_counts = Counter(subreddits)
            
            # Subreddit sentiment analysis
            subreddit_sentiment = defaultdict(list)
            for post in posts:
                subreddit = post.get('subreddit', '')
                sentiment = post.get('overall_sentiment', 0)
                subreddit_sentiment[subreddit].append(sentiment)
            
            # Calculate average sentiment per subreddit
            subreddit_avg_sentiment = {}
            for subreddit, sentiments in subreddit_sentiment.items():
                subreddit_avg_sentiment[subreddit] = np.mean(sentiments)
            
            return {
                'subreddit_distribution': dict(subreddit_counts.most_common(20)),
                'total_subreddits': len(subreddit_counts),
                'top_subreddit': subreddit_counts.most_common(1)[0] if subreddit_counts else ('', 0),
                'subreddit_sentiment': dict(sorted(subreddit_avg_sentiment.items(), 
                                                 key=lambda x: x[1], reverse=True)[:10]),
                'most_positive_subreddit': max(subreddit_avg_sentiment.items(), 
                                             key=lambda x: x[1]) if subreddit_avg_sentiment else ('', 0),
                'most_negative_subreddit': min(subreddit_avg_sentiment.items(), 
                                             key=lambda x: x[1]) if subreddit_avg_sentiment else ('', 0)
            }
        except Exception as e:
            logger.error(f"Error in _get_subreddit_analytics: {e}")
            return {}
    
    def _get_user_behavior_analytics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        try:
            # Author analysis
            authors = [post.get('author', '') for post in posts]
            author_counts = Counter([a for a in authors if a and a != 'Unknown'])
            
            # Comment author analysis
            comment_authors = []
            for post in posts:
                for comment in post.get('comments', []):
                    author = comment.get('author', '')
                    if author and author != 'Unknown':
                        comment_authors.append(author)
            
            comment_author_counts = Counter(comment_authors)
            
            # User engagement patterns
            user_engagement = defaultdict(list)
            for post in posts:
                author = post.get('author', '')
                if author and author != 'Unknown':
                    user_engagement[author].append(post.get('engagement_score', 0))
            
            return {
                'active_users': {
                    'total_post_authors': len(author_counts),
                    'total_comment_authors': len(comment_author_counts),
                    'top_posters': dict(author_counts.most_common(10)),
                    'top_commenters': dict(comment_author_counts.most_common(10))
                },
                'user_participation': {
                    'users_with_multiple_posts': len([k for k, v in author_counts.items() if v > 1]),
                    'average_posts_per_user': np.mean(list(author_counts.values())) if author_counts else 0,
                    'most_active_poster': author_counts.most_common(1)[0] if author_counts else ('', 0)
                }
            }
        except Exception as e:
            logger.error(f"Error in _get_user_behavior_analytics: {e}")
            return {}
    
    async def _get_topic_modeling(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform basic topic modeling and keyword extraction"""
        try:
            # Combine all text content
            all_text = []
            for post in posts:
                title = post.get('title', '')
                selftext = post.get('selftext', '')
                all_text.append(f"{title} {selftext}")
            
            # Simple keyword extraction using word frequency
            combined_text = ' '.join(all_text)
            words = re.findall(r'\b[a-zA-Z]{4,}\b', combined_text.lower())
            
            # Filter out common stop words
            stop_words = {'that', 'this', 'with', 'have', 'will', 'from', 'they', 'been', 
                         'were', 'said', 'each', 'which', 'their', 'time', 'more', 'very',
                         'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also',
                         'make', 'only', 'come', 'could', 'other', 'after', 'would', 'when'}
            
            filtered_words = [word for word in words if word not in stop_words]
            word_freq = Counter(filtered_words)
            
            # Extract potential topics (most frequent meaningful words)
            topics = word_freq.most_common(20)
            
            return {
                'top_keywords': dict(topics),
                'total_unique_words': len(word_freq),
                'most_common_word': topics[0] if topics else ('', 0),
                'word_diversity': len(word_freq) / len(words) if words else 0
            }
        except Exception as e:
            logger.error(f"Error in _get_topic_modeling: {e}")
            return {}
    
    def _get_correlation_analysis(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlations between different metrics"""
        try:
            if len(posts) < 2:
                return {}
            
            # Extract metrics for correlation analysis
            data = []
            for post in posts:
                data.append({
                    'score': post.get('score', 0),
                    'sentiment': post.get('overall_sentiment', 0),
                    'engagement': post.get('engagement_score', 0),
                    'num_comments': len(post.get('comments', [])),
                    'upvote_ratio': post.get('upvote_ratio', 0.5),
                    'title_length': len(post.get('title', '')),
                    'selftext_length': len(post.get('selftext', ''))
                })
            
            df = pd.DataFrame(data)
            
            # Calculate correlations
            correlations = {}
            try:
                correlations['sentiment_score'] = np.corrcoef([d['sentiment'] for d in data], 
                                                            [d['score'] for d in data])[0, 1]
                correlations['sentiment_engagement'] = np.corrcoef([d['sentiment'] for d in data], 
                                                                  [d['engagement'] for d in data])[0, 1]
                correlations['score_comments'] = np.corrcoef([d['score'] for d in data], 
                                                           [d['num_comments'] for d in data])[0, 1]
                correlations['engagement_comments'] = np.corrcoef([d['engagement'] for d in data], 
                                                                [d['num_comments'] for d in data])[0, 1]
            except:
                correlations = {}
            
            return {
                'correlations': correlations,
                'strongest_positive_correlation': max(correlations.items(), key=lambda x: x[1]) if correlations else ('', 0),
                'strongest_negative_correlation': min(correlations.items(), key=lambda x: x[1]) if correlations else ('', 0)
            }
        except Exception as e:
            logger.error(f"Error in _get_correlation_analysis: {e}")
            return {}
    
    def _get_trend_analysis(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends over time"""
        try:
            # Sort posts by time
            time_sorted_posts = sorted(posts, key=lambda x: x.get('created_utc', 0))
            
            if len(time_sorted_posts) < 3:
                return {}
            
            # Calculate rolling averages
            window_size = min(10, len(time_sorted_posts) // 3)
            sentiments = [post.get('overall_sentiment', 0) for post in time_sorted_posts]
            
            # Simple trend calculation
            first_half_sentiment = np.mean(sentiments[:len(sentiments)//2])
            second_half_sentiment = np.mean(sentiments[len(sentiments)//2:])
            
            sentiment_trend = "increasing" if second_half_sentiment > first_half_sentiment else "decreasing"
            
            return {
                'sentiment_trend': sentiment_trend,
                'sentiment_change': second_half_sentiment - first_half_sentiment,
                'trend_strength': abs(second_half_sentiment - first_half_sentiment),
                'data_points': len(time_sorted_posts)
            }
        except Exception as e:
            logger.error(f"Error in _get_trend_analysis: {e}")
            return {}
    
    def _generate_visualization_data(self, posts: List[Dict[str, Any]], analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data structures for frontend visualizations"""
        try:
            viz_data = {}
            
            # Sentiment over time data
            time_sentiment_data = []
            for post in sorted(posts, key=lambda x: x.get('created_utc', 0)):
                try:
                    timestamp = datetime.utcfromtimestamp(post.get('created_utc', 0))
                    time_sentiment_data.append({
                        'date': timestamp.isoformat(),
                        'sentiment': post.get('overall_sentiment', 0),
                        'title': post.get('title', '')[:50] + '...'
                    })
                except:
                    continue
            
            viz_data['sentiment_timeline'] = time_sentiment_data
            
            # Subreddit sentiment distribution
            subreddit_data = []
            subreddit_sentiment = analytics.get('subreddit_analysis', {}).get('subreddit_sentiment', {})
            for subreddit, sentiment in list(subreddit_sentiment.items())[:10]:
                subreddit_data.append({
                    'subreddit': subreddit,
                    'sentiment': sentiment,
                    'post_count': len([p for p in posts if p.get('subreddit') == subreddit])
                })
            
            viz_data['subreddit_sentiment'] = subreddit_data
            
            # Engagement vs sentiment scatter plot data
            scatter_data = []
            for post in posts:
                scatter_data.append({
                    'x': post.get('engagement_score', 0),
                    'y': post.get('overall_sentiment', 0),
                    'size': min(post.get('score', 0) / 10, 100),
                    'title': post.get('title', '')[:50] + '...',
                    'subreddit': post.get('subreddit', '')
                })
            
            viz_data['engagement_sentiment_scatter'] = scatter_data
            
            # Hourly activity heatmap data
            hourly_data = analytics.get('temporal_analysis', {}).get('posting_patterns', {}).get('hourly_distribution', {})
            viz_data['hourly_activity'] = [{'hour': k, 'count': v} for k, v in hourly_data.items()]
            
            return viz_data
            
        except Exception as e:
            logger.error(f"Error generating visualization data: {e}")
            return {}