# Abrir o projeto para apresentacao

Os inicializadores preparam um ambiente Python separado, instalam as dependencias na primeira abertura, iniciam a API e abrem o navegador quando o servidor estiver pronto.

## Preparacao

- Instale Python 3.10 ou superior. No Windows, marque a opcao de adicionar Python ao PATH.
- Tenha uma chave da API Gemini. Se ainda nao estiver configurada no `.env`, o inicializador pedira a chave no terminal, com entrada oculta, e a salvara nesse arquivo.
- Tenha internet para instalar as dependencias e para conversar com o Gemini durante a apresentacao.
- Copie a pasta inteira do projeto e extraia o ZIP antes de abrir. Nao transporte `.venv` ou `.venv-apresentacao`: cada computador cria seu proprio ambiente.
- Abra e teste antes da apresentacao para concluir a instalacao e conferir sua chave. Nao compartilhe o `.env` ou sua chave em arquivos publicos.

## Windows

De dois cliques em **`iniciar_windows.bat`**.

O navegador abrira em http://127.0.0.1:8000/. Mantenha o terminal aberto durante a apresentacao. Para encerrar, pressione **Ctrl+C** nessa janela e confirme se o Windows perguntar se deseja encerrar o arquivo em lotes.

## macOS (Mac)

Na primeira vez, abra o Terminal na pasta do projeto e execute:

```bash
chmod +x iniciar_mac.command
```

Depois, de dois cliques em **`iniciar_mac.command`**. O navegador abrira automaticamente. Mantenha o Terminal aberto e pressione **Ctrl+C** para encerrar.

Voce tambem pode iniciar pelo Terminal sem alterar a permissao:

```bash
bash iniciar_mac.command
```

## iOS (iPhone/iPad)

iOS e diferente de macOS: os inicializadores rodam no computador. Para apresentar pelo Safari no iPhone/iPad, deixe o servidor rodando em um Windows ou Mac conectado a mesma rede Wi-Fi.

No Windows, abra o PowerShell na pasta do projeto e execute:

```powershell
.\iniciar_windows.bat --rede-local
```

No Mac, pelo Terminal:

```bash
bash iniciar_mac.command --rede-local
```

Descubra o IPv4 do computador: no Windows, execute `ipconfig` e procure o endereco do adaptador Wi-Fi; no Mac, consulte Ajustes do Sistema > Wi-Fi > Detalhes > TCP/IP.

No Safari, abra `http://IP-DO-COMPUTADOR:8000/`. Por exemplo: `http://192.168.1.20:8000/`.

Se o firewall solicitar permissao, permita acesso pela rede privada. Redes de convidados podem bloquear a comunicacao entre dispositivos. Use uma rede confiavel: `--rede-local` disponibiliza a API para dispositivos da rede e o projeto nao possui autenticacao.

## Solucao de problemas

- **Python nao encontrado:** instale Python 3.10 ou superior e reabra o inicializador.
- **Falha ao instalar dependencias:** confira a internet e tente novamente. Se faltar `venv`, use uma instalacao completa do Python.
- **Porta ocupada:** encerre a outra instancia ou use outra porta, como nos exemplos abaixo.
- **Navegador nao abriu:** acesse http://127.0.0.1:8000/ manualmente, ou a porta escolhida.
- **Erro da IA:** confira a chave e o modelo no `.env`, a internet e a disponibilidade/cota da API Gemini.

Windows, usando outra porta:

```powershell
.\iniciar_windows.bat --porta 8001
```

Mac, usando outra porta:

```bash
bash iniciar_mac.command --porta 8001
```

Os argumentos `--porta` e `--rede-local` podem ser usados juntos.

## Arquivos

- `iniciar_windows.bat`: inicializador para Windows.
- `iniciar_mac.command`: inicializador para macOS.
- `iniciar.py`: configura o ambiente e abre o servidor/navegador.
- `.venv-apresentacao/`: ambiente automatico, reutilizado nas proximas aberturas. As dependencias sao reinstaladas quando `requirements.txt` muda.

Estes arquivos sao scripts executaveis; Python precisa estar instalado. A simulacao continua sem registrar pagamentos ou solicitacoes de reembolso.
