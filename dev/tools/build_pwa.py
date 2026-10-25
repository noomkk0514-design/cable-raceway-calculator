"""Build pwa/index.html from cable-raceway-calculator.html (the artifact source).
Usage: python tools/build_pwa.py cable-raceway-calculator.html pwa/index.html
"""
import sys, pathlib
src, dst = map(pathlib.Path, sys.argv[1:3])
h = src.read_text(encoding="utf-8")

h = h.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
head_end = h.index("</style>") + len("</style>")
head, body = h[:head_end], h[head_end:]

reset = """
/* Base reset (replaces the artifact skeleton) */
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;-webkit-text-size-adjust:100%}
img{max-width:100%}
[hidden]{display:none!important}
.hdr-actions{margin-left:auto;display:flex;gap:8px;align-items:center}
.install{font:inherit;font-size:14px;font-weight:600;border:0;border-radius:6px;padding:8px 14px;background:var(--accent);color:var(--on-accent);cursor:pointer}
.offline{font-size:12px;font-weight:600;padding:3px 10px;border-radius:999px;background:#3a4652;color:#E9EEF2}
.toast{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:20;display:flex;gap:12px;align-items:center;background:var(--head);color:var(--head-ink);padding:10px 14px;border-radius:8px;box-shadow:0 6px 24px rgba(0,0,0,.25);font-size:14px;max-width:calc(100% - 32px)}
.toast button{font:inherit;font-weight:600;border:0;border-radius:5px;padding:5px 10px;background:var(--accent);color:var(--on-accent);cursor:pointer}
</style>"""
head = head[: -len("</style>")] + reset

meta = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#18232D">
<meta name="description" content="เลือกขนาดสายไฟ เบรกเกอร์ สายดิน แรงดันตก ท่อร้อยสาย Wireway และรางเคเบิล">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Cable Calc">
"""

anchor = "      <p>เลือกขนาดสายไฟ · แรงดันตก · ท่อร้อยสาย · รางเดินสาย/รางเคเบิล · สายดิน</p>\n    </div>\n"
assert anchor in body
body = body.replace(anchor, anchor +
    '    <div class="hdr-actions"><span class="offline" id="offline" hidden>ออฟไลน์</span>'
    '<button type="button" class="install" id="install" hidden>ติดตั้งแอป</button></div>\n', 1)
body = body.replace("<p>การคำนวณทั้งหมดทำในเบราว์เซอร์ ไม่มีการส่งข้อมูลออกไปภายนอก</p>",
    "<p>การคำนวณทั้งหมดทำในเครื่อง ไม่มีการส่งข้อมูลออกไปภายนอก และใช้งานออฟไลน์ได้หลังเปิดครั้งแรก</p>")

pwa_js = """
<div class="toast" id="update" hidden><span>มีเวอร์ชันใหม่</span><button type="button" id="reload">อัปเดต</button></div>
<script>
(function(){
  /* Install prompt (Chrome/Edge/Android). iOS: Share > Add to Home Screen. */
  let deferred = null;
  const btn = document.getElementById("install");
  window.addEventListener("beforeinstallprompt", e => { e.preventDefault(); deferred = e; btn.hidden = false; });
  btn.addEventListener("click", async () => {
    if (!deferred) return;
    deferred.prompt(); await deferred.userChoice; deferred = null; btn.hidden = true;
  });
  window.addEventListener("appinstalled", () => { btn.hidden = true; });

  const off = document.getElementById("offline");
  const net = () => { off.hidden = navigator.onLine; };
  window.addEventListener("online", net); window.addEventListener("offline", net); net();

  /* Hash links from manifest shortcuts */
  window.addEventListener("hashchange", () => {
    const t = location.hash.slice(1), b = document.querySelector('nav.tabs button[data-tab="'+t+'"]');
    if (b) b.click();
  });

  if (!("serviceWorker" in navigator)) return;
  navigator.serviceWorker.register("sw.js").then(reg => {
    const toast = document.getElementById("update");
    const offer = w => { toast.hidden = false; document.getElementById("reload").onclick = () => w.postMessage("skipWaiting"); };
    if (reg.waiting && navigator.serviceWorker.controller) offer(reg.waiting);
    reg.addEventListener("updatefound", () => {
      const w = reg.installing;
      w.addEventListener("statechange", () => { if (w.state === "installed" && navigator.serviceWorker.controller) offer(w); });
    });
  }).catch(() => {});
  let reloading = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => { if (!reloading) { reloading = true; location.reload(); } });
})();
</script>
"""
out = meta + head + "\n</head>\n<body>\n" + body.rstrip() + "\n" + pwa_js + "</body>\n</html>\n"
dst.write_text(out, encoding="utf-8", newline="\n")
print("wrote", dst, len(out))
