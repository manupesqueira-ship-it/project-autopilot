import subprocess, sys
from pathlib import Path
ROOT=Path(r"C:\Users\manup\projects\project-autopilot")
REM=ROOT/"infra"/"remotion-render"; ASM=ROOT/"infra"/"assembler"
for s in sys.argv[1:]:
    W=ASM/"out"/"_editorial_reels"/s
    print(f"=== render {s} ===", flush=True)
    subprocess.run(f'npx remotion render EditorialReel "{W/"video.mp4"}" --props="{W/"props.json"}" --crf=16 --concurrency=2 --timeout=600000 --log=error', cwd=str(REM), shell=True, check=True)
    subprocess.run([sys.executable, "finish_reel_audio.py", s], cwd=str(ASM), check=True)
    print(f"=== DONE {s} ===", flush=True)
