import streamlit as st
import os
import tempfile
from datetime import datetime
import time

from audio_processor import extract_audio_from_video, get_audio_duration
from transcription_ai import transcribe_audio, get_transcription_status
from minutes_generator import generate_structured_minutes

def main():
    st.set_page_config(
        page_title="Cyber - Ata de reunião", 
        page_icon="🔬", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    with st.sidebar:
        st.title("Laboratório Cyber")
        st.markdown("---")
        
        st.subheader("Status do Sistema")
        status = get_transcription_status()
        
        if status["model_loaded"]:
            st.success("Modelo Whisper Carregado")
            st.info(f"Hardware: {status['device'].upper()}")
        else:
            st.warning("Modelo não carregado")
        
        st.markdown("---")
        st.markdown("### Sobre")
        st.markdown("""
        **Transcrição Real com Whisper:**
        """)
        
        st.markdown("---")
        st.markdown("**Desenvolvido para Laboratório Cyber**")
    
    st.title("Cyber - Ata de Reunião com IA")
    st.markdown("Sistema de transcrição automática com IA para reuniões técnicas")
    
    uploaded_file = st.file_uploader(
        "**Faça upload do vídeo ou áudio da reunião**", 
        type=['mp4', 'avi', 'mov', 'wav', 'mp3', 'm4a', 'ogg'],
        help="Formatos suportados: MP4, AVI, MOV, WAV, MP3, M4A, OGG"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Arquivo Carregado")
            if uploaded_file.type.startswith('video'):
                st.video(uploaded_file)
            else:
                st.audio(uploaded_file)
            
            file_info = f"""
            **Nome:** {uploaded_file.name}  
            **Tipo:** {uploaded_file.type}  
            **Tamanho:** {uploaded_file.size / 1024 / 1024:.2f} MB
            """
            st.info(file_info)
        
        with col2:
            st.subheader("Configurações")            
            st.warning("**Tempo estimado:** 1-5 minutos dependendo do tamanho do áudio")
            
            if st.button("**INICIAR TRANSCRIÇÃO REAL**", 
                        type="primary", 
                        use_container_width=True,
                        help="Clique para processar com IA real"):
                
                process_file(uploaded_file)

def process_file(uploaded_file):
    with st.spinner("Iniciando processamento com Whisper..."):
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=f'.{uploaded_file.name.split(".")[-1]}'
            ) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                media_path = tmp_file.name
            
            progress_container = st.container()
            
            with progress_container:
                st.write("**Etapa 1/3:** Extraindo áudio do vídeo...")
                if uploaded_file.type.startswith('video'):
                    audio_path = extract_audio_from_video(media_path)
                    duration = get_audio_duration(audio_path)
                    st.info(f"Duração do áudio: {duration:.1f} segundos")
                else:
                    audio_path = media_path
                    duration = get_audio_duration(audio_path)
                    st.info(f"Duração do áudio: {duration:.1f} segundos")
                
                progress_bar = st.progress(0)
                progress_bar.progress(33)
                
                st.write("**Etapa 2/3:** Transcrevendo com Whisper...")
                st.info("**Processando áudio...** Isso pode levar alguns minutos.")
                
                estimated_time = max(30, duration / 10)  
                st.warning(f"Tempo estimado: {estimated_time:.0f} segundos")
                
                start_time = time.time()
                transcription = transcribe_audio(audio_path)
                end_time = time.time()
                
                progress_bar.progress(66)
                
                processing_time = end_time - start_time
                st.success(f"Transcrição concluída em {processing_time:.1f} segundos")
                
                st.write("**Etapa 3/3:** Gerando ata estruturada...")
                minutes = generate_structured_minutes(transcription)
                progress_bar.progress(100)
                
                display_results(minutes, transcription, processing_time, duration)
            
            cleanup_files(media_path, audio_path, uploaded_file)
            
        except Exception as e:
            st.error(f"Erro no processamento: {str(e)}")
            st.info("**Dicas:** Verifique se o áudio está claro e com boa qualidade.")

def display_results(minutes, transcription, processing_time, duration):
    st.success("**Processamento concluído com sucesso!**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tempo de Processamento", f"{processing_time:.1f}s")
    with col2:
        st.metric("Duração do Áudio", f"{duration:.1f}s")
    with col3:
        st.metric("Texto Transcrito", f"{len(transcription)} chars")
    
    tab1, tab2 = st.tabs(["**ATA ESTRUTURADA**", "**TRANSCRIÇÃO COMPLETA**"])
    
    with tab1:
        st.markdown(minutes)
        st.download_button(
            label="**BAIXAR ATA EM MARKDOWN**",
            data=minutes,
            file_name=f"ata_cyberlab_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with tab2:
        st.text_area(
            "Texto transcrito:",
            transcription,
            height=400,
            label_visibility="collapsed"
        )
        
        st.download_button(
            label="**BAIXAR TRANSCRIÇÃO**",
            data=transcription,
            file_name=f"transcricao_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

def cleanup_files(media_path, audio_path, uploaded_file):
    try:
        if os.path.exists(media_path):
            os.unlink(media_path)
        if (uploaded_file.type.startswith('video') and 
            os.path.exists(audio_path) and 
            audio_path != media_path):
            os.unlink(audio_path)
    except Exception as e:
        print(f"Aviso na limpeza: {e}")

if __name__ == "__main__":
    main()