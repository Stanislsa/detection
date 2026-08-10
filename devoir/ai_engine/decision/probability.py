"""
Probability Functions for Injury Risk

Reference: docs/scientific_engine/10_InjuryProbability.md
D. R. Cox - The Regression Analysis of Binary Sequences (1958)
"""

import math
from typing import Tuple


def logistic_regression(severity: float, age: float, mobility: float, 
                       history: float, comorbidities: float = 0.0,
                       medications: float = 0.0,
                       coefficients: Tuple[float, float, float, float, float, float, float] = None) -> float:
    """
    Calculate injury probability using logistic regression.
    
    Formula: P = 1 / (1 + exp(-(beta0 + beta1*S + beta2*F_age + beta3*F_mobility + beta4*F_history + beta5*F_comorbidities + beta6*F_medications)))
    
    Reference: D. R. Cox (1958) - DOI: 10.1111/j.2517-6161.1958.tb00292.x
    
    Args:
        severity: Severity score [0, 1]
        age: Age in years
        mobility: Mobility factor [0, 1]
        history: Fall history factor [0, 1]
        comorbidities: Comorbidities factor [0, 1]
        medications: Medications factor [0, 1]
        coefficients: Optional tuple of (beta0, beta1, beta2, beta3, beta4, beta5, beta6)
    
    Returns:
        Injury probability [0, 1]
    """
    if coefficients is None:
        coefficients = (-3.0, 4.0, 0.03, 0.5, 0.3, 0.1, 0.05)
    
    beta0, beta1, beta2, beta3, beta4, beta5, beta6 = coefficients
    
    z = (beta0 + beta1 * severity + beta2 * age + beta3 * mobility + 
         beta4 * history + beta5 * comorbidities + beta6 * medications)
    
    probability = 1.0 / (1.0 + math.exp(-z))
    
    return max(0.0, min(1.0, probability))


def age_risk_factor(age: float, min_age: float = 65.0, max_age: float = 115.0) -> float:
    """
    Calculate age risk factor for probability model.
    
    Formula: F_age = (age - min_age) / (max_age - min_age)
    
    Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
    
    Args:
        age: Age in years
        min_age: Minimum age for normalization (default 65)
        max_age: Maximum age for normalization (default 115)
    
    Returns:
        Age risk factor [0, 1]
    """
    return max(0.0, min(1.0, (age - min_age) / (max_age - min_age)))


def mobility_risk_factor(mobility_level: str) -> float:
    """
    Calculate mobility risk factor for probability model.
    
    Reference: M. J. O'Brien, D. N. Bohannon (2007) - DOI: 10.1007/s00147-007-0214-4
    
    Args:
        mobility_level: One of 'AUTONOME', 'CANNE', 'DEAMBULATEUR', 'FAUTEUIL'
    
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


def history_risk_factor(falls_per_year: int, max_falls: int = 5) -> float:
    """
    Calculate fall history risk factor for probability model.
    
    Formula: F_history = min(0.5, 0.1 * falls_per_year)
    
    Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
    
    Args:
        falls_per_year: Number of falls in the past year
        max_falls: Maximum falls for cap (default 5)
    
    Returns:
        History risk factor [0, 0.5]
    """
    return min(0.5, 0.1 * min(falls_per_year, max_falls))


def comorbidities_risk_factor(num_comorbidities: int) -> float:
    """
    Calculate comorbidities risk factor for probability model.
    
    Formula: F_comorbidities = 0.1 * num_comorbidities
    
    Reference: J. M. G. A. Schroll et al. (2004) - DOI: 10.1007/s00198-004-0565-5
    
    Args:
        num_comorbidities: Number of comorbidities
    
    Returns:
        Comorbidities risk factor [0, 0.7]
    """
    return min(0.7, 0.1 * num_comorbidities)


def medications_risk_factor(num_risk_medications: int) -> float:
    """
    Calculate medications risk factor for probability model.
    
    Formula: F_medications = 0.05 * num_risk_medications
    
    Reference: L. Z. Rubenstein et al. (1996) - DOI: 10.7326/0003-4819-124-11-1002
    
    Args:
        num_risk_medications: Number of risk medications
    
    Returns:
        Medications risk factor [0, 0.5]
    """
    return min(0.5, 0.05 * num_risk_medications)


def bayesian_probability(prior: float, likelihood: float, evidence: float) -> float:
    """
    Calculate posterior probability using Bayes' theorem.
    
    Formula: P(A|B) = (P(B|A) * P(A)) / P(B)
    
    Reference: Thomas Bayes (1763)
    
    Args:
        prior: Prior probability P(A)
        likelihood: Likelihood P(B|A)
        evidence: Evidence P(B)
    
    Returns:
        Posterior probability P(A|B)
    """
    if evidence == 0:
        return 0.0
    return (likelihood * prior) / evidence


def injury_type_probability(injury_probability: float, type_weights: Tuple[float, ...]) -> Tuple[float, ...]:
    """
    Calculate probabilities for specific injury types.
    
    Formula: P(type_i) = P(injury) * (w_i / sum(w_j))
    
    Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
    
    Args:
        injury_probability: Overall injury probability [0, 1]
        type_weights: Weights for each injury type
    
    Returns:
        Tuple of probabilities for each injury type
    """
    total_weight = sum(type_weights)
    if total_weight == 0:
        return tuple(0.0 for _ in type_weights)
    
    return tuple(injury_probability * (w / total_weight) for w in type_weights)


def calibrated_probability(raw_probability: float, a: float = 1.0, b: float = 0.0) -> float:
    """
    Calibrate probability using Platt scaling.
    
    Formula: P_calibrated = 1 / (1 + exp(-(a * logit(P_raw) + b)))
    
    Reference: Platt et al. (1999)
    
    Args:
        raw_probability: Raw probability [0, 1]
        a: Scaling parameter (default 1.0)
        b: Offset parameter (default 0.0)
    
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


