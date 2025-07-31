import streamlit as st
import textwrap # Para formatar o código gerado
from datetime import datetime
import plotly.graph_objects as go # Para visualização 3D com Plotly
from stl import mesh # Para ler arquivos STL com numpy-stl
import numpy as np # Para manipulação de arrays

# --- Interface do Usuário com Streamlit ---
st.set_page_config(layout="wide") # Opcional: para usar a largura total da tela
st.title("��️ Designer Paramétrico de Inserts para Jogos de Tabuleiro (OpenSCAD)")
st.write("Ajuste os parâmetros do seu insert e gere o código OpenSCAD (`.scad`) para criar o modelo 3D localmente.")

st.warning("Atenção: A geração do modelo 3D é feita localmente no seu computador. Este aplicativo gera o código OpenSCAD para você.")

# --- Seção de Parâmetros na barra lateral ---
st.sidebar.header("Parâmetros do Insert")
st.sidebar.subheader("Dimensões da Caixa Principal")
length = st.sidebar.slider("Comprimento do Insert (mm)", 10, 300, 100, key="len_insert_scad")
width = st.sidebar.slider("Largura do Insert (mm)", 10, 200, 50, key="wid_insert_scad")
height = st.sidebar.slider("Altura do Insert (mm)", 5, 100, 25, key="hei_insert_scad")
thickness = st.sidebar.slider("Espessura da Parede (mm)", 0.5, 5.0, 1.5, step=0.1, key="thick_insert_scad")

# Seção de Parâmetros do Slot (Exemplo de Corte)
st.sidebar.subheader("Detalhes do Corte/Slot (Opcional)")
add_slot = st.sidebar.checkbox("Adicionar Corte/Slot?", value=True, key="add_slot_scad")

# Variáveis para garantir que os sliders do slot tenham limites válidos
# Estes valores são usados apenas para o range do slider, não para a geometria real do slot
# O range ideal é 0 até (dimensão - dimensão_do_slot), então usamos defaults para cálculo do range.
slot_length_for_range = length / 2
slot_width_for_range = width / 2
slot_height_for_range = height / 2


if add_slot:
    st.sidebar.subheader("Posição do Corte (Canto Inferior Frontal)")
    # Calcula limites dos sliders para evitar que o slot saia da caixa
    max_x_pos = max(0.0, float(length - slot_length_for_range))
    max_y_pos = max(0.0, float(width - slot_width_for_range))
    max_z_pos = max(0.0, float(height - slot_height_for_range))

    slot_x_pos = st.sidebar.slider("Posição X do Corte (mm)", 0.0, max_x_pos, float(length)/4, step=1.0, key="sx_pos_scad")
    slot_y_pos = st.sidebar.slider("Posição Y do Corte (mm)", 0.0, max_y_pos, float(width)/4, step=1.0, key="sy_pos_scad")
    slot_z_pos = st.sidebar.slider("Posição Z do Corte (mm)", 0.0, max_z_pos, 0.0, step=1.0, key="sz_pos_scad")

    st.sidebar.subheader("Dimensões do Corte")
    slot_length_val = st.sidebar.slider("Comprimento do Corte (mm)", 1.0, float(length), float(slot_length_for_range), step=1.0, key="sl_len_scad")
    slot_width_val = st.sidebar.slider("Largura do Corte (mm)", 1.0, float(width), float(slot_width_for_range), step=1.0, key="sl_wid_scad")
    slot_height_val = st.sidebar.slider("Altura do Corte (mm)", 1.0, float(height), float(slot_height_for_range), step=1.0, key="sl_hei_scad")
else:
    # Valores dummy se o slot não for adicionado (não aparecerão no código gerado)
    slot_x_pos, slot_y_pos, slot_z_pos = 0, 0, 0
    slot_length_val, slot_width_val, slot_height_val = 1, 1, 1

st.sidebar.markdown("---")
st.sidebar.info("Ajuste os parâmetros na barra lateral para gerar o código OpenSCAD. Use a seção 'Visualizador 3D' para ver seu arquivo STL.")

# --- Geração do Código OpenSCAD ---

generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Definição do módulo da caixa oca
hollow_box_module_def = f"""
// --- Módulo principal do Insert (Caixa Oca) ---
module create_hollow_box(len, wid, hei, thick_val) {{
    difference() {{
        // Caixa externa
        cube([len, wid, hei]);

        // Caixa interna (buraco), posicionada para deixar fundo e paredes com espessura 'thick_val', e topo aberto.
        // A altura da caixa interna é maior que a externa para garantir o corte total do topo.
        translate([thick_val, thick_val, thick_val]) {{
            cube([len - (2 * thick_val), wid - (2 * thick_val), hei * 2]); // 'hei * 2' garante que o topo seja cortado completamente
        }}
    }}
}}
"""

# Chamada do módulo da caixa oca para o modelo base
base_shape_call = "create_hollow_box(insert_length, insert_width, insert_height, wall_thickness);"

# Definição do cortador de slot (se ativado)
slot_cutter_def = ""
slot_cutter_geometry_call = ""
if add_slot:
    slot_cutter_def = f"""
// Parâmetros do Corte/Slot
slot_pos_x = {slot_x_pos};
slot_pos_y = {slot_y_pos};
slot_pos_z = {slot_z_pos};
slot_len = {slot_length_val};
slot_wid = {slot_width_val};
slot_hei = {slot_height_val};

// Geometria do cortador de slot
// É um cubo transladado para a posição e dimensões definidas
slot_cutter_geometry = translate([slot_pos_x, slot_pos_y, slot_pos_z]) {{
    cube([slot_len, slot_wid, slot_hei]);
}};
"""
    slot_cutter_geometry_call = "slot_cutter_geometry;" # Nome da geometria para ser usada na operação final

