# Sistema de Transcrição de Áudio

Este programa oferece uma interface gráfica para capturar áudio do microfone em tempo real e convertê-lo em texto, salvando automaticamente em um arquivo. Perfeito para transcrição de reuniões, aulas, entrevistas ou qualquer situação onde você precisa documentar comunicação verbal.

## Funcionalidades

- **Transcrição em tempo real**: Converte automaticamente fala em texto usando a API do Google Speech Recognition
- **Interface gráfica intuitiva**: Controles simples para iniciar e parar a transcrição
- **Configurações ajustáveis**: Personalize a sensibilidade do microfone e o tempo de pausa entre frases
- **Registro visual de atividades**: Log detalhado das transcrições e eventos do sistema
- **Salva automaticamente**: Todas as transcrições são salvas em um arquivo de texto com data e hora

## Requisitos do Sistema

- Python 3.6+
- Windows, macOS ou Linux
- Microfone funcional
- Conexão com a internet (necessária para API de reconhecimento de voz)

## Instalação

### 1. Instale as dependências necessárias:

```bash
pip install SpeechRecognition pyaudio
pip install psutil  # Opcional, para otimização de prioridade do processo
pip install pystray
```

### 2. Baixe o código fonte:

Salve o arquivo `transcricao_app.py` no seu computador.

### 3. Execute o programa:

```bash
python transcricao_app.py
```

## Guia de Uso

### Interface Básica

- **Iniciar Transcrição**: Clique para começar a captura e transcrição do áudio
- **Parar Transcrição**: Interrompe o processo de transcrição
- **Log de Atividades**: Mostra as transcrições recentes e mensagens do sistema
- **Indicador de Status**: Mostra visualmente se a transcrição está ativa (verde) ou parada (vermelho)

### Ajustes Avançados

#### Sensibilidade (Energy Threshold)

Controla quão alto um som precisa ser para ser reconhecido como fala:

- **Valores mais baixos (100-300)**: Capta sons mais suaves, ideal para ambientes silenciosos
- **Valores mais altos (500-1000)**: Ignora ruídos de fundo, melhor para ambientes barulhentos

#### Tempo de Pausa (Pause Threshold)

Define quanto tempo de silêncio indica o final de uma frase:

- **Valores menores (0.3-0.7s)**: Processa frases mais rapidamente, ideal para fala contínua
- **Valores maiores (1.0-2.0s)**: Permite pausas naturais dentro de uma frase, ideal para fala pausada

## Configuração para Inicialização Automática

### Criando um Executável

1. Instale o PyInstaller:

```bash
pip install pyinstaller
```

2. Crie o executável:

```bash
pyinstaller --onefile --windowed --icon=microfone.ico transcricao_app.py
```

O arquivo .exe será criado na pasta `dist`.

### Adicionando à Inicialização do Windows

1. Pressione `Win + R` e digite `shell:startup`
2. Crie um atalho para o seu executável nesta pasta

### Criando um Atalho na Área de Trabalho

1. Clique com o botão direito no arquivo executável
2. Selecione "Enviar para" → "Área de trabalho (criar atalho)"
3. Para personalizar o ícone:
   - Clique com o botão direito no atalho e selecione "Propriedades"
   - Clique em "Alterar ícone" e escolha um ícone personalizado

## Método Alternativo (sem PyInstaller)

1. Crie um arquivo `iniciar_transcricao.bat` com o seguinte conteúdo:

```bat
@echo off
cd "C:\Caminho\Para\Seu\Script"
pythonw "C:\Caminho\Para\Seu\Script\transcricao_app.py"
```

2. Adicione este arquivo .bat à pasta de inicialização do Windows

## Solução de Problemas

### O programa não reconhece o microfone

- Verifique se o microfone está corretamente conectado
- Confirme se o microfone é o dispositivo de entrada padrão nas configurações do Windows
- Tente usar um microfone diferente

### A transcrição não está funcionando

- Verifique sua conexão com a internet
- Aumente a sensibilidade (valor menor) se sua voz não estiver sendo detectada
- Fale claramente e perto do microfone
- Tente em um ambiente mais silencioso

### O programa trava ou fecha inesperadamente

- Verifique se todas as dependências estão corretamente instaladas
- Execute o programa com privilégios administrativos
- Verifique o console para mensagens de erro detalhadas

## Arquivos de Saída

As transcrições são salvas no arquivo `transcricoes.txt` no mesmo diretório do programa. Cada transcrição inclui um carimbo de data e hora no formato:

```
[2025-04-16 15:30:45] Texto transcrito aqui.
```

## Limitações

- A qualidade da transcrição depende da clareza do áudio e da pronúncia
- Necessita de conexão com a internet para usar a API do Google Speech Recognition
- Pode ter dificuldades com vocabulário técnico ou específico
- Suporta principalmente o idioma português-brasileiro, mas pode ser configurado para outros idiomas

## Créditos

Este programa utiliza:

- SpeechRecognition para processamento de áudio
- Google Speech Recognition API para conversão de voz para texto
- Tkinter para a interface gráfica

## Licença

Este programa é distribuído sob a licença MIT. Sinta-se livre para usar, modificar e distribuir conforme necessário.
