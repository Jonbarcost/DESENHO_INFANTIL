
import subprocess
import os
from pathlib import Path

base = Path(r"C:\ESTUDIO_INFANTIL\EPISODIO_01")
export = base / "EXPORTACAO"
cenas = base / "CENAS"

ffmpeg = next(
    Path(r"C:\ESTUDIO_INFANTIL\ffmpeg").rglob("ffmpeg.exe")
)

video = export / "teste_animacao.mp4"
audio = export / "episodio_01_audio.mp3"
saida = export / "episodio_01_narrativo.mp4"

# Duracoes aproximadas das seis partes
partes = [
    ("A Clareira Encantada", 5.7),
    ("A Descoberta", 13.8),
    ("Vamos Plantar!", 8.0),
    ("Cuidando da Sementinha", 1.0),
    ("A Magica Acontece", 13.3),
    ("Ate a Proxima!", 8.5),
]

# O video 3D de 3 segundos sera repetido nesta previa.
# A montagem definitiva tera animacoes proprias para cada cena.

comando = [
    str(ffmpeg), "-y",
    "-stream_loop", "-1",
    "-i", str(video),
    "-i", str(audio),
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    "-movflags", "+faststart",
    str(saida)
]

subprocess.run(comando, check=True)

print("PREVIA NARRATIVA CRIADA")
print(saida)
