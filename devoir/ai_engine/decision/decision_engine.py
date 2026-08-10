"""
Decision Engine

Reference: docs/scientific_engine/08_DecisionEngine.md
A. Bourke et al. - Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm (2010)
"""

from typing import Tuple, Optional


class DecisionEngine:
    """
    Makes final decision on fall detection using multi-criteria fusion.
    
    Reference: A. Bourke et al. (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
    """
    
    def __init__(self, threshold_severity: float = 0.7,
                 weights: Tuple[float, float, float, float, float] = None):
        """
        Initialize the decision engine.
        
        Args:
            threshold_severity: Severity threshold for fall confirmation
            weights: Weights for (angle, speed, acceleration, immobility, floor_time)
        """
        self.threshold_severity = threshold_severity
        
        if weights is None:
            weights = (0.20, 0.25, 0.20, 0.15, 0.20)
        
        self.weights = weights
    
    def make_decision(self, angle_indicator: float, speed_indicator: float,
                     acceleration_indicator: float, immobility_indicator: float,
                     floor_time_indicator: float) -> dict:
        """
        Make final decision on fall detection.
        
        Reference: A. Bourke et al. (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
        
        Args:
            angle_indicator: Angle indicator [0, 1]
            speed_indicator: Speed indicator [0, 1]
            acceleration_indicator: Acceleration indicator [0, 1]
            immobility_indicator: Immobility indicator [0, 1]
            floor_time_indicator: Floor time indicator [0, 1]
        
        Returns:
            Dictionary with decision results
        """
        # Calculate fall score using weighted fusion
        fall_score = self._calculate_fall_score(
            angle_indicator, speed_indicator, acceleration_indicator,
            immobility_indicator, floor_time_indicator
        )
        
        # Determine decision class
        decision_class = self._classify_decision(fall_score)
        
        # Determine alert level
        alert_level = self._determine_alert_level(fall_score)
        
        return {
            'fall_score': fall_score,
            'decision_class': decision_class,
            'alert_level': alert_level,
            'is_fall': fall_score >= self.threshold_severity
        }
    
    def _calculate_fall_score(self, angle: float, speed: float, acceleration: float,
                            immobility: float, floor_time: float) -> float:
        """
        Calculate fall score using weighted fusion.
        
        Formula: S = w1*I1 + w2*I2 + w3*I3 + w4*I4 + w5*I5
        
        Reference: A. Bourke et al. (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
        
        Args:
            angle, speed, acceleration, immobility, floor_time: Indicators [0, 1]
        
        Returns:
            Fall score [0, 1]
        """
        w1, w2, w3, w4, w5 = self.weights
        
        score = (w1 * angle + w2 * speed + w3 * acceleration +
                w4 * immobility + w5 * floor_time)
        
        return max(0.0, min(1.0, score))
    
    def _classify_decision(self, score: float) -> str:
        """
        Classify decision based on score.
        
        Reference: G. M. Weiss et al. (2012) - DOI: 10.1186/1475-925X-11-115
        
        Args:
            score: Fall score [0, 1]
        
        Returns:
            Decision class
        """
        if score < 0.5:
            return 'PAS_CHUTE'
        elif score < 0.7:
            return 'INDETERMINE'
        else:
            return 'CHUTE_CONFIRMEE'
    
    def _determine_alert_level(self, score: float) -> str:
        """
        Determine alert level based on score.
        
        Reference: J. Fleming et al. (2008) - DOI: 10.1191/0269215508pm920oa
        
        Args:
            score: Fall score [0, 1]
        
        Returns:
            Alert level
        """
        if score < 0.5:
            return 'AUCUNE'
        elif score < 0.7:
            return 'BASSE'
        elif score < 0.8:
            return 'MOYENNE'
        elif score < 0.9:
            return 'HAUTE'
        else:
            return 'CRITIQUE'
    
    def apply_special_rules(self, trunk_angle: float, vertical_speed: float,
                          immobility_duration: float, floor_time: float) -> Optional[str]:
        """
        Apply special decision rules.
        
        Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
        
        Args:
            trunk_angle: Trunk angle in degrees
            vertical_speed: Vertical speed in m/s
            immobility_duration: Immobility duration in seconds
            floor_time: Floor time in seconds
        
        Returns:
            Special rule result or None
        """
        # Rule 1: Rapid fall
        if abs(vertical_speed) > 3.0 and trunk_angle > 60.0:
            return 'CHUTE_IMMEDIATE'
        
        # Rule 2: Prolonged immobility
        if immobility_duration >= 60.0:
            return 'ALERTE_URGENCE'
        
        # Rule 3: Critical floor time
        if floor_time >= 120.0:
            return 'ALERTE_CRITIQUE'
        
        # Rule 4: False positive - normal movement
        if abs(vertical_speed) < 0.5 and trunk_angle < 30.0:
            return 'MOUVEMENT_NORMAL'
        
        return None


class AlertEscalation:
    """
    Manages alert escalation based on response time.
    
    Reference: J. Fleming et al. (2008) - DOI: 10.1191/0269215508pm920oa
    """
    
    def __init__(self):
        """Initialize the alert escalation manager."""
        self.escalation_levels = ['BASSE', 'MOYENNE', 'HAUTE', 'CRITIQUE']
        self.escalation_delays = {
            'CRITIQUE': 300,  # 5 minutes
            'HAUTE': 600,     # 10 minutes
            'MOYENNE': 1800   # 30 minutes
        }
    
    def should_escalate(self, current_level: str, time_since_alert: float,
                        acknowledged: bool) -> bool:
        """
        Determine if alert should be escalated.
        
        Reference: J. Fleming et al. (2008) - DOI: 10.1191/0269215508pm920oa
        
        Args:
            current_level: Current alert level
            time_since_alert: Time since alert was sent in seconds
            acknowledged: Whether alert has been acknowledged
        
        Returns:
            True if alert should be escalated
        """
        if acknowledged:
            return False
        
        if current_level not in self.escalation_delays:
            return False
        
        return time_since_alert >= self.escalation_delays[current_level]
    
    def escalate(self, current_level: str) -> str:
        """
        Escalate alert to next level.
        
        Args:
            current_level: Current alert level
        
        Returns:
            Escalated alert level
        """
        try:
            current_index = self.escalation_levels.index(current_level)
            if current_index < len(self.escalation_levels) - 1:
                return self.escalation_levels[current_index + 1]
        except ValueError:
            pass
        
        return current_level
