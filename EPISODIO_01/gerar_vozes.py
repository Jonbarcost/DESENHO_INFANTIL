
import asyncio
from pathlib import Path
import edge_tts

base = Path(r"C:\ESTUDIO_INFANTIL\EPISODIO_01")
roteiro = base / "ROTEIRO" / "episodio_01.txt"
destino = base / "VOZES"

vozes = {
    "NARRADORA": ("pt-BR-FranciscaNeural", "+5%", "+5Hz"),
    "MAYA": ("pt-BR-FranciscaNeural", "+8%", "+18Hz"),
    "TECO": ("pt-BR-AntonioNeural", "+22%", "+35Hz"),
    "CAPI": ("pt-BR-AntonioNeural", "+12%", "+15Hz"),
}

async def gerar():
    cena = 0
    contador = 0

    for linha in roteiro.read_text(encoding="utf-8-sig").splitlines():
        linha = linha.strip()

        if linha.startswith("CENA"):
            cena += 1
            continue

        if ":" not in linha:
            continue

        personagem, fala = linha.split(":", 1)
        personagem = personagem.strip().upper()
        fala = fala.strip()

        if personagem not in vozes or not fala:
            continue

        contador += 1
        voz, velocidade, tom = vozes[personagem]

        arquivo = destino / (
            f"cena_{cena:02d}_{contador:03d}_"
            f"{personagem.lower()}.mp3"
        )

        print(f"Gerando: {arquivo.name}", flush=True)

        comunicacao = edge_tts.Communicate(
            text=fala,
            voice=voz,
            rate=velocidade,
            pitch=tom
        )

        await comunicacao.save(str(arquivo))

    print(f"Concluido: {contador} falas geradas.")

asyncio.run(gerar())
