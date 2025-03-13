import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import librosa
import librosa.display
import argparse
from collections import Counter
import matplotlib.ticker as ticker

class DatasetAnalysis:
    def __init__(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.dataset_name = os.path.basename(os.path.dirname(json_file))
        self.categories = {cat["id"]: cat["Name"] for cat in self.data["categories"]}
        self.sounds = self.data["sounds"]
        self.annotations = self.data["annotations"]
        self.sounds_dir = os.path.join(os.path.dirname(json_file), "soundscape_data")
        
        self.visualization_dir = os.path.join("visualizations", self.dataset_name)
        os.makedirs(self.visualization_dir, exist_ok=True)
    
    def get_category_distribution(self):
        """Displays the class distribution in the dataset and saves it as an image."""
        category_counts = Counter([anno['category'] for anno in self.annotations])
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        plt.figure(figsize=(12, 6))
        sns.barplot(x=[cat[0] for cat in sorted_categories], y=[cat[1] for cat in sorted_categories])
        plt.xticks(rotation=90, ha='right', fontsize=8)
        plt.xlabel("Species")
        plt.ylabel("Frequency")
        plt.title("Species distribution in the dataset")
        
        output_path = os.path.join(self.visualization_dir, "category_distribution.png")
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
    
    def plot_duration_distribution(self):
        """Displays the distribution of audio durations and saves it as an image."""
        durations = [sound['duration'] for sound in self.sounds]
        
        plt.figure(figsize=(8, 5))
        sns.histplot(durations, bins=20, kde=True)
        plt.xlabel("Duration (s)")
        plt.ylabel("Frequency")
        plt.title("Audio duration distribution")
        
        output_path = os.path.join(self.visualization_dir, "duration_distribution.png")
        plt.savefig(output_path)
        plt.close()

    def plot_annotations_per_audio(self):
        """Displays the number of annotations per audio file and saves it as an image."""
        annotation_counts = Counter([anno['sound_id'] for anno in self.annotations])
        
        plt.figure(figsize=(12, 6))
        sns.barplot(x=list(annotation_counts.keys()), y=list(annotation_counts.values()))
        plt.xticks(rotation=90, ha='right', fontsize=8)
        plt.xlabel("Audio ID")
        plt.ylabel("Number of Annotations")
        plt.title("Annotations per Audio File")
        
        output_path = os.path.join(self.visualization_dir, "annotations_per_audio.png")
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
    
    def plot_spectrogram_with_annotations(self, sound_id):
        """Generates the spectrogram of an audio file and saves it with its annotations if available."""
        sound = next((s for s in self.sounds if s['id'] == sound_id), None)
        if sound is None:
            print("Audio ID not found.")
            return
        
        audio_path = os.path.join(self.sounds_dir, sound['file_name'])
        y, sr = librosa.load(audio_path, sr=sound['sample_rate'])
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        
        plt.figure(figsize=(10, 5))
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title(f"Spectrogram of {sound['file_name']}")
        
        for anno in self.annotations:
            if anno['sound_id'] == sound_id:
                plt.hlines(y=[anno['f_min'], anno['f_max']], xmin=anno['t_min'], xmax=anno['t_max'], color='red', linewidth=2)
                plt.text(anno['t_min'], anno['f_max'], anno['category'], color='red', fontsize=10, verticalalignment='bottom')
        
        output_path = os.path.join(self.visualization_dir, f"spectrogram_sound_id_{sound_id}.png")
        plt.savefig(output_path)
        plt.close()

    def plot_spectrogram_with_relevant_annotations(self, sound_id):
        """Generates a spectrogram for the first annotations and saves it."""
        sound = next((s for s in self.sounds if s['id'] == sound_id), None)
        if sound is None:
            print(f"Audio ID {sound_id} not found.")
            return

        # Get up to 10 annotations for this sound_id
        relevant_annotations = [anno for anno in self.annotations if anno['sound_id'] == sound_id]
        if not relevant_annotations:
            print(f"No annotations found for sound_id {sound_id}")
            return

        relevant_annotations = relevant_annotations[:5]  # Limit to first 5 annotations

        audio_path = os.path.join(self.sounds_dir, sound['file_name'])
        y, sr = librosa.load(audio_path, sr=sound['sample_rate'])

        t_min_global = min(anno['t_min'] for anno in relevant_annotations)
        t_max_global = max(anno['t_max'] for anno in relevant_annotations)
        # Añadir un margen para mejor visualización (5 segundos antes y después)
        margin = 5
        t_min_display = max(0, t_min_global - margin)
        t_max_display = min(len(y) / sr, t_max_global + margin)
        
        # Extraer el segmento relevante del audio
        segment_start_sample = int(t_min_display * sr)
        segment_end_sample = int(t_max_display * sr)
        y_segment = y[segment_start_sample:segment_end_sample]
        
        # Calcular el espectrograma
        n_fft = 2048
        hop_length = 512
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y_segment, n_fft=n_fft, hop_length=hop_length)), ref=np.max)
        
        # Crear la figura
        plt.figure(figsize=(15, 8))
        
        # Mostrar el espectrograma
        img = librosa.display.specshow(
            D, 
            sr=sr, 
            hop_length=hop_length,
            x_axis='time', 
            y_axis='hz', 
            cmap='magma',
            x_coords=np.linspace(t_min_display, t_max_display, D.shape[1])
        )
        
        # Ajustar los límites del eje Y (frecuencia)
        f_min_global = min(anno['f_min'] for anno in relevant_annotations)
        f_max_global = max(anno['f_max'] for anno in relevant_annotations)
        
        # Añadir margen en las frecuencias
        f_margin_percentage = 0.1
        f_margin_min = f_min_global * f_margin_percentage
        f_margin_max = f_max_global * f_margin_percentage
        
        plt.ylim([max(20, f_min_global - f_margin_min), f_max_global + f_margin_max])

         # Personalizar el formato del eje X para mostrar minutos:segundos
        def format_time(x, pos=None):
            minutes = int(x // 60)
            seconds = int(x % 60)
            return f"{minutes}:{seconds:02d}"
        
        ax = plt.gca()
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_time))
        
        # Dibujar las cajas de anotaciones
        for i, anno in enumerate(relevant_annotations):
            # Usamos directamente los tiempos absolutos
            t_min = anno['t_min']
            t_max = anno['t_max']
            
            # Crear el rectángulo (x, y, ancho, alto)
            width = t_max - t_min
            height = anno['f_max'] - anno['f_min']
            
            # Dibujar el rectángulo
            rect = plt.Rectangle(
                (t_min, anno['f_min']), 
                width, 
                height, 
                linewidth=2, 
                edgecolor='red', 
                facecolor='none',
                alpha=0.8
            )
            plt.gca().add_patch(rect)
            
            # Añadir etiqueta con el ID y categoría
            plt.text(
                t_min + width/2, 
                anno['f_max'] + height*0.1,
                f"{anno['category']} (ID: {anno['anno_id']})",
                color='white', 
                fontsize=9,
                ha='center',
                va='bottom',
                bbox=dict(facecolor='black', alpha=0.7)
            )
            
        # Configurar ejes y títulos
        plt.colorbar(img, format='%+2.0f dB')
        plt.title(f"Spectrogram of {sound['file_name']} (5 Annotations examples)", fontsize=14)
        plt.xlabel('Time (s)', fontsize=12)
        plt.ylabel('Frecuency (Hz)', fontsize=12)
        
        # Añadir anotación de tiempo absoluto
        plt.figtext(
            0.01, 0.01, 
            f"Absolut time: {t_min_display:.2f}s - {t_max_display:.2f}s",
            fontsize=10
        )
        
        # Guardar la figura
        output_path = os.path.join(self.visualization_dir, f"spectrogram_sound_id_{sound_id}.png")
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.tight_layout()
        plt.show()
        plt.close()
    
    def show_summary(self):
        """Displays a general summary of the dataset."""
        total_duration = sum(sound['duration'] for sound in self.sounds)
        total_hours = total_duration / 3600
        
        print(f"Dataset: {self.dataset_name}")
        print(f"Total species: {len(self.categories)}")
        print(f"Total audio recordings: {len(self.sounds)}")
        print(f"Total annotations: {len(self.annotations)}")
        print(f"Total duration: {total_hours:.2f} hours")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze and visualize bioacoustic datasets.")
    parser.add_argument("--json", type=str, required=True, help="Path to the JSON dataset file. Make sure json file is at the same level as the audio files")
    parser.add_argument("--sound_id", type=int, default=0, help="ID of the sound to visualize.")
    args = parser.parse_args()

    json_file = args.json 
    dataset = DatasetAnalysis(json_file)
    dataset.show_summary()
    dataset.get_category_distribution()
    dataset.plot_duration_distribution()
    dataset.plot_annotations_per_audio()
    dataset.plot_spectrogram_with_relevant_annotations(sound_id=args.sound_id)
