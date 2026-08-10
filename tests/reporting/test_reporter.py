"""
Générateur de rapports de tests.
Produit des tableaux de résultats, journaux d'essais et rapports HTML/PDF.
"""

import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class PerformanceTarget:
    """Objectif de performance."""
    name: str
    target_value: float
    unit: str
    measured_value: Optional[float] = None
    result: Optional[str] = None  # PASS, FAIL, N/A


@dataclass
class TestRun:
    """Exécution de test."""
    date: str
    configuration: Dict[str, str]
    camera_count: int
    ai_backend: str
    machine: str
    results: Dict[str, float] = field(default_factory=dict)
    observations: List[str] = field(default_factory=list)
    problems: List[str] = field(default_factory=list)
    fixes: List[str] = field(default_factory=list)


class TestReporter:
    """
    Générateur de rapports de tests.
    """
    
    def __init__(self):
        self.performance_targets = {
            "camera_open_time": PerformanceTarget("Ouverture caméra", 2.0, "s"),
            "inference_time": PerformanceTarget("Temps d'inférence", 40.0, "ms"),
            "total_latency": PerformanceTarget("Latence totale", 200.0, "ms"),
            "fps": PerformanceTarget("FPS", 20.0, ""),
            "memory": PerformanceTarget("Mémoire", 2.0, "GB"),
            "cpu": PerformanceTarget("CPU", 80.0, "%"),
            "gpu": PerformanceTarget("GPU", 90.0, "%"),
            "availability": PerformanceTarget("Disponibilité", 99.0, "%")
        }
        
        self.test_runs: List[TestRun] = []
        self.current_run: Optional[TestRun] = None
    
    def start_test_run(self, configuration: Dict[str, str], camera_count: int, ai_backend: str, machine: str):
        """
        Démarre une nouvelle exécution de test.
        
        Args:
            configuration: Configuration du test
            camera_count: Nombre de caméras
            ai_backend: Backend IA utilisé
            machine: Machine utilisée
        """
        self.current_run = TestRun(
            date=datetime.now().isoformat(),
            configuration=configuration,
            camera_count=camera_count,
            ai_backend=ai_backend,
            machine=machine
        )
        
        print(f"\n{'=' * 80}")
        print(f"DÉBUT DU TEST - {self.current_run.date}")
        print(f"Configuration: {configuration}")
        print(f"Caméras: {camera_count}")
        print(f"Backend IA: {ai_backend}")
        print(f"Machine: {machine}")
        print(f"{'=' * 80}")
    
    def record_result(self, metric_name: str, value: float):
        """
        Enregistre un résultat de mesure.
        
        Args:
            metric_name: Nom de la métrique
            value: Valeur mesurée
        """
        if self.current_run:
            self.current_run.results[metric_name] = value
            
            # Mettre à jour l'objectif correspondant
            if metric_name in self.performance_targets:
                target = self.performance_targets[metric_name]
                target.measured_value = value
                
                # Déterminer le résultat
                if metric_name == "fps":  # Plus c'est élevé, mieux c'est
                    target.result = "PASS" if value >= target.target_value else "FAIL"
                else:  # Plus c'est bas, mieux c'est
                    target.result = "PASS" if value <= target.target_value else "FAIL"
    
    def add_observation(self, observation: str):
        """Ajoute une observation."""
        if self.current_run:
            self.current_run.observations.append(observation)
    
    def add_problem(self, problem: str):
        """Ajoute un problème rencontré."""
        if self.current_run:
            self.current_run.problems.append(problem)
    
    def add_fix(self, fix: str):
        """Ajoute un correctif appliqué."""
        if self.current_run:
            self.current_run.fixes.append(fix)
    
    def end_test_run(self):
        """Termine l'exécution de test actuelle."""
        if self.current_run:
            self.test_runs.append(self.current_run)
            self.current_run = None
            
            print(f"\n{'=' * 80}")
            print("FIN DU TEST")
            print(f"{'=' * 80}")
    
    def print_results_table(self):
        """Affiche le tableau des résultats (objectifs vs mesurés)."""
        print("\n" + "=" * 80)
        print("TABLEAU DE RÉSULTATS")
        print("=" * 80)
        print(f"{'Test':<20} {'Objectif':<15} {'Mesuré':<15} {'Résultat':<10}")
        print("-" * 80)
        
        for name, target in self.performance_targets.items():
            measured_str = f"{target.measured_value:.2f} {target.unit}" if target.measured_value is not None else "N/A"
            target_str = f"{target.target_value:.2f} {target.unit}"
            result_str = target.result if target.result else "N/A"
            
            print(f"{target.name:<20} {target_str:<15} {measured_str:<15} {result_str:<10}")
        
        print("=" * 80)
        
        # Statistiques
        passed = sum(1 for t in self.performance_targets.values() if t.result == "PASS")
        failed = sum(1 for t in self.performance_targets.values() if t.result == "FAIL")
        total = passed + failed
        
        print(f"\nStatistiques: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
        print("=" * 80)
    
    def print_load_test_comparison(self):
        """Affiche la comparaison des tests de charge."""
        if not self.test_runs:
            print("Aucun test de charge exécuté")
            return
        
        print("\n" + "=" * 80)
        print("COMPARAISON TESTS DE CHARGE")
        print("=" * 80)
        
        print(f"\n{'Caméras':<10} {'FPS Total':<12} {'FPS/Cam':<10} {'Latence(ms)':<15} {'Mémoire(GB)':<12} {'CPU(%)':<10}")
        print("-" * 80)
        
        for run in self.test_runs:
            fps_total = run.results.get("fps_total", 0)
            fps_per_cam = run.results.get("fps_per_camera", 0)
            latency = run.results.get("latency", 0)
            memory = run.results.get("memory", 0)
            cpu = run.results.get("cpu", 0)
            
            print(f"{run.camera_count:<10} {fps_total:<12.1f} {fps_per_cam:<10.1f} "
                  f"{latency:<15.1f} {memory:<12.2f} {cpu:<10.1f}")
        
        print("=" * 80)
        
        # Analyse de scalabilité
        if len(self.test_runs) >= 2:
            print("\nAnalyse de scalabilité:")
            
            run_1 = self.test_runs[0]
            run_last = self.test_runs[-1]
            
            if run_1.results.get("fps_total", 0) > 0:
                fps_ratio = run_last.results.get("fps_total", 0) / run_1.results.get("fps_total", 1)
                camera_ratio = run_last.camera_count / run_1.camera_count
                scalability = fps_ratio / camera_ratio if camera_ratio > 0 else 0
                
                print(f"  FPS (1→{run_last.camera_count} caméras): {fps_ratio:.2f}x (idéal: {camera_ratio:.2f}x)")
                print(f"  Scalabilité: {scalability:.2f} (1.0 = linéaire)")
                
                if scalability >= 0.8:
                    print("  ✓ Scalabilité: Excellente")
                elif scalability >= 0.5:
                    print("  ⚠ Scalabilité: Bonne")
                else:
                    print("  ✗ Scalabilité: Insuffisante")
        
        print("=" * 80)
    
    def print_test_journal(self):
        """Affiche le journal d'essais."""
        if not self.test_runs:
            print("Aucun test exécuté")
            return
        
        print("\n" + "=" * 80)
        print("JOURNAL D'ESSAIS")
        print("=" * 80)
        
        for i, run in enumerate(self.test_runs, 1):
            print(f"\n--- Test #{i} ---")
            print(f"Date: {run.date}")
            print(f"Configuration: {run.configuration}")
            print(f"Caméras: {run.camera_count}")
            print(f"Backend IA: {run.ai_backend}")
            print(f"Machine: {run.machine}")
            
            print(f"\nRésultats:")
            for metric, value in run.results.items():
                print(f"  {metric}: {value}")
            
            if run.observations:
                print(f"\nObservations:")
                for obs in run.observations:
                    print(f"  - {obs}")
            
            if run.problems:
                print(f"\nProblèmes rencontrés:")
                for problem in run.problems:
                    print(f"  - {problem}")
            
            if run.fixes:
                print(f"\nCorrectifs:")
                for fix in run.fixes:
                    print(f"  - {fix}")
        
        print("\n" + "=" * 80)
    
    def generate_html_report(self, output_path: str = "test_report.html"):
        """
        Génère un rapport HTML.
        
        Args:
            output_path: Chemin du fichier de sortie
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SentinelAI - Rapport de Tests</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
        .section {{ margin: 30px 0; }}
    </style>
</head>
<body>
    <h1>SentinelAI - Rapport de Tests</h1>
    <p>Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="section">
        <h2>Tableau de Résultats</h2>
        <table>
            <tr>
                <th>Test</th>
                <th>Objectif</th>
                <th>Mesuré</th>
                <th>Résultat</th>
            </tr>
"""
        
        for name, target in self.performance_targets.items():
            measured_str = f"{target.measured_value:.2f} {target.unit}" if target.measured_value is not None else "N/A"
            target_str = f"{target.target_value:.2f} {target.unit}"
            result_class = target.result.lower() if target.result else ""
            result_str = target.result if target.result else "N/A"
            
            html += f"""
            <tr>
                <td>{target.name}</td>
                <td>{target_str}</td>
                <td>{measured_str}</td>
                <td class="{result_class}">{result_str}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Journal d'Essais</h2>
"""
        
        for i, run in enumerate(self.test_runs, 1):
            html += f"""
        <h3>Test #{i}</h3>
        <p><strong>Date:</strong> {run.date}</p>
        <p><strong>Configuration:</strong> {run.configuration}</p>
        <p><strong>Caméras:</strong> {run.camera_count}</p>
        <p><strong>Backend IA:</strong> {run.ai_backend}</p>
        <p><strong>Machine:</strong> {run.machine}</p>
        
        <h4>Résultats</h4>
        <ul>
"""
            for metric, value in run.results.items():
                html += f"            <li>{metric}: {value}</li>\n"
            
            html += "        </ul>\n"
            
            if run.observations:
                html += "        <h4>Observations</h4>\n        <ul>\n"
                for obs in run.observations:
                    html += f"            <li>{obs}</li>\n"
                html += "        </ul>\n"
            
            if run.problems:
                html += "        <h4>Problèmes</h4>\n        <ul>\n"
                for problem in run.problems:
                    html += f"            <li>{problem}</li>\n"
                html += "        </ul>\n"
            
            if run.fixes:
                html += "        <h4>Correctifs</h4>\n        <ul>\n"
                for fix in run.fixes:
                    html += f"            <li>{fix}</li>\n"
                html += "        </ul>\n"
        
        html += """
    </div>
    
    <div class="section">
        <h2>Conclusion</h2>
        <p>Ce rapport a été généré automatiquement par le système de test de SentinelAI.</p>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Rapport HTML généré: {output_path}")
    
    def save_json_report(self, output_path: str = "test_report.json"):
        """
        Sauvegarde le rapport en JSON.
        
        Args:
            output_path: Chemin du fichier de sortie
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "performance_targets": {
                name: {
                    "name": target.name,
                    "target_value": target.target_value,
                    "unit": target.unit,
                    "measured_value": target.measured_value,
                    "result": target.result
                }
                for name, target in self.performance_targets.items()
            },
            "test_runs": [
                {
                    "date": run.date,
                    "configuration": run.configuration,
                    "camera_count": run.camera_count,
                    "ai_backend": run.ai_backend,
                    "machine": run.machine,
                    "results": run.results,
                    "observations": run.observations,
                    "problems": run.problems,
                    "fixes": run.fixes
                }
                for run in self.test_runs
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Rapport JSON sauvegardé: {output_path}")
    
    def get_version_1_0_status(self) -> Dict[str, bool]:
        """
        Retourne le statut des critères pour la version 1.0.
        
        Returns:
            Dictionnaire des critères et leur statut
        """
        criteria = {
            "pipeline_functional": False,  # Pipeline fonctionnel bout en bout
            "ai_detection_real": False,  # Détection IA sur flux réels
            "support_4_cameras": False,  # Support 4 caméras simultanées
            "latence_objectives": False,  # Latence conforme objectifs
            "no_ui_blocking": False,  # Aucun blocage UI après heures
            "auto_reconnect": False,  # Reconnexion automatique
            "recording_notifications": False,  # Enregistrement et notifications fonctionnels
            "test_report": False  # Rapport tests démontrant performances
        }
        
        # Vérifier les objectifs de performance
        latency_ok = self.performance_targets["total_latency"].result == "PASS"
        fps_ok = self.performance_targets["fps"].result == "PASS"
        memory_ok = self.performance_targets["memory"].result == "PASS"
        
        criteria["latence_objectives"] = latency_ok and fps_ok and memory_ok
        
        # Vérifier si des tests ont été exécutés
        criteria["test_report"] = len(self.test_runs) > 0
        
        # Vérifier support multi-caméras
        if self.test_runs:
            max_cameras = max(run.camera_count for run in self.test_runs)
            criteria["support_4_cameras"] = max_cameras >= 4
        
        return criteria
    
    def print_version_1_0_status(self):
        """Affiche le statut des critères pour la version 1.0."""
        print("\n" + "=" * 80)
        print("STATUT VERSION 1.0")
        print("=" * 80)
        
        criteria = self.get_version_1_0_status()
        
        print(f"\n{'Critère':<40} {'Statut':<10}")
        print("-" * 80)
        
        criteria_names = {
            "pipeline_functional": "Pipeline fonctionnel bout en bout",
            "ai_detection_real": "Détection IA sur flux réels",
            "support_4_cameras": "Support 4 caméras simultanées",
            "latence_objectives": "Latence conforme objectifs",
            "no_ui_blocking": "Aucun blocage UI après heures",
            "auto_reconnect": "Reconnexion automatique",
            "recording_notifications": "Enregistrement et notifications fonctionnels",
            "test_report": "Rapport tests démontrant performances"
        }
        
        for key, name in criteria_names.items():
            status = "✓" if criteria[key] else "✗"
            print(f"{name:<40} {status:<10}")
        
        print("=" * 80)
        
        total = len(criteria)
        passed = sum(criteria.values())
        print(f"\nProgression: {passed}/{total} critères ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("✓ VERSION 1.0 PRÊTE")
        else:
            print(f"⚠ VERSION 1.0 NON PRÊTE ({total - passed} critère(s) manquant(s))")
        
        print("=" * 80)


def get_test_reporter() -> TestReporter:
    """
    Fonction utilitaire pour récupérer le TestReporter.
    
    Returns:
        Instance singleton du TestReporter
    """
    if not hasattr(get_test_reporter, "_instance"):
        get_test_reporter._instance = TestReporter()
    return get_test_reporter._instance
