"""
Metrics and KPI Functions

Reference: docs/scientific_engine/11_KPI.md
D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
"""

from typing import List, Tuple


def accuracy(tp: int, tn: int, fp: int, fn: int) -> float:
    """
    Calculate accuracy.
    
    Formula: Accuracy = (TP + TN) / (TP + TN + FP + FN)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        tp: True positives
        tn: True negatives
        fp: False positives
        fn: False negatives
    
    Returns:
        Accuracy [0, 1]
    """
    total = tp + tn + fp + fn
    if total == 0:
        return 0.0
    return (tp + tn) / total


def precision(tp: int, fp: int) -> float:
    """
    Calculate precision.
    
    Formula: Precision = TP / (TP + FP)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        tp: True positives
        fp: False positives
    
    Returns:
        Precision [0, 1]
    """
    total = tp + fp
    if total == 0:
        return 0.0
    return tp / total


def recall(tp: int, fn: int) -> float:
    """
    Calculate recall (sensitivity).
    
    Formula: Recall = TP / (TP + FN)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        tp: True positives
        fn: False negatives
    
    Returns:
        Recall [0, 1]
    """
    total = tp + fn
    if total == 0:
        return 0.0
    return tp / total


def specificity(tn: int, fp: int) -> float:
    """
    Calculate specificity.
    
    Formula: Specificity = TN / (TN + FP)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        tn: True negatives
        fp: False positives
    
    Returns:
        Specificity [0, 1]
    """
    total = tn + fp
    if total == 0:
        return 0.0
    return tn / total


def f1_score(precision: float, recall: float) -> float:
    """
    Calculate F1-score.
    
    Formula: F1 = 2 * (Precision * Recall) / (Precision + Recall)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        precision: Precision value [0, 1]
        recall: Recall value [0, 1]
    
    Returns:
        F1-score [0, 1]
    """
    total = precision + recall
    if total == 0:
        return 0.0
    return 2 * (precision * recall) / total


def false_positive_rate(fp: int, tn: int) -> float:
    """
    Calculate false positive rate.
    
    Formula: FPR = FP / (FP + TN)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        fp: False positives
        tn: True negatives
    
    Returns:
        False positive rate [0, 1]
    """
    total = fp + tn
    if total == 0:
        return 0.0
    return fp / total


def false_negative_rate(fn: int, tp: int) -> float:
    """
    Calculate false negative rate.
    
    Formula: FNR = FN / (FN + TP)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        fn: False negatives
        tp: True positives
    
    Returns:
        False negative rate [0, 1]
    """
    total = fn + tp
    if total == 0:
        return 0.0
    return fn / total


def mean_detection_time(detection_times: List[float], fall_start_times: List[float]) -> float:
    """
    Calculate mean detection time.
    
    Formula: MDT = (1/N) * sum(t_detection - t_fall_start)
    
    Reference: N. Noury et al. (2000) - DOI: 10.1109/58.897022
    
    Args:
        detection_times: List of detection timestamps (s)
        fall_start_times: List of fall start timestamps (s)
    
    Returns:
        Mean detection time in seconds
    """
    if len(detection_times) != len(fall_start_times) or len(detection_times) == 0:
        return 0.0
    
    delays = [d - f for d, f in zip(detection_times, fall_start_times)]
    return sum(delays) / len(delays)


def mean_alert_time(alert_times: List[float], detection_times: List[float]) -> float:
    """
    Calculate mean alert time.
    
    Formula: MAT = (1/N) * sum(t_alert - t_detection)
    
    Reference: J. Fleming et al. (2008) - DOI: 10.1191/0269215508pm920oa
    
    Args:
        alert_times: List of alert timestamps (s)
        detection_times: List of detection timestamps (s)
    
    Returns:
        Mean alert time in seconds
    """
    if len(alert_times) != len(detection_times) or len(alert_times) == 0:
        return 0.0
    
    delays = [a - d for a, d in zip(alert_times, detection_times)]
    return sum(delays) / len(delays)


