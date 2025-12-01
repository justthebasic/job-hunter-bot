# Job Hunter Bot 🤖

O **Job Hunter Bot** é uma ferramenta de automação inteligente projetada para simplificar e acelerar o processo de candidatura a vagas de emprego. Ele utiliza navegação automatizada (Playwright) e Inteligência Artificial (OpenAI GPT-4o) para extrair detalhes de vagas, adaptar seu currículo (CV) especificamente para cada oportunidade e gerar um PDF otimizado para ATS (Applicant Tracking Systems).

## 🚀 Funcionalidades

-   **Extração Inteligente & Stealth**: Navega até a URL da vaga usando técnicas de "stealth" para evitar detecção de bots. Extrai apenas o conteúdo relevante (Título, Empresa, Skills, Descrição), ignorando menus e rodapés.
-   **Adaptação de CV (Tailoring)**:
    -   **Otimização ATS**: Reescreve seu Resumo Profissional e reordena suas Skills para se alinhar perfeitamente aos requisitos da vaga.
    -   **Keywords & Verbos de Ação**: Garante que as palavras-chave da vaga estejam presentes e utiliza verbos de ação fortes.
    -   **Preservação de Dados**: Mantém seus dados de contato e histórico intactos, focando apenas na relevância.
-   **Geração de PDF Profissional**: Converte o CV adaptado (Markdown) em um PDF limpo e formatado usando `wkhtmltopdf` e CSS padronizado, garantindo leitura perfeita por robôs e humanos.
-   **Autenticação Persistente**: Realize login uma única vez e o bot reutilizará sua sessão (cookies/storage) para acessar vagas no LinkedIn, Glassdoor, etc., sem precisar logar novamente ou enfrentar 2FA.
-   **Logging Estruturado**: Acompanhe cada passo do processo através de logs detalhados no console e em arquivo.

## 🛠️ Tecnologias Utilizadas

-   **Python 3.10+**: Linguagem base.
-   **Playwright & Playwright-Stealth**: Para automação de navegador robusta e indetectável.
-   **OpenAI API (GPT-4o-mini)**: O "cérebro" que entende a vaga e reescreve o CV com precisão de especialista.
-   **wkhtmltopdf & pdfkit**:
    -   *Por que usamos?* O `wkhtmltopdf` usa o motor de renderização WebKit para converter HTML em PDF com fidelidade visual pixel-perfect, permitindo o uso de CSS padrão para um design limpo e profissional.
-   **Markdown2**: Para converter o texto gerado pela IA em HTML.

## 📋 Pré-requisitos

1.  **Python 3**: Certifique-se de ter o Python instalado.
2.  **Google Chrome**: Necessário para o Playwright.
3.  **wkhtmltopdf**: Necessário para gerar os PDFs.
    -   *Linux (Debian/Ubuntu)*: `sudo apt-get install wkhtmltopdf`
    -   *Windows/Mac*: Baixe o instalador no [site oficial](https://wkhtmltopdf.org/downloads.html).

## ⚙️ Instalação e Configuração

1.  **Clone o repositório**:
    ```bash
    git clone https://github.com/justthebasic/job-hunter-bot.git
    cd job-hunter-bot
    ```

2.  **Crie um ambiente virtual e instale as dependências**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # No Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Instale os navegadores do Playwright**:
    ```bash
    playwright install chromium
    ```

4.  **Configure as Variáveis de Ambiente**:
    Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

    ```env
    OPENAI_API_KEY=sk-sua-chave-aqui
    # CHROME_USER_DATA_DIR: Opcional, usado apenas para referência.
    ```

5.  **Configuração de Autenticação (Setup Único)**:
    Para evitar bloqueios e a necessidade de login constante, o bot usa um arquivo de sessão (`auth.json`).
    Execute o script de setup:
    ```bash
    python setup_auth.py
    ```
    - Uma janela do Chrome abrirá.
    - Faça login no LinkedIn (e outros sites que pretende usar).
    - Volte ao terminal e pressione ENTER para salvar a sessão.
    - Um arquivo `auth.json` será criado. O bot usará este arquivo automaticamente nas próximas execuções.

6.  **Prepare seu CV Base**:
    Edite o arquivo `base_cv.md` na raiz do projeto com suas informações reais. Este será o modelo mestre que a IA usará.

## 🏃‍♂️ Como Usar

1.  Execute o bot:
    ```bash
    python main.py
    ```
2.  Insira a URL da vaga quando solicitado.
3.  O bot irá:
    -   Carregar sua sessão salva (`auth.json`).
    -   Acessar a página da vaga em modo "stealth".
    -   Extrair e limpar a descrição da vaga.
    -   Gerar uma versão adaptada do seu CV focada na vaga.
    -   Salvar o PDF na pasta `generated_cvs/`.
    -   (Simulado) Iniciar o processo de upload.

## 📂 Estrutura do Projeto

```
job-hunter-bot/
├── assets/
│   └── style.css       # Estilos CSS otimizados para ATS
├── generated_cvs/      # Onde os PDFs finais são salvos
├── src/
│   ├── cv_generator.py # Lógica de adaptação (Prompt ATS) e geração de PDF
│   ├── exceptions.py   # Exceções customizadas
│   ├── logger.py       # Configuração de logs
│   ├── scraper.py      # Navegação stealth e extração de dados
│   └── submitter.py    # Lógica de envio (Upload)
├── auth.json           # Arquivo de sessão (gerado pelo setup_auth.py)
├── base_cv.md          # Seu currículo mestre em Markdown
├── config.py           # Gerenciamento de configurações
├── main.py             # Ponto de entrada
├── requirements.txt    # Dependências Python
├── setup_auth.py       # Script de configuração de login
└── README.md           # Documentação
```

## ⚠️ Notas Importantes

-   **Segurança**: O arquivo `auth.json` contém seus cookies de sessão. **Nunca compartilhe este arquivo** ou faça commit dele em repositórios públicos (ele já está no `.gitignore`).
-   **Custos da API**: O uso da API da OpenAI gera custos. O modelo `gpt-4o-mini` foi escolhido por ser extremamente eficiente e barato para essa tarefa.
