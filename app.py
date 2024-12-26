import streamlit as st
from openai import OpenAI
from collections import Counter
from fpdf import FPDF
import os
from datetime import datetime

# Configuração do cliente OpenAI - usando direto o secrets do Streamlit Cloud
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

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

def calcular_linguagem_amor(respostas):
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
    
    return contagem

def calcular_temperamento(respostas):
    categorias = {
        "Sanguíneo": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 20],
        "Colérico": [1, 3, 5, 6, 7, 9, 10, 13, 14, 15],
        "Melancólico": [1, 2, 4, 5, 8, 9, 11, 12, 14, 15],
        "Fleumático": [6, 9, 10, 18, 20]
    }
    
    contagem = {categoria: 0 for categoria in categorias}
    
    for idx, resposta in enumerate(respostas.values(), start=1):
        if resposta == 'Sim':
            for categoria, indices in categorias.items():
                if idx in indices:
                    contagem[categoria] += 1
    
    return contagem

def calcular_eneagrama(respostas):
    categorias = [
        "Perfeccionista", "Doador", "Desempenhador", "Romântico", "Observador",
        "Questionador", "Entusiasta", "Desafiador", "Mediador"
    ]
    
    contagem = Counter(respostas)
    return {categorias[i]: contagem[chr(65+i)] for i in range(9)}

def exibir_top_resultados(categoria, resultados):
    resultados_ordenados = sorted(resultados.items(), key=lambda x: x[1], reverse=True)[:2]
    st.subheader(categoria)
    for categoria, valor in resultados_ordenados:
        st.markdown(f"<div class='result-item'><b>{categoria}:</b> {valor}</div>", unsafe_allow_html=True)

def exibir_identificacao():
    st.title("Mentoria RECONECTE-SE")
    st.write("Por favor, preencha os dados abaixo para começar.")
    
    nome = st.text_input("Nome Completo", key="nome_completo")
    tempo_casado = st.number_input("Tempo de casados (em anos)", min_value=0, max_value=100, key="tempo_casado")
    maior_queixa = st.text_area("Maior queixa no casamento", key="maior_queixa")
    maior_felicidade = st.text_area("Maior felicidade no casamento", key="maior_felicidade")
    
    if st.button("Iniciar Testes", key="iniciar_testes"):
        st.session_state["Identificação"] = {
            "nome": nome,
            "tempo_casado": tempo_casado,
            "maior_queixa": maior_queixa,
            "maior_felicidade": maior_felicidade
        }
        st.session_state["pagina_atual"] = "Linguagem_do_Amor"
        st.rerun()

def exibir_linguagens_do_amor():
    st.title("Teste das 5 Linguagens do Amor")
    respostas = []
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
    
    for pergunta, opcao in zip(perguntas, opcoes):
        st.write(pergunta)
        resposta = st.radio("", opcao, key=pergunta)
        respostas.append(resposta[0])

    if st.button("Enviar", key="enviar_linguagem"):
        resultado = calcular_linguagem_amor(respostas)
        st.session_state["Linguagem_do_Amor"] = resultado
        st.session_state["pagina_atual"] = "Temperamentos"
        st.rerun()

def exibir_resultados_simples(titulo, resultados):
    st.subheader(titulo)
    for categoria, valor in resultados.items():
        st.markdown(f"<div class='result-item'><b>{categoria}:</b> {valor}</div>", unsafe_allow_html=True)

def corrigir_caracteres(texto):
    return texto.encode('latin1', 'replace').decode('latin1')

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, corrigir_caracteres('Devolutiva Personalizada'), 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, corrigir_caracteres(title), 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, corrigir_caracteres(body))
        self.ln()

    def add_section(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)