def alert_response_time(acknowledgment_times: List[float], alert_times: List[float]) -> float:
    """
    Calculate alert response time.
    
    Formula: ART = (1/N) * sum(t_acknowledgment - t_alert)
    
    Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
    
    Args:
        acknowledgment_times: List of acknowledgment timestamps (s)
        alert_times: List of alert timestamps (s)
    
    Returns:
        Mean response time in seconds
    """
    if len(acknowledgment_times) != len(alert_times) or len(acknowledgment_times) == 0:
        return 0.0
    
    delays = [a - t for a, t in zip(acknowledgment_times, alert_times)]
    return sum(delays) / len(delays)


def uptime(uptime_seconds: float, total_seconds: float) -> float:
    """
    Calculate uptime percentage.
    
    Formula: Uptime = (uptime / total) * 100
    
    Reference: ITIL v4
    
    Args:
        uptime_seconds: Uptime in seconds
        total_seconds: Total time in seconds
    
    Returns:
        Uptime percentage [0, 100]
    """
    if total_seconds == 0:
        return 0.0
    return (uptime_seconds / total_seconds) * 100


def downtime(uptime_seconds: float, total_seconds: float) -> float:
    """
    Calculate downtime.
    
    Formula: Downtime = total - uptime
    
    Reference: ITIL v4
    
    Args:
        uptime_seconds: Uptime in seconds
        total_seconds: Total time in seconds
    
    Returns:
        Downtime in seconds
    """
    return total_seconds - uptime_seconds


def frame_rate(num_frames: float, duration: float) -> float:
    """
    Calculate frame rate.
    
    Formula: FR = num_frames / duration
    
    Reference: Google Research - MediaPipe Pose (2020)
    
    Args:
        num_frames: Number of frames
        duration: Duration in seconds
    
    Returns:
        Frame rate in fps
    """
    if duration == 0:
        return 0.0
    return num_frames / duration


def pose_detection_confidence(confidences: List[float]) -> float:
    """
    Calculate mean pose detection confidence.
    
    Formula: PDC = (1/N) * sum(confidence_i)
    
    Reference: Google Research - MediaPipe Pose (2020)
    
    Args:
        confidences: List of confidence values [0, 1]
    
    Returns:
        Mean confidence [0, 1]
    """
    if len(confidences) == 0:
        return 0.0
    return sum(confidences) / len(confidences)


def data_completeness(valid_points: int, total_points: int) -> float:
    """
    Calculate data completeness.
    
    Formula: DC = valid_points / total_points
    
    Reference: D. A. Winter (1990)
    
    Args:
        valid_points: Number of valid points
        total_points: Total number of points
    
    Returns:
        Completeness ratio [0, 1]
    """
    if total_points == 0:
        return 0.0
    return valid_points / total_points


def alert_acknowledgment_rate(acknowledged_alerts: int, total_alerts: int) -> float:
    """
    Calculate alert acknowledgment rate.
    
    Formula: AAR = acknowledged_alerts / total_alerts
    
    Reference: J. Fleming et al. (2008) - DOI: 10.1191/0269215508pm920oa
    
    Args:
        acknowledged_alerts: Number of acknowledged alerts
        total_alerts: Total number of alerts
    
    Returns:
        Acknowledgment rate [0, 1]
    """
    if total_alerts == 0:
        return 0.0
    return acknowledged_alerts / total_alerts


def false_alert_rate(false_alerts: int, total_alerts: int) -> float:
    """
    Calculate false alert rate.
    
    Formula: FAR = false_alerts / total_alerts
    
    Reference: A. Bourke et al. (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
    
    Args:
        false_alerts: Number of false alerts
        total_alerts: Total number of alerts
    
    Returns:
        False alert rate [0, 1]
    """
    if total_alerts == 0:
        return 0.0
    return false_alerts / total_alerts


