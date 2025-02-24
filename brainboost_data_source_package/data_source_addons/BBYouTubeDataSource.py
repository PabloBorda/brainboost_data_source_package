import glob
import logging
import os
import re
import sys
import tempfile
import time
from datetime import datetime

from pydub import AudioSegment  # Used to convert audio format
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer
from transformers import pipeline
from yt_dlp import YoutubeDL
import whisper

from brainboost_configuration_package.BBConfig import BBConfig
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_data_source_package.data_source_abstract.BBDataSource import BBDataSource


# Configuración de logging a nivel de módulo
logging.basicConfig(
    filename='single_video_summary_spanish.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class BBYouTubeDataSource(BBDataSource):
    # Definir constantes a nivel de clase
    WHISPER_MODEL_SIZE = 'base'  # Puedes ajustar según las capacidades de tu sistema
    SPANISH_SUMMARIZATION_MODEL = "mrm8488/bert2bert_shared-spanish-finetuned-summarization"
    ENGLISH_SUMMARIZATION_MODEL = "facebook/bart-large-cnn"

    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources,
                         subscribers=subscribers, params=params)
        self.params = params

    def fetch(self, youtube_link, language='es'):
        """
        Método principal para descargar, transcribir y resumir un video de YouTube.

        :param youtube_link: URL del video de YouTube.
        :param language: Idioma del video ('es' para español, 'en' para inglés).
        """
        if not youtube_link:
            logging.error("No se proporcionó una URL de YouTube.")
            raise ValueError("Se requiere una URL de YouTube para procesar.")

        video_url = youtube_link
        logging.info(f"Iniciado procesamiento de la URL del video: '{video_url}'.")

        # Obtener información del video (por ejemplo, título) usando yt-dlp
        try:
            with YoutubeDL({'quiet': True, 'skip_download': True, 'forcejson': True}) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                video_title = info_dict.get('title', 'Título_Desconocido')
        except Exception as e:
            logging.error(f"Error al obtener la información del video para {video_url}: {e}")
            raise RuntimeError(f"Error al obtener la información del video: {e}")

        print(f"Procesando Video: {video_title}")
        print(f"URL: {video_url}")

        # Crear un título sanitizado para usar en nombres de archivos
        sanitized_title = self.sanitize_filename(video_title)
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        summary_filename = f"{sanitized_title}-{timestamp}.txt"
        summary_filepath = os.path.join(os.getcwd(), summary_filename)

        # Cargar el modelo Whisper para la transcripción
        print(f"Cargando modelo Whisper ({self.WHISPER_MODEL_SIZE})...")
        logging.info(f"Cargando modelo Whisper '{self.WHISPER_MODEL_SIZE}'.")
        try:
            whisper_model = whisper.load_model(self.WHISPER_MODEL_SIZE)
        except Exception as e:
            logging.error(f"Error al cargar el modelo Whisper: {e}")
            raise RuntimeError(f"Error al cargar el modelo Whisper: {e}")

        # Crear una carpeta temporal para almacenar el audio descargado
        with tempfile.TemporaryDirectory() as tmpdirname:
            print("Descargando audio...")
            audio_file = self.download_audio(video_url, tmpdirname)
            if audio_file:
                print(f"Audio descargado en {audio_file}")
                logging.info(f"Audio descargado exitosamente en {audio_file}.")

                # Convertir MP3 a WAV mono para mejorar la precisión de la transcripción
                wav_path = os.path.join(tmpdirname, "audio_mono.wav")
                converted_audio = self.convert_to_mono_wav(audio_file, wav_path)
                if not converted_audio:
                    logging.error("Conversión de audio fallida.")
                    raise RuntimeError("Error al convertir el audio a WAV.")

                # Verificar la duración del archivo de audio
                try:
                    audio = AudioSegment.from_wav(converted_audio)
                    duration = audio.duration_seconds
                    print(f"Duración del audio (s): {duration:.1f}")
                    logging.info(f"Duración del audio: {duration:.1f} segundos")
                except Exception as e:
                    logging.error(f"No se pudo determinar la duración del audio: {e}")

                # Transcribir el audio descargado usando Whisper
                transcript, lang = self.transcribe_audio(converted_audio, whisper_model)
                if transcript.strip():
                    print("Transcripción completada.")
                    logging.info("Transcripción completada exitosamente.")

                    # Determinar el modelo de resumen según el idioma
                    summarizer, summary_model = self.get_summarizer(language)

                    # Generar el resumen del texto transcrito
                    print("Generando resumen...")
                    logging.info("Iniciando resumen de la transcripción.")
                    summary = self.summarize_text(transcript, summarizer)

                    if not summary.strip():
                        logging.warning("El resumen está vacío después de la generación.")
                        summary = "No se generó ningún resumen."

                    print("\n--- Resumen ---\n")
                    print(summary)

                    # Preparar el contenido completo para guardar (incluyendo transcripción y resumen)
                    file_content = (
                        f"URL del Video: {video_url}\n"
                        f"Título del Video: {video_title}\n"
                        f"Idioma Detectado: {lang}\n"
                        f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        "=== Transcripción ===\n\n"
                        f"{transcript}\n\n"
                        "=== Resumen ===\n\n"
                        f"{summary}"
                    )

                    # Guardar la transcripción y el resumen en un archivo de texto en el directorio actual
                    try:
                        with open(summary_filepath, 'w', encoding='utf-8') as f:
                            f.write(file_content)
                        print(f"\nResumen guardado en '{summary_filename}'.")
                        logging.info(f"Resumen guardado en '{summary_filepath}'.")
                    except Exception as e:
                        logging.error(f"Error al guardar el archivo '{summary_filepath}': {e}")
                        raise RuntimeError(f"Error al guardar el resumen: {e}")
                else:
                    logging.warning("La transcripción estaba vacía después del procesamiento del audio.")
                    raise RuntimeError("No se generó ninguna transcripción.")
            else:
                logging.error("La descarga del audio falló para la URL proporcionada.")
                raise RuntimeError("Error al descargar el audio.")

    # ------------------------ Métodos Auxiliares ----------------------------- #

    def sanitize_filename(self, name):
        """
        Sanitiza el título del video (o cualquier cadena) para crear un nombre de archivo válido.
        Elimina o reemplaza caracteres que no son válidos en los nombres de archivos.
        """
        name = name.replace(' ', '_')  # Reemplaza espacios por guiones bajos
        name = re.sub(r'[^\w\-]', '', name)  # Elimina caracteres no alfanuméricos/guiones bajos/guiones
        return name

    def download_audio(self, video_url, download_path, max_retries=3):
        """
        Descarga el stream de audio de un video de YouTube usando yt-dlp y lo convierte a mp3.
        Implementa un mecanismo de reintentos en caso de fallos de red.
        Después de la descarga, busca el archivo mp3 en el directorio de descarga.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'retries': max_retries,
        }

        attempt = 0
        while attempt < max_retries:
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=True)
                    logging.info(f"Descargado info del video para {video_url}: {info_dict.get('title', 'Título Desconocido')}")
                # Después de la descarga, encuentra el archivo mp3 en la carpeta de descarga
                mp3_files = glob.glob(os.path.join(download_path, "*.mp3"))
                if mp3_files:
                    audio_file = mp3_files[0]
                    logging.info(f"Archivo de audio encontrado: {audio_file}")
                    return audio_file
                else:
                    logging.error("No se encontró ningún archivo MP3 después de la descarga.")
                    return None
            except Exception as e:
                attempt += 1
                logging.error(f"Intento {attempt} - Error al descargar {video_url}: {e}")
                if attempt < max_retries:
                    time.sleep(3)  # Espera un poco antes de reintentar
                else:
                    return None

    def convert_to_mono_wav(self, mp3_path, output_path):
        """
        Convierte un archivo MP3 a un archivo WAV mono.
        """
        try:
            audio = AudioSegment.from_mp3(mp3_path)
            audio = audio.set_channels(1)  # Convierte a mono
            audio.export(output_path, format="wav")
            logging.info(f"Convertido {mp3_path} a WAV mono en {output_path}.")
            return output_path
        except Exception as e:
            logging.error(f"Error al convertir {mp3_path} a WAV: {e}")
            return None

    def transcribe_audio(self, audio_path, model):
        """
        Transcribe el audio a texto usando Whisper.
        Devuelve tanto la transcripción como el código del idioma detectado.
        """
        try:
            # Especifica el idioma para mejorar la precisión
            result = model.transcribe(audio_path, language="es")
            transcript = result.get('text', "")
            language = result.get('language', "es")
            logging.info(f"Transcrito el archivo de audio {audio_path} con idioma detectado: {language}.")
            return transcript, language
        except Exception as e:
            logging.error(f"Error al transcribir {audio_path}: {e}")
            return "", "es"

    def summarize_text(self, text, summarizer):
        """
        Genera un resumen del texto proporcionado usando un pipeline de resumen de Hugging Face o sumy.
        """
        try:
            # Dependiendo del summarizer, la implementación puede variar
            if isinstance(summarizer, pipeline):
                # Usando Hugging Face
                max_chunk = 1024  # Ajusta según el tamaño máximo de tokens de entrada del modelo
                text_chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
                summaries = []
                for chunk in text_chunks:
                    summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0]['summary_text']
                    summaries.append(summary)
                full_summary = ' '.join(summaries)
                logging.info("Resumen generado utilizando Hugging Face.")
                return full_summary
            elif isinstance(summarizer, LexRankSummarizer):
                # Usando sumy
                parser = PlaintextParser.from_string(text, Tokenizer("spanish"))
                summary = summarizer(parser.document, sentences_count=5)
                summary_text = ' '.join([str(sentence) for sentence in summary])
                logging.info("Resumen generado utilizando sumy.")
                return summary_text
            else:
                logging.error("Tipo de summarizer no reconocido.")
                return ""
        except Exception as e:
            logging.error(f"Error al resumir el texto: {e}")
            return ""

    def get_summarizer(self, language):
        """
        Retorna el summarizer adecuado basado en el idioma.

        :param language: Código del idioma ('es' para español, 'en' para inglés).
        :return: Tuple (summarizer, modelo)
        """
        if language == "es":
            # Usar sumy con LexRank para español
            summarizer = LexRankSummarizer()
            summary_model = "sumy LexRank"
        else:
            # Usar Hugging Face para inglés
            summarizer = pipeline("summarization", model=self.ENGLISH_SUMMARIZATION_MODEL)
            summary_model = "Hugging Face BART"
        logging.info(f"Usando modelo de resumen: {summary_model}")
        return summarizer, summary_model

    def get_icon(self):
        """Return the SVG code for the YouTube icon."""
        return """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48px" height="48px">
            <path fill="#FF0000" d="M45,12c0-2.761-2.239-5-5-5H8C5.239,7,3,9.239,3,12v24c0,2.761,2.239,5,5,5h32c2.761,0,5-2.239,5-5V12z"></path>
            <path fill="#FFFFFF" d="M20 34V14l16 10-16 10z"></path>
        </svg>
        """

    def get_connection_data(self):
        """
        Return the connection type and required fields for YouTube.
        """
        return {
            "connection_type": "YouTube",
            "fields": ["youtube_link", "language"]
        }

