// index.js — descarga WAVs desde YouTube o playlists, con soporte de cookies y fallback completo
const fs = require("fs");
const path = require("path");
const ffmpegPath = require("ffmpeg-static");
const ytdlp = require("yt-dlp-exec");

// === Configuración: mezcla vídeos y playlists aquí ===
const uncheckedUrls = [
  "https://www.youtube.com/watch?v=2UXpZPqjOIM&list=PLxA687tYuMWjmrWhl-bXEC_CBwbSTuDJQ",
];

const outputDir = path.join(__dirname, "songs");
const includeIdInFilename = true;

// === Helpers ===
function sanitizeTitle(t) {
  return (t || "audio").replace(/[<>:\"/\\|?*]+/g, "").trim();
}
function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}
function findLatestFileByExt(dir, ext) {
  const files = fs.readdirSync(dir).filter(f => f.toLowerCase().endsWith("." + ext));
  let pick = null, tmax = -1;
  for (const f of files) {
    const stat = fs.statSync(path.join(dir, f));
    if (stat.mtimeMs > tmax) { tmax = stat.mtimeMs; pick = f; }
  }
  return pick ? path.join(dir, pick) : null;
}
function targetBaseName(title, id) {
  const safe = sanitizeTitle(title);
  return includeIdInFilename && id ? `${safe} [${id}]` : safe;
}
function possibleExistingPaths(dir, title, id) {
  const names = [];
  const baseWithId = targetBaseName(title, id);
  if (baseWithId) names.push(path.join(dir, `${baseWithId}.wav`));
  const baseNoId = targetBaseName(title, null);
  if (baseNoId) names.push(path.join(dir, `${baseNoId}.wav`));
  return Array.from(new Set(names));
}
function existsAny(paths) {
  return paths.some(p => fs.existsSync(p));
}

// === Parámetros yt-dlp globales ===
const commonFlags = {
  format: "bestaudio[ext=m4a]/bestaudio[acodec^=opus]/bestaudio/best",
  retries: 10,
  "fragment-retries": 10,
  "http-chunk-size": 10 * 1024 * 1024,
  "geo-bypass": true,
  "cookies-from-browser": "chrome", // usa cookies locales de Chrome (muy importante)
  "extractor-args": "youtube:player_client=android", // desbloquea streams con restricciones
};

// === Expansión de playlists ===
async function expandInputs(urls) {
  const result = [];
  for (const url of urls) {
    if (!url) continue;
    if (/[\?&]list=/.test(url) || /\/playlist\?/.test(url)) {
      console.log(`📜 Expandiendo playlist: ${url}`);
      const stdout = await ytdlp(url, {
        ...commonFlags,
        "flat-playlist": true,
        print: "%(id)s",
      });
      const ids = String(stdout).split(/\r?\n/).map(s => s.trim()).filter(Boolean);
      ids.forEach(id => result.push(`https://www.youtube.com/watch?v=${id}`));
    } else {
      result.push(url);
    }
  }
  return result;
}

(async () => {
  ensureDir(outputDir);

  const allVideoUrls = await expandInputs(uncheckedUrls);
  if (allVideoUrls.length === 0) {
    console.error("No hay URLs válidas.");
    process.exit(1);
  }

  for (const url of allVideoUrls) {
    try {
      console.log(`⏬ Info: ${url}`);
      let info = null;

      // Primer intento (preferido)
      try {
        info = await ytdlp(url, {
          ...commonFlags,
          "dump-single-json": true,
          "no-warnings": true,
        });
      } catch {
        console.warn(`⚠️ Formato no disponible, probando con 'bestaudio/best'...`);
        try {
          info = await ytdlp(url, {
            ...commonFlags,
            format: "bestaudio/best",
            "dump-single-json": true,
            "no-warnings": true,
          });
        } catch {
          // Último intento: usar android extractor sin formato fijo
          console.warn(`🔁 Último intento con extractor android...`);
          try {
            info = await ytdlp(url, {
              format: "bestaudio/best",
              "dump-single-json": true,
              "no-warnings": true,
              "extractor-args": "youtube:player_client=android",
              "cookies-from-browser": "chrome",
            });
          } catch {
            console.warn(`🚫 No hay audio disponible para ${url}. Saltando este vídeo.`);
            continue;
          }
        }
      }

      const id = info.id || "";
      const title = info.title || "audio";
      const base = targetBaseName(title, id);
      const targetWav = path.join(outputDir, `${base}.wav`);

      const variants = possibleExistingPaths(outputDir, title, id);
      if (existsAny(variants)) {
        console.log(`⏭️ Ya existe: ${path.basename(targetWav)} — se salta la descarga.`);
        continue;
      }

      console.log("🎧 Extrayendo a WAV (yt-dlp + ffmpeg)...");
      await ytdlp(url, {
        ...commonFlags,
        "extract-audio": true,
        "audio-format": "wav",
        "audio-quality": 0,
        "ffmpeg-location": ffmpegPath,
        output: path.join(outputDir, "%(id)s.%(ext)s"),
      });

      const tmpWav = path.join(outputDir, `${id}.wav`);
      let wavPath = fs.existsSync(tmpWav)
        ? tmpWav
        : findLatestFileByExt(outputDir, "wav");

      if (!wavPath || !fs.existsSync(wavPath)) {
        throw new Error("No se encontró el WAV descargado.");
      }
      if (path.resolve(wavPath) !== path.resolve(targetWav)) {
        try {
          fs.renameSync(wavPath, targetWav);
          wavPath = targetWav;
        } catch (e) {
          console.warn("No se pudo renombrar el WAV:", e.message);
        }
      }

      console.log(`✅ WAV listo: ${wavPath}`);
    } catch (err) {
      console.error(`❌ Error con ${url}: ${err.message}`);
      try { await ytdlp([], { "rm-cache-dir": true }); } catch {}
    }
  }
})();
