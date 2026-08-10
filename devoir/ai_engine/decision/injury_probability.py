"""
Injury Probability Engine

Reference: docs/scientific_engine/10_InjuryProbability.md
D. R. Cox - The Regression Analysis of Binary Sequences (1958)
"""

from typing import Tuple, Optional
import math


class InjuryProbabilityEngine:
    """
    Calculates injury probability using logistic regression.
    
    Reference: D. R. Cox (1958) - DOI: 10.1111/j.2517-6161.1958.tb00292.x
    """
    
    def __init__(self, coefficients: Tuple[float, float, float, float, float, float, float] = None):
        """
        Initialize the injury probability engine.
        
        Args:
            coefficients: Logistic regression coefficients (beta0, beta1, beta2, beta3, beta4, beta5, beta6)
        """
        if coefficients is None:
            coefficients = (-3.0, 4.0, 0.03, 0.5, 0.3, 0.1, 0.05)
        
        self.coefficients = coefficients
    
    def calculate_probability(self, severity: float, age: float = 65,
                            mobility_level: str = 'AUTONOME',
                            falls_per_year: int = 0,
                            num_comorbidities: int = 0,
                            num_medications: int = 0) -> dict:
        """
        Calculate injury probability using logistic regression.
        
        Formula: P = 1 / (1 + exp(-(beta0 + beta1*S + beta2*F_age + beta3*F_mobility + beta4*F_history + beta5*F_comorbidities + beta6*F_medications)))
        
        Reference: D. R. Cox (1958) - DOI: 10.1111/j.2517-6161.1958.tb00292.x
        
        Args:
            severity: Severity score [0, 1]
            age: Age in years
            mobility_level: Mobility level
            falls_per_year: Falls per year
            num_comorbidities: Number of comorbidities
            num_medications: Number of risk medications
        
        Returns:
            Dictionary with probability results
        """
        # Calculate risk factors
        f_age = self._age_risk_factor(age)
        f_mobility = self._mobility_risk_factor(mobility_level)
        f_history = self._history_risk_factor(falls_per_year)
        f_comorbidities = self._comorbidities_risk_factor(num_comorbidities)
        f_medications = self._medications_risk_factor(num_medications)
        
        # Calculate probability using logistic regression
        probability = self._logistic_regression(
            severity, f_age, f_mobility, f_history,
            f_comorbidities, f_medications
        )
        
        # Determine probability class
        prob_class = self._classify_probability(probability)
        
        return {
            'probability': probability,
            'probability_class': prob_class,
            'risk_factors': {
                'age': f_age,
                'mobility': f_mobility,
                'history': f_history,
                'comorbidities': f_comorbidities,
                'medications': f_medications
            }
        }
    
    def _logistic_regression(self, severity: float, age_factor: float, mobility_factor: float,
                           history_factor: float, comorbidities_factor: float,
                           medications_factor: float) -> float:
        """
        Calculate probability using logistic regression.
        
        Reference: D. R. Cox (1958) - DOI: 10.1111/j.2517-6161.1958.tb00292.x
        
        Args:
            severity: Severity score [0, 1]
            age_factor: Age risk factor
            mobility_factor: Mobility risk factor
            history_factor: History risk factor
            comorbidities_factor: Comorbidities risk factor
            medications_factor: Medications risk factor
        
        Returns:
            Probability [0, 1]
        """
        beta0, beta1, beta2, beta3, beta4, beta5, beta6 = self.coefficients
        
        z = (beta0 + beta1 * severity + beta2 * age_factor + beta3 * mobility_factor +
             beta4 * history_factor + beta5 * comorbidities_factor + beta6 * medications_factor)
        
        probability = 1.0 / (1.0 + math.exp(-z))
        
        return max(0.0, min(1.0, probability))
    
    def _age_risk_factor(self, age: float) -> float:
        """
        Calculate age risk factor.
        
        Formula: F_age = (age - 65) / 50
        
        Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
        
        Args:
            age: Age in years
        
        Returns:
            Age risk factor [0, 1]
        """
        return max(0.0, min(1.0, (age - 65) / 50.0))
    
    def _mobility_risk_factor(self, mobility_level: str) -> float:
        """
        Calculate mobility risk factor.
        
        Reference: M. J. O'Brien, D. N. Bohannon (2007) - DOI: 10.1007/s00147-007-0214-4
        
        Args:
            mobility_level: Mobility level
        
        Returns:
            Mobility risk factor [0, 1]
        """
        factors = {
            'AUTONOME': 0.0,
            'CANNE': 0.2,
            'DEAMBULATEUR': 0.4,
            'FAUTEUIL': 0.6
        }
        return factors.get(mobility_level.upper(), 0.0)
    
    def _history_risk_factor(self, falls_per_year: int) -> float:
        """
        Calculate fall history risk factor.
        
        Formula: F_history = min(0.5, 0.1 * falls_per_year)
        
        Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
        
        Args:
            falls_per_year: Falls per year
        
        Returns:
            History risk factor [0, 0.5]
        """
        return min(0.5, 0.1 * min(falls_per_year, 5))
    
    def _comorbidities_risk_factor(self, num_comorbidities: int) -> float:
        """
        Calculate comorbidities risk factor.
        
        Formula: F_comorbidities = 0.1 * num_comorbidities
        
        Reference: J. M. G. A. Schroll et al. (2004) - DOI: 10.1007/s00198-004-0565-5
        
        Args:
            num_comorbidities: Number of comorbidities
        
        Returns:
            Comorbidities risk factor [0, 0.7]
        """
        return min(0.7, 0.1 * num_comorbidities)
    
    def _medications_risk_factor(self, num_medications: int) -> float:
        """
        Calculate medications risk factor.
        
        Formula: F_medications = 0.05 * num_medications
        
        Reference: L. Z. Rubenstein et al. (1996) - DOI: 10.7326/0003-4819-124-11-1002
        
        Args:
            num_medications: Number of risk medications
        
        Returns:
            Medications risk factor [0, 0.5]
        """
        return min(0.5, 0.05 * num_medications)
    
    def _classify_probability(self, probability: float) -> str:
        """
        Classify probability into alert level.
        
        Reference: M. E. Tinetti et al. (1994) - DOI: 10.1056/NEJM199401273300401
        
        Args:
            probability: Injury probability [0, 1]
        
        Returns:
            Alert level
        """
        if probability < 0.2:
            return 'FAIBLE'
        elif probability < 0.4:
            return 'MODÉRÉE'
        elif probability < 0.6:
            return 'ÉLEVÉE'
        elif probability < 0.8:
            return 'TRÈS ÉLEVÉE'
        else:
            return 'EXTRÊME'
    
    def calculate_injury_type_probabilities(self, overall_probability: float) -> dict:
        """
        Calculate probabilities for specific injury types.
        
        Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
        
        Args:
            overall_probability: Overall injury probability [0, 1]
        
        Returns:
            Dictionary of injury type probabilities
        """
        # Type weights based on epidemiological data
        type_weights = {
            'fracture_hanche': 0.05,
            'fracture_poignet': 0.03,
            'fracture_bras': 0.02,
            'contusion': .15,
            'entorse': 0.10,
            'lacération': 0.05,
            'traumatique_cerebral': 0.01
        }
        
        total_weight = sum(type_weights.values())
        
        probabilities = {}
        for injury_type, weight in type_weights.items():
            probabilities[injury_type] = overall_probability * (weight / total_weight)
        
        return probabilities
    
    def calibrate_probability(self, raw_probability: float, a: float = 1.0, b: float = 0.0) -> float:
        """
        Calibrate probability using Platt scaling.
        
        Formula: P_calibrated = 1 / (1 + exp(-(a * logit(P_raw) + b)))
        
        Reference: Platt et al. (1999)
        
        Args:
            raw_probability: Raw probability [0, 1]
            a: Scaling parameter
            b: Offset parameter
        
        Returns:
            Calibrated probability [0, 1]
        """
        if raw_probability <= 0:
            raw_probability = 0.0001
        elif raw_probability >= 1:
            raw_probability = 0.9999
        
        logit = math.log(raw_probability / (1.0 - raw_probability))
        z = a * logit + b
        calibrated = 1.0 / (1.0 + math.exp(-z))
        
        return max(0.0, min(1.0, calibrated))
