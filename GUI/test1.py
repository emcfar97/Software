"""
Author: Luban studio
qq:1514149460
wx:18550030945
"""
# coding:utf-8

from PyQt5.Qt import QThread, QThreadPool, QRunnable, QObject, QWidget, QApplication, QPushButton, QGridLayout, QTextEdit, pyqtSignal, QTextCursor
import sys


# Execute the core code here
class Thread(QRunnable):
    communication = None

    def __init__(self):
        super(Thread, self).__init__()
        self.thread_logo = None

    def run(self):
        self.communication.log_signal.emit('{}Thread has been executed'.format(self.thread_logo))

    # Custom function, used to initialize some variables
    def transfer(self, thread_logo, communication):
        """
                 :param thread_logo: Thread logo for easy identification.
                 :param communication:signal
        :return:
        """

        self.thread_logo = thread_logo
        self.communication = communication


# Define tasks, where the main thread is created
class Tasks(QObject):
    communication = None
    max_thread_number = 0

    def __init__(self, communication, max_thread_number):
        """
                 :param communication:Communication
                 :param max_thread_number: Maximum number of threads
        """
        super(Tasks, self).__init__()

        self.max_thread_number = max_thread_number
        self.communication = communication

        self.pool = QThreadPool()
        self.pool.globalInstance()

    def start(self):
        # Set the maximum number of threads

        self.pool.setMaxThreadCount(self.max_thread_number)
        for i in range(10):
            task_thread = Thread()
            task_thread.transfer(thread_logo=i, communication=self.communication)
            task_thread.setAutoDelete(True)  # Whether to delete automatically
            self.pool.start(task_thread)

        self.pool.waitForDone()  # Wait for the task to complete
        self.communication.log_signal.emit('All threads are executed')


# Override the QThread class
class NowThread(QThread):
    def __init__(self, communication, max_thread_number):
        """
                 :param communication:Communication
                 :param max_thread_number: Maximum number of threads
        """
        super(NowThread, self).__init__()
        self.task = Tasks(
            communication=communication,
            max_thread_number=max_thread_number
        )

    def run(self):
        self.task.start()


class Window(QWidget):
    # Define signal
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.resize(1280, 800)
        self.setWindowTitle('QThreadPool instance')
        self.setup_ui()
        self.show()

    def setup_ui(self):
        # Initialize the signal associated slot function
        self.log_signal.connect(self.log_signal_event)

        layout = QGridLayout(self)  # Create layout

        button = QPushButton('Test button', self)
        button.clicked.connect(self.button_event)
        text_edit = QTextEdit()
        text_edit.setObjectName('text_edit')

        layout.addWidget(button, 0, 0)
        layout.addWidget(text_edit, 0, 1)
        self.setLayout(layout)

    def button_event(self):
        thread = NowThread(
            communication=self,
            max_thread_number=5
        )
        thread.start()  # Start thread
        thread.wait()  # Waiting for threads

    def log_signal_event(self, p_str):
        text_edit = self.findChild(QTextEdit, 'text_edit')
        text_cursor = QTextCursor(text_edit.textCursor())
        text_cursor.setPosition(0, QTextCursor.MoveAnchor)  # Move the cursor
        text_cursor.insertHtml('<p style="font-size:20px;color:red;">{}</p>'.format(p_str))
        text_cursor.insertHtml('<br>')
        text_edit.setTextCursor(text_cursor)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())

