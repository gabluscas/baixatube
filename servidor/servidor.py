"""
BaixaTube - servidor.py
Servidor local que recebe pedidos da extensão e executa yt-dlp
"""

import subprocess
import sys
import os
import re
import json
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# ─── Configurações ────────────────────────────────────────────────────────────

PORTA = 9999
PASTA_DOWNLOADS = str(Path.home() / "Downloads" / "BaixaTube")

# Garante que a pasta de downloads existe
os.makedirs(PASTA_DOWNLOADS, exist_ok=True)

# ─── Cores no terminal ────────────────────────────────────────────────────────

class Cor:
    RESET  = "\033[0m"
    VERMELHO = "\033[91m"
    VERDE  = "\033[92m"
    AMARELO = "\033[93m"
    AZUL   = "\033[94m"
    CINZA  = "\033[90m"
    NEGRITO = "\033[1m"

def log(nivel, msg):
    hora = datetime.now().strftime("%H:%M:%S")
    cores = {
        "INFO":  Cor.AZUL,
        "OK":    Cor.VERDE,
        "ERRO":  Cor.VERMELHO,
        "AVISO": Cor.AMARELO,
    }
    cor = cores.get(nivel, Cor.RESET)
    print(f"{Cor.CINZA}{hora}{Cor.RESET} {cor}{nivel:5}{Cor.RESET}  {msg}")

# ─── Sanitiza nome de arquivo ─────────────────────────────────────────────────

def sanitizar_nome(titulo):
    nome = re.sub(r'[\\/*?:"<>|]', '', titulo)
    nome = nome.strip().replace('  ', ' ')
    return nome[:80] if len(nome) > 80 else nome

# ─── Handler HTTP ─────────────────────────────────────────────────────────────

class BaixaTubeHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Silencia o log padrão do HTTPServer

    def headers_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json; charset=utf-8")

    def do_OPTIONS(self):
        self.send_response(200)
        self.headers_cors()
        self.end_headers()

    def responder(self, dados, codigo=200):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.headers_cors()
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        # ── GET /status ───────────────────────────────────────────────────────
        if parsed.path == "/status":
            self.responder({"ok": True, "versao": "1.0.0", "pasta": PASTA_DOWNLOADS})
            return

        # ── GET /download ─────────────────────────────────────────────────────
        if parsed.path == "/download":
            url       = params.get("url",       [""])[0]
            formato   = params.get("formato",   ["mp4"])[0]
            qualidade = params.get("qualidade", ["1080"])[0]
            titulo    = params.get("titulo",    ["video"])[0]

            if not url:
                self.responder({"ok": False, "erro": "URL não informada."}, 400)
                return

            # Roda o download em thread separada para não bloquear
            resultado = {"ok": False, "arquivo": "", "erro": ""}
            evento = threading.Event()

            def executar():
                try:
                    arquivo = self._executar_download(url, formato, qualidade, titulo)
                    resultado["ok"] = True
                    resultado["arquivo"] = arquivo
                except Exception as e:
                    resultado["erro"] = str(e)
                finally:
                    evento.set()

            t = threading.Thread(target=executar, daemon=True)
            t.start()
            evento.wait(timeout=300)  # Aguarda até 5 minutos

            if resultado["ok"]:
                self.responder(resultado)
            else:
                self.responder(resultado, 500)
            return

        self.responder({"erro": "Rota não encontrada."}, 404)

    def _executar_download(self, url, formato, qualidade, titulo):
        nome = sanitizar_nome(titulo) or "video"
        log("INFO", f"Iniciando download: {nome[:50]}...")
        log("INFO", f"Formato: {formato} | Qualidade: {qualidade}")

        cmd = ytdlp_cmd()

        # Configurações por formato
        if formato == "mp3":
            cmd += [
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "0",
            ]
            extensao = "mp3"

        elif formato == "webm":
            if qualidade == "bestvideo+bestaudio":
                cmd += ["-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]"]
            else:
                cmd += ["-f", f"bestvideo[height<={qualidade}][ext=webm]+bestaudio[ext=webm]/best[height<={qualidade}][ext=webm]"]
            extensao = "webm"

        else:  # mp4
            if qualidade == "bestvideo+bestaudio":
                cmd += ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"]
            else:
                cmd += ["-f", f"bestvideo[height<={qualidade}][ext=mp4]+bestaudio[ext=m4a]/best[height<={qualidade}][ext=mp4]"]
            cmd += ["--merge-output-format", "mp4"]
            extensao = "mp4"

        # Caminho de saída
        saida = os.path.join(PASTA_DOWNLOADS, f"{nome}.%(ext)s")
        cmd += [
            "-o", saida,
            "--no-playlist",
            "--no-warnings",
            "--ffmpeg-location", _ffmpeg_path(),
            url
        ]

        log("INFO", f"Executando: {' '.join(cmd[:4])}...")

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if proc.returncode != 0:
            erro = proc.stderr.strip().split("\n")[-1] if proc.stderr else "Erro desconhecido"
            log("ERRO", f"yt-dlp falhou: {erro}")
            raise Exception(erro)

        arquivo_final = os.path.join(PASTA_DOWNLOADS, f"{nome}.{extensao}")
        log("OK", f"Salvo em: {arquivo_final}")
        return arquivo_final


