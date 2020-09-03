from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def make_model(input_shape, num_classes, chckpnt=False, load=False):
    
    inputs = keras.Input(shape=input_shape)
    # Image augmentation block
    x = data_augmentation(inputs)

    if load: model = keras.load_model(f'{name}.h5')(x)
    
    else:
        # Entry block
        x = layers.experimental.preprocessing.Rescaling(1./255)(x)
        x = layers.Conv2D(32, 3, strides=2, padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)

        x = layers.Conv2D(64, 3, padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)

        previous_block_activation = x  # Set aside residual
        
        for size in [128, 256, 512, 728]:

            x = layers.Activation('relu')(x)
            x = layers.SeparableConv2D(size, 3, padding='same')(x)
            x = layers.BatchNormalization()(x)

            x = layers.Activation('relu')(x)
            x = layers.SeparableConv2D(size, 3, padding='same')(x)
            x = layers.BatchNormalization()(x)

            x = layers.MaxPooling2D(3, strides=2, padding='same')(x)
            
            # Project residual
            residual = layers.Conv2D(
                size, 1, strides=2, padding='same')(previous_block_activation
                )
            x = layers.add([x, residual])  # Add back residual
            previous_block_activation = x  # Set aside next residual

        x = layers.SeparableConv2D(1024, 3, padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        
        x = layers.GlobalAveragePooling2D()(x)
        if num_classes == 2:
            activation = 'sigmoid'
            units = 1
        else:
            activation = 'softmax'
            units = num_classes
        
        x = layers.Dropout(0.5)(x)
        outputs = layers.Dense(units, activation=activation)(x)
        model = keras.Model(inputs, outputs)
        
    if chckpnt: 
        
        path = home / 'Checkpoints'
        checkpoints = list(path.glob(f'{name}_*'))
        checkpoint = checkpoints[-1]
        model.load_weights(checkpoint)
    
    return model

def cleanup(num_skipped=0):

    import PIL
    
    root = Path(path)
    
    for folder in root.iterdir():

        for fpath in folder.iterdir():
            
            try: 
                jfif = tf.compat.as_bytes('JFIF') in fpath.read_bytes()
                size = PIL.Image.open(fpath).size == (512, 512)
            except PIL.UnidentifiedImageError: jfif = size = False
            
            if not jfif or not size:
                fpath.unlink()
                num_skipped += 1
                                
    print(f'Deleted {num_skipped} images\n')

path = r'E:\Users\Emc11\Training'
home = Path(__file__).parent
name = home / 'Medium-01'
image_size = 180, 180
batch_size = 32
epochs = 4 

# cleanup()
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    path, validation_split=0.2, subset='training', seed=1337,
    image_size=image_size, batch_size=batch_size
    )
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    path, validation_split=0.2, subset='validation', seed=1337,
    image_size=image_size, batch_size=batch_size
    )

data_augmentation = keras.Sequential([
    layers.experimental.preprocessing.RandomFlip('vertical'),
    layers.experimental.preprocessing.RandomRotation(0.33),
    layers.experimental.preprocessing.RandomZoom(
        height_factor=(-0.3, -0.2),
        width_factor=(-0.3, -0.2)
        ),
    ])
augmented_train_ds = train_ds.map(
    lambda x, y: (data_augmentation(x, training=True), y)
    )
train_ds = train_ds.prefetch(buffer_size=32)
val_ds = val_ds.prefetch(buffer_size=32)

model = make_model(image_size + (3,), 2, chckpnt=True)
# keras.utils.plot_model(model, show_shapes=True)

callbacks = keras.callbacks.ModelCheckpoint(
    home / rf'Checkpoints\{name}_{{epoch:02}}.hdf5',
    save_freq=2
    )
for i in range(16):
    
    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss='binary_crossentropy',
        metrics=['accuracy']
        )
    model.fit(
        train_ds, epochs=epochs, 
        callbacks=[callbacks], 
        validation_data=val_ds
        )
    model.save(home / f'{name}.h5')
