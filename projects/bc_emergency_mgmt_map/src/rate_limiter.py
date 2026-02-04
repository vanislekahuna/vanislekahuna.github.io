import time
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    """Rate limiter with daily caps and cost tracking"""
    
    def __init__(self, 
                 requests_per_second=10,
                 requests_per_day=1000,  # Set your daily limit
                 cost_per_request=0.005,  # $5 per 1000 requests
                 monthly_budget=200):     # Your max monthly spend
        
        self.requests_per_second = requests_per_second
        self.requests_per_day = requests_per_day
        self.cost_per_request = cost_per_request
        self.monthly_budget = monthly_budget
        
        self.last_request_time = 0
        self.daily_count = 0
        self.monthly_count = 0
        self.last_reset_day = datetime.now().date()
        self.last_reset_month = datetime.now().month
        
        # Track costs
        self.daily_cost = 0.0
        self.monthly_cost = 0.0
    
    def can_make_request(self):
        """Check if request is allowed"""
        now = datetime.now()
        
        # Reset daily counter
        if now.date() > self.last_reset_day:
            print(f"[RATE LIMITER] Daily reset - Previous: {self.daily_count} requests, ${self.daily_cost:.2f}")
            self.daily_count = 0
            self.daily_cost = 0.0
            self.last_reset_day = now.date()
        
        # Reset monthly counter
        if now.month != self.last_reset_month:
            print(f"[RATE LIMITER] Monthly reset - Previous: {self.monthly_count} requests, ${self.monthly_cost:.2f}")
            self.monthly_count = 0
            self.monthly_cost = 0.0
            self.last_reset_month = now.month
        
        # Check monthly budget
        if self.monthly_cost >= self.monthly_budget:
            print(f"[RATE LIMITER] BLOCKED - Monthly budget ${self.monthly_budget:.2f} exceeded (${self.monthly_cost:.2f})")
            return False
        
        # Check daily limit
        if self.daily_count >= self.requests_per_day:
            print(f"[RATE LIMITER] BLOCKED - Daily limit {self.requests_per_day} reached")
            return False
        
        # Check rate limit (requests per second)
        elapsed = time.time() - self.last_request_time
        if elapsed < (1.0 / self.requests_per_second):
            time.sleep((1.0 / self.requests_per_second) - elapsed)
        
        return True
    
    def record_request(self):
        """Record that a request was made"""
        self.last_request_time = time.time()
        self.daily_count += 1
        self.monthly_count += 1
        self.daily_cost += self.cost_per_request
        self.monthly_cost += self.cost_per_request
    
    def get_stats(self):
        """Get current usage stats"""
        return {
            'daily_requests': self.daily_count,
            'daily_cost': self.daily_cost,
            'monthly_requests': self.monthly_count,
            'monthly_cost': self.monthly_cost,
            'daily_remaining': self.requests_per_day - self.daily_count,
            'budget_remaining': self.monthly_budget - self.monthly_cost
        }


# Global rate limiter instance
_rate_limiter = RateLimiter(
    requests_per_second=10,      # Max 10 requests/second
    requests_per_day=500,         # Max 500 requests/day (adjust as needed)
    cost_per_request=0.005,       # $5 per 1000 = $0.005 each
    monthly_budget=50             # Max $50/month (well under $200 free tier)
)


def get_rate_limiter():
    """Get the global rate limiter instance"""
    return _rate_limiter