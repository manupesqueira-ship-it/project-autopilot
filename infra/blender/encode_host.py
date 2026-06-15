"""
Encode secuencia PNG (alpha) -> WebM VP9 transparente, sube a catbox, imprime URL.
Uso: python encode_host.py
"""
import subprocess, os, uuid, urllib.request, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "out")
WEBM = os.path.join(HERE, "coin.webm")
FFMPEG = os.environ.get("FFMPEG_BIN") or r"C:\Users\manup\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"

pngs = sorted(glob.glob(os.path.join(OUT, "coin_*.png")))
if not pngs:
    print("NO PNGS in", OUT); sys.exit(1)
print(f"[..] {len(pngs)} frames -> webm vp9 alpha")

cmd = [FFMPEG, "-y", "-framerate", "30",
       "-i", os.path.join(OUT, "coin_%04d.png"),
       "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
       "-b:v", "0", "-crf", "26", "-an", WEBM]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("FFMPEG FAIL\n", r.stderr[-2000:]); sys.exit(1)
print(f"[ok] webm {os.path.getsize(WEBM)}B -> {WEBM}")

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