def cpu_usage(busy_time: float, total_time: float) -> float:
    """
    Calculate CPU usage percentage.
    
    Formula: CPU = (busy_time / total_time) * 100
    
    Reference: System specification
    
    Args:
        busy_time: CPU busy time in seconds
        total_time: Total time in seconds
    
    Returns:
        CPU usage percentage [0, 100]
    """
    if total_time == 0:
        return 0.0
    return (busy_time / total_time) * 100


def memory_usage(used_memory: float, total_memory: float) -> float:
    """
    Calculate memory usage percentage.
    
    Formula: Memory = (used_memory / total_memory) * 100
    
    Reference: System specification
    
    Args:
        used_memory: Used memory in bytes
        total_memory: Total memory in bytes
    
    Returns:
        Memory usage percentage [0, 100]
    """
    if total_memory == 0:
        return 0.0
    return (used_memory / total_memory) * 100


def storage_usage(used_storage: float, total_storage: float) -> float:
    """
    Calculate storage usage percentage.
    
    Formula: Storage = (used_storage / total_storage) * 100
    
    Reference: System specification
    
    Args:
        used_storage: Used storage in bytes
        total_storage: Total storage in bytes
    
    Returns:
        Storage usage percentage [0, 100]
    """
    if total_storage == 0:
        return 0.0
    return (used_storage / total_storage) * 100


def true_positive_rate(tp: int, fn: int) -> float:
    """
    Calculate true positive rate (same as recall).
    
    Formula: TPR = TP / (TP + FN)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        tp: True positives
        fn: False negatives
    
    Returns:
        True positive rate [0, 1]
    """
    return recall(tp, fn)


def true_negative_rate(tn: int, fp: int) -> float:
    """
    Calculate true negative rate (same as specificity).
    
    Formula: TNR = TN / (TN + FP)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        tn: True negatives
        fp: False positives
    
    Returns:
        True negative rate [0, 1]
    """
    return specificity(tn, fp)


def negative_predictive_value(tn: int, fn: int) -> float:
    """
    Calculate negative predictive value.
    
    Formula: NPV = TN / (TN + FN)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        tn: True negatives
        fn: False negatives
    
    Returns:
        Negative predictive value [0, 1]
    """
    total = tn + fn
    if total == 0:
        return 0.0
    return tn / total


def positive_predictive_value(tp: int, fp: int) -> float:
    """
    Calculate positive predictive value (same as precision).
    
    Formula: PPV = TP / (TP + FP)
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        tp: True positives
        fp: False positives
    
    Returns:
        Positive predictive value [0, 1]
    """
    return precision(tp, fp)


def matthews_correlation_coefficient(tp: int, tn: int, fp: int, fn: int) -> float:
    """
    Calculate Matthews correlation coefficient.
    
    Formula: MCC = (TP*TN - FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))
    
    Reference: B. W. Matthews (1975)
    
    Args:
        tp: True positives
        tn: True negatives
        fp: False positives
        fn: False negatives
    
    Returns:
        MCC [-1, 1]
    """
    numerator = tp * tn - fp * fn
    denominator = ((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)) ** 0.5
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def confusion_matrix(y_true: List[int], y_pred: List[int]) -> Tuple[int, int, int, int]:
    """
    Calculate confusion matrix values.
    
    Reference: D. M. Powers (2011) - DOI: 10.1145/2003476.2003486
    
    Args:
        y_true: List of true labels (0 or 1)
        y_pred: List of predicted labels (0 or 1)
    
    Returns:
        Tuple of (TP, TN, FP, FN)
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    tp = tn = fp = fn = 0
    
    for true, pred in zip(y_true, y_pred):
        if true == 1 and pred == 1:
            tp += 1
        elif true == 0 and pred == 0:
            tn += 1
        elif true == 0 and pred == 1:
            fp += 1
        elif true == 1 and pred == 0:
            fn += 1
    
    return (tp, tn, fp, fn)
