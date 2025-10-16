export function init() {
  const c = document.getElementById('content');
  c.innerHTML = `
  <div class="card">
    <h2>Gerador de Contrato</h2>
    <input id="partes" placeholder="Nome das partes">
    <input id="servico" placeholder="Serviço">
    <input id="valor" placeholder="Valor (R$)">
    <button id="gerarContrato">Gerar Contrato</button>
  </div>`;

  document.getElementById('gerarContrato').onclick = () => {
    const doc = new jsPDF();
    const partes = document.getElementById('partes').value;
    const servico = document.getElementById('servico').value;
    const valor = document.getElementById('valor').value;
    doc.text(`Contrato de ${servico}`, 10, 20);
    doc.text(`Entre: ${partes}`, 10, 40);
    doc.text(`Valor acordado: R$${valor}`, 10, 60);
    doc.text("Kdefy", 90, 280, { angle: 45 });
    doc.save(`Contrato_${servico}.pdf`);
    log('contratos', 'Contrato criado');
  };
}

function log(tool, msg) {
  window.dbPromise.result.transaction('logs', 'readwrite')
    .objectStore('logs').add({ tool, msg, date: new Date().toISOString() });
}
