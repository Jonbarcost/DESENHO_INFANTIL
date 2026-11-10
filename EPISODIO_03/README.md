# Episódio 03 — O Segredo do Riachinho

**Produção concluída e validada: 4min15s, 1920×1080 nativos, 12 fps, 48 falas e 55 tomadas com movimento.** 30 testes de automação aprovados.

 Personagens, malhas da clareira e configurações de vozes locais reaproveitados. Episódios 01 e 02 preservados. Sem publicação no YouTube.

## Produzir e retomar

Na raiz do projeto, com Blender 4.3, FFmpeg, Python 3.12 e o ambiente Kokoro local já instalado:

```sh
python -m producao.riacho EPISODIO_03/ROTEIRO/roteiro.json --tts kokoro
```

O comando gera vozes, timeline medida, cena Blender editável com animação baked, trilha original, efeitos sintetizados, mixagem, render em lotes e MP4. Renderizações válidas são retomadas. Somente um candidato aprovado nos testes recebe o nome final. Não executa upload.

A primeira execução usa os modelos gratuitos de `build/tts-models` e o Python de `build/tts-local`. Checksums e licenças estão documentados em `EPISODIO_02/RELATORIOS/VOZES_LOCAIS.md`. Os timbres locais são os utilizados no Episódio 02; não são clones das vozes Microsoft.

`--stage voices|prepare|render|assemble|verify` permite executar etapas individualmente. `--output` aceita outra pasta de produção, mas rejeita pastas de episódios anteriores. Depois de renderizar, alterações de roteiro/código/cena exigem outra saída para evitar mistura de quadros. Arquivos originais nunca são removidos.

## Revisão

O roteiro inclui correnteza e gravidade, habitat, raízes protegendo o solo e a diferença entre água transparente e água potável. Personagens ficam na margem seca. O adulto supervisor é citado na narração, fora de quadro. A coleta usa luvas e pinça e somente papéis; objetos cortantes não devem ser tocados. Recolher lixo não torna água potável.

Os relatórios verificam formato, duração, decodificação integral, falas e intervalos, níveis de áudio, quadros pretos/congelados, geometria e boca animada. `producao/qa.py` mede movimento dentro de cada tomada. `validar_sincronismo.py` compara a boca baked com o RMS dos arquivos reais; sincronismo aproximado de energia, sem visemas fonéticos.

## Próxima aventura

O gancho propõe **A Viagem da Gotinha**, introduzindo evaporação, nuvens e chuva. Copie o esquema de roteiro para EPISODIO_04, mantenha os perfis de voz e adapte a cena para os fenômenos do novo episódio. Não reutilize uma cena pronta para uma história diferente sem adaptar ações e controle de qualidade.

No Windows: execute `EPISODIO_03\produzir_windows.cmd`. O lançador instala dependências gratuitas em ambiente local e verifica os modelos antes de usá-los. Para renderizar a partir do pacote editável, use `EPISODIO_03\produzir_windows.cmd --output EPISODIO_03/RENDER_WINDOWS`, pois os masters e PNGs são regenerados. Lançador preparado, sem teste nativo no Windows.

A cena Blender contém as animações editáveis em curvas. A mixagem é feita externamente pelo pipeline, a partir das vozes, música e efeitos; o áudio não está embutido no arquivo Blender.

Os downloads estão no branch `entrega-episodio-03`: MP4 1080p, versão leve 720p e ZIP do projeto editável. Consulte `RELATORIOS/validacao-final.json` para os testes e hashes.
