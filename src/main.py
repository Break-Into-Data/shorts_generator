
from src.script import Script, ScriptCodeHighlight
from src.audio_processing import generate_audio
from src.video_processing import generate_video


def main():
    code = """
import tensorflow as tf

# Simulated data: features and labels
features = tf.random.normal([100, 10])
labels = tf.concat([tf.zeros(80, dtype=tf.int32), tf.ones(20, dtype=tf.int32)], axis=0)

# Model setup
model = tf.keras.Sequential([
    tf.keras.layers.Dense(10, activation='relu', input_shape=(10,)),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Class weights to handle imbalance
class_weights = {0: 1, 1: 4}

# Compile the model
model.compile(optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy'])

# Fit the model
model.fit(features, labels, epochs=10, class_weight=class_weights)
"""

    script = Script(
        code=code,
        intro_text="Hello",
        highlights=[
            ScriptCodeHighlight(
                text="""This line imports everything""",
                line_number=0,
                line_count=1,
            ),
            ScriptCodeHighlight(
                text="""Here we create some simulated data""",
                line_number=4,
                line_count=7,
            ),
            ScriptCodeHighlight(
                text="""We use a simple model with two layers""",
                line_number=13,
                line_count=12,
            ),
            ScriptCodeHighlight(
                text="""Class imbalance is defined here""",
                line_number=27,
                line_count=1,
            ),
        ],
        cta_text="",
    )

                
    for idx, code_block in enumerate(script.highlights):
        voice_file = f"./assets/audio/voice_{idx}.mp3"
        voice_clip = generate_audio(code_block.text, voice_file)
        code_block.voice_clip = voice_clip


    video_path = generate_video(script)


if __name__ == "__main__":
    main()
