import streamlit as st
import cadquery as cq
import plotly.graph_objects as go
import numpy as np

# --- Funções de Criação e Conversão ---

def create_box_with_slot(length, width, height, add_slot, slot_x, slot_y, slot_z, slot_l, slot_w, slot_h):
    """
    Cria um modelo 3D de uma caixa com um slot opcional usando CadQuery.
    """
    # Cria a caixa principal centralizada na origem (0,0,0)
    box = cq.Workplane("XY").box(length, width, height)

    if add_slot:
        # Cria o slot como uma caixa
        slot_box = cq.Workplane("XY").box(slot_l, slot_w, slot_h)

        # Translada o slot para a posição correta, considerando que a caixa principal
        # e o slot são criados com seus centros na origem por padrão.
        # As coordenadas do slot_x, slot_y, slot_z são relativas ao canto da caixa no UI,
        # então precisamos ajustar para o centro da caixa e do slot.
        # Ex: Se slot_x é 0, o canto está no início, o centro do slot_l fica em slot_l/2.
        # A caixa principal está centralizada, então seu canto está em -length/2.
        # Posição central do slot = (slot_x + slot_l/2) - length/2
        translated_slot = slot_box.translate((slot_x - length / 2 + slot_l / 2,
                                                slot_y - width / 2 + slot_w / 2,
                                                slot_z - height / 2 + slot_h / 2))

        # Corta o slot da caixa principal
        result = box.cut(translated_slot)
    else:
        result = box

    return result

def cadquery_to_plotly_mesh(cq_object):
    """
    Converte um objeto CadQuery em dados de malha (vertices, faces) para Plotly.
    """
    # Usa o método to_mesh() do CadQuery para obter vertices e faces.
    # Esta função pode exigir a instalação de 'ocp_tessellate' para melhor tesselação,
    # mas a instalação padrão do cadquery geralmente lida com isso.
    mesh = cq_object.val().to_mesh()

    # mesh.vertices é um array numpy de shape (N, 3) para as coordenadas (x, y, z)
    # mesh.faces é um array numpy de shape (M, 3) para os índices dos vértices de cada triângulo (i, j, k)
    x, y, z = mesh.vertices.T
    i, j, k = mesh.faces.T

    return x, y, z, i, j, k

# --- Interface do Usuário com Streamlit ---
st.set_page_config(layout="wide") # Opcional: para usar a largura total da tela
st.title("📦 Gerador de Caixa com Slot Paramétrico (Visualização 3D)")
st.write("Ajuste os parâmetros da caixa e do slot para visualizar o modelo 3D interativo.")

# Seção de Parâmetros na barra lateral
st.sidebar.header("Parâmetros da Caixa Principal")
length = st.sidebar.slider("Comprimento da Caixa (mm)", 10, 200, 100, key="len_box")
width = st.sidebar.slider("Largura da Caixa (mm)", 10, 200, 50, key="wid_box")
height = st.sidebar.slider("Altura da Caixa (mm)", 10, 200, 25, key="hei_box")

# Seção de Parâmetros do Slot na barra lateral
st.sidebar.header("Parâmetros do Slot (Corte)")
add_slot = st.sidebar.checkbox("Adicionar Slot?", value=True)

# Exibe os controles do slot apenas se o checkbox estiver marcado
if add_slot:
    st.sidebar.subheader("Posição do Slot")
    slot_x_pos = st.sidebar.slider("Posição X do Slot (mm)", 0.0, float(length), float(length)/4, step=1.0, key="sx_pos")
    slot_y_pos = st.sidebar.slider("Posição Y do Slot (mm)", 0.0, float(width), float(width)/4, step=1.0, key="sy_pos")
    slot_z_pos = st.sidebar.slider("Posição Z do Slot (mm)", 0.0, float(height), 0.0, step=1.0, key="sz_pos")

    st.sidebar.subheader("Dimensões do Slot")
    slot_length = st.sidebar.slider("Comprimento do Slot (mm)", 1.0, float(length), float(length)/2, step=1.0, key="sl_len")
    slot_width = st.sidebar.slider("Largura do Slot (mm)", 1.0, float(width), float(width)/2, step=1.0, key="sl_wid")
    slot_height = st.sidebar.slider("Altura do Slot (mm)", 1.0, float(height), float(height)/2, step=1.0, key="sl_hei")
else:
    # Define valores padrão ou mínimos se o slot não for adicionado
    # Esses valores não serão usados no cálculo do modelo se add_slot for False
    slot_x_pos, slot_y_pos, slot_z_pos = 0, 0, 0
    slot_length, slot_width, slot_height = 1, 1, 1

# --- Geração e Visualização do Modelo 3D ---

# Cria o modelo 3D com base nos parâmetros do UI
try:
    model_cq = create_box_with_slot(length, width, height, add_slot,
                                    slot_x_pos, slot_y_pos, slot_z_pos,
                                    slot_length, slot_width, slot_height)

    # Converte o modelo CadQuery para o formato do Plotly
    x, y, z, i, j, k = cadquery_to_plotly_mesh(model_cq)

    # Cria a figura 3D com Plotly
    fig = go.Figure(data=[go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k,
                                    color='lightblue', opacity=0.75)])

    # Configura o layout da cena 3D para manter a proporção correta
    fig.update_layout(
        scene_aspectmode='data', # Garante que as proporções X, Y, Z sejam respeitadas
        scene=dict(
            xaxis_title='Comprimento (mm)',
            yaxis_title='Largura (mm)',
            zaxis_title='Altura (mm)',
            # Desativa a grade e eixos para uma visualização mais limpa, opcional
            xaxis=dict(showgrid=False, showbackground=False, zeroline=False),
            yaxis=dict(showgrid=False, showbackground=False, zeroline=False),
            zaxis=dict(showgrid=False, showbackground=False, zeroline=False),
        ),
        margin=dict(l=0, r=0, b=0, t=0), # Remove margens para maximizar o espaço
        height=600 # Altura fixa do gráfico
    )

    # Exibe o gráfico Plotly no Streamlit
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Configurações Atuais:")
    st.write(f"**Caixa Principal:** {length} x {width} x {height} mm")
    if add_slot:
        st.write(f"**Slot:** Posição ({slot_x_pos}, {slot_y_pos}, {slot_z_pos}) mm, Dimensões ({slot_length} x {slot_width} x {slot_height}) mm")
    else:
        st.write("**Slot:** Não adicionado.")

except Exception as e:
    st.error(f"Ocorreu um erro ao gerar o modelo 3D. Verifique os parâmetros. Erro: {e}")
    st.info("Pode ser que a combinação de parâmetros esteja criando um modelo inválido ou muito complexo para ser renderizado.")
