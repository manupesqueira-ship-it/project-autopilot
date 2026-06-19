"""
Encode secuencia PNG (alpha) -> WebM VP9 transparente. Opcionalmente sube a
catbox e imprime URL (solo si hace falta hospedarlo para un render remoto).

Uso:
  python encode_host.py                                  # coin (out/coin_*.png -> coin.webm + upload)
  python encode_host.py --dir out_demo --prefix demo_ --out demo.webm --no-upload
  python encode_host.py --dir out_chart --prefix bar_ --out chart3d.webm --no-upload

Parametros (todos opcionales; defaults = la moneda, por compatibilidad):
  --dir <sub>      subcarpeta con los PNG (default 'out')
  --prefix <p>     prefijo de los PNG (default 'coin_')
  --out <name>     nombre del .webm de salida (default '<prefix sin _>.webm')
  --fps <n>        framerate (default 30)
  --no-upload      NO subir a catbox (pipeline local $0: Remotion lee el archivo)
"""
import subprocess, os, uuid, urllib.request, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = os.environ.get("FFMPEG_BIN") or r"C:\Users\manup\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"


def _arg(name, default):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


SUBDIR = _arg("--dir", "out")
PREFIX = _arg("--prefix", "coin_")
FPS = _arg("--fps", "30")
OUT = os.path.join(HERE, SUBDIR)
WEBM = os.path.join(HERE, _arg("--out", f"{PREFIX.rstrip('_')}.webm"))
UPLOAD = "--no-upload" not in sys.argv

pngs = sorted(glob.glob(os.path.join(OUT, f"{PREFIX}*.png")))
if not pngs:
    print(f"NO PNGS ({PREFIX}*.png) in", OUT); sys.exit(1)
print(f"[..] {len(pngs)} frames -> webm vp9 alpha")

cmd = [FFMPEG, "-y", "-framerate", str(FPS),
       "-i", os.path.join(OUT, f"{PREFIX}%04d.png"),
       "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
       "-b:v", "0", "-crf", "26", "-an", WEBM]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("FFMPEG FAIL\n", r.stderr[-2000:]); sys.exit(1)
print(f"[ok] webm {os.path.getsize(WEBM)}B -> {WEBM}")

if not UPLOAD:
    print("LOCAL (sin subir):", WEBM)
    sys.exit(0)

def catbox(path, name, ctype):
    data = open(path, "rb").read()
    b = "----WB" + uuid.uuid4().hex
    pre = (f"--{b}\r\nContent-Disposition: form-data; name=\"reqtype\"\r\n\r\nfileupload\r\n"
           f"--{b}\r\nContent-Disposition: form-data; name=\"fileToUpload\"; filename=\"{name}\"\r\nContent-Type: {ctype}\r\n\r\n").encode()
    post = f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request("https://catbox.moe/user/api.php", data=pre + data + post,
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}", "User-Agent": "curl/8"})
    return urllib.request.urlopen(req, timeout=180).read().decode().strip()

url = catbox(WEBM, "coin.webm", "video/webm")
print("WEBM_URL:", url)
