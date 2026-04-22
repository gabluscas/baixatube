# ▼ BaixaTube

> Extensão do Chrome + servidor local para baixar vídeos e áudios do YouTube.

![Status](https://img.shields.io/badge/status-funcional-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Manifest](https://img.shields.io/badge/manifest-v3-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Sobre o projeto

O BaixaTube surgiu da necessidade de baixar vídeos do YouTube sem depender de sites externos cheios de anúncios ou extensões duvidosas da Chrome Web Store.

A solução foi criar uma arquitetura em duas partes: uma **extensão Chrome** que injeta um painel diretamente na página do YouTube, e um **servidor Python local** que processa o download usando `yt-dlp` e `ffmpeg`. Nenhum dado sai da sua máquina.

---

## Como funciona

```
[Extensão Chrome]  ──HTTP──▶  [servidor.py :9999]
   painel na página                    │
                                  yt-dlp + ffmpeg
                                       │
                              ~/Downloads/BaixaTube/
```

---

## Funcionalidades

- Baixa vídeos em **MP4** (até 1080p ou melhor qualidade disponível)
- Extrai **áudio em MP3** com qualidade máxima
- Suporte a **WebM**
- Seleção de qualidade: Melhor, 1080p, 720p, 480p
- Painel injetado diretamente na página do YouTube
- Popup com **status do servidor em tempo real**
- Barra de progresso visual
- Compatível com navegação SPA do YouTube (troca de vídeos sem recarregar)

---

## Pré-requisitos

- Python 3.8+
- [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) instalado e no PATH
- Google Chrome

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/gabluscas/baixatube.git
cd baixatube
```

### 2. Inicie o servidor

```bash
cd servidor
pip install -r requirements.txt
python servidor.py
```

O servidor sobe em `http://localhost:9999` e salva os arquivos em `~/Downloads/BaixaTube/`.

### 3. Carregue a extensão no Chrome

1. Acesse `chrome://extensions`
2. Ative o **Modo do desenvolvedor**
3. Clique em **Carregar sem compactação**
4. Selecione a pasta `extensao/`

---

## Uso

1. Com o servidor rodando, abra qualquer vídeo no YouTube
2. Role a página — o painel BaixaTube aparece abaixo do player
3. Escolha formato e qualidade
4. Clique em **⬇ Baixar**

---

## Estrutura do projeto

```
baixatube/
├── extensao/
│   ├── manifest.json     # Manifest V3
│   ├── content.js        # Painel injetado no YouTube
│   ├── content.css       # Estilos do painel
│   ├── background.js     # Service worker
│   ├── popup.html        # Interface do ícone na toolbar
│   ├── popup.js          # Verificação de status do servidor
│   └── icons/
└── servidor/
    ├── servidor.py        # Servidor HTTP local (sem dependências externas além do yt-dlp)
    └── requirements.txt
```

---

## O que aprendi neste projeto

- Estrutura de extensões Chrome com **Manifest V3** e suas restrições de segurança
- Como o YouTube serve streams em **DASH** (áudio e vídeo separados) e por que isso exige ffmpeg para remuxar
- Criação de um servidor HTTP do zero em Python usando apenas `http.server` da stdlib
- Problemas reais de ambiente: múltiplos Pythons no PATH, localização de executáveis, CORS em localhost
- Injeção de UI em páginas de terceiros via content scripts e como lidar com SPAs que não recarregam a página

---

## Observações

- Esta extensão é para **uso pessoal**. A política da Chrome Web Store proíbe extensões de download do YouTube, por isso ela não pode ser publicada na store.
- Respeite os direitos autorais dos criadores de conteúdo.

---

## Autor

**Lucas Gabriel Alves Araújo**  
Estudante de Engenharia Elétrica | Desenvolvedor em formação  
[LinkedIn](www.linkedin.com/in/lucas-gabriel-alves-araújo-422705203) · [GitHub](https://github.com/gabluscas)
