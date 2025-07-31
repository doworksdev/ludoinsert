import streamlit as st

# --- Interface do Usuário com Streamlit ---
st.title("📦 Gerador de Caixa com Slot Paramétrico (Versão de Teste)")
st.write("Ajuste os parâmetros da caixa e do slot. Esta versão é para verificar a implantação básica do Streamlit.")

# Seção de Parâmetros da Caixa Principal na barra lateral
st.sidebar.header("Parâmetros da Caixa Principal")
length = st.sidebar.slider("Comprimento da Caixa (mm)", 10, 200, 100)
width = st.sidebar.slider("Largura da Caixa (mm)", 10, 200, 50)
height = st.sidebar.slider("Altura da Caixa (mm)", 10, 200, 25)

# Seção de Parâmetros do Slot na barra lateral
st.sidebar.header("Parâmetros do Slot (Corte)")
add_slot = st.sidebar.checkbox("Adicionar Slot?", value=True)

# Exibe os controles do slot apenas se o checkbox estiver marcado
if add_slot:
    slot_x_pos = st.sidebar.number_input("Posição X do Slot (mm)", min_value=0.0, max_value=float(length), value=float(length)/4, step=1.0)
    slot_y_pos = st.sidebar.number_input("Posição Y do Slot (mm)", min_value=0.0, max_value=float(width), value=float(width)/4, step=1.0)
    slot_z_pos = st.sidebar.number_input("Posição Z do Slot (mm)", min_value=0.0, max_value=float(height), value=0.0, step=1.0)
    slot_length = st.sidebar.number_input("Comprimento do Slot (mm)", min_value=1.0, max_value=float(length), value=float(length)/2, step=1.0)
    slot_width = st.sidebar.number_input("Largura do Slot (mm)", min_value=1.0, max_value=float(width), value=float(width)/2, step=1.0)
    slot_height = st.sidebar.number_input("Altura do Slot (mm)", min_value=1.0, max_value=float(height), value=float(height)/2, step=1.0)
else:
    # Define valores mínimos para evitar erros, embora não serão usados para cálculo nesta versão
    slot_x_pos, slot_y_pos, slot_z_pos = 0, 0, 0
    slot_length, slot_width, slot_height = 1, 1, 1 

# Botão para simular as configurações
if st.button("Simular Configurações"):
    st.subheader("Configurações Selecionadas:")
    st.write(f"**Caixa Principal:**")
    st.write(f"  - Comprimento: {length} mm")
    st.write(f"  - Largura: {width} mm")
    st.write(f"  - Altura: {height} mm")

    if add_slot:
        st.write(f"**Detalhes do Slot:**")
        st.write(f"  - Posição (X, Y, Z): ({slot_x_pos}, {slot_y_pos}, {slot_z_pos}) mm")
        st.write(f"  - Dimensões (C, L, A): ({slot_length}, {slot_width}, {slot_height}) mm")
    else:
        st.write(f"**Slot:** Não adicionado.")

st.info("Esta é uma versão de teste para verificar a implantação do Streamlit. Não há visualização 3D nem geração de arquivo STL nesta versão.")
