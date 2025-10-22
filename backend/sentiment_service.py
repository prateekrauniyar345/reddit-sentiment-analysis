"""
Sentiment Analysis Service with improved LLM integration
Supports batch processing for large-scale analysis
"""

import asyncio
import os
from typing import List, Dict, Any, Optional, Callable
from openai import OpenAI
import logging
import json
from concurrent.futures import ThreadPoolExecutor
import time
from textblob import TextBlob
import numpy as np

logger = logging.getLogger(__name__)

class SentimentService:
    def __init__(self):
        """Initialize sentiment analysis service"""
        self.client = OpenAI(
            base_url="https://api.studio.nebius.com/v1/",
            api_key=os.getenv("NEIBUS_API_KEY"),
        )
        self.max_batch_size = 10  # Comments per API call
        self.max_workers = 5  # Concurrent API calls
        self.request_delay = 1.0  # Delay between API calls to avoid rate limits
        
    async def analyze_posts_batch(
        self,
        posts_data: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple posts and their comments
        """
        logger.info(f"Starting sentiment analysis for {len(posts_data)} posts")
        
        analyzed_posts = []
        
        try:
            # Process posts in batches to manage API limits
            batch_size = 20
            
            for i in range(0, len(posts_data), batch_size):
                batch = posts_data[i:i + batch_size]
                
                # Process batch concurrently
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = []
                    
                    for post in batch:
                        future = executor.submit(self._analyze_single_post, post)
                        futures.append(future)
                    
                    # Collect results
                    batch_results = []
                    for future in futures:
                        try:
                            result = future.result(timeout=60)  # 60 second timeout
                            batch_results.append(result)
                        except Exception as e:
                            logger.error(f"Error analyzing post: {e}")
                            # Create fallback result
                            batch_results.append(self._create_fallback_result(batch[0]))
                
                analyzed_posts.extend(batch_results)
                
                # Update progress
                if progress_callback:
                    progress = min(int(((i + batch_size) / len(posts_data)) * 100), 100)
                    progress_callback(progress)
                
                # Rate limiting between batches
                if i + batch_size < len(posts_data):
                    await asyncio.sleep(2.0)
                    
        except Exception as e:
            logger.error(f"Error in analyze_posts_batch: {e}")
            raise
            
        logger.info(f"Completed sentiment analysis for {len(analyzed_posts)} posts")
        return analyzed_posts
    
    def _analyze_single_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment for a single post and its comments"""
        try:
            # Analyze post title and content
            post_text = f"{post_data.get('title', '')} {post_data.get('selftext', '')}"
            post_sentiment = self._get_text_sentiment(post_text)
            
            # Analyze comments in batches
            comments = post_data.get('comments', [])
            analyzed_comments = []
            
            if comments:
                # Process comments in smaller batches
                for i in range(0, len(comments), self.max_batch_size):
                    comment_batch = comments[i:i + self.max_batch_size]
                    
                    try:
                        # Get sentiment scores for this batch
                        sentiment_scores = self._get_batch_sentiment_scores(comment_batch)
                        
                        # Apply scores to comments
                        for j, comment in enumerate(comment_batch):
                            if j < len(sentiment_scores):
                                comment['sentiment_score'] = sentiment_scores[j]
                                comment['sentiment_label'] = self._score_to_label(sentiment_scores[j])
                            else:
                                # Fallback to TextBlob
                                fallback_score = self._textblob_sentiment(comment.get('body', ''))
                                comment['sentiment_score'] = fallback_score
                                comment['sentiment_label'] = self._score_to_label(fallback_score)
                            
                            analyzed_comments.append(comment)
                        
                        # Rate limiting between comment batches
                        time.sleep(self.request_delay)
                        
                    except Exception as e:
                        logger.warning(f"Error analyzing comment batch: {e}")
                        # Fallback to TextBlob for this batch
                        for comment in comment_batch:
                            fallback_score = self._textblob_sentiment(comment.get('body', ''))
                            comment['sentiment_score'] = fallback_score
                            comment['sentiment_label'] = self._score_to_label(fallback_score)
                            analyzed_comments.append(comment)
            
            # Calculate overall post sentiment
            if analyzed_comments:
                comment_scores = [c['sentiment_score'] for c in analyzed_comments]
                # Weighted average: post sentiment (30%) + average comment sentiment (70%)
                overall_sentiment = (post_sentiment * 0.3) + (np.mean(comment_scores) * 0.7)
            else:
                overall_sentiment = post_sentiment
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(post_data, analyzed_comments)
            
            # Create result
            result = {
                **post_data,
                'comments': analyzed_comments,
                'post_sentiment_score': post_sentiment,
                'post_sentiment_label': self._score_to_label(post_sentiment),
                'overall_sentiment': overall_sentiment,
                'sentiment_label': self._score_to_label(overall_sentiment),
                'engagement_score': engagement_score,
                'sentiment_distribution': self._get_sentiment_distribution(analyzed_comments)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing single post: {e}")
            return self._create_fallback_result(post_data)
    
    def _get_batch_sentiment_scores(self, comments: List[Dict[str, Any]]) -> List[float]:
        """Get sentiment scores for a batch of comments using LLM"""
        try:
            # Prepare comment texts
            comment_texts = [comment.get('body', '')[:500] for comment in comments]  # Limit length
            comment_texts = [text.strip().replace('\n', ' ') for text in comment_texts if text.strip()]
            
            if not comment_texts:
                return []
            
            # Create prompt for batch analysis
            combined_comments = '\n---\n'.join([f"Comment {i+1}: {text}" for i, text in enumerate(comment_texts)])
            
            prompt = (
                f"Analyze the sentiment of the following {len(comment_texts)} comments. "
                f"Rate each comment's sentiment on a scale from -1.0 to 1.0, where:\n"
                f"- -1.0 = extremely negative\n"
                f"- 0.0 = neutral\n"
                f"- 1.0 = extremely positive\n\n"
                f"Return ONLY a comma-separated list of numerical scores (no text, no explanations).\n"
                f"Example format: 0.8, -0.3, 0.1, 0.9\n\n"
                f"Comments to analyze:\n{combined_comments}\n\n"
                f"Sentiment scores:"
            )
            
            # Make API call
            completion = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            response_content = completion.choices[0].message.content.strip()
            
            # Parse response
            scores = []
            try:
                score_strings = response_content.split(',')
                for score_str in score_strings:
                    # Clean and convert to float
                    clean_score = score_str.strip().replace('"', '').replace("'", "")
                    score = float(clean_score)
                    # Clamp to valid range
                    score = max(-1.0, min(1.0, score))
                    scores.append(score)
            except ValueError as e:
                logger.warning(f"Error parsing sentiment scores: {e}, response: {response_content}")
                # Fallback to TextBlob
                return [self._textblob_sentiment(comment.get('body', '')) for comment in comments]
            
            # Ensure we have scores for all comments
            while len(scores) < len(comments):
                scores.append(0.0)  # Default to neutral
            
            return scores[:len(comments)]  # Return only needed scores
            
        except Exception as e:
            logger.error(f"Error in _get_batch_sentiment_scores: {e}")
            # Fallback to TextBlob sentiment
            return [self._textblob_sentiment(comment.get('body', '')) for comment in comments]
    
    def _get_text_sentiment(self, text: str) -> float:
        """Get sentiment for a single text using LLM with fallback"""
        try:
            if not text.strip():
                return 0.0
            
            prompt = (
                f"Analyze the sentiment of the following text and return a single numerical score "
                f"between -1.0 (extremely negative) and 1.0 (extremely positive). "
                f"Return ONLY the numerical score, no other text.\n\n"
                f"Text: {text[:1000]}\n\n"
                f"Sentiment score:"
            )
            
            completion = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=50
            )
            
            response = completion.choices[0].message.content.strip()
            score = float(response)
            return max(-1.0, min(1.0, score))  # Clamp to valid range
            
        except Exception as e:
            logger.warning(f"LLM sentiment analysis failed, using TextBlob fallback: {e}")
            return self._textblob_sentiment(text)
    
    def _textblob_sentiment(self, text: str) -> float:
        """Fallback sentiment analysis using TextBlob"""
        try:
            if not text.strip():
                return 0.0
            
            blob = TextBlob(text)
            # TextBlob returns polarity between -1 and 1
            return blob.sentiment.polarity
            
        except Exception as e:
            logger.error(f"TextBlob sentiment analysis failed: {e}")
            return 0.0
    
    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_engagement_score(self, post_data: Dict[str, Any], comments: List[Dict[str, Any]]) -> float:
        """Calculate engagement score based on various metrics"""
        try:
            post_score = post_data.get('score', 0)
            num_comments = len(comments)
            upvote_ratio = post_data.get('upvote_ratio', 0.5)
            
            # Normalize scores
            score_component = min(post_score / 1000, 1.0)  # Normalize to 0-1
            comment_component = min(num_comments / 100, 1.0)  # Normalize to 0-1
            ratio_component = upvote_ratio
            
            # Weighted average
            engagement = (score_component * 0.4) + (comment_component * 0.4) + (ratio_component * 0.2)
            
            return round(engagement, 3)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.0
    
    def _get_sentiment_distribution(self, comments: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of sentiment labels in comments"""
        distribution = {"positive": 0, "neutral": 0, "negative": 0}
        
        for comment in comments:
            label = comment.get('sentiment_label', 'neutral')
            if label in distribution:
                distribution[label] += 1
        
        return distribution
    
    def _create_fallback_result(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback result when analysis fails"""
        return {
            **post_data,
            'comments': post_data.get('comments', []),
            'post_sentiment_score': 0.0,
            'post_sentiment_label': 'neutral',
            'overall_sentiment': 0.0,
            'sentiment_label': 'neutral',
            'engagement_score': 0.0,
            'sentiment_distribution': {"positive": 0, "neutral": 0, "negative": 0}
        }
    
    async def get_sentiment_insights(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from sentiment analysis results"""
        try:
            if not posts:
                return {}
            
            # Calculate overall statistics
            all_sentiments = [post.get('overall_sentiment', 0) for post in posts]
            
            insights = {
                'total_posts': len(posts),
                'average_sentiment': np.mean(all_sentiments),
                'sentiment_std': np.std(all_sentiments),
                'positive_posts': len([s for s in all_sentiments if s > 0.3]),
                'negative_posts': len([s for s in all_sentiments if s < -0.3]),
                'neutral_posts': len([s for s in all_sentiments if -0.3 <= s <= 0.3]),
                'most_positive_post': max(posts, key=lambda x: x.get('overall_sentiment', 0)),
                'most_negative_post': min(posts, key=lambda x: x.get('overall_sentiment', 0)),
                'highest_engagement': max(posts, key=lambda x: x.get('engagement_score', 0))
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating sentiment insights: {e}")
            return {}