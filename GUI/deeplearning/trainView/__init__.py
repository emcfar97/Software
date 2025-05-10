# import tensorflow as tf
# import keras

from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QMessageBox, QSpinBox, QSizePolicy
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PyQt6.QtCore import Qt, QThreadPool, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter

from GUI import Worker

class Train(QWidget):

    training_commplete = pyqtSignal(object)
    key_pressed = pyqtSignal(object)
    
    def __init__(self, parent):
        
        super(Train, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
    
        self.center = QHBoxLayout(self)
        self.controls = QVBoxLayout()
        self.formLayout = QFormLayout()
        
        self.setLayout(self.center)
        
    def create_widgets(self):

        self.chart = Chart(self)
        self.threadpool = QThreadPool(self)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        self.formLayout.addRow('Epochs:', QSpinBox(self))
    
        self.start_training = QPushButton('Start training', self)
        self.start_training.clicked.connect(self.train)
        
        self.center.addWidget(self.chart_view, stretch=3)
        self.center.addLayout(self.controls, stretch=1)
        
        self.controls.addLayout(self.formLayout)
        self.controls.addWidget(self.start_training)
        
        self.training_commplete.connect(self.completed_training)

    def train(self):
        
        x_train, y_train, y_test, x_test = self.get_dataset()
        
        predictions = self.model(x_train[:1]).numpy()

        loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        loss_fn(y_train[:1], predictions).numpy()

        tracking = keras.callbacks.LambdaCallback(
            on_epoch_begin=self.on_epoch_begin,
            on_epoch_end=self.on_epoch_end, 
            on_train_begin=self.on_train_begin, 
            on_train_end=self.on_train_end
            )
        
        self.model.compile(
            optimizer='adam',
            loss=loss_fn,
            metrics=['accuracy'],
            )
        
        worker = Worker(
            self.model.fit, 
            x_train, y_train, 
            epochs=self.get_variable('Epoch'), 
            callbacks=[tracking], verbose=0
            )
        self.threadpool.start(worker)
    
    def get_variable(self, field):
        
        field = self.formLayout.itemAt(0, QFormLayout.FieldRole).widget()
        
        return field.value()
    
    def get_dataset(self):
        
        mnist = tf.keras.datasets.mnist

        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        
        return x_train / 255.0, y_train, x_test / 255.0, y_test
    
    def completed_training(self, logs,):
        
        QMessageBox.information(
            self, 'Training Complete', 
            f'Final values\nLoss: {logs["loss"]:.2%}\nAccuracy: {logs["accuracy"]:.2%}',
            QMessageBox.Ok
            )
        
    def on_train_begin(self, logs=None):
        
        for key in self.series:
            
            self.series[key].clear()
            
        self.chart.axisX().setMax(0)

        keys = list(logs.keys())
        print(f"Starting training; got log keys: {keys}")

    def on_train_end(self, logs=None):

        self.training_commplete.emit(logs)
        
        keys = list(logs.keys())
        print(f"Stop training; got log keys: {keys}")

    def on_epoch_begin(self, epoch, logs=None):

        keys = list(logs.keys())
        print(f"Start epoch {epoch} of training; got log keys: {keys}")

    def on_epoch_end(self, epoch, logs=None):

        for key in logs.keys():
            
            self.series[key].append(QPointF(epoch, logs[key]))
        
        self.chart.axisX().setMax(epoch)
        
        keys = list(logs.keys())
        print(f"End epoch {epoch} of training; got log keys: {keys}")
    
    def keyPressEvent(self, event):
        
        key_press = event.key()
                
        if key_press == Qt.Key.Key_Escape: self.close()
        
        else: self.key_pressed.emit(event)

class Chart(QChart):
    
    def __init__(self, parent):
        
        super(Chart, self).__init__()
        self.parent = parent
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
        
        self.setTitle("Line Chart Example")
        self.legend().setVisible(True)
        self.legend().setAlignment(Qt.AlignBottom)
        self.setAnimationOptions(QChart.SeriesAnimations)
 
        self.createDefaultAxes()
        axisX = QValueAxis()
        axisX.setTickType(QValueAxis.TicksDynamic)
        axisX.setTickAnchor(0.0)
        axisX.setTickInterval(1)
        axisX.setTitleText("Epochs")
        self.setAxisX(axisX)
        # self.axisY().setRange(0, 1)
        
    def create_widgets(self):

        self.series = {
            'accuracy': QLineSeries(), 
            'loss': QLineSeries()
            }
        for label, series in self.series.items():
            
            series.setName(label.capitalize())
            self.addSeries(series)
        
        self.chart_view = QChartView(self)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
# class TrackingCallback(keras.callbacks.Callback):
    
    # def on_train_begin(self, logs=None):

    #     keys = list(logs.keys())
    #     print(f"Starting training; got log keys: {keys}")

    # def on_train_end(self, logs=None):

    #     keys = list(logs.keys())
    #     print(f"Stop training; got log keys: {keys}")

    # def on_epoch_begin(self, epoch, logs=None):

    #     keys = list(logs.keys())
    #     print(f"Start epoch {epoch} of training; got log keys: {keys}")

    # def on_epoch_end(self, epoch, logs=None):

    #     keys = list(logs.keys())
    #     print(f"End epoch {epoch} of training; got log keys: {keys}")

    # def on_test_begin(self, logs=None):

    #     keys = list(logs.keys())
    #     print(f"Start testing; got log keys: {keys}")

    # def on_test_end(self, logs=None):

    #     keys = list(logs.keys())
    #     print(f"Stop testing; got log keys: {keys}")

    # def on_predict_begin(self, logs=None):

    #     keys = list(logs.keys())
    #     print(f"Start predicting; got log keys: {keys}")

    # def on_predict_end(self, logs=None):

    #     keys = list(logs.keys())
    #     print(f"Stop predicting; got log keys: {keys}")

    # def on_train_batch_begin(self, batch, logs=None):

    #     keys = list(logs.keys())
    #     print(f"...Training: start of batch {batch}; got log keys: {keys}")

    # def on_train_batch_end(self, batch, logs=None):

    #     keys = list(logs.keys())
    #     print(f"...Training: end of batch {batch}; got log keys: {keys}")

    # def on_test_batch_begin(self, batch, logs=None):

    #     keys = list(logs.keys())
    #     print(f"...Evaluating: start of batch {batch}; got log keys: {keys}")

    # def on_test_batch_end(self, batch, logs=None):

    #     keys = list(logs.keys())
    #     print(f"...Evaluating: end of batch {batch}; got log keys: {keys}")

    # def on_predict_batch_begin(self, batch, logs=None):

    #     keys = list(logs.keys())
    #     print(f"...Predicting: start of batch {batch}; got log keys: {keys}")

    # def on_predict_batch_end(self, batch, logs=None):

    #     keys = list(logs.keys())
    #     print(f"...Predicting: end of batch {batch}; got log keys: {keys}")