def exibir_temperamentos():
    st.title("Teste de Temperamentos")
    
    temperamentos = {
        "Sanguíneo": [
            "1. Gosta de conversar?",
            "2. Gosta de atividade, ação?",
            "3. Emociona-se com facilidade?",
            "4. 'Explode' facilmente?",
            "5. Tem inclinação para conhecer muitos assuntos de vez, para cultura geral?",
            "6. Sua imaginação é viva?",
            "7. Tem inclinação para a crítica e para ironia?",
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
            "19. Gosta de andar elegante, bem(a) trajado?",
            "20. Gosta de ser admirado(a) pelos outros?"
        ],
        "Colérico": [
            "1. Irrita-se com facilidade?",
            "2. Quando se irrita, dissimula a irritação?",
            "3. Guarda rancor?",
            "4. Perdoa facilmente?",
            "5. Diante de uma oposição à sua opinião, tem tendência natural a ser intolerante?",
            "6. É obstinado? (teimoso, inflexível)",
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
            "17. Costuma pensar; meditar?",
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
    
    respostas = {}
    for temp, perguntas in temperamentos.items():
        st.subheader(f"Perguntas para o temperamento {temp}")
        for pergunta in perguntas:
            resposta = st.radio(pergunta, ["Sim", "Não"], key=f"{temp}_{pergunta}")
            respostas[f"{temp}_{pergunta}"] = resposta

    if st.button("Enviar", key="enviar_temperamentos"):
        resultado = calcular_temperamento(respostas)
        st.session_state["Temperamentos"] = resultado
        st.session_state["pagina_atual"] = "Eneagrama"
        st.rerun()
def exibir_eneagrama():
    st.title("Teste do Eneagrama")
    
    perguntas = [
        "1) Em qual situação você se enquadra?",
        "2) Concordo que…",
        "3) Em geral…",
        "4) Sinto que…",
        "5) Percebo que…",
        "6) Sei que…",
        "7) Na verdade"
    ]
    
    opcoes = [
        [
            "A - Sinto minha vida como uma busca incessante daquilo que julgo perfeito.",
            "B - Sou do tipo de pessoa que adora ser reconhecido e bajulado!",
            "C - Tenho compulsão pelo trabalho!",
            "D - Tenho a sensação permanente de falta… Simplesmente algo ainda não aconteceu na minha vida!",
            "E - Gosto de estar sozinho, pensando, meditando no meu canto em silêncio.",
            "F - Sou muito inseguro, tenho medo de qualquer situação nova ou daquelas que eu acho perigosas, pois podem não dar certo e me machucar.",
            "G - Sempre acho um significado positivo em tudo. Sou um idealista e otimista inveterado!",
            "H - Tenho dificuldades em aceitar opiniões contrárias às minhas.",
            "I - Às vezes, protelo o que tenho para fazer de mais importante, inventando um monte de desculpas."
        ],
        [
            "A - Primeiro a obrigação, depois a diversão!",
            "B - Toda a minha vida foi uma constante entrega de amor!",
            "C - Gosto de criar uma imagem positiva de mim mesmo.",
            "D - Sou extremamente sensível!",
            "E - Ter que ir a uma festa é um sofrimento para mim, especialmente por ter que ouvir tanta bobagem!",
            "F - Sempre demoro a concretizar algo, pois fico imaginando as possíveis consequências.",
            "G - Adoro explorar territórios novos. Gostaria de poder voar ou de colocar uma mochila nas costas e sair viajando pelo mundo!",
            "H - Para mim não existem obstáculos, sou capaz de qualquer esforço para conseguir o que quero.",
            "I - Tenho procurado pensar mais em mim, no meu bem-estar, mas confesso que é difícil."
        ],
        [
            "A - Meu dia-a-dia é tenso, cheio de cobranças e exigências.",
            "B - Agradar aos outros é bom, porque desse modo recebo o que quero.",
            "C - Tenho grandes dificuldades para expressar meus sentimentos.",
            "D - Nada no presente me faz feliz: a lembrança do passado é muito forte!",
            "E - Somente com pessoas do meu nível intelectual me sinto mais à vontade.",
            "F - Minha imaginação é poderosa e me provoca uma grande ansiedade.",
            "G - Sou uma pessoa muito versátil, sei fazer várias coisas diferentes.",
            "H - A vida é uma luta constante, só me aparecem desafios, só entro em complicações, mas no fundo até que gosto.",
            "I - Demoro a fazer as coisas, mas tento fazê-las bem feitas."
        ],
        [
            "A - Estou sempre dizendo: 'eu tenho que…', 'eu deveria…'",
            "B - Com jeitinho, consigo tudo o que quero.",
            "C - Tenho grandes dificuldades para ficar quieto, meditando!",
            "D - Não posso ser feliz em um mundo tão cego e insensível!",
            "E - Gosto de ser reconhecido pelos meus conhecimentos especializados.",
            "F - Tomar decisões é algo que não gosto e tento evitar sempre que possível.",
            "G - Considero-me uma pessoa muito criativa e audaciosa. Planejar me dá prazer, executar nem sempre.",
            "H - Abraço com muita determinação as causas que considero justas e verdadeiras.",
            "I - Estou sempre disposto a ajudar os outros."
        ],
        [
            "A - Se não pode ser bem feito, melhor não fazer!",
            "B - Fico zangado quando as pessoas das quais espero reconhecimento me ignoram ou me fazem sentir em segundo lugar!",
            "C - Quando fracasso, recupero-me rapidamente.",
            "D - Ninguém compreende meus sentimentos.",
            "E - Meu quarto é o único local da casa no qual posso ficar mais livre, sem ter que falar com ninguém.",
            "F - Não aceito ser controlado ou obrigado a fazer algo.",
            "G - Tento manter sempre o alto astral!",
            "H - Preciso controlar tudo, mesmo percebendo quanto isso me faz mal no sentido de gastar muita energia.",
            "I - É fácil me adaptar a qualquer tipo de pessoa."
        ],
        [
            "A - Desde muito cedo me foi incutido um senso de responsabilidade, no sentido de que deveria dar o exemplo.",
            "B - Ajudar as pessoas é maravilhoso.",
            "C - É difícil ter tempo para minhas próprias necessidades.",
            "D - Melancolia, esse é meu estado permanente!",
            "E - Tenho dificuldades para viver relacionamentos amorosos.",
            "F - Sentir-se seguro é essencial.",
            "G - Minhas grandes paixões são as ideias, os novos conhecimentos e desafios.",
            "H - Nunca estou satisfeito, sempre desejo conquistar mais e mais!",
            "I - Costumo adiar muitas coisas importantes para mim."
        ],
        [
            "A - Sempre faço tudo bem feito!",
            "B - Adoro aplausos! A vida é um espetáculo…",
            "C - Modestamente, sou o melhor na minha área.",
            "D - Me sinto diferente aos demais, sinto o que ninguém é capaz de sentir.",
            "E - Eu sou capaz de ter momentos privados de lazer; sozinho é melhor!",
            "F - Não gosto nada de falar de mim. Além de não gostar, não tenho a menor vontade.",
            "G - Sou um pouco (ou muito) narcisista, simplesmente me adoro!",
            "H - Sinto que posso conquistar o mundo!",
            "I - Procuro me ajustar ao mundo, dividindo-me entre todos os que me rodeiam, facilitando-lhes ou resolvendo a vida."
        ]
    ]
    
    respostas = []
    
    for pergunta, opcoes_pergunta in zip(perguntas, opcoes):
        st.write(pergunta)
        resposta = st.radio("", opcoes_pergunta, key=pergunta)
        respostas.append(resposta[0])
    
    if st.button("Enviar", key="enviar_eneagrama"):
        resultado = calcular_eneagrama(respostas)
        st.session_state["Eneagrama"] = resultado
        st.session_state["pagina_atual"] = "Análise Final"
        st.rerun()



def gerar_pdf_completo_ia(identificacao, linguagem_amor, temperamento, eneagrama, analise):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Página de Identificação
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, corrigir_caracteres('Devolutiva Personalizada'), ln=True, align='C')
    pdf.ln(10)
    
    # Dados Pessoais
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, corrigir_caracteres('Dados Pessoais'), ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, corrigir_caracteres(
        f"Nome: {identificacao['nome']}\n"
        f"Tempo de Casamento: {identificacao['tempo_casado']} anos\n"
        f"Maior Queixa: {identificacao['maior_queixa']}\n"
        f"Maior Felicidade: {identificacao['maior_felicidade']}"
    ))
    
    # Página de Resultados
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, corrigir_caracteres('Resultados dos Testes'), ln=True)
    
    # Linguagens do Amor
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, corrigir_caracteres('Linguagens do Amor:'), ln=True)
    pdf.set_font('Arial', '', 12)
    for linguagem, valor in sorted(linguagem_amor.items(), key=lambda x: x[1], reverse=True):
        pdf.cell(0, 10, corrigir_caracteres(f"{linguagem}: {valor} pontos"), ln=True)
    
    # Temperamentos
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, corrigir_caracteres('Temperamentos:'), ln=True)
    pdf.set_font('Arial', '', 12)
    for temp, valor in sorted(temperamento.items(), key=lambda x: x[1], reverse=True):
        pdf.cell(0, 10, corrigir_caracteres(f"{temp}: {valor} pontos"), ln=True)
    
    # Eneagrama
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, corrigir_caracteres('Eneagrama:'), ln=True)
    pdf.set_font('Arial', '', 12)
    for tipo, valor in sorted(eneagrama.items(), key=lambda x: x[1], reverse=True):
        pdf.cell(0, 10, corrigir_caracteres(f"{tipo}: {valor} pontos"), ln=True)
    
    # Análise Detalhada
    sections = [
        "1. ANÁLISE DAS LINGUAGENS DO AMOR",
        "2. ANÁLISE DOS TEMPERAMENTOS",
        "3. ANÁLISE DO ENEAGRAMA",
        "4. RECOMENDAÇÕES PRÁTICAS",
        "5. CONCLUSÃO PERSONALIZADA"
    ]
    
    current_section = ""
    section_content = []
    
    for line in analise.split('\n'):
        if any(section in line for section in sections):
            if current_section and section_content:
                pdf.add_page()
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, corrigir_caracteres(current_section), ln=True)
                pdf.set_font('Arial', '', 12)
                pdf.multi_cell(0, 10, corrigir_caracteres('\n'.join(section_content)))
            current_section = line
            section_content = []
        else:
            section_content.append(line)
    
    # Adicionar última seção
    if current_section and section_content:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, corrigir_caracteres(current_section), ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, corrigir_caracteres('\n'.join(section_content)))
    
    output_filename = f"devolutiva_{identificacao['nome']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(output_filename)
    return output_filename