# Monta a operação geométrica final de forma declarativa
final_geometric_operation = ""
if add_slot:
    final_geometric_operation = f"""
difference() {{
    {base_shape_call} // O modelo base
    {slot_cutter_geometry_call} // O cortador de slot
}}
"""
else:
    final_geometric_operation = base_shape_call # Apenas o modelo base se não houver slot

# Assemble the full OpenSCAD code string
openscad_code = f"""
// Generated by Streamlit Insert Designer on {generated_date}

// --- Parâmetros do Insert ---
// As dimensões são em milímetros (mm)
insert_length = {length};
insert_width = {width};
insert_height = {height};
wall_thickness = {thickness};

// --- Cálculo das dimensões internas para ocação (apenas para referência, não usado diretamente no módulo) ---
inner_length = insert_length - (2 * wall_thickness);
inner_width = insert_width - (2 * wall_thickness);
inner_height = insert_height - wall_thickness; 

// Garante que as dimensões internas não sejam negativas (apenas para referência)
inner_length = max(0.1, inner_length);
inner_width = max(0.1, inner_width);
inner_height = max(0.1, inner_height);

{hollow_box_module_def} 

{slot_cutter_def} 

// --- Renderizar o Modelo Final ---
// O modelo é construído de forma declarativa aqui, usando as operações e módulos definidos.
{final_geometric_operation}

// Você pode exportar este modelo como STL no OpenSCAD:
// File -> Export -> Export as STL...
"""

formatted_code = textwrap.dedent(openscad_code).strip()

st.subheader("Seu Código OpenSCAD Gerado (.scad):")
st.code(formatted_code, language="c")

# Botões para Copiar e Baixar
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.button("Copiar Código", on_click=lambda: st.session_state.update(copy_code_scad=formatted_code), key="copy_btn_scad")
    if 'copy_code_scad' in st.session_state:
        st.code(st.session_state.copy_code_scad, language="c", show_copy_button=True)
with col2:
    st.download_button(
        label="Baixar Script OpenSCAD",
        data=formatted_code,
        file_name="insert_design.scad",
        mime="text/plain"
    )

st.markdown("---")
st.subheader("Como Usar o Código Gerado no OpenSCAD:")
st.markdown("""
1.  **Baixe o script** (`insert_design.scad`) ou **copie o código** acima.
2.  Abra o arquivo `.scad` baixado (ou cole o código copiado) no seu software **OpenSCAD** instalado no computador.
3.  No OpenSCAD, você verá uma visualização do seu insert.
4.  Para obter o arquivo 3D para impressão, vá em `File > Export > Export as STL...` e salve o modelo (`.stl`).
""")

st.markdown("---")
st.header("✨ Visualizador 3D de Modelos STL (Powered by Plotly)")
st.write("Faça o upload do seu arquivo STL (gerado pelo OpenSCAD localmente) para visualizá-lo aqui.")

uploaded_file = st.file_uploader("Escolha um arquivo STL", type=["stl"])

if uploaded_file is not None:
    try:
        # Lê o conteúdo do arquivo STL em memória
        import io
        byte_stream = io.BytesIO(uploaded_file.getvalue())
        
        # Carrega a malha STL
        your_mesh = mesh.Mesh.from_file(None, fh=byte_stream)

        # Extrai os dados para Plotly
        # Cada triângulo tem 3 vértices, cada vértice tem 3 coordenadas (x,y,z)
        # Reshape the vectors to get a list of all unique vertices
        x, y, z = your_mesh.vectors.reshape(-1, 3).T
        
        # Create indices for the faces (triangles)
        # Each face is a set of 3 indices from the flattened list of vertices
        # This assumes a sequential indexing for the flattened vertices
        i = np.arange(len(your_mesh.vectors) * 3).reshape(-1, 3)[:, 0]
        j = np.arange(len(your_mesh.vectors) * 3).reshape(-1, 3)[:, 1]
        k = np.arange(len(your_mesh.vectors) * 3).reshape(-1, 3)[:, 2]

        # Cria a figura 3D com Plotly
        fig = go.Figure(data=[go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k,
                                        color='lightblue', opacity=0.8)])

        # Configura o layout da cena 3D para manter a proporção correta
        fig.update_layout(
            scene_aspectmode='data', # Garante que as proporções X, Y, Z sejam respeitadas
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                xaxis=dict(showgrid=False, showbackground=False, zeroline=False),
                yaxis=dict(showgrid=False, showbackground=False, zeroline=False),
                zaxis=dict(showgrid=False, showbackground=False, zeroline=False),
            ),
            margin=dict(l=0, r=0, b=0, t=0), # Remove margens para maximizar o espaço
            height=600 # Altura fixa do gráfico
        )

        st.plotly_chart(fig, use_container_width=True)
        st.success("Modelo STL carregado e visualizado com sucesso!")
        st.info("Você pode arrastar o mouse para rotacionar o modelo e usar a roda do scroll para zoom.")

    except Exception as e:
        st.error(f"Não foi possível visualizar o arquivo STL. Erro: {e}")
        st.info("Por favor, verifique se o arquivo STL está bem formado ou tente novamente.")
else:
    st.info("Faça o upload de um arquivo .stl para visualizar seu modelo 3D.")


st.markdown("---")
st.info("Michel, este aplicativo age como seu 'designer' paramétrico online e agora também como um 'visualizador' para seus modelos STL. O OpenSCAD no seu computador continua sendo a 'fábrica' para gerar o STL.")
