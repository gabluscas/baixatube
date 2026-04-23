// BaixaTube - content.js
// Injeta o painel de download na página do YouTube

const SERVIDOR = 'http://localhost:9999';

let painelInjetado = false;

function isShort() {
  return window.location.pathname.startsWith('/shorts/');
}

function getVideoInfo() {
  const titulo = document.title.replace(' - YouTube', '').trim();
  const url = window.location.href;
  let videoId = null;
  if (isShort()) {
    videoId = window.location.pathname.split('/shorts/')[1]?.split('?')[0];
  } else {
    videoId = new URLSearchParams(window.location.search).get('v');
  }
  const thumb = videoId ? `https://img.youtube.com/vi/${videoId}/mqdefault.jpg` : '';
  return { titulo, url, videoId, thumb };
}

function criarPainel() {
  const ehShort = isShort();
  if (painelInjetado || (!window.location.search.includes('v=') && !ehShort)) return;

  const info = getVideoInfo();

  const painel = document.createElement('div');
  painel.id = 'baixatube-painel';
  painel.innerHTML = `
    <div class="bt-card">
      <div class="bt-header">
        <span class="bt-logo">▼ BaixaTube</span>
        <span class="bt-status" id="bt-status">pronto</span>
      </div>

      <div class="bt-titulo" id="bt-titulo" title="${info.titulo}">${info.titulo}</div>

      <div class="bt-opcoes">
        <div class="bt-grupo">
          <label class="bt-label">Formato</label>
          <div class="bt-btns-formato">
            <button class="bt-fmt ativo" data-fmt="mp4">🎬 MP4</button>
            <button class="bt-fmt" data-fmt="mp3">🎵 MP3</button>
            <button class="bt-fmt" data-fmt="webm">📹 WebM</button>
          </div>
        </div>

        <div class="bt-grupo" id="bt-grupo-qualidade">
          <label class="bt-label">Qualidade</label>
          <div class="bt-btns-qualidade">
            <button class="bt-qual" data-qual="bestvideo+bestaudio">🏆 Melhor</button>
            <button class="bt-qual ativo" data-qual="1080">1080p</button>
            <button class="bt-qual" data-qual="720">720p</button>
            <button class="bt-qual" data-qual="480">480p</button>
          </div>
        </div>
      </div>

      <button class="bt-baixar" id="bt-baixar">
        <span id="bt-baixar-text">⬇ Baixar Vídeo</span>
        <div class="bt-spinner" id="bt-spinner"></div>
      </button>

      <div class="bt-progress" id="bt-progress">
        <div class="bt-progress-bar" id="bt-progress-bar"></div>
      </div>

      <div class="bt-log" id="bt-log"></div>
    </div>
  `;

  // Injeta no lugar certo dependendo do tipo de página
  let alvo;
  if (ehShort) {
    alvo = document.querySelector('ytd-shorts')
        || document.querySelector('#shorts-container')
        || document.querySelector('ytd-page-manager')
        || document.body;
    painel.style.position = 'fixed';
    painel.style.bottom = '80px';
    painel.style.right = '16px';
    painel.style.width = '300px';
    painel.style.zIndex = '9999';
  } else {
    alvo = document.querySelector('#below') || document.querySelector('#secondary') || document.body;
  }
  alvo.prepend(painel);
  painelInjetado = true;

  // Lógica de seleção de formato
  let formatoAtual = 'mp4';
  let qualidadeAtual = '1080';

  painel.querySelectorAll('.bt-fmt').forEach(btn => {
    btn.addEventListener('click', () => {
      painel.querySelectorAll('.bt-fmt').forEach(b => b.classList.remove('ativo'));
      btn.classList.add('ativo');
      formatoAtual = btn.dataset.fmt;

      const grupoQual = document.getElementById('bt-grupo-qualidade');
      const textoBaixar = document.getElementById('bt-baixar-text');

      if (formatoAtual === 'mp3') {
        grupoQual.style.display = 'none';
        textoBaixar.textContent = '⬇ Baixar Áudio';
      } else {
        grupoQual.style.display = 'block';
        textoBaixar.textContent = '⬇ Baixar Vídeo';
      }
    });
  });

  painel.querySelectorAll('.bt-qual').forEach(btn => {
    btn.addEventListener('click', () => {
      painel.querySelectorAll('.bt-qual').forEach(b => b.classList.remove('ativo'));
      btn.classList.add('ativo');
      qualidadeAtual = btn.dataset.qual;
    });
  });

  // Botão baixar
  document.getElementById('bt-baixar').addEventListener('click', async () => {
    const info = getVideoInfo();
    const btn = document.getElementById('bt-baixar');
    const spinner = document.getElementById('bt-spinner');
    const texto = document.getElementById('bt-baixar-text');
    const status = document.getElementById('bt-status');
    const log = document.getElementById('bt-log');
    const progressBar = document.getElementById('bt-progress-bar');
    const progress = document.getElementById('bt-progress');

    btn.disabled = true;
    spinner.style.display = 'block';
    texto.style.display = 'none';
    status.textContent = 'baixando...';
    status.className = 'bt-status baixando';
    progress.style.display = 'block';
    log.textContent = '';

    // Simula progresso visual enquanto aguarda
    let prog = 0;
    const intervalo = setInterval(() => {
      prog = Math.min(prog + Math.random() * 8, 90);
      progressBar.style.width = prog + '%';
    }, 400);

    try {
      const params = new URLSearchParams({
        url: info.url,
        formato: formatoAtual,
        qualidade: qualidadeAtual,
        titulo: info.titulo
      });

      const resp = await fetch(`${SERVIDOR}/download?${params}`);
      const data = await resp.json();

      clearInterval(intervalo);

      if (data.ok) {
        progressBar.style.width = '100%';
        progressBar.style.background = 'var(--bt-verde)';
        status.textContent = 'concluído ✓';
        status.className = 'bt-status concluido';
        log.textContent = `✓ Salvo em: ${data.arquivo}`;
      } else {
        throw new Error(data.erro || 'Erro desconhecido');
      }
    } catch (err) {
      clearInterval(intervalo);
      progressBar.style.width = '100%';
      progressBar.style.background = 'var(--bt-vermelho)';
      status.textContent = 'erro';
      status.className = 'bt-status erro';

      if (err.message.includes('Failed to fetch')) {
        log.textContent = '⚠ Servidor offline. Execute: python servidor.py';
      } else {
        log.textContent = `✗ ${err.message}`;
      }
    } finally {
      btn.disabled = false;
      spinner.style.display = 'none';
      texto.style.display = 'inline';
    }
  });
}

// Observa mudanças de URL (SPA do YouTube)
let urlAtual = location.href;
const observer = new MutationObserver(() => {
  if (location.href !== urlAtual) {
    urlAtual = location.href;
    painelInjetado = false;
    const antigo = document.getElementById('baixatube-painel');
    if (antigo) antigo.remove();
    setTimeout(criarPainel, 1500);
  }
});

observer.observe(document.body, { childList: true, subtree: true });

// Inicializa
const ehShortInicial = window.location.pathname.startsWith('/shorts/');
setTimeout(criarPainel, ehShortInicial ? 1000 : 2000);
