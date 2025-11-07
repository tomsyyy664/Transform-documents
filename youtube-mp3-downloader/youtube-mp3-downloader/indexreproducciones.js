const fs = require("fs");
const path = require("path");
const ffmpeg = require("fluent-ffmpeg");
const ffmpegPath = require("ffmpeg-static");
const youtubedl = require("youtube-dl-exec");

ffmpeg.setFfmpegPath(ffmpegPath);

// Cambia esta URL por la de tu lista de reproducción
const playlistUrl = "https://youtube.com/playlist?list=PLwzY5lgMXm_ujrXlQn1W-cnHJzzY4GNOX&si=CA52aA--5Zrb0LvH";

function sanitizeTitle(title) {
    return title.replace(/[<>:"/\\|?*]+/g, "");
}

const outputDir = path.join(__dirname, "songs");
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

async function downloadPlaylist(url) {
    try {
        console.log(`⏬ Obteniendo videos de la lista de reproducción: ${url}`);

        const playlistInfo = await youtubedl(url, {
            dumpSingleJson: true,
            noWarnings: true,
            noCheckCertificate: true,
            preferFreeFormats: true,
            addHeader: ["referer:youtube.com", "user-agent:googlebot"],
        });

        // Verifica si se obtuvieron entradas
        if (!playlistInfo || !playlistInfo.entries || playlistInfo.entries.length === 0) {
            console.error("❌ No se encontraron videos en la lista de reproducción.");
            return;
        }

        const videoUrls = playlistInfo.entries.map(entry => entry.url);

        for (const videoUrl of videoUrls) {
            await downloadVideo(videoUrl);
        }
    } catch (err) {
        console.error(`❌ Error al obtener la lista de reproducción: ${err.message}`);
    }
}

async function downloadVideo(url) {
    try {
        console.log(`⏬ Descargando desde: ${url}`);

        const info = await youtubedl(url, {
            dumpSingleJson: true,
            noWarnings: true,
            noCheckCertificate: true,
            preferFreeFormats: true,
            addHeader: ["referer:youtube.com", "user-agent:googlebot"],
        });

        const title = sanitizeTitle(info.title);
        const mp3Path = path.join(outputDir, `${title}.mp3`);
        const wavPath = path.join(outputDir, `${title}.wav`);

        await youtubedl(url, {
            extractAudio: true,
            audioFormat: "mp3",
            audioQuality: 0,
            output: mp3Path,
            ffmpegLocation: ffmpegPath
        });

        console.log(`🎵 MP3 guardado: ${mp3Path}`);

        await new Promise((resolve, reject) => {
            ffmpeg(mp3Path)
                .toFormat("wav")
                .on("end", () => {
                    console.log(`✅ Convertido a WAV: ${wavPath}`);
                    fs.unlinkSync(mp3Path); // Elimina el archivo MP3 después de la conversión
                    resolve();
                })
                .on("error", (err) => {
                    console.error(`❌ Error al convertir: ${err.message}`);
                    reject(err);
                })
                .save(wavPath);
        });

    } catch (err) {
        console.error(`❌ Error con ${url}: ${err.message}`);
    }
}

// Inicia la descarga de la lista de reproducción
downloadPlaylist(playlistUrl);
