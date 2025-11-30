// Small helpers for UI: copy to clipboard and toggle collapse
function copyToClipboard(text, el) {
  if (!navigator.clipboard) {
    // fallback
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    ta.remove();
    flashCopy(el);
    return;
  }
  navigator.clipboard.writeText(text).then(() => flashCopy(el));
}

function flashCopy(el) {
  if (!el) return;
  const original = el.innerText;
  el.innerText = 'Copié';
  el.classList.add('copied');
  setTimeout(() => { el.innerText = original; el.classList.remove('copied'); }, 1200);
}

function toggleCollapse(id) {
  const el = document.getElementById(id);
  if (!el) return;
  if (el.style.display === 'none' || getComputedStyle(el).display === 'none') el.style.display = '';
  else el.style.display = 'none';
}

// Attach click handlers for elements with data-copy="selector" attribute
document.addEventListener('click', function(e){
  const btn = e.target.closest('[data-copy]');
  if (!btn) return;
  const selector = btn.getAttribute('data-copy');
  const src = document.querySelector(selector);
  if (!src) return;
  copyToClipboard(src.innerText.trim(), btn);
});
