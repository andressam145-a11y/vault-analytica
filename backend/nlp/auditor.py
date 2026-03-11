import re

class ForensicAuditor:
    """
    Módulo de Auditoría de Integridad y Detección de Cisnes Negros.
    Monitorea palabras clave críticas en documentos oficiales (SEC/Legal).
    """
    
    CRITICAL_KEYWORDS = [
        "fraud", "investigation", "delisting", "material weakness",
        "misleading", "restatement", "pacer", "lawsuit", "sanction",
        "doj", "sec investigation", "breach", "bankruptcy"
    ]
    
    def __init__(self):
        self.risk_score = 0.0
        self.findings = []

    def analyze_text(self, text: str, source: str = "OFFICIAL"):
        """
        Analiza un bloque de texto (ej. un Formulario 8-K o noticia).
        Aplica un peso mayor si la fuente es oficial.
        """
        self.findings = []
        text_lower = text.lower()
        matches_found = 0
        
        weight = 2.0 if source == "OFFICIAL" else 1.0
        
        for word in self.CRITICAL_KEYWORDS:
            if word in text_lower:
                count = len(re.fetchall(rf"\b{word}\b", text_lower))
                if count > 0:
                    self.findings.append({
                        "keyword": word,
                        "occurrences": count,
                        "severity": "HIGH" if weight > 1.5 else "MEDIUM"
                    })
                    matches_found += count
        
        # Cálculo de Score (Simplificado para el Core V1)
        self.risk_score = min(100.0, (matches_found * 10.0 * weight))
        
        return {
            "risk_score": self.risk_score,
            "status": "DANGER" if self.risk_score > 50 else "STABLE",
            "findings": self.findings,
            "source_reliability": "HIGH" if source == "OFFICIAL" else "LOW"
        }

    def get_integrity_lock(self, risk_report: dict) -> bool:
        """
        Retorna True si el sistema debe BLOQUEAR cualquier compra.
        """
        return risk_report["risk_score"] > 40.0

# --- TEST RÁPIDO ---
if __name__ == "__main__":
    auditor = ForensicAuditor()
    
    # Ejemplo de un texto que dispararía las alertas
    sample_sec_text = "The company is currently under a DOJ investigation regarding material weakness in financial reporting."
    
    report = auditor.analyze_text(sample_sec_text, source="OFFICIAL")
    print("=== REPORTE FORENSE DE INTEGRIDAD ===")
    print(f"Score de Riesgo: {report['risk_score']}%")
    print(f"Estado: {report['status']}")
    print(f"Hallazgos: {report['findings']}")
    print(f"Bloqueo de Seguridad: {'ACTIVO' if auditor.get_integrity_lock(report) else 'DESACTIVADO'}")
