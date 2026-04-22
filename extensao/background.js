// BaixaTube - background.js

chrome.runtime.onInstalled.addListener(() => {
  console.log('BaixaTube instalado.');
});

// Permite mensagens do content script
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.tipo === 'status') {
    chrome.action.setBadgeText({ text: msg.texto });
    chrome.action.setBadgeBackgroundColor({ color: msg.cor || '#ff3d00' });
  }
  return true;
});
