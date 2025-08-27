# 🐾 Dr. Tobias - Especialista em Pets

## 🌟 Visão Geral

Dr. Tobias é um assistente veterinário virtual inteligente construído com Streamlit e IA avançada. Ele oferece uma experiência personalizada de orientação sobre pets, com autenticação segura de usuários, armazenamento persistente de conversas sobre animais e conselhos personalizados baseados no perfil de cada usuário e seus pets.

## 🐾 Funcionalidades Principais

### 1. Sistema de Autenticação
- Login seguro através de contas Google
- Autenticação gerenciada pelo Streamlit (`st.user`)
- Proteção das conversas sobre pets
- Registro automático de novos usuários

### 2. Interface de Conversa Veterinária
- Design acolhedor e profissional
- Componentes nativos do Streamlit para conversas sobre pets
- Respostas personalizadas em tempo real
- Ambiente seguro para discutir questões dos seus animais

### 3. Sistema de Memória das Conversas
- Armazenamento completo do histórico de conversas sobre pets
- Organização de conversas por usuário
- Capacidade de retomar conversas anteriores sobre animais
- Backup automático das interações veterinárias

### 4. Perfil Personalizado para Pets
- Informações coletadas para personalização:
  * Nome/apelido do tutor
  * Idade
  * Experiência com pets
  * Tipos de pets que possui/possuiu
  * Situação atual com pets
  * Email e foto do perfil
- Conselhos personalizados baseados no perfil

### 5. Sistema de Logs Veterinário
- Registro detalhado respeitando a privacidade
- Monitoramento de:
  * Acessos ao sistema
  * Criação de novas conversas
  * Atualizações de perfil de pets

### 6. IA Especializada em Pets
- Utiliza a API da OpenAI com prompts especializados em veterinária
- Personalidade calorosa e profissional do Dr. Tobias
- Conselhos baseados em cuidados veterinários
- Orientações sempre priorizando o bem-estar animal

### 7. Páginas Essenciais
- **🐾 Conversar:** Interface principal para chat com Dr. Tobias
- **👤 Meu Perfil:** Gestão das informações sobre pets
- **📜 Termos e Privacidade:** Políticas adaptadas para assistente veterinário

### 8. Segurança e Responsabilidade
- Máxima proteção das conversas sobre pets
- Termos adaptados para orientação veterinária
- Disclaimers importantes sobre limitações da IA
- Orientações para buscar veterinário presencial quando necessário

## 🛠️ Configuração do Ambiente

### Requisitos do Sistema
- Python 3.7+
- Conta no Firebase para armazenar conversas
- Conta na OpenAI para a IA do Dr. Tobias
- Ambiente para execução Streamlit

### Passo a Passo de Instalação

1. **Clone o Repositório:**
```bash
git clone <url_do_repositorio>
cd dr-tobias
```

2. **Configure o Ambiente Virtual:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Instale as Dependências:**
```bash
pip install -r requirements.txt
```

## 🔧 Configuração das APIs

### Firebase
1. Crie um projeto no Firebase Console
2. Configure o Firestore Database para armazenar conversas
3. Gere e baixe a chave privada
4. Configure as credenciais no projeto

### OpenAI
1. Crie uma conta na OpenAI
2. Gere uma API Key
3. Configure para usar GPT-4o-mini (otimizado para assistência veterinária)
4. Adicione as credenciais ao projeto

## 📁 Estrutura do Banco de Dados

### Coleção Principal: `dr-tobias`
- Documentos por email do usuário
- Subcoleções:
  * `logs`: Registro de atividades
  * `chats`: Conversas sobre pets armazenadas

### Estrutura de Dados do Usuário
```json
{
    "email": "string",
    "nome_completo": "string",
    "foto": "string (URL)",
    "idade": "number",
    "experiencia_pets": "string",
    "tipos_pets": "array", 
    "situacao_atual": "string",
    "data_cadastro": "timestamp",
    "ultimo_acesso": "timestamp",
    "primeiro_acesso_concluido": "boolean",
    "consentimento_assistente": "boolean"
}
```

## 🚀 Como Executar

1. **Desenvolvimento Local:**
```bash
streamlit run app.py
```

2. **Deploy no Streamlit Cloud:**
- Configure os secrets no painel do Streamlit Cloud
- Conecte com seu repositório
- Deploy automático

## 🎨 Personalização do Dr. Tobias

### Elementos Visuais
- Logos e ícones relacionados a pets em `arquivos/`
- Estilos CSS com tema veterinário acolhedor
- Cores e emojis que transmitem profissionalismo e cuidado

### Personalidade do Assistente
- Prompts especializados em cuidados com pets
- Linguagem calorosa e profissional
- Orientações para todos os tipos de pets
- Conselhos práticos e seguros

### Campos de Perfil Pet
- Informações relevantes para orientação veterinária
- Perguntas sobre experiência com animais
- Privacidade máxima dos dados pessoais

## 🔒 Segurança e Privacidade

- Autenticação via Google
- Proteção máxima das conversas sobre pets
- Criptografia de dados sensíveis
- Políticas claras sobre uso de dados pessoais
- Disclaimers sobre limitações da IA veterinária

## 💡 Propósito e Limitações

### O que Dr. Tobias Faz:
- Oferece orientações gerais sobre cuidados com pets
- Escuta com atenção questões sobre comportamento animal
- Dá suporte e orientações práticas sobre pets
- Ajuda com dúvidas básicas de cuidados veterinários

### O que Dr. Tobias NÃO Faz:
- Não substitui atendimento veterinário profissional
- Não diagnostica doenças ou prescreve medicamentos
- Não é adequado para emergências veterinárias
- Não oferece conselhos médicos ou cirúrgicos

### Quando Buscar Ajuda Veterinária Profissional:
- Sintomas de doença ou lesão
- Emergências veterinárias
- Comportamentos anormais preocupantes
- Problemas que requerem diagnóstico profissional

**Recursos de Emergência:**
- Hospital Veterinário 24h
- Clínica Veterinária de Emergência
- Emergência: 190 (se envolver risco humano)

## 📚 Arquivos do Projeto

### Estrutura Principal
```
├── app.py                     # Entrada principal
├── requirements.txt           # Dependências
├── termos_e_privacidade.md   # Termos adaptados
├── .streamlit/
│   └── secrets.toml          # Configurações secretas
├── paginas/
│   ├── chatbot.py            # Dr. Tobias chat
│   ├── perfil.py             # Perfil de pets
│   ├── termos.py             # Página de termos
│   └── funcoes.py            # Utilitários
└── arquivos/                 # Recursos visuais
```

## 🐾 Contribuindo para Dr. Tobias

- Reporte bugs ou sugestões via Issues
- Contribuições para melhorar a assistência veterinária
- Mantenha o foco no bem-estar animal
- Preserve a confidencialidade e segurança

## 📄 Licença

Este projeto está sob a licença MIT. Dr. Tobias foi criado com cuidado para ajudar pessoas a cuidarem melhor de seus pets! 🐾 