export function init() {
  const c = document.getElementById('content');
  c.innerHTML = `
  <div class="card">
    <h2>Gerador de Postagens</h2>
    <input id="postText" placeholder="Texto do post">
    <button id="gerarPost">Gerar Imagem</button>
    <div id="postPreview" style="margin-top:20px;background:#fff;padding:20px;width:300px;text-align:center;">Prévia</div>
  </div>`;

  document.getElementById('gerarPost').onclick = () => {
    const text = document.getElementById('postText').value;
    const box = document.getElementById('postPreview');
    box.innerHTML = `<h3>${text}</h3>`;
    html2canvas(box).then(canvas => {
      const link = document.createElement('a');
      link.download = 'post_kdefy.png';
      link.href = canvas.toDataURL();
      link.click();
      log('posts', 'Postagem gerada');
    });
  };
}

function log(tool, msg) {
  window.dbPromise.result.transaction('logs', 'readwrite')
    .objectStore('logs').add({ tool, msg, date: new Date().toISOString() });
}
