import streamlit as st
import cadquery as cq
import os
# Importa o novo componente
from streamlit_3d_model import st_3d_model

# --- 1. Função de Modelagem 3D com CadQuery ---
def create_box_with_slot(length, width, height,
                        add_slot,
                        slot_x_pos, slot_y_pos, slot_z_pos,
                        slot_length, slot_width, slot_height):
    """
    Cria uma caixa com um slot opcional usando CadQuery.
    A caixa principal terá seu canto inferior-frontal-esquerdo em (0,0,0)
    para facilitar o posicionamento do slot a partir do canto.
    """
    # Cria a caixa principal.
    # 'centered=(False, False, False)' faz com que o canto inferior-frontal-esquerdo da caixa
    # esteja na origem (0,0,0), similar ao comportamento padrão do cube() no OpenSCAD.
    box = cq.Workplane("XY").box(length, width, height, centered=(False, False, False))
    
    result_shape = box # Começamos com a forma da caixa completa

    if add_slot:
        # Cria o volume que será o slot.
        # Por padrão, cq.Workplane(...).box() cria uma caixa centrada em seu próprio ponto de origem.
        slot_cutout = (
            cq.Workplane("XY")
            .box(slot_length, slot_width, slot_height)
            # Precisamos mover o slot para a posição desejada.
            # 'slot_x_pos', 'slot_y_pos', 'slot_z_pos' representam o canto inferior-frontal-esquerdo do slot.
            # Para centralizar o slot (que é centrado por padrão) nesse canto, adicionamos metade das dimensões do slot.
            .translate((slot_x_pos + slot_length/2,
                        slot_y_pos + slot_width/2,
                        slot_z_pos + slot_height/2))
        )
        # Subtrai o volume do slot da caixa principal
        result_shape = result_shape.cut(slot_cutout)
        
    return result_shape

# --- 2. Interface do Usuário com Streamlit ---
st.title("📦 Gerador de Caixa com Slot Paramétrico")
st.write("Ajuste os parâmetros da caixa e do slot para gerar e visualizar seu modelo 3D.")

# Seção de Parâmetros da Caixa Principal na barra lateral
st.sidebar.header("Parâmetros da Caixa Principal")
length = st.sidebar.slider("Comprimento da Caixa (mm)", 10, 200, 100)
width = st.sidebar.slider("Largura da Caixa (mm)", 10, 200, 50)
height = st.sidebar.slider("Altura da Caixa (mm)", 10, 200, 25)

# Seção de Parâmetros do Slot na barra lateral
st.sidebar.header("Parâmetros do Slot (Corte)")
add_slot = st.sidebar.checkbox("Adicionar Slot?", value=True) # Checkbox para ativar/desativar o slot

# Exibe os controles do slot apenas se o checkbox estiver marcado
if add_slot:
    # Posições do canto inferior-frontal-esquerdo do slot
    slot_x_pos = st.sidebar.number_input("Posição X do Slot (mm)", min_value=0.0, max_value=float(length), value=float(length)/4, step=1.0)
    slot_y_pos = st.sidebar.number_input("Posição Y do Slot (mm)", min_value=0.0, max_value=float(width), value=float(width)/4, step=1.0)
    slot_z_pos = st.sidebar.number_input("Posição Z do Slot (mm)", min_value=0.0, max_value=float(height), value=0.0, step=1.0) # Z=0 para cortar da base

    # Dimensões do slot
    slot_length = st.sidebar.number_input("Comprimento do Slot (mm)", min_value=1.0, max_value=float(length), value=float(length)/2, step=1.0)
    slot_width = st.sidebar.number_input("Largura do Slot (mm)", min_value=1.0, max_value=float(width), value=float(width)/2, step=1.0)
    slot_height = st.sidebar.number_input("Altura do Slot (mm)", min_value=1.0, max_value=float(height), value=float(height)/2, step=1.0)
else:
    # Define valores mínimos para evitar erros se o slot não estiver habilitado,
    # embora esses valores não serão usados no corte.
    slot_x_pos, slot_y_pos, slot_z_pos = 0, 0, 0
    slot_length, slot_width, slot_height = 1, 1, 1 

# --- 3. Geração e Visualização do Modelo ---
# Botão para gerar e visualizar o modelo
if st.button("Gerar e Visualizar Modelo"):
    st.subheader("Pré-visualização 3D")

    # Chama a função CadQuery para gerar o modelo com os parâmetros da UI
    my_model = create_box_with_slot(length, width, height,
                                    add_slot,
                                    slot_x_pos, slot_y_pos, slot_z_pos,
                                    slot_length, slot_width, slot_height)

    # Define um caminho temporário para o arquivo STL
    stl_file_path = "temp_model.stl"

    try:
        # Exporta o modelo CadQuery para um arquivo STL
        cq.exporters.export(my_model, stl_file_path)

        # Exibe o modelo 3D usando o NOVO componente st_3d_model
        # Ele precisa de uma URL ou caminho para o arquivo.
        # Streamlit precisa de um caminho acessível via URL, então vamos usar o arquivo local.
        # Nota: 'background_color' deve ser uma tupla de RGB, ex: (255, 255, 255) para branco
        st_3d_model(stl_file_path, key="model_viewer",
                    height=400,
                    camera_position=[length, width * 2, height], # Ajuste a posição da câmera para ver a caixa
                    background_color=(0, 0, 0), # Fundo preto
                    object_color="#CCCCCC", # Cor do objeto (cinza claro)
                    rotation_x=0, # Rotação inicial
                    rotation_y=0,
                    rotation_z=0,
                    center_object=True) # Tenta centralizar o objeto automaticamente

        # --- 4. Funcionalidade de Download ---
        # Cria um botão para o usuário baixar o arquivo STL gerado
        with open(stl_file_path, "rb") as file:
            btn = st.download_button(
                label="Baixar STL",
                data=file,
                file_name=f"modelo_com_slot_{length}x{width}x{height}.stl",
                mime="application/octet-stream"
            )
        st.success("Modelo gerado com sucesso! Você pode interagir com ele e baixá-lo.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar ou visualizar o modelo: {e}")
        st.code(str(e)) # Exibe o erro completo para depuração
    finally:
        # Garante que o arquivo temporário seja removido após o uso, mesmo se ocorrer um erro
        if os.path.exists(stl_file_path):
            os.remove(stl_file_path)

st.info("Altere os parâmetros na barra lateral e clique em 'Gerar e Visualizar Modelo' para ver o modelo atualizado.")