export function init() {
  const c = document.getElementById('content');
  c.innerHTML = `
  <div class="card">
    <h2>Gerador de PDF</h2>
    <input id="pdfTitle" placeholder="Título">
    <textarea id="pdfBody" rows="5" placeholder="Conteúdo"></textarea>
    <button id="genPDF">Gerar PDF</button>
    <canvas id="pdfPreview" style="margin-top:20px;width:100%"></canvas>
  </div>`;

  document.getElementById('genPDF').onclick = () => {
    const doc = new jsPDF();
    const title = document.getElementById('pdfTitle').value;
    const body = document.getElementById('pdfBody').value;
    doc.text(title, 10, 20);
    doc.text(body, 10, 40);
    doc.text("Kdefy", 90, 280, { angle: 45 });
    doc.save(`${title || 'documento'}.pdf`);
    log('pdf', 'PDF gerado');
  };
}

function log(tool, msg) {
  const req = window.dbPromise.result.transaction('logs', 'readwrite')
    .objectStore('logs').add({ tool, msg, date: new Date().toISOString() });
}
