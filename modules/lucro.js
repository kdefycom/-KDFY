export function init() {
  const c = document.getElementById('content');
  c.innerHTML = `
  <div class="card">
    <h2>Calculadora de Lucro / ROI</h2>
    <input id="custo" placeholder="Custo">
    <input id="preco" placeholder="Preço de Venda">
    <input id="despesas" placeholder="Despesas">
    <button id="calc">Calcular</button>
    <div id="res"></div>
    <canvas id="grafico"></canvas>
  </div>`;

  document.getElementById('calc').onclick = () => {
    const custo = +document.getElementById('custo').value;
    const preco = +document.getElementById('preco').value;
    const desp = +document.getElementById('despesas').value;
    const lucro = preco - custo - desp;
    const roi = ((lucro / custo) * 100).toFixed(1);
    document.getElementById('res').innerHTML = `<b>Lucro:</b> R$${lucro.toFixed(2)} | ROI: ${roi}%`;
    const ctx = document.getElementById('grafico');
    new Chart(ctx, {
      type: 'bar',
      data: { labels: ['Custo', 'Lucro'], datasets: [{ data: [custo, lucro] }] },
      options: { responsive: true }
    });
    log('lucro', 'Cálculo ROI executado');
  };
}

function log(tool, msg) {
  window.dbPromise.result.transaction('logs', 'readwrite')
    .objectStore('logs').add({ tool, msg, date: new Date().toISOString() });
}
