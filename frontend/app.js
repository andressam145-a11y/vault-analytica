const API_URL = '/api';

document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const ticker = document.getElementById('tickerInput').value.trim();
    const news = document.getElementById('newsInput').value.trim();

    if (!ticker) {
        alert("Por favor ingrese un ticker.");
        return;
    }

    // Reset UI
    const resultsSection = document.getElementById('resultsSection');
    const statusBadge = document.getElementById('statusBadge');
    resultsSection.classList.remove('hidden');
    statusBadge.innerText = "PROCESANDO...";
    statusBadge.className = "badge";

    try {
        const response = await fetch(`${API_URL}/evaluate_asset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ticker: ticker,
                news_text: news || null
            })
        });

        if (!response.ok) {
            throw new Error('Falla en la respuesta de la API');
        }

        const data = await response.json();
        updateUI(data);

    } catch (error) {
        console.error('Error:', error);
        statusBadge.innerText = "ERROR DE CONEXIÓN";
        statusBadge.classList.add('rejected');
    }
});

function updateUI(data) {
    const statusBadge = document.getElementById('statusBadge');
    const sigmaVal = document.getElementById('sigmaVal');
    const rvolVal = document.getElementById('rvolVal');
    const kellyVal = document.getElementById('kellyVal');
    const quantMsg = document.getElementById('quantMsg');
    const sigmaProgress = document.getElementById('sigmaProgress');
    const forensicStatus = document.getElementById('forensicStatus');
    const forensicFindings = document.getElementById('forensicFindings');

    // 1. Status Signal
    statusBadge.innerText = data.status;
    statusBadge.className = `badge ${data.status.toLowerCase()}`;

    // 2. Quant Stats
    sigmaVal.innerText = data.sigma_deviation.toFixed(2);
    rvolVal.innerText = data.relative_volume.toFixed(2);
    kellyVal.innerText = `${data.kelly_allocation_percentage.toFixed(1)}%`;
    quantMsg.innerText = data.message;

    // Progress bar logic (map sigma to 0-100% based on 2.0 scale)
    let progress = (Math.abs(data.sigma_deviation) / 2.0) * 100;
    progress = Math.min(100, progress);
    sigmaProgress.style.width = `${progress}%`;
    sigmaProgress.style.backgroundColor = data.status === "APPROVED" ? "#00e676" : "#7c4dff";

    // 3. Forensic
    if (data.forensic_clear) {
        forensicStatus.innerText = "LIMPIO - SIN RIESGO ESTRUCTURAL";
        forensicStatus.style.color = "#00e676";
        forensicFindings.innerHTML = "<p>No se detectaron discrepancias en los registros oficiales.</p>";
    } else {
        forensicStatus.innerText = "ALERTA - RIESGO DE INTEGRIDAD";
        forensicStatus.style.color = "#ff5252";
        forensicFindings.innerHTML = "<p>El sistema detectó palabras clave de alto riesgo en documentos relacionados.</p>";
    }
}
