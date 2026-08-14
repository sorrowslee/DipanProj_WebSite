#!/usr/bin/env node
/**
 * 本地預覽伺服器 —— 零依賴，不用 npm install。
 *
 *   npm run dev
 *
 * 會做三件事：
 *   1. 從 public/ 提供網站
 *   2. 自動找一個沒被佔用的埠（預設 8000，被佔用就往上找）
 *   3. 自動用預設瀏覽器打開
 *
 * 支援 Range 請求，所以 Safari 也能正常播影片。
 */

const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { exec } = require('node:child_process');

const ROOT = path.join(__dirname, '..', 'public');
const START_PORT = Number(process.env.PORT) || 8000;
const MAX_TRIES = 20;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.js':   'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.xml':  'application/xml; charset=utf-8',
  '.txt':  'text/plain; charset=utf-8',
  '.webp': 'image/webp',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
  '.mp4':  'video/mp4',
  '.webm': 'video/webm',
  '.woff2':'font/woff2',
};

function openBrowser(url) {
  const cmd = process.platform === 'darwin' ? 'open'
            : process.platform === 'win32'  ? 'start ""'
            : 'xdg-open';
  exec(`${cmd} "${url}"`, (err) => {
    if (err) console.log(`（沒能自動開啟瀏覽器，請手動打開 ${url}）`);
  });
}

const server = http.createServer((req, res) => {
  // 去掉查詢字串，並擋掉 ../ 之類的路徑穿越
  let rel = decodeURIComponent(req.url.split('?')[0]);
  if (rel.endsWith('/')) rel += 'index.html';
  const file = path.normalize(path.join(ROOT, rel));
  if (!file.startsWith(ROOT)) {
    res.writeHead(403).end('Forbidden');
    return;
  }

  fs.stat(file, (err, stat) => {
    if (err || !stat.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(`<meta charset="utf-8"><body style="background:#15110e;color:#f0e5d9;
        font-family:system-ui;padding:60px;line-height:2">
        <h1 style="font-weight:400">404</h1>
        <p>找不到 <code>${rel}</code></p>
        <p><a href="/" style="color:#ff8f4d">回首頁</a></p></body>`);
      return;
    }

    const type = MIME[path.extname(file).toLowerCase()] || 'application/octet-stream';
    // HTML 不快取，這樣改完重新整理一定看得到新的
    const cache = type.startsWith('text/html') ? 'no-store' : 'no-cache';
    const range = req.headers.range;

    if (range) {                      // 影片拖曳進度條需要
      const m = /bytes=(\d*)-(\d*)/.exec(range);
      const start = m && m[1] ? parseInt(m[1], 10) : 0;
      const end = m && m[2] ? parseInt(m[2], 10) : stat.size - 1;
      res.writeHead(206, {
        'Content-Type': type,
        'Content-Range': `bytes ${start}-${end}/${stat.size}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': end - start + 1,
        'Cache-Control': cache,
      });
      fs.createReadStream(file, { start, end }).pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Type': type,
        'Content-Length': stat.size,
        'Accept-Ranges': 'bytes',
        'Cache-Control': cache,
      });
      fs.createReadStream(file).pipe(res);
    }
  });
});

let port = START_PORT;
let tries = 0;

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE' && ++tries < MAX_TRIES) {
    port += 1;
    server.listen(port);
  } else {
    console.error('伺服器啟動失敗：', err.message);
    process.exit(1);
  }
});

server.listen(port, () => {
  const url = `http://localhost:${port}`;
  console.log('');
  console.log('  \x1b[38;5;209m燃燈劫 LAMPBLACK\x1b[0m — 本地預覽');
  console.log('');
  console.log(`  網址   \x1b[4m${url}\x1b[0m`);
  console.log(`  來源   ${path.relative(process.cwd(), ROOT) || 'public'}/`);
  console.log('');
  console.log('  改完檔案直接重新整理瀏覽器即可，按 Ctrl+C 停止。');
  console.log('');
  openBrowser(url);
});
