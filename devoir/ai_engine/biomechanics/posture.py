"""
Posture Analysis

Reference: docs/scientific_engine/06_Biomechanics.md
D. A. Winter - Biomechanics and Motor Control of Human Movement (1990)
"""

from typing import Tuple, List
import math


class PostureAnalyzer:
    """
    Analyzes human posture from landmark data.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    """
    
    def __init__(self):
        """Initialize the posture analyzer."""
        pass
    
    def calculate_trunk_angle(self, shoulder_left: Tuple[float, float, float],
                              shoulder_right: Tuple[float, float, float],
                              hip_left: Tuple[float, float, float],
                              hip_right: Tuple[float, float, float],
                              degrees: bool = True) -> float:
        """
        Calculate trunk inclination angle.
        
        Formula: theta = arccos((v_trunk . v_vertical) / (||v_trunk|| * ||v_vertical||))
        
        Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
        
        Args:
            shoulder_left: Left shoulder position
            shoulder_right: Right shoulder position
            hip_left: Left hip position
            hip_right: Right hip position
            degrees: If True, return in degrees
        
        Returns:
            Trunk inclination angle
        """
        # Calculate shoulder center
        shoulder_center = (
            (shoulder_left[0] + shoulder_right[0]) / 2,
            (shoulder_left[1] + shoulder_right[1]) / 2,
            (shoulder_left[2] + shoulder_right[2]) / 2
        )
        
        # Calculate hip center
        hip_center = (
            (hip_left[0] + hip_right[0]) / 2,
            (hip_left[1] + hip_right[1]) / 2,
            (hip_left[2] + hip_right[2]) / 2
        )
        
        # Trunk vector (from hip to shoulder)
        v_trunk = (
            shoulder_center[0] - hip_center[0],
            shoulder_center[1] - hip_center[1],
            shoulder_center[2] - hip_center[2]
        )
        
        # Vertical vector
        v_vertical = (0, 1, 0)
        
        # Calculate angle
        dot = v_trunk[0] * v_vertical[0] + v_trunk[1] * v_vertical[1] + v_trunk[2] * v_vertical[2]
        norm_trunk = math.sqrt(v_trunk[0]**2 + v_trunk[1]**2 + v_trunk[2]**2)
        norm_vertical = 1.0
        
        if norm_trunk == 0:
            return 0.0
        
        cos_theta = dot / (norm_trunk * norm_vertical)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        
        angle = math.acos(cos_theta)
        
        if degrees:
            angle = math.degrees(angle)
        
        return angle
    
    def calculate_hip_angle(self, hip: Tuple[float, float, float],
                           knee: Tuple[float, float, float],
                           ankle: Tuple[float, float, float],
                           degrees: bool = True) -> float:
        """
        Calculate hip angle.
        
        Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
        
        Args:
            hip: Hip position
            knee: Knee position
            ankle: Ankle position
            degrees: If True, return in degrees
        
        Returns:
            Hip angle
        """
        # Thigh vector
        v_thigh = (knee[0] - hip[0], knee[1] - hip[1], knee[2] - hip[2])
        # Leg vector
        v_leg = (ankle[0] - knee[0], ankle[1] - knee[1], ankle[2] - knee[2])
        
        n1 = math.sqrt(v_thigh[0]**2 + v_thigh[1]**2 + v_thigh[2]**2)
        n2 = math.sqrt(v_leg[0]**2 + v_leg[1]**2 + v_leg[2]**2)
        
        if n1 == 0 or n2 == 0:
            return 0.0
        
        dot = v_thigh[0] * v_leg[0] + v_thigh[1] * v_leg[1] + v_thigh[2] * v_leg[2]
        cos_theta = dot / (n1 * n2)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        
        angle = math.acos(cos_theta)
        
        if degrees:
            angle = math.degrees(angle)
        
        return angle
    
    def calculate_knee_angle(self, hip: Tuple[float, float, float],
                            knee: Tuple[float, float, float],
                            ankle: Tuple[float, float, float],
                            degrees: bool = True) -> float:
        """
        Calculate knee angle.
        
        Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
        
        Args:
            hip: Hip position
            knee: Knee position
            ankle: Ankle position
            degrees: If True, return in degrees
        
        Returns:
            Knee angle
        """
        # Thigh vector
        v_thigh = (knee[0] - hip[0], knee[1] - hip[1], knee[2] - hip[2])
        # Leg vector
        v_leg = (ankle[0] - knee[0], ankle[1] - knee[1], ankle[2] - knee[2])
        
        n1 = math.sqrt(v_thigh[0]**2 + v_thigh[1]**2 + v_thigh[2]**2)
        n2 = math.sqrt(v_leg[0]**2 + v_leg[1]**2 + v_leg[2]**2)
        
        if n1 == 0 or n2 == 0:
            return 0.0
        
        dot = v_thigh[0] * v_leg[0] + v_thigh[1] * v_leg[1] + v_thigh[2] * v_leg[2]
        cos_theta = dot / (n1 * n2)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        
        angle = math.acos(cos_theta)
        
        if degrees:
            angle = math.degrees(angle)
        
        return angle
    
    def detect_abnormal_posture(self, trunk_angle: float, threshold: float = 45.0) -> bool:
        """
        Detect abnormal posture based on trunk angle.
        
        Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
        
        Args:
            trunk_angle: Trunk angle in degrees
            threshold: Angle threshold in degrees
        
        Returns:
            True if posture is abnormal
        """
        return trunk_angle > threshold
    
    def calculate_postural_symmetry(self, point_left: Tuple[float, float, float],
                                   point_right: Tuple[float, float, float]) -> float:
        """
        Calculate postural symmetry index.
        
        Formula: ISP = 1 - ||p_left - p_right|| / (||p_left|| + ||p_right||)
        
        Reference: J. H. J. Allum, A. F. Bloem (1999) - DOI: 10.1016/S0966-6362(99)00034-6
        
        Args:
            point_left: Left side point
            point_right: Right side point
        
        Returns:
            Symmetry index (0 = asymmetric, 1 = symmetric)
        """
        diff = math.sqrt(
            (point_left[0] - point_right[0])**2 +
            (point_left[1] - point_right[1])**2 +
            (point_left[2] - point_right[2])**2
        )
        
        norm_left = math.sqrt(point_left[0]**2 + point_left[1]**2 + point_left[2]**2)
        norm_right = math.sqrt(point_right[0]**2 + point_right[1]**2 + point_right[2]**2)
        
        if norm_left + norm_right == 0:
            return 1.0
        
        return 1.0 - (diff / (norm_left + norm_right))
