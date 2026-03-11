from sec_edgar_downloader import Downloader
import os
from datetime import datetime
import glob

class SECScraper:
    """
    Componente Forense: Automatización de descarga de Formas 8-K y 10-Q de la SEC.
    'Primero lo primero': No dependemos de lo que dice la prensa, sino de lo que la empresa le dice al gobierno.
    """
    
    def __init__(self, storage_dir: str = "backend/data/sec_filings"):
        self.storage_dir = storage_dir
        self.dl = Downloader("Vault-Analytica", "admin@vault-analytica.local", storage_dir)
        
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def download_latest_filings(self, ticker: str, amount: int = 3):
        """Descarga las últimas presentaciones 8-K (Eventos Actuales) y 10-Q (Trimestrales)."""
        ticker = ticker.upper()
        print(f"[SEC] Iniciando descarga de registros oficiales para {ticker}...")
        
        try:
            # 8-K: Reportes de eventos materiales (demandas, fraude, cambios de CFO, etc)
            self.dl.get("8-K", ticker, after="2024-01-01", limit=amount)
            # 10-Q: Reportes financieros trimestrales (buscamos 'material weakness')
            self.dl.get("10-Q", ticker, after="2024-01-01", limit=amount)
            
            return True
        except Exception as e:
            print(f"[SEC ERROR] No se pudo obtener datos del ticker {ticker}: {e}")
            return False

    def extract_text_for_analysis(self, ticker: str) -> str:
        """
        Lee los archivos descargados y extrae el texto bruto para que el Auditor Forense
        y el modelo BERT puedan trabajar.
        """
        ticker_path = os.path.join(self.storage_dir, "sec-edgar-filings", ticker)
        full_text = ""
        
        # Buscamos archivos .txt o .html dentro de las carpetas descargadas
        search_pattern = os.path.join(ticker_path, "**", "*.txt")
        files = glob.glob(search_pattern, recursive=True)
        
        # Limitamos el análisis a los últimos 2 archivos para eficiencia (primero lo primero)
        for file_path in files[:2]:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Limpiamos un poco el HTML básico si existe
                    content = f.read()
                    full_text += content + "\n\n"
            except Exception as e:
                print(f"[SEC READ ERROR] Error leyendo {file_path}: {e}")
                
        return full_text

# --- TEST RÁPIDO ---
if __name__ == "__main__":
    scraper = SECScraper()
    # Usamos un ticker institucional para probar
    if scraper.download_latest_filings("NVDA", amount=1):
        text = scraper.extract_text_for_analysis("NVDA")
        print(f"\n[SEC] Extracción exitosa. Longitud de texto legal: {len(text)} caracteres.")
        if "material weakness" in text.lower():
            print("!!! ALERTA: DEBILIDAD MATERIAL DETECTADA EN DOCUMENTO OFICIAL !!!")
        else:
            print("AuditadoSEC: Sin anomalías críticas de texto superficial.")
