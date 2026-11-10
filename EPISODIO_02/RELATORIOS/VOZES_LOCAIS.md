# Continuação — síntese local em português brasileiro

O Edge TTS continuou retornando HTTP 403 em nova verificação da rede. A leitura
das configurações do ambiente permaneceu indisponível (INVALID_ARGUMENT). Os
controles de rede e TLS não foram alterados. Não foram usados serviços pagos.

Alternativa autorizada pelo usuário na continuação: **Kokoro ONNX**, executado
inteiramente na CPU local. Roteiro não enviado a serviço externo de síntese.
Os arquivos foram obtidos da distribuição oficial do projeto, em destinos
permitidos pela rede, e seus SHA-256 foram comparados aos publicados no GitHub.

Fonte e instruções:
https://github.com/thewh1teagle/kokoro-onnx

Release: `model-files-v1.1`.

| Arquivo | SHA-256 publicado e verificado |
|---|---|
| kokoro-v1.0.int8.onnx | ae315a79b623f244700e4afb9246c46a26066782e049ba174bf3ba433970ee9c |
| voices-v1.0.bin | bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d |

Licenças declaradas pelo projeto: kokoro-onnx MIT, modelo Kokoro Apache 2.0.
ONNX Runtime é usado como runtime local; espeak-ng/phonemizer fazem a conversão
fonética local. As licenças dos pacotes acompanham suas distribuições instaladas.
As fontes DejaVu usadas nas cartelas foram incluídas com sua licença em producao/fonts.

## Perfis da alternativa

| Papel | Voz local | Velocidade | Ajuste de altura |
|---|---|---|---|
| Capi | pm_alex | 1,12× | +1,2 semitons |
| Teco | pm_santa | 1,22× | +2,6 semitons |
| Maya | pf_dora | 1,08× | +1,8 semitons |
| Narradora | pf_dora | 1,05× | +0,4 semitom |

Todos usam fonetização `pt-br`. Mantêm-se as diferenças de velocidade e a intenção
de vozes masculinas/femininas, Teco mais ágil, Maya mais aguda e narração mais calma.
**A identidade vocal é diferente da Microsoft.** As configurações aprovadas do
Episódio 01 continuam no roteiro original, sem sobrescrita, e o pipeline pode
voltar ao Edge em outra pasta de produção quando a rede permitir.

As 44 falas foram geradas. Cada MP3 tem texto/perfil/modelo assinados, checksum,
duração medida e WAV de origem preservado. Cache local e cache Edge ficam em
pastas distintas. A escolha efetiva está em ARTEFATOS/voice-provider.json.

Não se refizeram roteiro, layout provisório ou teste anterior. Criou-se a cena
final com tempos medidos; música e efeitos existentes foram sincronizados com
esses tempos. A correção pontual da trajetória preservou a animação dos personagens
e os quadros já equivalentes, com comparação entre cenas registrada nos artefatos.

## Windows

Com Python 3.12, Blender 4.3.x e FFmpeg instalados, executar na raiz do projeto:

```bat
EPISODIO_02\produzir_windows.cmd
```

O lançador prepara um venv próprio, instala dependências gratuitas, obtém modelos
oficiais com TLS e checksum, preserva recursos presentes e executa o pipeline.
Se já existir filme validado com recursos idênticos, apenas confere hashes e encerra.
Não desativa política de execução, não exige API paga e não publica.

Se os renders antigos do Episódio 01 não tiverem sido transferidos ao Windows,
essa ausência é registrada em arquivo próprio; os recursos originais obrigatórios
continuam exigidos e todos os arquivos presentes ficam protegidos por hashes.
Transfira o projeto em ZIP ou com finais de linha preservados. Não copie venvs Linux
para uso no Windows. O lançador cria build/venv-windows independentemente.

Execução nativa do lançador Windows não foi testada nesta máquina Linux. A síntese,
os checksums e o pipeline Linux são executados e validados aqui; o relatório final
registra o resultado real da produção, separadamente desta preparação multiplataforma.
