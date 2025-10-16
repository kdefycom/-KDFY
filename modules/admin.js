export function init() {
  const c = document.getElementById('content');
  c.innerHTML = `
  <div class="card"><h2>Painel Administrativo</h2>
  <canvas id="logChart"></canvas>
  </div>`;

  const tx = window.dbPromise.result.transaction('logs', 'readonly');
  const store = tx.objectStore('logs');
  const req = store.getAll();

  req.onsuccess = () => {
    const logs = req.result;
    const counts = {};
    logs.forEach(l => counts[l.tool] = (counts[l.tool] || 0) + 1);
    new Chart(document.getElementById('logChart'), {
      type: 'pie',
      data: { labels: Object.keys(counts), datasets: [{ data: Object.values(counts) }] },
      options: { responsive: true }
    });
  };
}
