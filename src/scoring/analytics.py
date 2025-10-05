"""
Unsubscribe Result Analytics for Email Unsubscriber.

This module provides analytics and reporting on unsubscribe attempts,
strategy effectiveness, and failure patterns to help improve the system
and provide insights to users.
"""
import csv
from collections import Counter, defaultdict
from typing import Dict, List, Optional
import logging
from datetime import datetime

from src.database.db_manager import DBManager


class UnsubscribeAnalytics:
    """
    Analytics for unsubscribe operations.
    
    Provides insights into:
    - Overall success/failure rates
    - Strategy effectiveness
    - Common failure patterns
    - Problem senders
    """
    
    def __init__(self, db_manager: DBManager):
        """
        Initialize analytics.
        
        Args:
            db_manager: DBManager instance for data access
        """
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive analytics report.
        
        Returns:
            Dictionary with analytics data:
                - total_attempts: Total unsubscribe attempts
                - successful: Number of successful attempts
                - failed: Number of failed attempts
                - success_rate: Success percentage
                - strategy_stats: Per-strategy statistics
                - top_failures: Most problematic senders
        """
        try:
            stats = self.db.get_strategy_stats()
            
            total = stats.get('total', 0)
            successful = stats.get('successful', 0)
            failed = stats.get('failed', 0)
            
            success_rate = (successful / total * 100) if total > 0 else 0
            
            report = {
                'total_attempts': total,
                'successful': successful,
                'failed': failed,
                'success_rate': success_rate,
                'strategy_stats': stats.get('by_strategy', {}),
                'top_failures': self.get_top_failures(limit=10),
                'failure_reasons': self.db.get_failure_reasons()
            }
            
            self.logger.info(f"Generated analytics report: {successful}/{total} successful ({success_rate:.1f}%)")
            return report
        
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return {
                'total_attempts': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0,
                'strategy_stats': {},
                'top_failures': [],
                'failure_reasons': []
            }
    
    def get_top_failures(self, limit: int = 10) -> List[Dict]:
        """
        Get senders with most failed unsubscribe attempts.
        
        Args:
            limit: Maximum number of results
        
        Returns:
            List of dictionaries with sender and failure count
        """
        try:
            actions = self.db.get_action_history()
            
            # Count failures per sender
            failures = defaultdict(int)
            failure_reasons = defaultdict(list)
            
            for action in actions:
                if action.get('action_type') == 'unsubscribe' and not action.get('success'):
                    sender = action.get('sender_email', 'unknown')
                    failures[sender] += 1
                    details = action.get('details', '')
                    if details:
                        failure_reasons[sender].append(details)
            
            # Sort by failure count
            top_failures = [
                {
                    'sender': sender,
                    'failure_count': count,
                    'reasons': failure_reasons[sender][:3]  # Top 3 reasons
                }
                for sender, count in sorted(failures.items(), 
                                           key=lambda x: x[1], 
                                           reverse=True)[:limit]
            ]
            
            return top_failures
        
        except Exception as e:
            self.logger.error(f"Error getting top failures: {e}")
            return []
    
    def get_strategy_effectiveness(self) -> Dict[str, float]:
        """
        Calculate win rate for each unsubscribe strategy.
        
        Returns:
            Dictionary mapping strategy name to success rate (0-100)
        """
        try:
            stats = self.db.get_strategy_stats()
            by_strategy = stats.get('by_strategy', {})
            
            effectiveness = {}
            for strategy, counts in by_strategy.items():
                total = counts.get('total', 0)
                successful = counts.get('successful', 0)
                if total > 0:
                    effectiveness[strategy] = (successful / total * 100)
                else:
                    effectiveness[strategy] = 0
            
            return effectiveness
        
        except Exception as e:
            self.logger.error(f"Error calculating strategy effectiveness: {e}")
            return {}
    
    def export_to_csv(self, filepath: str) -> bool:
        """
        Export analytics to CSV file.
        
        Args:
            filepath: Path to output CSV file
        
        Returns:
            True if export successful, False otherwise
        """
        try:
            report = self.generate_report()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Summary section
                writer.writerow(['Email Unsubscriber Analytics Report'])
                writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])
                
                # Overall stats
                writer.writerow(['Overall Statistics'])
                writer.writerow(['Total Attempts', report['total_attempts']])
                writer.writerow(['Successful', report['successful']])
                writer.writerow(['Failed', report['failed']])
                writer.writerow(['Success Rate', f"{report['success_rate']:.1f}%"])
                writer.writerow([])
                
                # Strategy effectiveness
                writer.writerow(['Strategy Effectiveness'])
                writer.writerow(['Strategy', 'Total', 'Successful', 'Failed', 'Success Rate'])
                for strategy, counts in report['strategy_stats'].items():
                    total = counts.get('total', 0)
                    successful = counts.get('successful', 0)
                    failed = counts.get('failed', 0)
                    rate = (successful / total * 100) if total > 0 else 0
                    writer.writerow([strategy, total, successful, failed, f"{rate:.1f}%"])
                writer.writerow([])
                
                # Top failures
                writer.writerow(['Top Failed Senders'])
                writer.writerow(['Sender', 'Failure Count', 'Recent Reasons'])
                for failure in report['top_failures']:
                    reasons = '; '.join(failure['reasons'][:2])  # Top 2 reasons
                    writer.writerow([
                        failure['sender'],
                        failure['failure_count'],
                        reasons
                    ])
                writer.writerow([])
                
                # Failure reasons summary
                writer.writerow(['Common Failure Reasons'])
                writer.writerow(['Reason', 'Count'])
                for reason in report['failure_reasons']:
                    writer.writerow([reason['reason'], reason['count']])
            
            self.logger.info(f"Analytics exported to {filepath}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting analytics: {e}")
            return False
    
    def get_success_rate(self) -> float:
        """
        Get overall unsubscribe success rate.
        
        Returns:
            Success rate as percentage (0-100)
        """
        try:
            stats = self.db.get_strategy_stats()
            total = stats.get('total', 0)
            successful = stats.get('successful', 0)
            return (successful / total * 100) if total > 0 else 0
        except Exception as e:
            self.logger.error(f"Error calculating success rate: {e}")
            return 0

