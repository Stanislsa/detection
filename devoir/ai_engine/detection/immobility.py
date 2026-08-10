"""
Immobility Detector

Reference: docs/scientific_engine/07_FallDetectionLogic.md
S. R. Lord et al. - Physiological risk factors for falls in older people (2001)
"""

from typing import List, Optional
import time


class ImmobilityDetector:
    """
    Detects prolonged immobility after a fall.
    
    Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
    """
    
    def __init__(self, threshold_time: float = 30.0, velocity_threshold: float = 0.1):
        """
        Initialize the immobility detector.
        
        Args:
            threshold_time: Immobility threshold in seconds (default 30)
            velocity_threshold: Velocity threshold for immobility in m/s (default 0.1)
        """
        self.threshold_time = threshold_time
        self.velocity_threshold = velocity_threshold
        
        self.immobility_start_time = None
        self.is_immobile = False
        self.immobility_duration = 0.0
    
    def update(self, velocity: float, timestamp: float = None) -> dict:
        """
        Update immobility detection with current velocity.
        
        Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
        
        Args:
            velocity: Current velocity magnitude in m/s
            timestamp: Current timestamp
        
        Returns:
            Dictionary with immobility status
        """
        if timestamp is None:
            timestamp = time.time()
        
        is_currently_immobile = abs(velocity) < self.velocity_threshold
        
        if is_currently_immobile:
            if self.immobility_start_time is None:
                self.immobility_start_time = timestamp
            else:
                self.immobility_duration = timestamp - self.immobility_start_time
            
            if self.immobility_duration >= self.threshold_time:
                self.is_immobile = True
        else:
            # Movement detected, reset immobility
            self.immobility_start_time = None
            self.immobility_duration = 0.0
            self.is_immobile = False
        
        return {
            'is_immobile': self.is_immobile,
            'immobility_duration': self.immobility_duration,
            'threshold_exceeded': self.immobility_duration >= self.threshold_time,
            'timestamp': timestamp
        }
    
    def check_prolonged_immobility(self, duration: float = 60.0) -> bool:
        """
        Check if immobility is prolonged (critical condition).
        
        Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
        
        Args:
            duration: Critical duration threshold in seconds (default 60)
        
        Returns:
            True if immobility is prolonged
        """
        return self.immobility_duration >= duration
    
    def reset(self):
        """Reset immobility detection state."""
        self.immobility_start_time = None
        self.is_immobile = False
        self.immobility_duration = 0.0


class FloorTimeTracker:
    """
    Tracks time spent on the floor after a fall.
    
    Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
    """
    
    def __init__(self, critical_time: float = 60.0):
        """
        Initialize the floor time tracker.
        
        Args:
            critical_time: Critical time threshold in seconds (default 60)
        """
        self.critical_time = critical_time
        self.floor_start_time = None
        self.floor_duration = 0.0
        self.on_floor = False
    
    def start_tracking(self, timestamp: float = None):
        """
        Start tracking floor time.
        
        Args:
            timestamp: Start timestamp
        """
        if timestamp is None:
            timestamp = time.time()
        self.floor_start_time = timestamp
        self.on_floor = True
    
    def update(self, timestamp: float = None) -> dict:
        """
        Update floor time tracking.
        
        Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
        
        Args:
            timestamp: Current timestamp
        
        Returns:
            Dictionary with floor time status
        """
        if timestamp is None:
            timestamp = time.time()
        
        if self.on_floor and self.floor_start_time is not None:
            self.floor_duration = timestamp - self.floor_start_time
        
        return {
            'on_floor': self.on_floor,
            'floor_duration': self.floor_duration,
            'critical_exceeded': self.floor_duration >= self.critical_time,
            'timestamp': timestamp
        }
    
    def stop_tracking(self):
        """Stop tracking floor time."""
        self.on_floor = False
    
    def reset(self):
        """Reset floor time tracking state."""
        self.floor_start_time = None
        self.floor_duration = 0.0
        self.on_floor = False
