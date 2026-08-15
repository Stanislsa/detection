"""
Service pour la gestion de la santé des services.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

from app.desktop.models.service_health_model import (
    ServiceHealth, SystemHealthOverview,
    ServiceStatus, ServiceType
)


class ServiceHealthService:
    """Service de gestion de la santé des services."""
    
    def __init__(self):
        self._services: Dict[ServiceType, ServiceHealth] = {}
        self._initialize_demo_services()
    
    def _initialize_demo_services(self) -> None:
        """Initialise les services de démonstration."""
        services = [
            ServiceHealth(
                service_type=ServiceType.CAMERA_MANAGER,
                name="Camera Manager",
                status=ServiceStatus.HEALTHY,
                uptime=timedelta(days=5, hours=12, minutes=30),
                latency=15.5,
                last_check=datetime.now(),
                version="2.1.0",
                metadata={"active_cameras": 6, "total_cameras": 6}
            ),
            ServiceHealth(
                service_type=ServiceType.AI_ENGINE,
                name="AI Engine",
                status=ServiceStatus.HEALTHY,
                uptime=timedelta(days=3, hours=8, minutes=45),
                latency=45.2,
                last_check=datetime.now(),
                version="3.0.1",
                metadata={"model": "yolov8", "fps": 30}
            ),
            ServiceHealth(
                service_type=ServiceType.EVENT_BUS,
                name="Event Bus",
                status=ServiceStatus.HEALTHY,
                uptime=timedelta(days=7, hours=2, minutes=15),
                latency=8.3,
                last_check=datetime.now(),
                version="1.5.2",
                metadata={"events_per_sec": 45}
            ),
            ServiceHealth(
                service_type=ServiceType.DATABASE,
                name="Database",
                status=ServiceStatus.HEALTHY,
                uptime=timedelta(days=10, hours=15, minutes=20),
                latency=12.7,
                last_check=datetime.now(),
                version="PostgreSQL 14.2",
                metadata={"connections": 15, "size_gb": 45.3}
            ),
            ServiceHealth(
                service_type=ServiceType.API,
                name="API",
                status=ServiceStatus.HEALTHY,
                uptime=timedelta(days=2, hours=18, minutes=50),
                latency=25.4,
                last_check=datetime.now(),
                version="1.8.0",
                metadata={"requests_per_sec": 120}
            ),
            ServiceHealth(
                service_type=ServiceType.STORAGE,
                name="Storage",
                status=ServiceStatus.WARNING,
                uptime=timedelta(days=15, hours=5, minutes=10),
                latency=35.8,
                last_check=datetime.now(),
                version="1.2.0",
                metadata={"usage_gb": 920, "max_gb": 1000}
            ),
            ServiceHealth(
                service_type=ServiceType.NOTIFICATION_SERVICE,
                name="Notification Service",
                status=ServiceStatus.HEALTHY,
                uptime=timedelta(days=4, hours=11, minutes=40),
                latency=18.9,
                last_check=datetime.now(),
                version="2.0.0",
                metadata={"pending": 0, "sent_today": 156}
            )
        ]
        
        for service in services:
            self._services[service.service_type] = service
    
    def get_system_overview(self) -> SystemHealthOverview:
        """Récupère la vue d'ensemble du système."""
        overview = SystemHealthOverview(
            services=list(self._services.values()),
            last_updated=datetime.now()
        )
        overview.overall_status = overview.calculate_overall_status()
        return overview
    
    def get_service_health(self, service_type: ServiceType) -> Optional[ServiceHealth]:
        """Récupère la santé d'un service."""
        return self._services.get(service_type)
    
    def get_all_services(self) -> List[ServiceHealth]:
        """Récupère tous les services."""
        return list(self._services.values())
    
    def update_service_health(
        self,
        service_type: ServiceType,
        status: Optional[ServiceStatus] = None,
        latency: Optional[float] = None
    ) -> None:
        """Met à jour la santé d'un service."""
        service = self._services.get(service_type)
        if not service:
            return
        
        if status:
            service.status = status
        if latency is not None:
            service.latency = latency
        
        service.last_check = datetime.now()
    
    def simulate_health_changes(self) -> None:
        """Simule des changements de santé pour la démo."""
        for service in self._services.values():
            # Simuler des variations de latence
            base_latency = {
                ServiceType.CAMERA_MANAGER: 15.0,
                ServiceType.AI_ENGINE: 45.0,
                ServiceType.EVENT_BUS: 8.0,
                ServiceType.DATABASE: 12.0,
                ServiceType.API: 25.0,
                ServiceType.STORAGE: 35.0,
                ServiceType.NOTIFICATION_SERVICE: 18.0
            }.get(service.service_type, 20.0)
            
            service.latency = base_latency + random.uniform(-5, 10)
            service.last_check = datetime.now()
            
            # Simuler occasionnellement des problèmes
            if random.random() < 0.05:
                service.status = ServiceStatus.WARNING
            elif random.random() < 0.01:
                service.status = ServiceStatus.CRITICAL
            elif service.status != ServiceStatus.HEALTHY and random.random() < 0.3:
                service.status = ServiceStatus.HEALTHY
    
    def get_health_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques de santé."""
        services = self.get_all_services()
        healthy = len([s for s in services if s.status == ServiceStatus.HEALTHY])
        warning = len([s for s in services if s.status == ServiceStatus.WARNING])
        critical = len([s for s in services if s.status == ServiceStatus.CRITICAL])
        offline = len([s for s in services if s.status == ServiceStatus.OFFLINE])
        
        overview = self.get_system_overview()
        
        return {
            "total": len(services),
            "healthy": healthy,
            "warning": warning,
            "critical": critical,
            "offline": offline,
            "overall_status": overview.overall_status.value
        }