def baixar_pdf(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.download_button(
                label="Baixar Relatório em PDF",
                data=f,
                file_name=os.path.basename(file_path),
                mime='application/pdf'
            )
def exibir_eneagrama():
    st.title("Teste do Eneagrama")
    
    perguntas = [
        "1) Em qual situação você se enquadra?",
        "2) Concordo que…",
        "3) Em geral…",
        "4) Sinto que…",
        "5) Percebo que…",
        "6) Sei que…",
        "7) Na verdade"
    ]
    
    opcoes = [
        [
            "A - Sinto minha vida como uma busca incessante daquilo que julgo perfeito.",
            "B - Sou do tipo de pessoa que adora ser reconhecido e bajulado!",
            "C - Tenho compulsão pelo trabalho!",
            "D - Tenho a sensação permanente de falta… Simplesmente algo ainda não aconteceu na minha vida!",
            "E - Gosto de estar sozinho, pensando, meditando no meu canto em silêncio.",
            "F - Sou muito inseguro, tenho medo de qualquer situação nova ou daquelas que eu acho perigosas, pois podem não dar certo e me machucar.",
            "G - Sempre acho um significado positivo em tudo. Sou um idealista e otimista inveterado!",
            "H - Tenho dificuldades em aceitar opiniões contrárias às minhas.",
            "I - Às vezes, protelo o que tenho para fazer de mais importante, inventando um monte de desculpas."
        ],
        [
            "A - Primeiro a obrigação, depois a diversão!",
            "B - Toda a minha vida foi uma constante entrega de amor!",
            "C - Gosto de criar uma imagem positiva de mim mesmo.",
            "D - Sou extremamente sensível!",
            "E - Ter que ir a uma festa é um sofrimento para mim, especialmente por ter que ouvir tanta bobagem!",
            "F - Sempre demoro a concretizar algo, pois fico imaginando as possíveis consequências.",
            "G - Adoro explorar territórios novos. Gostaria de poder voar ou de colocar uma mochila nas costas e sair viajando pelo mundo!",
            "H - Para mim não existem obstáculos, sou capaz de qualquer esforço para conseguir o que quero.",
            "I - Tenho procurado pensar mais em mim, no meu bem-estar, mas confesso que é difícil."
        ],
        [
            "A - Meu dia-a-dia é tenso, cheio de cobranças e exigências.",
            "B - Agradar aos outros é bom, porque desse modo recebo o que quero.",
            "C - Tenho grandes dificuldades para expressar meus sentimentos.",
            "D - Nada no presente me faz feliz: a lembrança do passado é muito forte!",
            "E - Somente com pessoas do meu nível intelectual me sinto mais à vontade.",
            "F - Minha imaginação é poderosa e me provoca uma grande ansiedade.",
            "G - Sou uma pessoa muito versátil, sei fazer várias coisas diferentes.",
            "H - A vida é uma luta constante, só me aparecem desafios, só entro em complicações, mas no fundo até que gosto.",
            "I - Demoro a fazer as coisas, mas tento fazê-las bem feitas."
        ],
        [
            "A - Estou sempre dizendo: 'eu tenho que…', 'eu deveria…'",
            "B - Com jeitinho, consigo tudo o que quero.",
            "C - Tenho grandes dificuldades para ficar quieto, meditando!",
            "D - Não posso ser feliz em um mundo tão cego e insensível!",
            "E - Gosto de ser reconhecido pelos meus conhecimentos especializados.",
            "F - Tomar decisões é algo que não gosto e tento evitar sempre que possível.",
            "G - Considero-me uma pessoa muito criativa e audaciosa. Planejar me dá prazer, executar nem sempre.",
            "H - Abraço com muita determinação as causas que considero justas e verdadeiras.",
            "I - Estou sempre disposto a ajudar os outros."
        ],
        [
            "A - Se não pode ser bem feito, melhor não fazer!",
            "B - Fico zangado quando as pessoas das quais espero reconhecimento me ignoram ou me fazem sentir em segundo lugar!",
            "C - Quando fracasso, recupero-me rapidamente.",
            "D - Ninguém compreende meus sentimentos.",
            "E - Meu quarto é o único local da casa no qual posso ficar mais livre, sem ter que falar com ninguém.",
            "F - Não aceito ser controlado ou obrigado a fazer algo.",
            "G - Tento manter sempre o alto astral!",
            "H - Preciso controlar tudo, mesmo percebendo quanto isso me faz mal no sentido de gastar muita energia.",
            "I - É fácil me adaptar a qualquer tipo de pessoa."
        ],
        [
            "A - Desde muito cedo me foi incutido um senso de responsabilidade, no sentido de que deveria dar o exemplo.",
            "B - Ajudar as pessoas é maravilhoso.",
            "C - É difícil ter tempo para minhas próprias necessidades.",
            "D - Melancolia, esse é meu estado permanente!",
            "E - Tenho dificuldades para viver relacionamentos amorosos.",
            "F - Sentir-se seguro é essencial.",
            "G - Minhas grandes paixões são as ideias, os novos conhecimentos e desafios.",
            "H - Nunca estou satisfeito, sempre desejo conquistar mais e mais!",
            "I - Costumo adiar muitas coisas importantes para mim."
        ],
        [
            "A - Sempre faço tudo bem feito!",
            "B - Adoro aplausos! A vida é um espetáculo…",
            "C - Modestamente, sou o melhor na minha área.",
            "D - Me sinto diferente aos demais, sinto o que ninguém é capaz de sentir.",
            "E - Eu sou capaz de ter momentos privados de lazer; sozinho é melhor!",
            "F - Não gosto nada de falar de mim. Além de não gostar, não tenho a menor vontade.",
            "G - Sou um pouco (ou muito) narcisista, simplesmente me adoro!",
            "H - Sinto que posso conquistar o mundo!",
            "I - Procuro me ajustar ao mundo, dividindo-me entre todos os que me rodeiam, facilitando-lhes ou resolvendo a vida."
        ]
    ]
    
    respostas = []
    
    for pergunta, opcoes_pergunta in zip(perguntas, opcoes):
        st.write(pergunta)
        resposta = st.radio("", opcoes_pergunta, key=pergunta)
        respostas.append(resposta[0])
    
    if st.button("Enviar", key="enviar_eneagrama"):
        resultado = calcular_eneagrama(respostas)
        st.session_state["Eneagrama"] = resultado
        st.session_state["pagina_atual"] = "Análise Final"
        st.rerun()

def gerar_analise_integrada(identificacao, linguagem_amor, temperamento, eneagrama):
    # Organizar os dados em ordem para fornecer ao modelo como contexto
    linguagens_ordenadas = sorted(linguagem_amor.items(), key=lambda x: x[1], reverse=True)
    temperamentos_ordenados = sorted(temperamento.items(), key=lambda x: x[1], reverse=True)
    eneagramas_ordenados = sorted(eneagrama.items(), key=lambda x: x[1], reverse=True)
    
    # Prompt ajustado para fornecer os dados como contexto, sem estrutura rígida
    prompt = f"""
    Você é um terapeuta especializado em casais. Forneça uma análise detalhada sobre o relacionamento de {identificacao['nome']} com base nas informações abaixo. Use as informações como contexto para sua análise e sugestões.

    DADOS DO RELACIONAMENTO:
    - Tempo de casamento: {identificacao['tempo_casado']} anos
    - Maior desafio: {identificacao['maior_queixa']}
    - Maior felicidade: {identificacao['maior_felicidade']}

    RESULTADOS DOS TESTES:

    Linguagens do Amor principais:
    - {linguagens_ordenadas[0][0]}: {linguagens_ordenadas[0][1]} pontos
    - {linguagens_ordenadas[1][0]}: {linguagens_ordenadas[1][1]} pontos

    Temperamentos predominantes:
    - {temperamentos_ordenados[0][0]}: {temperamentos_ordenados[0][1]} pontos
    - {temperamentos_ordenados[1][0]}: {temperamentos_ordenados[1][1]} pontos

    Eneagrama:
    - {eneagramas_ordenados[0][0]}: {eneagramas_ordenados[0][1]} pontos

    Com essas informações, faça uma análise livre, explicando como esses fatores influenciam o relacionamento de {identificacao['nome']}, e ofereça sugestões práticas para melhorar a relação.
    """

    try:
        # Chamada à API do OpenAI para gerar a análise
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um terapeuta conjugal experiente que fornece análises personalizadas e práticas."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,  # Mantenha a temperatura moderada para criatividade, mas com controle
            max_tokens=2000  # Ajuste o número de tokens conforme necessário
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Erro ao gerar análise: {e}")
        return None



def gerar_pdf_completo_ia(identificacao, linguagem_amor, temperamento, eneagrama, analise):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Página de Identificação
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, corrigir_caracteres('Devolutiva Personalizada'), ln=True, align='C')
    pdf.ln(10)
    
    # Dados Pessoais
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, corrigir_caracteres('Dados Pessoais'), ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, corrigir_caracteres(
        f"Nome: {identificacao['nome']}\n"
        f"Tempo de Casamento: {identificacao['tempo_casado']} anos\n"
        f"Maior Queixa: {identificacao['maior_queixa']}\n"
        f"Maior Felicidade: {identificacao['maior_felicidade']}"
    ))
    
    # Página de Resultados
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, corrigir_caracteres('Resultados dos Testes'), ln=True)
    
    # Linguagens do Amor
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, corrigir_caracteres('Linguagens do Amor:'), ln=True)
    pdf.set_font('Arial', '', 12)
    for linguagem, valor in sorted(linguagem_amor.items(), key=lambda x: x[1], reverse=True):
        pdf.cell(0, 10, corrigir_caracteres(f"{linguagem}: {valor} pontos"), ln=True)
    
    # Temperamentos
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, corrigir_caracteres('Temperamentos:'), ln=True)
    pdf.set_font('Arial', '', 12)
    for temp, valor in sorted(temperamento.items(), key=lambda x: x[1], reverse=True):
        pdf.cell(0, 10, corrigir_caracteres(f"{temp}: {valor} pontos"), ln=True)
    
    # Eneagrama
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, corrigir_caracteres('Eneagrama:'), ln=True)
    pdf.set_font('Arial', '', 12)
    for tipo, valor in sorted(eneagrama.items(), key=lambda x: x[1], reverse=True):
        pdf.cell(0, 10, corrigir_caracteres(f"{tipo}: {valor} pontos"), ln=True)
    
    # Análise Detalhada
    sections = [
        "1. ANÁLISE DAS LINGUAGENS DO AMOR",
        "2. ANÁLISE DOS TEMPERAMENTOS",
        "3. ANÁLISE DO ENEAGRAMA",
        "4. RECOMENDAÇÕES PRÁTICAS",
        "5. CONCLUSÃO PERSONALIZADA"
    ]
    
    current_section = ""
    section_content = []
    
    for line in analise.split('\n'):
        if any(section in line for section in sections):
            if current_section and section_content:
                pdf.add_page()
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, corrigir_caracteres(current_section), ln=True)
                pdf.set_font('Arial', '', 12)
                pdf.multi_cell(0, 10, corrigir_caracteres('\n'.join(section_content)))
            current_section = line
            section_content = []
        else:
            section_content.append(line)
    
    # Adicionar última seção
    if current_section and section_content:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, corrigir_caracteres(current_section), ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, corrigir_caracteres('\n'.join(section_content)))
    
    output_filename = f"devolutiva_{identificacao['nome']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(output_filename)
    return output_filename

