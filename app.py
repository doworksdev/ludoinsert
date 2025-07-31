import streamlit as st
import textwrap # Para formatar o código gerado

# --- Interface do Usuário com Streamlit ---
st.set_page_config(layout="wide") # Opcional: para usar a largura total da tela
st.title("🛠️ Designer Paramétrico de Inserts para Jogos de Tabuleiro (OpenSCAD)")
st.write("Ajuste os parâmetros do seu insert e gere o código OpenSCAD (`.scad`) para criar o modelo 3D localmente.")

st.warning("Atenção: A geração do modelo 3D é feita localmente no seu computador. Este aplicativo gera o código OpenSCAD para você.")

# Seção de Parâmetros na barra lateral
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
# Se o slot não for adicionado, esses valores não serão usados no código OpenSCAD final
slot_length_default = length / 2
slot_width_default = width / 2
slot_height_default = height / 2

if add_slot:
    st.sidebar.subheader("Posição do Corte (Canto Inferior Frontal)")
    slot_x_pos = st.sidebar.slider("Posição X do Corte (mm)", 0.0, float(length - slot_length_default), float(length)/4, step=1.0, key="sx_pos_scad")
    slot_y_pos = st.sidebar.slider("Posição Y do Corte (mm)", 0.0, float(width - slot_width_default), float(width)/4, step=1.0, key="sy_pos_scad")
    slot_z_pos = st.sidebar.slider("Posição Z do Corte (mm)", 0.0, float(height - slot_height_default), 0.0, step=1.0, key="sz_pos_scad") # Ajustado para não ir além da altura

    st.sidebar.subheader("Dimensões do Corte")
    slot_length_val = st.sidebar.slider("Comprimento do Corte (mm)", 1.0, float(length), float(slot_length_default), step=1.0, key="sl_len_scad")
    slot_width_val = st.sidebar.slider("Largura do Corte (mm)", 1.0, float(width), float(slot_width_default), step=1.0, key="sl_wid_scad")
    slot_height_val = st.sidebar.slider("Altura do Corte (mm)", 1.0, float(height), float(slot_height_default), step=1.0, key="sl_hei_scad")
else:
    # Valores dummy se o slot não for adicionado (não aparecerão no código gerado)
    slot_x_pos, slot_y_pos, slot_z_pos = 0, 0, 0
    slot_length_val, slot_width_val, slot_height_val = 1, 1, 1

st.sidebar.markdown("---")
st.sidebar.info("Ajuste os parâmetros na barra lateral e o código OpenSCAD será gerado abaixo.")

# --- Geração do Código OpenSCAD ---

# Declaração de variáveis OpenSCAD para melhor legibilidade no código gerado
openscad_code = f"""
// --- Parâmetros do Insert ---
// As dimensões são em milímetros (mm)
insert_length = {length};
insert_width = {width};
insert_height = {height};
wall_thickness = {thickness};

// --- Cálculo das dimensões internas para ocação ---
inner_length = insert_length - (2 * wall_thickness);
inner_width = insert_width - (2 * wall_thickness);
inner_height = insert_height - wall_thickness; // Para deixar o topo aberto

// Garante que as dimensões internas não sejam negativas
inner_length = max(0.1, inner_length);
inner_width = max(0.1, inner_width);
inner_height = max(0.1, inner_height);

// --- Módulo principal do Insert ---
module create_hollow_box(len, wid, hei, thick_val) {{
    difference() {{
        // Caixa externa
        cube([len, wid, hei]);

        // Caixa interna (para ocação), posicionada para deixar o topo aberto
        translate([thick_val, thick_val, thick_val]) {{
            cube([len - (2 * thick_val), wid - (2 * thick_val), hei - thick_val]);
        }}
    }}
}}

// --- Construção do Insert Principal ---
insert_model = create_hollow_box(insert_length, insert_width, insert_height, wall_thickness);

// --- Adicionar Corte/Slot (Opcional) ---
"""

if add_slot:
    openscad_code += f"""
// Parâmetros do Corte/Slot
slot_pos_x = {slot_x_pos};
slot_pos_y = {slot_y_pos};
slot_pos_z = {slot_z_pos};
slot_len = {slot_length_val};
slot_wid = {slot_width_val};
slot_hei = {slot_height_val};

// Adiciona o corte ao modelo do insert
insert_model = difference() {{
    insert_model; // O modelo atual do insert
    translate([slot_pos_x, slot_pos_y, slot_pos_z]) {{
        cube([slot_len, slot_wid, slot_hei]);
    }}
}};
"""

openscad_code += f"""
// --- Renderizar o Modelo Final ---
insert_model;

// Você pode exportar este modelo como STL no OpenSCAD:
// File -> Export -> Export as STL...
"""

# Remove recuo extra para o código exibido e ajusta indentação
# Use textwrap.dedent para remover o recuo inicial
formatted_code = textwrap.dedent(openscad_code).strip()
# Adicione um cabeçalho informativo com a data de geração
from datetime import datetime
generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
formatted_code = f"// Generated by Streamlit Insert Designer on {generated_date}\n\n" + formatted_code


st.subheader("Seu Código OpenSCAD Gerado (.scad):")
st.code(formatted_code, language="c") # Use 'c' ou 'text' para OpenSCAD, pois não há 'openscad' como idioma padrão

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
        mime="text/plain" # Tipo MIME para arquivos .scad
    )

st.markdown("---")
st.subheader("Como Usar o Código Gerado no OpenSCAD:")
st.markdown("""
1.  **Baixe o script** (`insert_design.scad`) ou **copie o código** acima.
2.  Abra o arquivo `.scad` baixado (ou cole o código copiado) no seu software **OpenSCAD** instalado no computador.
3.  No OpenSCAD, você verá uma visualização do seu insert.
4.  Para obter o arquivo 3D para impressão, vá em `File > Export > Export as STL...` e salve o modelo.
""")

st.info("Michel, este aplicativo age como seu 'designer' paramétrico online. O OpenSCAD no seu computador continua sendo a 'fábrica' para gerar o STL. Mas agora você tem uma interface web para criar seus designs de forma super fácil!")
