"""
Service pour la gestion de la santé du système.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import deque
import random

from app.desktop.models.system_model import (
    SystemMetric, ComponentHealth, SystemOverview,
    HealthStatus, ComponentType
)


class HealthService:
    """Service de gestion de la santé du système."""
    
    def __init__(self):
        self._components: Dict[ComponentType, ComponentHealth] = {}
        self._metric_history: Dict[ComponentType, deque] = {}
        self._max_history_size = 100
        self._initialize_demo_components()
    
    def _initialize_demo_components(self) -> None:
        """Initialise les composants de démonstration."""
        components = [
            ComponentHealth(
                component_type=ComponentType.CPU,
                name="CPU",
                status=HealthStatus.HEALTHY,
                message="CPU usage normal",
                last_updated=datetime.now()
            ),
            ComponentHealth(
                component_type=ComponentType.RAM,
                name="RAM",
                status=HealthStatus.HEALTHY,
                message="Memory usage normal",
                last_updated=datetime.now()
            ),
            ComponentHealth(
                component_type=ComponentType.GPU,
                name="GPU",
                status=HealthStatus.HEALTHY,
                message="GPU usage normal",
                last_updated=datetime.now()
            ),
            ComponentHealth(
                component_type=ComponentType.AI_INFERENCE,
                name="AI Inference",
                status=HealthStatus.HEALTHY,
                message="Inference latency normal",
                last_updated=datetime.now()
            ),
            ComponentHealth(
                component_type=ComponentType.API_LATENCY,
                name="API Latency",
                status=HealthStatus.HEALTHY,
                message="API response time normal",
                last_updated=datetime.now()
            ),
            ComponentHealth(
                component_type=ComponentType.CAMERA_STREAMS,
                name="Camera Streams",
                status=HealthStatus.HEALTHY,
                message="All camera streams active",
                last_updated=datetime.now()
            ),
            ComponentHealth(
                component_type=ComponentType.DATABASE,
                name="Database",
                status=HealthStatus.HEALTHY,
                message="Database connection healthy",
                last_updated=datetime.now()
            ),
            ComponentHealth(
                component_type=ComponentType.EVENT_BUS,
                name="Event Bus",
                status=HealthStatus.HEALTHY,
                message="Event bus processing normally",
                last_updated=datetime.now()
            )
        ]
        
        for component in components:
            self._components[component.component_type] = component
            self._metric_history[component.component_type] = deque(maxlen=self._max_history_size)
    
    def get_system_overview(self) -> SystemOverview:
        """Récupère la vue d'ensemble du système."""
        overall_status = self._calculate_overall_status()
        return SystemOverview(
            overall_status=overall_status,
            components=list(self._components.values()),
            timestamp=datetime.now()
        )
    
    def _calculate_overall_status(self) -> HealthStatus:
        """Calcule le statut global du système."""
        statuses = [c.status for c in self._components.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        if HealthStatus.UNKNOWN in statuses:
            return HealthStatus.UNKNOWN
        return HealthStatus.HEALTHY
    
    def get_component_health(self, component_type: ComponentType) -> Optional[ComponentHealth]:
        """Récupère la santé d'un composant."""
        return self._components.get(component_type)
    
    def update_component_metric(
        self,
        component_type: ComponentType,
        value: float,
        unit: str,
        status: Optional[HealthStatus] = None
    ) -> None:
        """Met à jour une métrique d'un composant."""
        component = self._components.get(component_type)
        if not component:
            return
        
        metric = SystemMetric(
            component_type=component_type,
            name=component.name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            status=status or component.status
        )
        
        component.metrics.append(metric)
        component.last_updated = datetime.now()
        
        if status:
            component.status = status
        
        # Ajouter à l'historique
        self._metric_history[component_type].append(metric)
    
    def get_metric_history(
        self,
        component_type: ComponentType,
        limit: int = 50
    ) -> List[SystemMetric]:
        """Récupère l'historique des métriques d'un composant."""
        history = self._metric_history.get(component_type, deque())
        return list(history)[-limit:]
    
    def get_all_components(self) -> List[ComponentHealth]:
        """Récupère tous les composants."""
        return list(self._components.values())
    
    def update_all_metrics(self) -> None:
        """Met à jour toutes les métriques avec des valeurs simulées."""
        # CPU
        cpu_usage = random.uniform(20, 80)
        cpu_status = HealthStatus.HEALTHY if cpu_usage < 70 else (HealthStatus.DEGRADED if cpu_usage < 90 else HealthStatus.UNHEALTHY)
        self.update_component_metric(ComponentType.CPU, cpu_usage, "%", cpu_status)
        
        # RAM
        ram_usage = random.uniform(40, 85)
        ram_status = HealthStatus.HEALTHY if ram_usage < 70 else (HealthStatus.DEGRADED if ram_usage < 90 else HealthStatus.UNHEALTHY)
        self.update_component_metric(ComponentType.RAM, ram_usage, "%", ram_status)
        
        # GPU
        gpu_usage = random.uniform(10, 90)
        gpu_status = HealthStatus.HEALTHY if gpu_usage < 80 else (HealthStatus.DEGRADED if gpu_usage < 95 else HealthStatus.UNHEALTHY)
        self.update_component_metric(ComponentType.GPU, gpu_usage, "%", gpu_status)
        
        # AI Inference
        inference_latency = random.uniform(10, 200)
        inference_status = HealthStatus.HEALTHY if inference_latency < 100 else (HealthStatus.DEGRADED if inference_latency < 200 else HealthStatus.UNHEALTHY)
        self.update_component_metric(ComponentType.AI_INFERENCE, inference_latency, "ms", inference_status)
        
        # API Latency
        api_latency = random.uniform(5, 150)
        api_status = HealthStatus.HEALTHY if api_latency < 50 else (HealthStatus.DEGRADED if api_latency < 100 else HealthStatus.UNHEALTHY)
        self.update_component_metric(ComponentType.API_LATENCY, api_latency, "ms", api_status)
        
        # Camera Streams
        active_streams = random.randint(4, 6)
        camera_status = HealthStatus.HEALTHY if active_streams >= 5 else HealthStatus.DEGRADED
        self.update_component_metric(ComponentType.CAMERA_STREAMS, active_streams, "streams", camera_status)
        
        # Database
        db_latency = random.uniform(1, 50)
        db_status = HealthStatus.HEALTHY if db_latency < 20 else (HealthStatus.DEGRADED if db_latency < 50 else HealthStatus.UNHEALTHY)
        self.update_component_metric(ComponentType.DATABASE, db_latency, "ms", db_status)
        
        # Event Bus
        events_per_sec = random.uniform(10, 100)
        event_status = HealthStatus.HEALTHY if events_per_sec < 80 else HealthStatus.DEGRADED
        self.update_component_metric(ComponentType.EVENT_BUS, events_per_sec, "events/sec", event_status)
    
    def get_health_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques de santé."""
        components = self.get_all_components()
        healthy = len([c for c in components if c.status == HealthStatus.HEALTHY])
        degraded = len([c for c in components if c.status == HealthStatus.DEGRADED])
        unhealthy = len([c for c in components if c.status == HealthStatus.UNHEALTHY])
        
        return {
            "total": len(components),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "overall_status": self._calculate_overall_status().value
        }
