// BaixaTube - popup.js

async function verificarServidor() {
  const dot = document.getElementById('dot');
  const titulo = document.getElementById('status-titulo');

  dot.className = 'dot checando';
  titulo.textContent = 'Verificando...';

  try {
    const resp = await fetch('http://localhost:9999/status', {
      signal: AbortSignal.timeout(3000)
    });
    const data = await resp.json();

    if (data.ok) {
      dot.className = 'dot online';
      titulo.textContent = 'Online ✓';
      titulo.style.color = '#00e676';
    } else {
      throw new Error();
    }
  } catch {
    dot.className = 'dot offline';
    titulo.textContent = 'Offline';
    titulo.style.color = '#ff1744';
  }
}

document.getElementById('btn-verificar').addEventListener('click', verificarServidor);

// Verifica ao abrir o popup
verificarServidor();
