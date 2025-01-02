import streamlit as st
from anthropic import Anthropic
from collections import Counter
from fpdf import FPDF
import os
import re
from typing import Dict, List, Any
import json
from datetime import datetime 

# Configuração do modelo Claude
CLAUDE_MODEL = "claude-3-sonnet-20240229"

# Configuração do cliente Anthropic
anthropic = Anthropic(api_key=st.secrets["anthropic"]["api_key"])

# Estilo CSS
st.markdown("""
<style>
    body {
        font-family: 'Georgia', serif;
        background-color: #333333;
        color: white;
    }
    h1, h2, h3 {
        font-family: 'Georgia', serif;
        color: white;
    }
    .stButton > button {
        background-color: #6D1E1E;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-family: 'Georgia', serif;
        margin: 5px;
    }
    .stExpander {
        border: 1px solid #6D1E1E;
        border-radius: 4px;
    }
    .stExpander > div:first-child {
        background-color: #6D1E1E;
        color: white;
    }
    .result-item {
        background-color: #444444;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        border: 1px solid #6D1E1E;
        color: white;
    }
    .analysis-text {
        background-color: #222222;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        border: 1px solid #6D1E1E;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def exibir_identificacao():
    """
    Exibe e processa o formulário de identificação
    """
    st.title("Mentoria RECONECTE-SE")
    st.write("Por favor, preencha os dados abaixo para começar.")
    
    nome = st.text_input("Nome Completo", key="nome_completo")
    tempo_casado = st.number_input("Tempo de casados (em anos)", 
                                 min_value=0, 
                                 max_value=100, 
                                 key="tempo_casado")
    maior_queixa = st.text_area("Maior queixa no casamento", key="maior_queixa")
    maior_felicidade = st.text_area("Maior felicidade no casamento", key="maior_felicidade")
    
    if st.button("Iniciar Testes", key="iniciar_testes"):
        if nome and tempo_casado and maior_queixa and maior_felicidade:
            st.session_state["Identificação"] = {
                "nome": nome,
                "tempo_casado": tempo_casado,
                "maior_queixa": maior_queixa,
                "maior_felicidade": maior_felicidade
            }
            st.session_state["pagina_atual"] = "Linguagem_do_Amor"
            st.rerun()
        else:
            st.error("Por favor, preencha todos os campos antes de continuar.")

# 2. Depois, as funções de processamento
def gerenciar_fluxo_testes():
    """
    Gerencia o fluxo de progressão dos testes
    """
    ordem_testes = ["Identificação", "Linguagem_do_Amor", "Temperamentos", "Eneagrama", "Análise Final"]
    
    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = ordem_testes[0]
    
    indice_atual = ordem_testes.index(st.session_state["pagina_atual"])
    
    for i in range(indice_atual, len(ordem_testes)):
        if ordem_testes[i] not in st.session_state or st.session_state[ordem_testes[i]] is None:
            st.session_state["pagina_atual"] = ordem_testes[i]
            return
    
    st.session_state["pagina_atual"] = "Análise Final"


# Classe PDF personalizada
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(20, 20, 20)
        
        # Cores
        self.brand_color = (109, 30, 30)  # Vinho
        self.secondary_color = (64, 64, 64)  # Cinza escuro
        self.background_color = (245, 245, 245)  # Cinza claro

    def header(self):
        # Header minimalista 
        self.set_font('Times', 'B', 12)
        self.set_text_color(*self.brand_color)
        self.cell(0, 10, '', 0, 1, 'R')  # Espaço reservado para cabeçalho
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.set_text_color(*self.secondary_color)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def add_cover(self, nome: str):
        self.add_page()
        self.set_font('Times', 'B', 24)
        self.set_text_color(*self.brand_color)
        self.cell(0, 60, '', 0, 1)  # Espaço superior
        self.cell(0, 20, "DEVOLUTIVA", 0, 1, 'C')
        self.cell(0, 20, "PERSONALIZADA", 0, 1, 'C')
        
        self.ln(40)
        self.set_font('Times', 'B', 16)
        self.set_text_color(*self.secondary_color)
        self.cell(0, 10, f"ANÁLISE DE PERFIL:", 0, 1, 'C')
        self.cell(0, 10, nome.upper(), 0, 1, 'C')
        
        self.ln(50)
        self.set_font('Times', 'I', 12)
        self.cell(0, 10, datetime.now().strftime("%d/%m/%Y"), 0, 1, 'C')

    def add_section(self, title: str, content: str):
        if not content or "não encontrada" in content:
            return
            
        self.add_page()
        self.set_font('Times', 'B', 14)
        self.set_text_color(*self.brand_color)
        
        # Título com linha decorativa
        self.cell(0, 10, title, 0, 1, 'L')
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(10)
        
        # Conteúdo
        self.set_font('Times', '', 12)
        self.set_text_color(*self.secondary_color)
        self.multi_cell(0, 6, content)
        self.ln(5)

    def add_result_box(self, title: str, value: str, percentage: str = None):
        # Box com resultados
        self.set_fill_color(*self.background_color)
        self.rect(self.get_x(), self.get_y(), 170, 25, 'F')
        
        self.set_font('Times', 'B', 12)
        self.set_text_color(*self.brand_color)
        self.set_xy(self.get_x() + 5, self.get_y() + 5)
        self.cell(50, 10, title, 0, 0)
        
        self.set_font('Times', '', 12)
        self.set_text_color(*self.secondary_color)
        self.cell(70, 10, value, 0, 0)
        
        if percentage:
            self.cell(40, 10, percentage, 0, 0, 'R')
            
        self.ln(30)

def criar_prompt_analise(identificacao: Dict, linguagem_amor: Dict, temperamento: Dict, eneagrama: Dict) -> str:
    return f"""
    Analise detalhadamente os dados de {identificacao['nome']} e gere uma análise estruturada que inclua TODAS as seguintes seções, mantendo exatamente esses títulos:

    IDENTIFICAÇÃO
    Faça uma introdução completa sobre a pessoa, incluindo tempo de casamento ({identificacao['tempo_casado']} anos), principais características, queixas e alegrias no casamento.

    PERSONALIDADE
    Analise o tipo predominante no eneagrama ({eneagrama['tipo_principal']}) e como isso se manifesta no comportamento e relacionamentos.

    PONTOS POSITIVOS
    Liste e explique detalhadamente os pontos fortes com base no tipo do eneagrama e temperamento dominante.

    PONTOS NEGATIVOS
    Liste e explique os principais desafios e áreas de crescimento com base no tipo do eneagrama e temperamento.

    PONTO DE ESTRESSE
    Explique detalhadamente como a pessoa reage sob estresse, considerando seu tipo no eneagrama.

    PONTO DE SEGURANÇA
    Descreva como a pessoa se comporta em situações de segurança e conforto.

    ASAS (WINGS)
    Analise as asas do tipo principal no eneagrama e como elas influenciam a personalidade.

    PAIXÃO OU EMOÇÃO DOMINANTE
    Identifique e explique a paixão dominante do tipo no eneagrama.

    TEMPERAMENTO
    Analise o temperamento predominante ({max(temperamento.items(), key=lambda x: x[1])[0]}) e suas implicações.

    LINGUAGEM DO AMOR
    Analise as principais linguagens do amor ({max(linguagem_amor.items(), key=lambda x: x[1])[0]}) e como isso afeta os relacionamentos.

    Dados completos para referência:
    Eneagrama: {json.dumps(eneagrama, indent=2)}
    Temperamento: {json.dumps(temperamento, indent=2)}
    Linguagem do Amor: {json.dumps(linguagem_amor, indent=2)}
    """

def estruturar_analise(texto: str) -> Dict[str, str]:
    """
    Extrai as seções da análise usando expressões regulares mais precisas
    """
    secoes = {
        'identificacao': extrair_secao_especifica(texto, "IDENTIFICAÇÃO", "PERSONALIDADE"),
        'personalidade': extrair_secao_especifica(texto, "PERSONALIDADE", "PONTOS POSITIVOS"),
        'pontos_positivos': extrair_secao_especifica(texto, "PONTOS POSITIVOS", "PONTOS NEGATIVOS"),
        'pontos_negativos': extrair_secao_especifica(texto, "PONTOS NEGATIVOS", "PONTO DE ESTRESSE"),
        'ponto_estresse': extrair_secao_especifica(texto, "PONTO DE ESTRESSE", "PONTO DE SEGURANÇA"),
        'ponto_seguranca': extrair_secao_especifica(texto, "PONTO DE SEGURANÇA", "ASAS"),
        'asas': extrair_secao_especifica(texto, "ASAS \\(WINGS\\)", "PAIXÃO"),
        'paixao_dominante': extrair_secao_especifica(texto, "PAIXÃO OU EMOÇÃO DOMINANTE", "TEMPERAMENTO"),
        'temperamento': extrair_secao_especifica(texto, "TEMPERAMENTO", "LINGUAGEM DO AMOR"),
        'linguagem_amor': extrair_secao_especifica(texto, "LINGUAGEM DO AMOR", "$")
    }
    
    return secoes

def extrair_secao_especifica(texto: str, inicio: str, fim: str) -> str:
    """
    Extrai uma seção específica do texto usando regex
    """
    padrao = f"{inicio}(.*?){fim}"
    match = re.search(padrao, texto, re.DOTALL)
    if match:
        conteudo = match.group(1).strip()
        # Remove o título da seção se estiver presente
        conteudo = re.sub(f"^{inicio}[\s:]*", "", conteudo, flags=re.IGNORECASE)
        return conteudo
    return f"Seção {inicio} não encontrada"

def gerar_analise_completa(identificacao: Dict, linguagem_amor: Dict, temperamento: Dict, eneagrama: Dict) -> Dict[str, str]:
    """
    Função principal que coordena todas as análises específicas e a integração final
    """
    analises = {
        'identificacao': gerar_analise_identificacao(identificacao),
        'eneagrama': gerar_analise_eneagrama(eneagrama),
        'temperamento': gerar_analise_temperamento(temperamento),
        'linguagem_amor': gerar_analise_linguagem_amor(linguagem_amor),
        'integracao': gerar_analise_integrada(identificacao, linguagem_amor, temperamento, eneagrama)
    }
    
    return analises

def gerar_analise_eneagrama(eneagrama: Dict) -> Dict[str, str]:
    """
    Gera análise específica do Eneagrama com todas suas dimensões
    """
    prompt = f"""
    Analise detalhadamente o perfil de Eneagrama tipo {eneagrama['tipo_principal']} (pontuação: {eneagrama['porcentagem_principal']}%), 
    considerando as seguintes dimensões:

    PERSONALIDADE BASE
    - Características fundamentais do tipo {eneagrama['tipo_principal']}
    - Como essas características se manifestam nos relacionamentos
    - Desafios específicos deste tipo em relacionamentos conjugais
    - Necessidades emocionais básicas e como atendê-las

    PONTOS POSITIVOS E NEGATIVOS
    Considere especificamente:
    - Forças naturais do tipo {eneagrama['tipo_principal']} no contexto conjugal
    - Desafios recorrentes e como superá-los
    - Padrões de comportamento sob diferentes circunstâncias
    - Estratégias de desenvolvimento pessoal

    DINÂMICA DE ESTRESSE E SEGURANÇA
    Analise detalhadamente:
    - Comportamentos específicos sob estresse
    - Padrões de reação em momentos de segurança
    - Como o cônjuge pode ajudar em cada situação
    - Estratégias de autorregulação emocional

    INFLUÊNCIA DAS ASAS
    Considerando as asas:
    Asa anterior: {eneagrama['asas']['anterior']}
    Asa posterior: {eneagrama['asas']['posterior']}
    - Como cada asa modifica o comportamento base
    - Situações que ativam cada asa
    - Como usar as asas construtivamente no relacionamento

    PAIXÃO DOMINANTE E CAMINHO DE CRESCIMENTO
    - Análise da paixão/emoção dominante deste tipo
    - Como isso afeta o relacionamento conjugal
    - Caminhos específicos de crescimento
    - Práticas de desenvolvimento recomendadas

    Para cada aspecto, forneça:
    1. Exemplos concretos do cotidiano conjugal
    2. Exercícios práticos específicos
    3. Recomendações de comunicação
    4. Estratégias de desenvolvimento
    5. Orientações para o cônjuge

    Dados completos do Eneagrama: {json.dumps(eneagrama, indent=2)}
    """

    try:
        response = anthropic.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            temperature=0.7,
            system="Você é um terapeuta especializado em Eneagrama e suas aplicações em relacionamentos conjugais. Forneça análises profundas e práticas.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return estruturar_analise_eneagrama(response.content[0].text)
    except Exception as e:
        raise Exception(f"Erro na análise do Eneagrama: {str(e)}")

def gerar_analise_temperamento(temperamento: Dict) -> Dict[str, str]:
    """
    Gera análise específica do Temperamento e suas implicações
    """
    temp_dominante = max(temperamento.items(), key=lambda x: x[1])
    
    prompt = f"""
    Analise detalhadamente o perfil de Temperamento, com foco no tipo dominante {temp_dominante[0]} ({temp_dominante[1]}%), 
    considerando todas as dimensões a seguir:

    PERFIL TEMPERAMENTAL BÁSICO
    - Características fundamentais do temperamento {temp_dominante[0]}
    - Como este temperamento influencia reações emocionais
    - Padrões de resposta a diferentes situações
    - Necessidades básicas deste temperamento

    DINÂMICA COMPORTAMENTAL
    - Reações típicas em situações de:
        * Conflito conjugal
        * Tomada de decisões
        * Comunicação diária
        * Expressão de afeto
        * Resolução de problemas
    - Como este temperamento processa emoções
    - Padrões de socialização e intimidade

    FORÇAS E DESAFIOS
    - Pontos fortes naturais deste temperamento
    - Desafios específicos no contexto conjugal
    - Como maximizar as forças no relacionamento
    - Estratégias para gerenciar os desafios

    INTERAÇÃO COM OUTROS TEMPERAMENTOS
    - Como este temperamento interage com diferentes perfis
    - Possíveis áreas de conflito e harmonia
    - Estratégias de adaptação e compreensão mútua
    - Dicas para melhorar a comunicação

    DESENVOLVIMENTO E CRESCIMENTO
    - Áreas específicas para desenvolvimento pessoal
    - Exercícios práticos recomendados
    - Estratégias de autoconhecimento
    - Caminhos para equilibrar características temperamentais

    Para cada aspecto, inclua:
    1. Exemplos práticos do dia a dia conjugal
    2. Exercícios específicos para o casal
    3. Técnicas de comunicação adaptadas
    4. Estratégias de gestão emocional
    5. Recomendações para o cônjuge

    Dados completos do Temperamento: {json.dumps(temperamento, indent=2)}
    """

    try:
        response = anthropic.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            temperature=0.7,
            system="Você é um terapeuta especializado em Temperamentos e sua influência nos relacionamentos conjugais. Forneça análises profundas e aplicáveis.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return estruturar_analise_temperamento(response.content[0].text)
    except Exception as e:
        raise Exception(f"Erro na análise do Temperamento: {str(e)}")

def gerar_analise_linguagem_amor(linguagem_amor: Dict) -> Dict[str, str]:
    """
    Gera análise específica das Linguagens do Amor e suas implicações práticas
    """
    # Ordena as linguagens por porcentagem
    linguagens_ordenadas = sorted(linguagem_amor.items(), key=lambda x: x[1], reverse=True)
    principais_linguagens = linguagens_ordenadas[:2]
    
    prompt = f"""
    Analise detalhadamente o perfil de Linguagens do Amor, focando nas duas linguagens predominantes:
    1. {principais_linguagens[0][0]} ({principais_linguagens[0][1]}%)
    2. {principais_linguagens[1][0]} ({principais_linguagens[1][1]}%)

    ANÁLISE DAS LINGUAGENS PRINCIPAIS
    Para cada uma das linguagens dominantes, analise:
    - Características fundamentais e como se manifestam
    - Necessidades específicas de expressão de amor
    - Como esta pessoa prefere receber amor
    - Sinais de "tanque de amor" vazio
    - Comportamentos quando se sente amado vs. não amado

    DINÂMICA DE COMUNICAÇÃO AFETIVA
    - Como essa combinação de linguagens afeta:
        * Expectativas no relacionamento
        * Forma de expressar carinho
        * Interpretação das ações do cônjuge
        * Necessidades de intimidade
        * Resolução de conflitos afetivos

    APLICAÇÕES PRÁTICAS
    Forneça exemplos detalhados de:
    1. Ações diárias específicas para cada linguagem
    2. Gestos especiais para ocasiões importantes
    3. Rotinas que podem ser estabelecidas
    4. Atividades para fazer juntos
    5. Formas de demonstração de amor em momentos de conflito

    DESAFIOS E SOLUÇÕES
    - Possíveis mal-entendidos devido às diferentes linguagens
    - Como evitar frustrações na comunicação do amor
    - Estratégias para superar barreiras
    - Como adaptar a expressão de amor às necessidades do parceiro

    PLANO DE DESENVOLVIMENTO
    Crie um guia prático com:
    1. Exercícios diários para praticar cada linguagem
    2. Checklist de demonstrações de amor
    3. Calendário sugerido de atividades
    4. Formas de avaliar o progresso
    5. Ajustes necessários ao longo do tempo

    Para cada aspecto, inclua:
    - Exemplos muito específicos e práticos
    - Sugestões detalhadas de implementação
    - Como adaptar às circunstâncias do casal
    - Formas de manter a consistência

    Dados completos das Linguagens do Amor: {json.dumps(linguagem_amor, indent=2)}
    """

    try:
        response = anthropic.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            temperature=0.7,
            system="Você é um terapeuta especializado em Linguagens do Amor e comunicação afetiva em relacionamentos. Forneça análises práticas e aplicáveis no dia a dia.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return estruturar_analise_linguagem_amor(response.content[0].text)
    except Exception as e:
        raise Exception(f"Erro na análise das Linguagens do Amor: {str(e)}")




def gerar_analise_integrada(dados: Dict) -> str:
    """
    Gera uma análise integrativa específica para correlacionar todos os resultados
    """
    # Extrair o temperamento principal
    temperamento_principal = max(dados['temperamento'].items(), key=lambda x: x[1])[0]
    
    # Extrair a linguagem do amor principal
    linguagem_principal = max(dados['linguagem_amor'].items(), key=lambda x: x[1])[0]
    
    prompt = f"""
    Gere uma análise integrativa detalhada para {dados['identificacao']['nome']}, conectando e correlacionando todos os resultados:

    DADOS BASE:
    Nome: {dados['identificacao']['nome']}
    Tempo de Casamento: {dados['identificacao']['tempo_casado']} anos
    Eneagrama: {dados['eneagrama']['tipo_principal']} ({dados['eneagrama']['porcentagem_principal']}%)
    Temperamento Principal: {temperamento_principal}
    Linguagem do Amor Principal: {linguagem_principal}

    Gere uma análise completa e detalhada que inclua EXATAMENTE estas seções:

    1. PERFIL COMPLETO
    Analise como as três dimensões (Eneagrama, Temperamento e Linguagem do Amor) se combinam para formar o perfil único desta pessoa no casamento.

    2. INTERAÇÕES ENTRE OS PERFIS
    Explique detalhadamente como cada característica interage com as outras, criando padrões únicos de comportamento.

    3. PADRÕES COMPORTAMENTAIS
    Descreva os principais padrões de comportamento que emergem desta combinação específica de características.

    4. INTERVENÇÕES TERAPÊUTICAS
    Sugira intervenções específicas baseadas nesta combinação única de características.

    5. RECOMENDAÇÕES PRÁTICAS
    Forneça recomendações práticas e detalhadas para implementação imediata.

    Para cada seção, inclua exemplos práticos e específicos do cotidiano conjugal.
    """

    try:
        response = anthropic.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            temperature=0.7,
            system="Você é um terapeuta especializado em análise integrativa de perfis comportamentais. Forneça análises detalhadas e práticas.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    except Exception as e:
        raise Exception(f"Erro na geração da análise integrativa: {str(e)}")

def gerar_pdf_personalizado(identificacao: Dict, linguagem_amor: Dict, temperamento: Dict, eneagrama: Dict, analise_completa: Dict) -> str:
    try:
        pdf = PDF()
        
        # Capa
        pdf.add_cover(identificacao['nome'])
        
        # Identificação
        pdf.add_section("IDENTIFICAÇÃO", f"""
        Nome: {identificacao['nome']}
        Tempo de Casamento: {identificacao['tempo_casado']} anos
        
        Maior Queixa:
        {identificacao['maior_queixa']}
        
        Maior Felicidade:
        {identificacao['maior_felicidade']}
        """)
        
        # Resultados
        pdf.add_page()
        pdf.add_section("RESULTADOS DOS TESTES", "")
        pdf.add_result_box("Eneagrama", 
                          f"Tipo {eneagrama['tipo_principal']}", 
                          f"{eneagrama['porcentagem_principal']}%")
        
        temp_dominante = max(temperamento.items(), key=lambda x: x[1])
        pdf.add_result_box("Temperamento", 
                          temp_dominante[0], 
                          f"{temp_dominante[1]}%")
        
        linguagens = sorted(linguagem_amor.items(), key=lambda x: x[1], reverse=True)[:2]
        pdf.add_result_box("Linguagens do Amor", 
                          f"1. {linguagens[0][0]}\n2. {linguagens[1][0]}", 
                          f"{linguagens[0][1]}%\n{linguagens[1][1]}%")
        
        # Seções de análise
        for titulo, conteudo in analise_completa.items():
            if conteudo and isinstance(conteudo, str) and "não encontrada" not in conteudo:
                pdf.add_section(titulo.replace('_', ' ').upper(), 
                              formatar_conteudo(conteudo))

        output_filename = f"devolutiva_{remover_caracteres_especiais(identificacao['nome'])}.pdf"
        pdf.output(output_filename)
        return output_filename

    except Exception as e:
        raise Exception(f"Erro na geração do PDF: {str(e)}")
        
def formatar_conteudo(texto: str) -> str:
    """
    Formata o conteúdo para melhor apresentação no PDF
    """
    # Remove múltiplos espaços em branco
    texto = re.sub(r'\s+', ' ', texto)
    
    # Adiciona quebras de linha após pontos finais
    texto = re.sub(r'\.(?=\s|$)', '.\n\n', texto)
    
    # Remove quebras de linha excessivas
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    
    return texto.strip()

def remover_caracteres_especiais(texto: str) -> str:
    """
    Remove caracteres especiais e espaços do nome do arquivo
    """
    return re.sub(r'[^a-zA-Z0-9]', '_', texto)

def baixar_pdf(file_path: str):
    """
    Cria botão para download do PDF
    """
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.download_button(
                label="Baixar Relatório em PDF",
                data=f,
                file_name=os.path.basename(file_path),
                mime="application/pdf"
            )
        # Remove o arquivo após o download
        os.remove(file_path)
    else:
        st.error("Erro: Arquivo PDF não encontrado")

def validar_dados(dados: Dict) -> bool:
    """
    Valida os dados antes de gerar a análise
    """
    if not dados:
        return False
        
    campos_requeridos = ['nome', 'tempo_casado', 'maior_queixa', 'maior_felicidade']
    return all(campo in dados and dados[campo] for campo in campos_requeridos)

def processar_analise_completa(identificacao: Dict, linguagem_amor: Dict, temperamento: Dict, eneagrama: Dict) -> Dict:
    """
    Processa a análise completa e retorna o resultado estruturado
    """
    if not validar_dados(identificacao):
        raise ValueError("Dados de identificação incompletos ou inválidos")

    prompt = criar_prompt_analise(identificacao, linguagem_amor, temperamento, eneagrama)
    analise_texto = gerar_analise_integrada(prompt)
    analise = estruturar_analise(analise_texto)
    
    return analise

def exibir_linguagens_do_amor():
    """
    Exibe e processa o teste das 5 linguagens do amor
    """
    st.title("Teste das 5 Linguagens do Amor")
    
    perguntas = [
        "1. Eu gosto de:",
        "2. Eu me sinto amado quando:",
        "3. Eu me sinto amado quando:",
        "4. Eu gosto quando:",
        "5. Eu me sinto amado quando:",
        "6. Eu gosto de:",
        "7. Eu gosto de:",
        "8. Eu gosto quando:",
        "9. Eu gosto de:",
        "10. Eu gosto de:",
        "11. Eu gosto quando:",
        "12. Eu gosto de:",
        "13. Eu gosto quando:",
        "14. Eu gosto quando:",
        "15. Eu gosto de:",
        "16. Eu gosto de:"
    ]
    
    opcoes = [
        ["A - Receber palavras de afirmação", "B - Passar tempo de qualidade com alguém especial"],
        ["A - Recebo presentes", "B - Alguém me ajuda com tarefas"],
        ["A - Alguém me toca carinhosamente", "B - Recebo elogios"],
        ["A - Alguém me dá total atenção", "B - Alguém faz algo para me ajudar"],
        ["A - Alguém me dá um presente", "B - Sou tocado carinhosamente"],
        ["A - Receber elogios", "B - Alguém me ajuda com as tarefas diárias"],
        ["A - Receber presentes que demonstrem que a pessoa pensou em mim", "B - Passar momentos a sós com quem amo"],
        ["A - Alguém me diz que me ama", "B - Alguém me abraça"],
        ["A - Passar tempo com alguém que amo", "B - Alguém faz algo prático para me ajudar"],
        ["A - Receber presentes", "B - Estar fisicamente próximo de quem amo"],
        ["A - Alguém me diz o quanto sou importante", "B - Alguém faz coisas para me ajudar"],
        ["A - Passar tempo de qualidade com alguém", "B - Receber presentes que demonstrem carinho"],
        ["A - Alguém me elogia", "B - Alguém demonstra afeto através do toque"],
        ["A - Alguém me escuta atentamente", "B - Alguém faz algo prático para me ajudar"],
        ["A - Receber presentes de alguém que amo", "B - Ouvir palavras de afirmação"],
        ["A - Passar tempo fazendo atividades com quem amo", "B - Alguém me toca carinhosamente"]
    ]
    
    st.write("""
    Para cada pergunta, escolha a opção que melhor reflete sua preferência. 
    Não há respostas certas ou erradas - escolha aquela que mais combina com você.
    """)
    
    respostas = []
    
    for pergunta, opcao in zip(perguntas, opcoes):
        st.write("---")
        st.write(pergunta)
        resposta = st.radio("", opcao, key=pergunta)
        respostas.append(resposta[0])
    
    if st.button("Enviar", key="enviar_linguagem"):
        resultado = calcular_linguagem_amor(respostas)
        st.session_state["Linguagem_do_Amor"] = resultado
        st.session_state["pagina_atual"] = "Temperamentos"
        st.rerun()

def exibir_temperamentos():
    """
    Exibe e processa o teste de temperamentos
    """
    st.title("Teste de Temperamentos")
    
    temperamentos = {
        "Sanguíneo": [
            "1. Gosta de conversar?",
            "2. Gosta de atividade, ação?",
            "3. Emociona-se com facilidade?",
            "4. 'Explode' facilmente?",
            "5. Tem inclinação para conhecer muitos assuntos de vez, para cultura geral?",
            "6. Sua imaginação é viva?",
            "7. Tem inclinação para crítica e para ironia?",
            "8. Tem tendência a mudar facilmente de opinião de argumentos razoáveis?",
            "9. Quando lhe pedem desculpas de uma ofensa, reconcilia-se com facilidade?",
            "10. Guarda rancor, ainda que não lhe peça desculpas?",
            "11. Gosta de fazer o bem sempre que pode?",
            "12. Aflige-se facilmente com os males do próximo?",
            "13. É inclinado mais ao otimismo do que ao pessimismo?",
            "14. Ri com facilidade quando há motivo?",
            "15. É muito constante, perseverante?",
            "16. Prefere encontrar os problemas de ordem intelectual já resolvidos?",
            "17. Aceita facilmente as notícias que lhe dão?",
            "18. Gosta de novidades?",
            "19. Gosta de andar elegante, bem trajado?",
            "20. Gosta de ser admirado pelos outros?"
        ],
        "Colérico": [
            "1. Irrita-se com facilidade?",
            "2. Quando se irrita, dissimula a irritação?",
            "3. Guarda rancor?",
            "4. Perdoa facilmente?",
            "5. Diante de uma oposição à sua opinião, tem tendência natural a ser intolerante?",
            "6. É obstinado (teimoso, inflexível)?",
            "7. Tem bastante dificuldade em pedir desculpas?",
            "8. Quando quer conseguir algo, tem tendência a se servir de meios que não sejam legítimos?",
            "9. Gosta de ficar ruminando ideias?",
            "10. Ama os outros com facilidade?",
            "11. Apaixona-se facilmente quando ama?",
            "12. Gosta de demonstrar exteriormente quando ama alguém?",
            "13. Gosta de estudar as matérias teóricas?",
            "14. Raciocina com firmeza?",
            "15. Gosta de ser pontual?",
            "16. Gosta de saber os motivos de um dever, de uma obrigação?",
            "17. Gosta de agir por razões afetivas, sentimentais?",
            "18. Gosta de admirar a si mesmo?",
            "19. Vive ansioso por novidades, boatos?",
            "20. Aceita com facilidade as notícias que lhe dão, afirmações que lhe fazem?"
        ],
        "Melancólico": [
            "1. Anda devagar?",
            "2. É observador?",
            "3. Reage prontamente?",
            "4. Gosta de apreciar as belezas da Natureza?",
            "5. Prefere a solidão ao buliço da vida social?",
            "6. Gosta de contar novidades?",
            "7. Gosta de esporte?",
            "8. Gosta de música?",
            "9. Guarda segredo?",
            "10. Costuma realizar seus próprios propósitos?",
            "11. É teimoso com certos pontos de vista?",
            "12. Apaixona-se facilmente por aquilo que ama?",
            "13. É rude, áspero com os outros?",
            "14. Gosta de ler?",
            "15. Costuma ser indeciso?",
            "16. Tem tendência para olhar os acontecimentos pelo lado ruim?",
            "17. Costuma pensar, meditar?",
            "18. Costuma soltar gargalhadas?",
            "19. Às vezes se sente alheio ao ambiente onde vive?",
            "20. Desculpa facilmente, esquece as ofensas que lhe fazem?"
        ],
        "Fleumático": [
            "1. Costuma apreciar as belezas da Natureza?",
            "2. Zanga-se com facilidade?",
            "3. Costuma empolgar-se com as coisas para as quais outros usam adjetivos: 'formidável', 'espetacular'?",
            "4. É esmerado no trajar?",
            "5. Gosta de maliciar os outros?",
            "6. Costuma ser paciente se tem de recomeçar o que não deu certo?",
            "7. Afoba-se nas horas de pronto-socorro?",
            "8. É obcecado pela atividade, pela ação?",
            "9. Gosta de 'sombra e água-fresca'? Isto é, de fugir das responsabilidades?",
            "10. Traz os seus aposentos bem arrumados?",
            "11. Apaixona-se facilmente?",
            "12. Tem especial interesse em cultivar amizades?",
            "13. Reage violentamente às agressões?",
            "14. Gosta de inovações?",
            "15. Abate-se com os insucessos?",
            "16. Fere-se facilmente com as ofensas e ironias?",
            "17. É vingativo?",
            "18. Acha sua vontade fraca na prática?",
            "19. Preocupa-se em ajudar os outros?",
            "20. Conforma-se à rotina da vida?"
        ]
    }
    
    st.write("""
    Para cada pergunta, responda 'Sim' ou 'Não' de acordo com o que melhor representa você.
    Seja honesto em suas respostas - não há respostas certas ou erradas.
    """)
    
    respostas = {}
    
    for temp, perguntas in temperamentos.items():
        st.subheader(f"Perguntas para o temperamento {temp}")
        st.write("---")
        
        for pergunta in perguntas:
            resposta = st.radio(pergunta, ["Sim", "Não"], key=f"{temp}_{pergunta}")
            respostas[f"{temp}_{pergunta}"] = resposta
        
        st.write("---")
    
    if st.button("Enviar", key="enviar_temperamentos"):
        resultado = calcular_temperamento(respostas)
        st.session_state["Temperamentos"] = resultado
        st.session_state["pagina_atual"] = "Eneagrama"
        st.rerun()

def exibir_eneagrama():
    """
    Exibe e processa o teste do Eneagrama
    """
    st.title("Teste do Eneagrama")
    
    perguntas = [
        {
            "titulo": "1) Em qual situação você se enquadra?",
            "opcoes": [
                "A - Sinto minha vida como uma busca incessante daquilo que julgo perfeito.",
                "B - Sou do tipo de pessoa que adora ser reconhecido e bajulado!",
                "C - Tenho compulsão pelo trabalho!",
                "D - Tenho a sensação permanente de falta... Simplesmente algo ainda não aconteceu na minha vida!",
                "E - Gosto de estar sozinho, pensando, meditando no meu canto em silêncio.",
                "F - Sou muito inseguro, tenho medo de qualquer situação nova ou daquelas que eu acho perigosas, pois podem não dar certo e me machucar.",
                "G - Sempre acho um significado positivo em tudo. Sou um idealista e otimista inveterado!",
                "H - Tenho dificuldades em aceitar opiniões contrárias às minhas.",
                "I - Às vezes, protelo o que tenho para fazer de mais importante, inventando um monte de desculpas."
            ]
        },
        {
            "titulo": "2) Concordo que...",
            "opcoes": [
                "A - Primeiro a obrigação, depois a diversão!",
                "B - Toda a minha vida foi uma constante entrega de amor!",
                "C - Gosto de criar uma imagem positiva de mim mesmo.",
                "D - Sou extremamente sensível!",
                "E - Ter que ir a uma festa é um sofrimento para mim, especialmente por ter que ouvir tanta bobagem!",
                "F - Sempre demoro a concretizar algo, pois fico imaginando as possíveis consequências.",
                "G - Adoro explorar territórios novos. Gostaria de poder voar ou de colocar uma mochila nas costas e sair viajando pelo mundo!",
                "H - Para mim não existem obstáculos, sou capaz de qualquer esforço para conseguir o que quero.",
                "I - Tenho procurado pensar mais em mim, no meu bem-estar, mas confesso que é difícil."
            ]
        },
        {
            "titulo": "3) Em geral...",
            "opcoes": [
                "A - Meu dia-a-dia é tenso, cheio de cobranças e exigências.",
                "B - Agradar aos outros é bom, porque desse modo recebo o que quero.",
                "C - Tenho grandes dificuldades para expressar meus sentimentos.",
                "D - Nada no presente me faz feliz: a lembrança do passado é muito forte!",
                "E - Somente com pessoas do meu nível intelectual me sinto mais à vontade.",
                "F - Minha imaginação é poderosa e me provoca uma grande ansiedade.",
                "G - Sou uma pessoa muito versátil, sei fazer várias coisas diferentes.",
                "H - A vida é uma luta constante, só me aparecem desafios, só entro em complicações, mas no fundo até que gosto.",
                "I - Demoro a fazer as coisas, mas tento fazê-las bem feitas."
            ]
        },
        {
            "titulo": "4) Sinto que...",
            "opcoes": [
                "A - Estou sempre dizendo: 'eu tenho que...', 'eu deveria...'",
                "B - Com jeitinho, consigo tudo o que quero.",
                "C - Tenho grandes dificuldades para ficar quieto, meditando!",
                "D - Não posso ser feliz em um mundo tão cego e insensível!",
                "E - Gosto de ser reconhecido pelos meus conhecimentos especializados.",
                "F - Tomar decisões é algo que não gosto e tento evitar sempre que possível.",
                "G - Considero-me uma pessoa muito criativa e audaciosa. Planejar me dá prazer, executar nem sempre.",
                "H - Abraço com muita determinação as causas que considero justas e verdadeiras.",
                "I - Estou sempre disposto a ajudar os outros."
            ]
        },
        {
            "titulo": "5) Percebo que...",
            "opcoes": [
                "A - Se não pode ser bem feito, melhor não fazer!",
                "B - Fico zangado quando as pessoas das quais espero reconhecimento me ignoram ou me fazem sentir em segundo lugar!",
                "C - Quando fracasso, recupero-me rapidamente.",
                "D - Ninguém compreende meus sentimentos.",
                "E - Meu quarto é o único local da casa no qual posso ficar mais livre, sem ter que falar com ninguém.",
                "F - Não aceito ser controlado ou obrigado a fazer algo.",
                "G - Tento manter sempre o alto astral!",
                "H - Preciso controlar tudo, mesmo percebendo quanto isso me faz mal no sentido de gastar muita energia.",
                "I - É fácil me adaptar a qualquer tipo de pessoa."
            ]
        },
        {
            "titulo": "6) Sei que...",
            "opcoes": [
                "A - Desde muito cedo me foi incutido um senso de responsabilidade, no sentido de que deveria dar o exemplo.",
                "B - Ajudar as pessoas é maravilhoso.",
                "C - É difícil ter tempo para minhas próprias necessidades.",
                "D - Melancolia, esse é meu estado permanente!",
                "E - Tenho dificuldades para viver relacionamentos amorosos.",
                "F - Sentir-se seguro é essencial.",
                "G - Minhas grandes paixões são as ideias, os novos conhecimentos e desafios.",
                "H - Nunca estou satisfeito, sempre desejo conquistar mais e mais!",
                "I - Costumo adiar muitas coisas importantes para mim."
            ]
        },
        {
            "titulo": "7) Na verdade...",
            "opcoes": [
                "A - Sempre faço tudo bem feito!",
                "B - Adoro aplausos! A vida é um espetáculo...",
                "C - Modestamente, sou o melhor na minha área.",
                "D - Me sinto diferente aos demais, sinto o que ninguém é capaz de sentir.",
                "E - Eu sou capaz de ter momentos privados de lazer; sozinho é melhor!",
                "F - Não gosto nada de falar de mim. Além de não gostar, não tenho a menor vontade.",
                "G - Sou um pouco (ou muito) narcisista, simplesmente me adoro!",
                "H - Sinto que posso conquistar o mundo!",
                "I - Procuro me ajustar ao mundo, dividindo-me entre todos os que me rodeiam, facilitando-lhes ou resolvendo a vida."
            ]
        }
    ]
    
    st.write("""
    Para cada grupo de afirmações, escolha aquela que melhor te descreve.
    Não há respostas certas ou erradas - escolha a opção que mais se aproxima de como você é.
    """)
    
    respostas = []
    
    for pergunta in perguntas:
        st.write("---")
        st.subheader(pergunta["titulo"])
        resposta = st.radio("", pergunta["opcoes"], key=pergunta["titulo"])
        respostas.append(resposta[0])  # Pega apenas a letra da opção (A, B, C, etc.)
    
    if st.button("Enviar", key="enviar_eneagrama"):
        resultado = calcular_eneagrama(respostas)
        st.session_state["Eneagrama"] = resultado
        st.session_state["pagina_atual"] = "Análise Final"
        st.rerun()

def calcular_linguagem_amor(respostas: List[str]) -> Dict[str, int]:
    """
    Calcula os resultados do teste de linguagem do amor
    """
    categorias = {
        "Palavras de Afirmação": [1, 3, 6, 8, 11, 13, 15],
        "Tempo de Qualidade": [1, 4, 7, 9, 12, 16],
        "Receber Presentes": [2, 5, 7, 10, 12, 15],
        "Atos de Serviço": [2, 4, 6, 9, 11, 14],
        "Toque Físico": [3, 5, 8, 10, 13, 16]
    }
    
    contagem = {categoria: 0 for categoria in categorias}
    
    for idx, resposta in enumerate(respostas, start=1):
        for categoria, indices in categorias.items():
            if idx in indices and resposta == ('A' if categoria in ["Palavras de Afirmação", "Receber Presentes", "Toque Físico"] else 'B'):
                contagem[categoria] += 1
    
    # Normaliza os resultados para porcentagens
    total = sum(contagem.values())
    if total > 0:
        contagem = {k: round((v/total) * 100, 2) for k, v in contagem.items()}
    
    # Ordena por pontuação
    contagem = dict(sorted(contagem.items(), key=lambda x: x[1], reverse=True))
    
    return contagem

def calcular_temperamento(respostas: Dict[str, str]) -> Dict[str, float]:
    """
    Calcula os resultados do teste de temperamentos
    """
    categorias = {
        "Sanguíneo": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 20],
        "Colérico": [1, 3, 5, 6, 7, 9, 10, 13, 14, 15],
        "Melancólico": [1, 2, 4, 5, 8, 9, 11, 12, 14, 15],
        "Fleumático": [6, 9, 10, 18, 20]
    }
    
    contagem = {categoria: 0 for categoria in categorias}
    
    for temp, indices in categorias.items():
        for idx in indices:
            chave = f"{temp}_{idx}"
            if chave in respostas and respostas[chave] == 'Sim':
                contagem[temp] += 1
    
    # Calcula porcentagens baseadas no número máximo possível para cada temperamento
    max_pontos = {
        "Sanguíneo": len(categorias["Sanguíneo"]),
        "Colérico": len(categorias["Colérico"]),
        "Melancólico": len(categorias["Melancólico"]),
        "Fleumático": len(categorias["Fleumático"])
    }
    
    for temp in contagem:
        contagem[temp] = round((contagem[temp] / max_pontos[temp]) * 100, 2)
    
    # Ordena por pontuação
    contagem = dict(sorted(contagem.items(), key=lambda x: x[1], reverse=True))
    
    return contagem

def calcular_eneagrama(respostas: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Calcula os resultados do teste do eneagrama
    """
    tipos = {
        'A': "Perfeccionista",
        'B': "Doador",
        'C': "Desempenhador",
        'D': "Romântico",
        'E': "Observador",
        'F': "Questionador",
        'G': "Entusiasta",
        'H': "Desafiador",
        'I': "Mediador"
    }
    
    # Conta as respostas
    contagem = Counter(respostas)
    
    # Calcula porcentagens
    total_respostas = len(respostas)
    resultados = {}
    
    for letra, tipo in tipos.items():
        quantidade = contagem.get(letra, 0)
        porcentagem = round((quantidade / total_respostas) * 100, 2)
        
        resultados[tipo] = {
            'quantidade': quantidade,
            'porcentagem': porcentagem,
            'letra': letra
        }
    
    # Ordena por porcentagem
    resultados = dict(sorted(resultados.items(), key=lambda x: x[1]['porcentagem'], reverse=True))
    
    # Identifica o tipo principal e as asas
    tipo_principal = list(resultados.keys())[0]
    porcentagem_principal = resultados[tipo_principal]['porcentagem']
    letra_principal = resultados[tipo_principal]['letra']
    
    # Determina as asas baseado no número do eneagrama
    numero_tipo = ord(letra_principal) - ord('A') + 1
    asa_anterior = tipos.get(chr(ord('A') + ((numero_tipo - 2) % 9)))
    asa_posterior = tipos.get(chr(ord('A') + (numero_tipo % 9)))
    
    return {
        'tipo_principal': tipo_principal,
        'porcentagem_principal': porcentagem_principal,
        'asas': {
            'anterior': asa_anterior,
            'posterior': asa_posterior
        },
        'todos_resultados': resultados
    }

def calcular_pontos_eneagrama(tipo_principal: str) -> Dict[str, Dict[str, Any]]:
    """
    Calcula os pontos de estresse e segurança baseados no tipo principal do eneagrama
    """
    mapeamento_tipos = {
        "Perfeccionista": {
            "numero": 1,
            "ponto_estresse": {
                "numero": 4,
                "tipo": "Romântico",
                "caracteristicas": [
                    "Pode se tornar mais emocional e introspectivo",
                    "Tendência a se recolher e ruminar sentimentos",
                    "Maior sensibilidade a críticas",
                    "Foco em suas falhas e imperfeições"
                ]
            },
            "ponto_seguranca": {
                "numero": 7,
                "tipo": "Entusiasta",
                "caracteristicas": [
                    "Torna-se mais espontâneo e alegre",
                    "Maior facilidade para relaxar e se divertir",
                    "Mais aberto a diferentes perspectivas",
                    "Menos rígido e mais flexível"
                ]
            }
        },
        "Doador": {
            "numero": 2,
            "ponto_estresse": {
                "numero": 8,
                "tipo": "Desafiador",
                "caracteristicas": [
                    "Pode se tornar mais confrontador e agressivo",
                    "Tendência a expressar raiva reprimida",
                    "Maior dificuldade em manter a diplomacia",
                    "Comportamento mais dominante"
                ]
            },
            "ponto_seguranca": {
                "numero": 4,
                "tipo": "Romântico",
                "caracteristicas": [
                    "Maior conexão com seus próprios sentimentos",
                    "Mais autêntico em suas emoções",
                    "Menos dependente da aprovação dos outros",
                    "Maior autoconsciência"
                ]
            }
        },
        "Desempenhador": {
            "numero": 3,
            "ponto_estresse": {
                "numero": 9,
                "tipo": "Mediador",
                "caracteristicas": [
                    "Pode se tornar mais passivo e indeciso",
                    "Tendência a procrastinar",
                    "Dificuldade em manter o foco",
                    "Menor motivação para realizações"
                ]
            },
            "ponto_seguranca": {
                "numero": 6,
                "tipo": "Questionador",
                "caracteristicas": [
                    "Mais cooperativo e leal",
                    "Maior capacidade de trabalhar em equipe",
                    "Mais atento às necessidades dos outros",
                    "Desenvolvimento de maior confiança nas pessoas"
                ]
            }
        },
        "Romântico": {
            "numero": 4,
            "ponto_estresse": {
                "numero": 2,
                "tipo": "Doador",
                "caracteristicas": [
                    "Pode se tornar mais manipulador",
                    "Busca excessiva por atenção",
                    "Dependência emocional aumentada",
                    "Maior necessidade de aprovação"
                ]
            },
            "ponto_seguranca": {
                "numero": 1,
                "tipo": "Perfeccionista",
                "caracteristicas": [
                    "Maior objetividade e clareza",
                    "Mais organizado e disciplinado",
                    "Melhor capacidade de estabelecer limites",
                    "Maior equilíbrio emocional"
                ]
            }
        },
        "Observador": {
            "numero": 5,
            "ponto_estresse": {
                "numero": 7,
                "tipo": "Entusiasta",
                "caracteristicas": [
                    "Pode se tornar mais impulsivo e disperso",
                    "Busca excessiva por experiências",
                    "Dificuldade em manter o foco",
                    "Comportamento mais errático"
                ]
            },
            "ponto_seguranca": {
                "numero": 8,
                "tipo": "Desafiador",
                "caracteristicas": [
                    "Mais assertivo e confiante",
                    "Maior capacidade de liderança",
                    "Mais presente no momento",
                    "Maior disposição para ação"
                ]
            }
        },
        "Questionador": {
            "numero": 6,
            "ponto_estresse": {
                "numero": 3,
                "tipo": "Desempenhador",
                "caracteristicas": [
                    "Pode se tornar mais competitivo e workaholic",
                    "Maior preocupação com imagem",
                    "Tendência a ignorar problemas emocionais",
                    "Comportamento mais mecânico"
                ]
            },
            "ponto_seguranca": {
                "numero": 9,
                "tipo": "Mediador",
                "caracteristicas": [
                    "Mais calmo e centrado",
                    "Maior capacidade de aceitar diferentes perspectivas",
                    "Menos ansioso e mais confiante",
                    "Melhor gestão do medo"
                ]
            }
        },
        "Entusiasta": {
            "numero": 7,
            "ponto_estresse": {
                "numero": 1,
                "tipo": "Perfeccionista",
                "caracteristicas": [
                    "Pode se tornar mais crítico e rígido",
                    "Maior foco em detalhes negativos",
                    "Comportamento mais controlador",
                    "Aumento da autocrítica"
                ]
            },
            "ponto_seguranca": {
                "numero": 5,
                "tipo": "Observador",
                "caracteristicas": [
                    "Mais focado e analítico",
                    "Maior profundidade de pensamento",
                    "Melhor capacidade de concentração",
                    "Mais reflexivo e contemplativo"
                ]
            }
        },
        "Desafiador": {
            "numero": 8,
            "ponto_estresse": {
                "numero": 5,
                "tipo": "Observador",
                "caracteristicas": [
                    "Pode se tornar mais isolado e distante",
                    "Tendência a se retrair",
                    "Maior necessidade de privacidade",
                    "Comportamento mais analítico e menos ativo"
                ]
            },
            "ponto_seguranca": {
                "numero": 2,
                "tipo": "Doador",
                "caracteristicas": [
                    "Mais atencioso e carinhoso",
                    "Maior capacidade de demonstrar afeto",
                    "Mais sensível às necessidades alheias",
                    "Comportamento mais gentil"
                ]
            }
        },
        "Mediador": {
            "numero": 9,
            "ponto_estresse": {
                "numero": 6,
                "tipo": "Questionador",
                "caracteristicas": [
                    "Pode se tornar mais ansioso e desconfiado",
                    "Maior tendência a duvidar",
                    "Comportamento mais defensivo",
                    "Aumento do medo e da insegurança"
                ]
            },
            "ponto_seguranca": {
                "numero": 3,
                "tipo": "Desempenhador",
                "caracteristicas": [
                    "Mais focado em objetivos",
                    "Maior capacidade de realização",
                    "Mais assertivo e decidido",
                    "Melhor capacidade de priorização"
                ]
            }
        }
    }

    if tipo_principal not in mapeamento_tipos:
        raise ValueError(f"Tipo {tipo_principal} não encontrado no mapeamento")

    return mapeamento_tipos[tipo_principal]

def analisar_direcoes_integracao(tipo_principal: str) -> Dict[str, str]:
    """
    Fornece uma análise detalhada das direções de integração (segurança) e desintegração (estresse)
    """
    pontos = calcular_pontos_eneagrama(tipo_principal)
    
    return {
        "direcao_integracao": f"""
        Em momentos de crescimento e segurança, o tipo {tipo_principal} (tipo {pontos['numero']}) 
        move-se em direção ao tipo {pontos['ponto_seguranca']['tipo']} (tipo {pontos['ponto_seguranca']['numero']}).
        
        Características positivas que emergem:
        {chr(10).join('- ' + carac for carac in pontos['ponto_seguranca']['caracteristicas'])}
        """,
        
        "direcao_desintegracao": f"""
        Em momentos de estresse e insegurança, o tipo {tipo_principal} (tipo {pontos['numero']}) 
        move-se em direção ao tipo {pontos['ponto_estresse']['tipo']} (tipo {pontos['ponto_estresse']['numero']}).
        
        Características que podem surgir:
        {chr(10).join('- ' + carac for carac in pontos['ponto_estresse']['caracteristicas'])}
        """
    }

def exibir_analise_final():
    """
    Exibe a análise final com todos os resultados dos testes
    """
    st.title("Análise Final Personalizada")
    
    # Verifica se todos os testes foram completados
    identificacao = st.session_state.get("Identificação", {})
    linguagem_amor = st.session_state.get("Linguagem_do_Amor", {})
    temperamento = st.session_state.get("Temperamentos", {})
    eneagrama = st.session_state.get("Eneagrama", {})
    
    if all([identificacao, linguagem_amor, temperamento, eneagrama]):
        try:
            # Gera a análise completa
            analise_completa = processar_analise_completa(
                identificacao,
                linguagem_amor,
                temperamento,
                eneagrama
            )
            
            # Exibe os resultados de forma organizada
            st.header("Resumo dos Resultados")
            
            # Identificação
            st.subheader("Dados Pessoais")
            st.markdown(f"""
            **Nome:** {identificacao['nome']}
            **Tempo de Casamento:** {identificacao['tempo_casado']} anos
            **Maior Queixa:** {identificacao['maior_queixa']}
            **Maior Felicidade:** {identificacao['maior_felicidade']}
            """)
            
            # Resultados dos testes
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Linguagens do Amor")
                for lingua, valor in linguagem_amor.items():
                    st.markdown(f"<div class='result-item'><b>{lingua}:</b> {valor}%</div>", unsafe_allow_html=True)
                
                st.subheader("Temperamentos")
                for temp, valor in temperamento.items():
                    st.markdown(f"<div class='result-item'><b>{temp}:</b> {valor}%</div>", unsafe_allow_html=True)
            
            with col2:
                st.subheader("Eneagrama")
                st.markdown(f"<div class='result-item'><b>Tipo Principal:</b> {eneagrama['tipo_principal']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-item'><b>Porcentagem:</b> {eneagrama['porcentagem_principal']}%</div>", unsafe_allow_html=True)
                
                st.markdown("**Asas:**")
                st.markdown(f"<div class='result-item'><b>Anterior:</b> {eneagrama['asas']['anterior']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-item'><b>Posterior:</b> {eneagrama['asas']['posterior']}</div>", unsafe_allow_html=True)
            
            # Análise Detalhada
            st.header("Análise Detalhada")
            st.markdown(f"<div class='analysis-text'>{analise_completa}</div>", unsafe_allow_html=True)
            
            # Gerar e disponibilizar PDF
            try:
                pdf_file = gerar_pdf_personalizado(
                    identificacao,
                    linguagem_amor,
                    temperamento,
                    eneagrama,
                    analise_completa
                )
                baixar_pdf(pdf_file)
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {str(e)}")
                
        except Exception as e:
            st.error(f"Erro ao gerar análise: {str(e)}")
            
    else:
        st.warning("Por favor, complete todos os testes antes de ver a análise final.")
        if st.button("Voltar ao Início"):
            st.session_state["pagina_atual"] = "Identificação"
            st.rerun()

def estruturar_analise_eneagrama(texto: str) -> Dict[str, str]:
    """
    Estrutura a análise do Eneagrama em seções
    """
    secoes = {
        'personalidade_base': extrair_secao_especifica(texto, "PERSONALIDADE BASE", "PONTOS POSITIVOS E NEGATIVOS"),
        'pontos_analise': extrair_secao_especifica(texto, "PONTOS POSITIVOS E NEGATIVOS", "DINÂMICA DE ESTRESSE E SEGURANÇA"),
        'dinamica_estresse_seguranca': extrair_secao_especifica(texto, "DINÂMICA DE ESTRESSE E SEGURANÇA", "INFLUÊNCIA DAS ASAS"),
        'influencia_asas': extrair_secao_especifica(texto, "INFLUÊNCIA DAS ASAS", "PAIXÃO DOMINANTE E CAMINHO DE CRESCIMENTO"),
        'paixao_crescimento': extrair_secao_especifica(texto, "PAIXÃO DOMINANTE E CAMINHO DE CRESCIMENTO", "$")
    }
    return secoes

def estruturar_analise_temperamento(texto: str) -> Dict[str, str]:
    """
    Estrutura a análise do Temperamento em seções
    """
    secoes = {
        'perfil_base': extrair_secao_especifica(texto, "PERFIL TEMPERAMENTAL BÁSICO", "DINÂMICA COMPORTAMENTAL"),
        'dinamica_comportamental': extrair_secao_especifica(texto, "DINÂMICA COMPORTAMENTAL", "FORÇAS E DESAFIOS"),
        'forcas_desafios': extrair_secao_especifica(texto, "FORÇAS E DESAFIOS", "INTERAÇÃO COM OUTROS TEMPERAMENTOS"),
        'interacao_temperamentos': extrair_secao_especifica(texto, "INTERAÇÃO COM OUTROS TEMPERAMENTOS", "DESENVOLVIMENTO E CRESCIMENTO"),
        'desenvolvimento': extrair_secao_especifica(texto, "DESENVOLVIMENTO E CRESCIMENTO", "$")
    }
    
    # Processa cada seção
    resultado = {}
    for nome_secao, conteudo in secoes.items():
        if "não encontrada" in conteudo or not conteudo.strip():
            resultado[nome_secao] = ""
        else:
            conteudo = re.sub(r'^\s*[A-ZÇÃÕÊÂÔÛÁÉÍÓÚ\s]+\s*', '', conteudo.strip())
            resultado[nome_secao] = conteudo.strip()
    
    return resultado

def estruturar_analise_linguagem_amor(texto: str) -> Dict[str, str]:
    """
    Estrutura a análise das Linguagens do Amor em seções
    """
    secoes = {
        'analise_principais': extrair_secao_especifica(texto, "ANÁLISE DAS LINGUAGENS PRINCIPAIS", "DINÂMICA DE COMUNICAÇÃO AFETIVA"),
        'dinamica_comunicacao': extrair_secao_especifica(texto, "DINÂMICA DE COMUNICAÇÃO AFETIVA", "APLICAÇÕES PRÁTICAS"),
        'aplicacoes_praticas': extrair_secao_especifica(texto, "APLICAÇÕES PRÁTICAS", "DESAFIOS E SOLUÇÕES"),
        'desafios_solucoes': extrair_secao_especifica(texto, "DESAFIOS E SOLUÇÕES", "PLANO DE DESENVOLVIMENTO"),
        'plano_desenvolvimento': extrair_secao_especifica(texto, "PLANO DE DESENVOLVIMENTO", "$")
    }
    return secoes

def criar_prompt_analise_integrativa(identificacao: Dict, linguagem_amor: Dict, temperamento: Dict, eneagrama: Dict) -> str:
    """
    Cria um prompt específico para a análise integrativa
    """
    # Extrair o temperamento principal e a linguagem do amor principal
    temperamento_principal = max(temperamento.items(), key=lambda x: x[1])[0]
    linguagem_principal = max(linguagem_amor.items(), key=lambda x: x[1])[0]
    
    return f"""
    Gere uma análise integrativa detalhada para {identificacao['nome']}, conectando e correlacionando todos os resultados:

    DADOS BASE:
    Nome: {identificacao['nome']}
    Tempo de Casamento: {identificacao['tempo_casado']} anos
    Eneagrama: {eneagrama['tipo_principal']} ({eneagrama['porcentagem_principal']}%)
    Temperamento Principal: {temperamento_principal}
    Linguagem do Amor Principal: {linguagem_principal}

    Por favor, crie uma análise que INTEGRE todos esses aspectos, seguindo esta estrutura:

    1. SÍNTESE DO PERFIL RELACIONAL
    Analise como a combinação do tipo no eneagrama, temperamento e linguagem do amor cria um padrão único de relacionamento.
    Explique como essas características se reforçam ou se compensam mutuamente.

    2. DINÂMICAS DE RELACIONAMENTO
    Mostre como os pontos de estresse e segurança do eneagrama interagem com o temperamento.
    Explique como a linguagem do amor influencia estas dinâmicas.
    Analise como isso afeta a expressão das asas do eneagrama no relacionamento.

    3. PADRÕES DE COMUNICAÇÃO E CONFLITO
    Baseado na combinação única dessas características, explique:
    - Padrões típicos de comunicação
    - Como conflitos tendem a surgir e se desenvolver
    - Como as diferentes características influenciam a resolução de conflitos

    4. RECOMENDAÇÕES INTEGRADAS
    Forneça recomendações práticas que considerem TODAS as características em conjunto:
    - Como usar os pontos fortes de cada aspecto para fortalecer o relacionamento
    - Como compensar desafios usando características complementares
    - Exercícios práticos que trabalhem múltiplos aspectos simultaneamente

    5. PLANO DE DESENVOLVIMENTO
    Crie um plano que integre todos os aspectos analisados:
    - Objetivos de desenvolvimento considerando todas as características
    - Estratégias práticas que utilizem os pontos fortes de cada perfil
    - Sugestões de atividades que promovam crescimento em múltiplas áreas

    Para cada seção, forneça exemplos práticos e específicos do cotidiano conjugal.
    """

def gerar_analise_integrada(identificacao: Dict, linguagem_amor: Dict, temperamento: Dict, eneagrama: Dict) -> str:
    """
    Gera uma análise integrativa específica correlacionando todos os resultados
    """
    prompt = criar_prompt_analise_integrativa(identificacao, linguagem_amor, temperamento, eneagrama)
    
    try:
        response = anthropic.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            temperature=0.7,
            system="Você é um terapeuta especializado em análise integrativa de perfis comportamentais. Forneça análises detalhadas e práticas.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    except Exception as e:
        raise Exception(f"Erro na geração da análise integrativa: {str(e)}")

def estruturar_analise_integrativa(texto: str) -> Dict[str, str]:
    """
    Estrutura a análise integrativa em seções
    """
    secoes = {
        'sintese_perfil': extrair_secao_especifica(texto, "1. SÍNTESE DO PERFIL RELACIONAL", "2. DINÂMICAS"),
        'dinamicas': extrair_secao_especifica(texto, "2. DINÂMICAS DE RELACIONAMENTO", "3. PADRÕES"),
        'padroes': extrair_secao_especifica(texto, "3. PADRÕES DE COMUNICAÇÃO E CONFLITO", "4. RECOMENDAÇÕES"),
        'recomendacoes': extrair_secao_especifica(texto, "4. RECOMENDAÇÕES INTEGRADAS", "5. PLANO"),
        'plano': extrair_secao_especifica(texto, "5. PLANO DE DESENVOLVIMENTO", "$")
    }
    
    # Verifica e processa cada seção
    for nome_secao, conteudo in secoes.items():
        if "não encontrada" in conteudo or not conteudo.strip():
            secoes[nome_secao] = "Esta seção está em desenvolvimento..."
        else:
            conteudo = re.sub(r'^\d+\.\s*[A-ZÇÃÕÊÂÔÛÁÉÍÓÚ\s]+\s*', '', conteudo.strip())
            secoes[nome_secao] = conteudo.strip()
    
    return secoes


def extrair_secao_especifica(texto: str, inicio: str, fim: str) -> str:
    """
    Extrai uma seção específica do texto usando regex
    """
    padrao = f"{inicio}(.*?){fim}" if fim != "$" else f"{inicio}(.*)"
    match = re.search(padrao, texto, re.DOTALL)
    if match:
        conteudo = match.group(1).strip()
        # Remove o título da seção se estiver presente
        conteudo = re.sub(f"^{inicio}[\s:]*", "", conteudo, flags=re.IGNORECASE)
        return conteudo
    return f"Seção {inicio} não encontrada"

def formatar_conteudo(texto: str) -> str:
    """
    Formata o conteúdo para melhor apresentação
    """
    # Remove múltiplos espaços em branco
    texto = re.sub(r'\s+', ' ', texto)
    
    # Adiciona quebras de linha após pontos finais
    texto = re.sub(r'\.(?=\s|$)', '.\n\n', texto)
    
    # Remove quebras de linha excessivas
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    
    return texto.strip()

def main():
   """
   Função principal que gerencia o fluxo da aplicação
   """
   if "pagina_atual" not in st.session_state:
       st.session_state["pagina_atual"] = "Identificação"

   # Sidebar com progresso
   with st.sidebar:
       st.title("Progresso") 
       etapas = {
           "Identificação": "✏️",
           "Linguagem_do_Amor": "❤️",
           "Temperamentos": "🎭",
           "Eneagrama": "🔄", 
           "Análise Final": "📊"
       }
       
       for etapa, emoji in etapas.items():
           if etapa in st.session_state:
               st.success(f"{emoji} {etapa.replace('_', ' ')} ✓")
           elif etapa == st.session_state["pagina_atual"]:
               st.info(f"{emoji} {etapa.replace('_', ' ')} ⌛")
           else:
               st.write(f"{emoji} {etapa.replace('_', ' ')}")

   # Renderiza a página atual
   if st.session_state["pagina_atual"] == "Identificação":
       exibir_identificacao()
       
   elif st.session_state["pagina_atual"] == "Linguagem_do_Amor":
       exibir_linguagens_do_amor()
       
   elif st.session_state["pagina_atual"] == "Temperamentos":
       exibir_temperamentos()
       
   elif st.session_state["pagina_atual"] == "Eneagrama":
       exibir_eneagrama()
       
   elif st.session_state["pagina_atual"] == "Análise Final":
       if all(etapa in st.session_state for etapa in ["Identificação", "Linguagem_do_Amor", "Temperamentos", "Eneagrama"]):
           # Verifica se a análise já foi gerada
           if "analise_completa" not in st.session_state:
               try:
                   with st.spinner("Gerando análise completa..."):
                       # Gera análises específicas
                       analise_eneagrama = gerar_analise_eneagrama(st.session_state["Eneagrama"])
                       analise_temperamento = gerar_analise_temperamento(st.session_state["Temperamentos"])
                       analise_linguagem = gerar_analise_linguagem_amor(st.session_state["Linguagem_do_Amor"])
                       
                       # Gera análise integrativa
                       analise_integrativa_texto = gerar_analise_integrada(
                           st.session_state["Identificação"],
                           st.session_state["Linguagem_do_Amor"],
                           st.session_state["Temperamentos"],
                           st.session_state["Eneagrama"]
                       )
                       analise_integrativa = estruturar_analise_integrativa(analise_integrativa_texto)
                       
                       # Combina todas as análises
                       st.session_state["analise_completa"] = {
                           **analise_eneagrama,
                           **analise_temperamento,
                           **analise_linguagem,
                           **analise_integrativa
                       }
               except Exception as e:
                   st.error(f"Erro ao gerar análise: {str(e)}")
                   return

           # Exibe resultados na interface
           st.title("Análise Final Personalizada")
           
           # Exibe identificação
           st.header("Dados do Participante")
           st.write(f"""
           **Nome:** {st.session_state['Identificação']['nome']}
           **Tempo de Casamento:** {st.session_state['Identificação']['tempo_casado']} anos
           **Maior Queixa:** {st.session_state['Identificação']['maior_queixa']}
           **Maior Felicidade:** {st.session_state['Identificação']['maior_felicidade']}
           """)
           
           # Exibe resultados dos testes
           st.header("Resultados dos Testes")
           col1, col2, col3 = st.columns(3)
           
           with col1:
               st.subheader("Eneagrama")
               st.write(f"Tipo: {st.session_state['Eneagrama']['tipo_principal']}")
               st.write(f"Porcentagem: {st.session_state['Eneagrama']['porcentagem_principal']}%")
           
           with col2:
               st.subheader("Temperamento")
               temp_dominante = max(st.session_state['Temperamentos'].items(), key=lambda x: x[1])
               st.write(f"Dominante: {temp_dominante[0]}")
               st.write(f"Porcentagem: {temp_dominante[1]}%")
           
           with col3:
               st.subheader("Linguagens do Amor")
               linguagens_ordenadas = sorted(st.session_state['Linguagem_do_Amor'].items(), key=lambda x: x[1], reverse=True)
               st.write(f"Principal: {linguagens_ordenadas[0][0]}")
               st.write(f"Porcentagem: {linguagens_ordenadas[0][1]}%")
               st.write(f"Segunda: {linguagens_ordenadas[1][0]}")
               st.write(f"Porcentagem: {linguagens_ordenadas[1][1]}%")
           
           # Exibe análises em seções expansíveis
           st.header("Análises Detalhadas")
           for titulo, conteudo in st.session_state["analise_completa"].items():
               with st.expander(titulo.replace('_', ' ').title()):
                   st.markdown(conteudo)
           
           # Gera e oferece PDF para download
           try:
               pdf_file = gerar_pdf_personalizado(
                   st.session_state["Identificação"],
                   st.session_state["Linguagem_do_Amor"],
                   st.session_state["Temperamentos"],
                   st.session_state["Eneagrama"],
                   st.session_state["analise_completa"]
               )
               baixar_pdf(pdf_file)
           except Exception as e:
               st.error(f"Erro ao gerar PDF: {str(e)}")
               
       else:
           st.warning("Por favor, complete todos os testes antes de ver a análise final.")
           if st.button("Voltar ao Início"):
               st.session_state["pagina_atual"] = "Identificação"
               st.rerun()
               
   else:
       st.error("Página não encontrada")
       st.session_state["pagina_atual"] = "Identificação"
       st.rerun()

if __name__ == "__main__":
   main()

