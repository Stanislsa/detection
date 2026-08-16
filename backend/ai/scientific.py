"""
Scientific AI engine with biomechanics, physics, and decision analysis.
Integrates devoir AI engine components.
"""

import numpy as np
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.core.constants import GRAVITY, BODY_SEGMENT_MASS, PROFILE_CONFIG
from backend.core.exceptions import DetectionException

logger = get_logger(__name__)


class BiomechanicsEngine:
    """
    Biomechanical analysis engine for human movement.
    
    Analyzes joint angles, segment velocities, and movement patterns.
    """
    
    def __init__(self):
        """Initialize biomechanics engine."""
        self._logger = get_logger(self.__class__.__name__)
    
    def calculate_joint_angle(
        self,
        point_a: Tuple[float, float],
        point_b: Tuple[float, float],
        point_c: Tuple[float, float]
    ) -> float:
        """
        Calculate angle at point_b formed by points a-b-c.
        
        Args:
            point_a: First point (x, y)
            point_b: Vertex point (x, y)
            point_c: Third point (x, y)
        
        Returns:
            Angle in degrees
        """
        try:
            # Vector BA
            ba = np.array([point_a[0] - point_b[0], point_a[1] - point_b[1]])
            # Vector BC
            bc = np.array([point_c[0] - point_b[0], point_c[1] - point_b[1]])
            
            # Calculate angle
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            
            return np.degrees(angle)
            
        except Exception as e:
            self._logger.error(f"Failed to calculate joint angle: {e}")
            return 0.0
    
    def calculate_angular_velocity(
        self,
        angle_history: List[float],
        time_delta: float
    ) -> float:
        """
        Calculate angular velocity from angle history.
        
        Args:
            angle_history: List of angles over time
            time_delta: Time between measurements (seconds)
        
        Returns:
            Angular velocity in degrees/second
        """
        if len(angle_history) < 2:
            return 0.0
        
        try:
            angle_change = angle_history[-1] - angle_history[-2]
            return angle_change / time_delta
        except Exception:
            return 0.0
    
    def calculate_center_of_mass(
        self,
        landmarks: List[Dict[str, float]]
    ) -> Tuple[float, float]:
        """
        Calculate body center of mass using anthropometric model.
        
        Args:
            landmarks: MediaPipe landmarks
        
        Returns:
            Center of mass coordinates (x, y)
        """
        try:
            total_mass = 0.0
            weighted_x = 0.0
            weighted_y = 0.0
            
            for landmark_id, mass_ratio in BODY_SEGMENT_MASS.items():
                if landmark_id < len(landmarks):
                    landmark = landmarks[landmark_id]
                    weighted_x += landmark["x"] * mass_ratio
                    weighted_y += landmark["y"] * mass_ratio
                    total_mass += mass_ratio
            
            if total_mass > 0:
                return (weighted_x / total_mass, weighted_y / total_mass)
            
            return (0.0, 0.0)
            
        except Exception as e:
            self._logger.error(f"Failed to calculate center of mass: {e}")
            return (0.0, 0.0)
    
    def analyze_posture_stability(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Analyze posture stability.
        
        Args:
            landmarks: MediaPipe landmarks
        
        Returns:
            Stability analysis results
        """
        try:
            # Calculate support base (foot positions)
            left_foot = landmarks[27] if len(landmarks) > 27 else None
            right_foot = landmarks[28] if len(landmarks) > 28 else None
            
            # Calculate center of mass
            com = self.calculate_center_of_mass(landmarks)
            
            # Calculate trunk angle
            trunk_angle = self.calculate_joint_angle(
                (landmarks[11]["x"], landmarks[11]["y"]),
                (landmarks[23]["x"], landmarks[23]["y"]),
                (landmarks[24]["x"], landmarks[24]["y"])
            )
            
            return {
                "center_of_mass": com,
                "trunk_angle": trunk_angle,
                "stability_score": self._calculate_stability_score(trunk_angle, com),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self._logger.error(f"Failed to analyze posture stability: {e}")
            return {}


class PhysicsEngine:
    """
    Physics engine for fall dynamics analysis.
    
    Calculates impact forces, velocities, and energy.
    """
    
    def __init__(self):
        """Initialize physics engine."""
        self._logger = get_logger(self.__class__.__name__)
    
    def calculate_impact_velocity(
        self,
        height: float,
        mass: float = 70.0
    ) -> float:
        """
        Calculate impact velocity from fall height.
        
        Args:
            height: Fall height in meters
            mass: Body mass in kg
        
        Returns:
            Impact velocity in m/s
        """
        try:
            # v = sqrt(2 * g * h)
            velocity = math.sqrt(2 * GRAVITY * height)
            return velocity
        except Exception:
            return 0.0
    
    def calculate_impact_force(
        self,
        velocity: float,
        mass: float = 70.0,
        impact_time: float = 0.1
    ) -> float:
        """
        Calculate impact force.
        
        Args:
            velocity: Impact velocity in m/s
            mass: Body mass in kg
            impact_time: Impact duration in seconds
        
        Returns:
            Impact force in Newtons
        """
        try:
            # F = m * (v / t)
            force = mass * (velocity / impact_time)
            return force
        except Exception:
            return 0.0
    
    def calculate_kinetic_energy(
        self,
        velocity: float,
        mass: float = 70.0
    ) -> float:
        """
        Calculate kinetic energy.
        
        Args:
            velocity: Velocity in m/s
            mass: Mass in kg
        
        Returns:
            Kinetic energy in Joules
        """
        try:
            # KE = 0.5 * m * v^2
            energy = 0.5 * mass * velocity ** 2
            return energy
        except Exception:
            return 0.0
    
    def calculate_deceleration(
        self,
        initial_velocity: float,
        final_velocity: float,
        distance: float
    ) -> float:
        """
        Calculate deceleration.
        
        Args:
            initial_velocity: Initial velocity in m/s
            final_velocity: Final velocity in m/s
            distance: Stopping distance in meters
        
        Returns:
            Deceleration in m/s²
        """
        try:
            # a = (v^2 - u^2) / (2 * s)
            deceleration = (final_velocity ** 2 - initial_velocity ** 2) / (2 * distance)
            return abs(deceleration)
        except Exception:
            return 0.0
    
    def analyze_fall_dynamics(
        self,
        vertical_velocity: float,
        trunk_angle: float,
        mass: float = 70.0,
        height: float = 1.7
    ) -> Dict[str, Any]:
        """
        Analyze fall dynamics.
        
        Args:
            vertical_velocity: Vertical velocity in m/s
            trunk_angle: Trunk angle in degrees
            mass: Body mass in kg
            height: Body height in meters
        
        Returns:
            Fall dynamics analysis
        """
        try:
            # Calculate impact parameters
            impact_velocity = self.calculate_impact_velocity(height * 0.5, mass)
            impact_force = self.calculate_impact_force(impact_velocity, mass)
            kinetic_energy = self.calculate_kinetic_energy(impact_velocity, mass)
            
            # Calculate g-force
            g_force = impact_force / (mass * GRAVITY)
            
            return {
                "impact_velocity": impact_velocity,
                "impact_force": impact_force,
                "kinetic_energy": kinetic_energy,
                "g_force": g_force,
                "trunk_angle": trunk_angle,
                "vertical_velocity": vertical_velocity,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self._logger.error(f"Failed to analyze fall dynamics: {e}")
            return {}


class DecisionEngine:
    """
    Decision engine for fall detection and severity assessment.
    
    Combines multiple indicators to make intelligent decisions.
    """
    
    def __init__(self):
        """Initialize decision engine."""
        self._logger = get_logger(self.__class__.__name__)
        self.biomechanics = BiomechanicsEngine()
        self.physics = PhysicsEngine()
    
    def assess_fall_severity(
        self,
        biomechanics_data: Dict[str, Any],
        physics_data: Dict[str, Any],
        person_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Assess fall severity using multi-factor analysis.
        
        Args:
            biomechanics_data: Biomechanics analysis results
            physics_data: Physics analysis results
            person_profile: Person profile for adaptive thresholds
        
        Returns:
            Severity assessment
        """
        try:
            # Get profile-specific weights
            if person_profile:
                profile_type = person_profile.get("profile_type", "senior_autonome")
                weights = PROFILE_CONFIG.get(profile_type, {}).get(
                    "gravity_time_weights",
                    {"intensity": 0.30, "time_on_ground": 0.35, 
                     "injury_probability": 0.15, "reactivity": 0.20}
                )
            else:
                weights = {
                    "intensity": 0.30,
                    "time_on_ground": 0.35,
                    "injury_probability": 0.15,
                    "reactivity": 0.20
                }
            
            # Extract indicators
            g_force = physics_data.get("g_force", 0.0)
            trunk_angle = biomechanics_data.get("trunk_angle", 0.0)
            stability_score = biomechanics_data.get("stability_score", 0.0)
            kinetic_energy = physics_data.get("kinetic_energy", 0.0)
            
            # Normalize indicators (0-1 scale)
            intensity_score = min(g_force / 10.0, 1.0)  # Normalize to 10g
            angle_score = min(trunk_angle / 90.0, 1.0)
            stability_score = 1.0 - stability_score  # Invert: lower stability = higher risk
            energy_score = min(kinetic_energy / 500.0, 1.0)  # Normalize to 500J
            
            # Calculate weighted severity score
            severity_score = (
                weights.get("intensity", 0.30) * intensity_score +
                weights.get("reactivity", 0.20) * angle_score +
                weights.get("injury_probability", 0.15) * stability_score +
                weights.get("time_on_ground", 0.35) * energy_score
            )
            
            # Determine gravity level
            from backend.core.constants import GravityLevel, GRAVITY_LEVEL_RANGES
            
            gravity_level = GravityLevel.FAIBLE
            for level, (min_score, max_score) in GRAVITY_LEVEL_RANGES.items():
                if min_score <= severity_score * 100 <= max_score:
                    gravity_level = level
                    break
            
            return {
                "severity_score": severity_score * 100,  # 0-100 scale
                "gravity_level": gravity_level,
                "indicators": {
                    "intensity": intensity_score * 100,
                    "angle": angle_score * 100,
                    "stability": stability_score * 100,
                    "energy": energy_score * 100
                },
                "weights": weights,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self._logger.error(f"Failed to assess fall severity: {e}")
            return {
                "severity_score": 0.0,
                "gravity_level": "faible",
                "error": str(e)
            }
    
    def make_fall_decision(
        self,
        detection_confidence: float,
        biomechanics_data: Dict[str, Any],
        physics_data: Dict[str, Any],
        person_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make final fall detection decision.
        
        Args:
            detection_confidence: Detection confidence from AI model
            biomechanics_data: Biomechanics analysis
            physics_data: Physics analysis
            person_profile: Person profile
        
        Returns:
            Final decision with confidence
        """
        try:
            # Assess severity
            severity_assessment = self.assess_fall_severity(
                biomechanics_data, physics_data, person_profile
            )
            
            # Combine detection confidence with severity
            combined_confidence = (
                0.6 * detection_confidence +
                0.4 * (severity_assessment["severity_score"] / 100.0)
            )
            
            # Get profile-specific threshold
            if person_profile:
                threshold = person_profile.get("velocity_threshold", -2.5)
            else:
                threshold = -2.5
            
            # Make decision
            fall_detected = combined_confidence > 0.75
            
            return {
                "fall_detected": fall_detected,
                "confidence": combined_confidence,
                "severity": severity_assessment,
                "decision_threshold": 0.75,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self._logger.error(f"Failed to make fall decision: {e}")
            return {
                "fall_detected": False,
                "confidence": 0.0,
                "error": str(e)
            }


class ScientificEngine:
    """
    Unified scientific AI engine combining biomechanics, physics, and decision analysis.
    
    Integrates devoir AI engine components into unified architecture.
    """
    
    def __init__(self):
        """Initialize scientific engine."""
        self._logger = get_logger(self.__class__.__name__)
        self.biomechanics = BiomechanicsEngine()
        self.physics = PhysicsEngine()
        self.decision = DecisionEngine()
    
    def analyze_fall(
        self,
        landmarks: List[Dict[str, float]],
        vertical_velocity: float,
        person_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive fall analysis.
        
        Args:
            landmarks: MediaPipe pose landmarks
            vertical_velocity: Vertical velocity in m/s
            person_profile: Person profile
        
        Returns:
            Comprehensive fall analysis
        """
        try:
            # Biomechanics analysis
            biomechanics_data = self.biomechanics.analyze_posture_stability(landmarks)
            
            # Physics analysis
            physics_data = self.physics.analyze_fall_dynamics(
                vertical_velocity,
                biomechanics_data.get("trunk_angle", 0.0),
                person_profile.get("weight", 70.0) if person_profile else 70.0,
                person_profile.get("height", 1.7) if person_profile else 1.7
            )
            
            # Decision analysis
            decision_data = self.decision.make_fall_decision(
                detection_confidence=0.8,  # Placeholder, should come from detector
                biomechanics_data=biomechanics_data,
                physics_data=physics_data,
                person_profile=person_profile
            )
            
            return {
                "biomechanics": biomechanics_data,
                "physics": physics_data,
                "decision": decision_data,
                "analysis_method": "scientific_engine"
            }
            
        except Exception as e:
            self._logger.error(f"Failed to analyze fall: {e}")
            return {"error": str(e)}
