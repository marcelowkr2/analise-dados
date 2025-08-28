# BanVic Analytics — Dashboard & Relatório PDF

Projeto desenvolvido em **Python** com **Streamlit** e **ReportLab** para análise e visualização de dados bancários, com exportação de relatórios em PDF.

---

## 🎯 Funcionalidades
- Upload ou leitura automática de arquivos CSV (transações, agências, clientes)
- Dashboard interativo com KPIs e gráficos (Plotly)
- Ranking das agências e segmentação de clientes
- Análises adicionais: sazonalidade e teste estatístico pares vs ímpares
- Exportação de relatório PDF com:
  - Capa
  - KPIs
  - Gráficos
  - Ranking Top 10
  - Metodologia e recomendações
  - Rodapé com data/hora, autor e paginação

---

## 📂 Estrutura do Projeto

```
banvic-analytics/
│
├── app.py                     # Aplicação principal Streamlit
├── requirements.txt           # Dependências do projeto
├── README.md                  # Documentação do projeto
├── styles.css                 # Estilos customizados
│
├── utils/
│   └── pdf_utils.py           # Funções para gerar PDF com ReportLab
│
├── data/                      # Pasta para dados CSV
│   ├── transacoes.csv         # Arquivo de transações (você coloca aqui)
│   ├── agencias.csv           # Arquivo de agências (opcional)
│   └── clientes.csv           # Arquivo de clientes (opcional)
│
├── assets/                    # Logo ou imagens para relatório
│   └── logo.png               # (opcional) Logo BanVic
│
└── reports/                   # Relatórios PDF gerados

```


---

## ▶️ Como Executar
1. Crie um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows

- Instalar dependências - pip install -r requirements.txt
- Rodar Projeto - streamlit run app.py