def probability_class(probability: float) -> str:
    """
    Classify probability into alert level.
    
    Reference: M. E. Tinetti et al. (1994) - DOI: 10.1056/NEJM199401273300401
    
    Args:
        probability: Injury probability [0, 1]
    
    Returns:
        Alert level: 'FAIBLE', 'MODÉRÉE', 'ÉLEVÉE', 'TRÈS ÉLEVÉE', 'EXTRÊME'
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


def odds_ratio(probability: float) -> float:
    """
    Calculate odds ratio from probability.
    
    Formula: OR = P / (1 - P)
    
    Reference: D. R. Cox (1958)
    
    Args:
        probability: Probability [0, 1]
    
    Returns:
        Odds ratio
    """
    if probability >= 1:
        return float('inf')
    if probability <= 0:
        return 0.0
    return probability / (1.0 - probability)


def log_odds(probability: float) -> float:
    """
    Calculate log odds (logit) from probability.
    
    Formula: logit(P) = ln(P / (1 - P))
    
    Reference: D. R. Cox (1958)
    
    Args:
        probability: Probability [0, 1]
    
    Returns:
        Log odds
    """
    if probability <= 0:
        return float('-inf')
    if probability >= 1:
        return float('inf')
    return math.log(probability / (1.0 - probability))


def probability_from_log_odds(log_odds: float) -> float:
    """
    Calculate probability from log odds.
    
    Formula: P = 1 / (1 + exp(-logit))
    
    Reference: D. R. Cox (1958)
    
    Args:
        log_odds: Log odds value
    
    Returns:
        Probability [0, 1]
    """
    return 1.0 / (1.0 + math.exp(-log_odds))


def risk_score(severity: float, age: float, mobility: float, history: float) -> float:
    """
    Calculate simplified risk score.
    
    Formula: Risk = 0.4*severity + 0.2*F_age + 0.2*F_mobility + 0.2*F_history
    
    Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
    
    Args:
        severity: Severity score [0, 1]
        age: Age in years
        mobility: Mobility factor [0, 1]
        history: History factor [0, 1]
    
    Returns:
        Risk score [0, 1]
    """
    f_age = age_risk_factor(age)
    
    risk = (0.4 * severity + 0.2 * f_age + 
            0.2 * mobility + 0.2 * history)
    
    return max(0.0, min(1.0, risk))


def confidence_interval(probability: float, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval for probability using Wilson score interval.
    
    Formula: CI = (p + z²/(2n) ± z*sqrt(p(1-p)/n + z²/(4n²))) / (1 + z²/n)
    
    Reference: Edwin B. Wilson (1927)
    
    Args:
        probability: Observed probability [0, 1]
        n: Sample size
        confidence: Confidence level (default 0.95)
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if n == 0:
        return (0.0, 1.0)
    
    z = 1.96  # For 95% confidence
    p = probability
    
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator
    
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    
    return (lower, upper)