def baixar_pdf(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.download_button(
                label="Baixar Relatório em PDF",
                data=f,
                file_name=os.path.basename(file_path),
                mime='application/pdf'
            )
def exibir_analise_final():
    st.title("Análise Final Personalizada")
    
    identificacao = st.session_state.get("Identificação", {})
    linguagem_amor = st.session_state.get("Linguagem_do_Amor", {})
    temperamento = st.session_state.get("Temperamentos", {})
    eneagrama = st.session_state.get("Eneagrama", {})
    
    if all([identificacao, linguagem_amor, temperamento, eneagrama]):
        # Exibir resultados atuais
        st.header("Seus Resultados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Dados Pessoais")
            st.write(f"**Nome:** {identificacao['nome']}")
            st.write(f"**Tempo de Casamento:** {identificacao['tempo_casado']} anos")
            st.write(f"**Maior Queixa:** {identificacao['maior_queixa']}")
            st.write(f"**Maior Felicidade:** {identificacao['maior_felicidade']}")
        
        with col2:
            linguagens_ordenadas = sorted(linguagem_amor.items(), key=lambda x: x[1], reverse=True)
            temperamentos_ordenados = sorted(temperamento.items(), key=lambda x: x[1], reverse=True)
            eneagramas_ordenados = sorted(eneagrama.items(), key=lambda x: x[1], reverse=True)
            
            exibir_top_resultados("Linguagens do Amor", dict(linguagens_ordenadas))
            exibir_top_resultados("Temperamentos", dict(temperamentos_ordenados))
            exibir_top_resultados("Eneagrama", dict(eneagramas_ordenados))

        analise = gerar_analise_integrada(identificacao, linguagem_amor, temperamento, eneagrama)
        
        if analise:
            st.header("Análise Personalizada")
            st.markdown(f"<div class='analysis-text'>{analise}</div>", unsafe_allow_html=True)
            
            pdf_file = gerar_pdf_completo_ia(identificacao, linguagem_amor, temperamento, eneagrama, analise)
            baixar_pdf(pdf_file)
            
            try:
                os.remove(pdf_file)
            except:
                pass
    else:
        st.warning("Complete todos os testes antes de ver a análise final.")

def main():
    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = "Identificação"

    if st.session_state["pagina_atual"] == "Identificação":
        exibir_identificacao()
    elif st.session_state["pagina_atual"] == "Linguagem_do_Amor":
        exibir_linguagens_do_amor()
    elif st.session_state["pagina_atual"] == "Temperamentos":
        exibir_temperamentos()
    elif st.session_state["pagina_atual"] == "Eneagrama":
        exibir_eneagrama()
    elif st.session_state["pagina_atual"] == "Análise Final":
        exibir_analise_final()
    else:
        st.error("Página não encontrada")
        st.session_state["pagina_atual"] = "Identificação"
        st.rerun()

if __name__ == "__main__":
    main()