def _ffmpeg_path():
    """Tenta localizar o ffmpeg no sistema."""
    for candidato in ["ffmpeg", "/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
        try:
            subprocess.run([candidato, "-version"], capture_output=True, check=True)
            return candidato
        except Exception:
            continue
    return "ffmpeg"  # Deixa o yt-dlp tentar encontrar


# ─── Verificação de dependências ──────────────────────────────────────────────

def ytdlp_cmd():
    """Retorna o comando correto para chamar o yt-dlp."""
    # Tenta executável direto primeiro
    for candidato in ["yt-dlp", "yt-dlp.exe"]:
        try:
            subprocess.run([candidato, "--version"], capture_output=True, check=True)
            return [candidato]
        except Exception:
            continue
    # Fallback: chama como módulo Python (pip install yt-dlp sem entry point no PATH)
    return [sys.executable, "-m", "yt_dlp"]


def verificar_dependencias():
    ok = True

    try:
        cmd = ytdlp_cmd()
        subprocess.run(cmd + ["--version"], capture_output=True, check=True)
        log("OK", f"yt-dlp encontrado ({' '.join(cmd)}).")
    except Exception:
        log("ERRO", "yt-dlp não encontrado! Execute: pip install yt-dlp")
        ok = False

    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        log("OK", "ffmpeg encontrado.")
    except FileNotFoundError:
        log("AVISO", "ffmpeg não encontrado. Downloads em MP4/WebM podem falhar.")
        log("AVISO", "Instale em: https://ffmpeg.org/download.html")

    return ok


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"""
{Cor.NEGRITO}{Cor.VERMELHO}
  ██████╗  █████╗ ██╗██╗  ██╗ █████╗ ████████╗██╗   ██╗██████╗ ███████╗
  ██╔══██╗██╔══██╗██║╚██╗██╔╝██╔══██╗╚══██╔══╝██║   ██║██╔══██╗██╔════╝
  ██████╔╝███████║██║ ╚███╔╝ ███████║   ██║   ██║   ██║██████╔╝█████╗
  ██╔══██╗██╔══██║██║ ██╔██╗ ██╔══██║   ██║   ██║   ██║██╔══██╗██╔══╝
  ██████╔╝██║  ██║██║██╔╝ ██╗██║  ██║   ██║   ╚██████╔╝██████╔╝███████╗
  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝
{Cor.RESET}""")

    print(f"  {Cor.CINZA}Servidor local para a extensão BaixaTube{Cor.RESET}\n")

    log("INFO", "Verificando dependências...")
    if not verificar_dependencias():
        sys.exit(1)

    log("INFO", f"Pasta de downloads: {PASTA_DOWNLOADS}")
    log("INFO", f"Iniciando servidor em http://localhost:{PORTA}")
    print()

    servidor = HTTPServer(("localhost", PORTA), BaixaTubeHandler)

    try:
        log("OK", f"Servidor rodando. Pressione Ctrl+C para parar.\n")
        servidor.serve_forever()
    except KeyboardInterrupt:
        print()
        log("INFO", "Servidor encerrado.")
        servidor.shutdown()


if __name__ == "__main__":
    main()