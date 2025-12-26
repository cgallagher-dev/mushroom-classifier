import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QDialog, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt

# matplotlib for charts in qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# our backend model
from mushroom_model import MushroomModel

# maps the letters from the csv to human-readable words
FEATURE_MAP = {
    'cap-shape': {'b': 'Bell', 'c': 'Conical', 'x': 'Convex', 'f': 'Flat', 'k': 'Knobbed', 's': 'Sunken'},
    'cap-surface': {'f': 'Fibrous', 'g': 'Grooves', 'y': 'Scaly', 's': 'Smooth'},
    'cap-color': {'n': 'Brown', 'b': 'Buff', 'c': 'Cinnamon', 'g': 'Gray', 'r': 'Green', 'p': 'Pink', 'u': 'Purple',
                  'e': 'Red', 'w': 'White', 'y': 'Yellow'},
    'bruises': {'t': 'Bruises', 'f': 'No Bruises'},
    'odor': {'a': 'Almond', 'l': 'Anise', 'c': 'Creosote', 'y': 'Fishy', 'f': 'Foul', 'm': 'Musty', 'n': 'None',
             'p': 'Pungent', 's': 'Spicy'},
    'gill-attachment': {'a': 'Attached', 'f': 'Free'},
    'gill-spacing': {'c': 'Close', 'w': 'Crowded'},
    'gill-size': {'b': 'Broad', 'n': 'Narrow'},
    'gill-color': {'k': 'Black', 'n': 'Brown', 'b': 'Buff', 'h': 'Chocolate', 'g': 'Gray', 'r': 'Green', 'o': 'Orange',
                   'p': 'Pink', 'u': 'Purple', 'e': 'Red', 'w': 'White', 'y': 'Yellow'},
    'stalk-shape': {'e': 'Enlarging', 't': 'Tapering'},
    'stalk-root': {'b': 'Bulbous', 'c': 'Club', 'e': 'Equal', 'r': 'Rooted', '?': 'Missing'},
    'stalk-surface-above-ring': {'f': 'Fibrous', 'y': 'Scaly', 'k': 'Silky', 's': 'Smooth'},
    'stalk-surface-below-ring': {'f': 'Fibrous', 'y': 'Scaly', 'k': 'Silky', 's': 'Smooth'},
    'stalk-color-above-ring': {'n': 'Brown', 'b': 'Buff', 'c': 'Cinnamon', 'g': 'Gray', 'o': 'Orange', 'p': 'Pink',
                               'e': 'Red', 'w': 'White', 'y': 'Yellow'},
    'stalk-color-below-ring': {'n': 'Brown', 'b': 'Buff', 'c': 'Cinnamon', 'g': 'Gray', 'o': 'Orange', 'p': 'Pink',
                               'e': 'Red', 'w': 'White', 'y': 'Yellow'},
    'veil-type': {'p': 'Partial'},
    'veil-color': {'n': 'Brown', 'o': 'Orange', 'w': 'White', 'y': 'Yellow'},
    'ring-number': {'n': 'None', 'o': 'One', 't': 'Two'},
    'ring-type': {'e': 'Evanescent', 'f': 'Flaring', 'l': 'Large', 'n': 'None', 'p': 'Pendant'},
    'spore-print-color': {'k': 'Black', 'n': 'Brown', 'b': 'Buff', 'h': 'Chocolate', 'r': 'Green', 'o': 'Orange',
                          'u': 'Purple', 'w': 'White', 'y': 'Yellow'},
    'population': {'a': 'Abundant', 'c': 'Clustered', 'n': 'Numerous', 's': 'Scattered', 'v': 'Several',
                   'y': 'Solitary'},
    'habitat': {'g': 'Grasses', 'l': 'Leaves', 'm': 'Meadows', 'p': 'Paths', 'u': 'Urban', 'w': 'Waste', 'd': 'Woods'}
}


def decode_feature_name(encoded_name):
    # convert encoded feature like "odor_n" to "Odour: None"

    if '_' not in encoded_name:
        return encoded_name

    # split into feature and value
    parts = encoded_name.split('_', 1)
    feature_name = parts[0]
    value_code = parts[1]

    # get human-readable names
    if feature_name in FEATURE_MAP:
        feature_readable = feature_name.replace('-', ' ').title()
        value_map = FEATURE_MAP[feature_name]
        value_readable = value_map.get(value_code, value_code)
        return f"{feature_readable}: {value_readable}"

    return encoded_name


class MplCanvas(FigureCanvas):
    # simple qt widget for matplotlib charts

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    # main gui window

    def __init__(self):
        super().__init__()

        # create the backend model (loads csv and trains)
        try:
            self.model = MushroomModel()
        except FileNotFoundError:
            self.show_error_dialog("'mushroom.csv' not found. Make sure it's in the same folder as the script.")
            sys.exit(1)

        # window setup
        self.setWindowTitle("MUSH-ID: Edibility Classifier")
        self.setGeometry(100, 100, 1100, 600)

        # main layout
        main_widget = QWidget()
        self.main_layout = QHBoxLayout()
        main_widget.setLayout(self.main_layout)

        # store all dropdown references
        self.combo_boxes = {}

        # create left and right panels
        self.main_layout.addWidget(self.create_classifier_panel(), 1)
        self.main_layout.addWidget(self.create_dashboard_panel(), 1)

        self.setCentralWidget(main_widget)

    def create_classifier_panel(self):
        # left panel with all the mushroom feature dropdowns

        panel_widget = QWidget()
        panel_layout = QVBoxLayout()
        panel_widget.setLayout(panel_layout)

        # title
        title = QLabel("Mushroom Features")
        title.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(title)

        # scrollable area for all the dropdowns
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QGridLayout()
        scroll_content.setLayout(scroll_layout)

        # create dropdowns for each feature
        features = self.model.features
        options = self.model.feature_options

        row = 0
        for feature in features:
            # label for this feature
            feature_label = QLabel(f"{feature.replace('-', ' ').title()}:")
            scroll_layout.addWidget(feature_label, row, 0)

            # dropdown with human-readable options
            combo = QComboBox()
            feature_map = FEATURE_MAP.get(feature, {})
            readable_options = [feature_map.get(opt, opt) for opt in options[feature]]
            combo.addItems(readable_options)
            scroll_layout.addWidget(combo, row, 1)

            # save reference so we can read it later
            self.combo_boxes[feature] = combo
            row += 1

        scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(scroll_area)

        # classify button
        predict_button = QPushButton("CLASSIFY")
        predict_button.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        predict_button.setMinimumHeight(50)
        predict_button.clicked.connect(self.on_predict_click)
        panel_layout.addWidget(predict_button)

        # student info
        student_info = QLabel("Charlie Gallagher - A00321687")
        student_info.setFont(QtGui.QFont("Arial", 9))
        student_info.setAlignment(Qt.AlignCenter)
        student_info.setStyleSheet("color: #666666; padding: 10px;")
        panel_layout.addWidget(student_info)

        return panel_widget

    def create_dashboard_panel(self):
        # right panel with model info and feature importance chart

        panel_widget = QWidget()
        panel_layout = QVBoxLayout()
        panel_widget.setLayout(panel_layout)

        # title
        title = QLabel("Model Dashboard")
        title.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(title)

        # status info
        status_font = QtGui.QFont("Arial", 10)

        s1 = QLabel("Model Status: Trained")
        s1.setFont(status_font)
        panel_layout.addWidget(s1)

        s2 = QLabel("Dataset: mushroom.csv (8,124 samples)")
        s2.setFont(status_font)
        panel_layout.addWidget(s2)

        # source attribution
        s3 = QLabel("Source: Donated to UC Irvine Machine Learning Repository by National Audubon Society on April 26, 1987")
        s3.setFont(status_font)
        s3.setWordWrap(True)
        panel_layout.addWidget(s3)

        s4 = QLabel("Classifier: DecisionTreeClassifier")
        s4.setFont(status_font)
        panel_layout.addWidget(s4)

        # accuracy from model
        acc_text = self.model.get_model_accuracy()
        self.accuracy_label = QLabel(f"Model Accuracy: {acc_text}")
        self.accuracy_label.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        panel_layout.addWidget(self.accuracy_label)

        panel_layout.addSpacing(15)

        # feature importance chart
        chart_title = QLabel("Top 5 Feature Importances")
        chart_title.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(chart_title)

        self.chart = MplCanvas(self, width=7, height=8, dpi=100)
        self.update_feature_importance_chart()
        panel_layout.addWidget(self.chart, stretch=4)

        # add explanation paragraph about odour importance
        explanation_text = QLabel(
            "The chart shows which features most influence the model's predictions. "
            "Odour is clearly the strongest predictor of toxicity - counterintuitively, "
            "pleasant smells like almond and anise are often the most dangerous, "
            "while foul odours don't always mean poison. Mushrooms with no odour at all are typically "
            "the safest bet for edibility."
        )
        explanation_text.setFont(QtGui.QFont("Arial", 9))
        explanation_text.setWordWrap(True)
        explanation_text.setStyleSheet("color: #555555; padding: 6px; background-color: #f9f9f9; border-radius: 3px;")
        panel_layout.addWidget(explanation_text, stretch=0)

        return panel_widget

    def update_feature_importance_chart(self):
        # draw the feature importance bar chart

        importances = self.model.get_feature_importances(top_n=5)

        # convert encoded names to human-readable
        readable_labels = [decode_feature_name(name) for name in importances.keys()]
        values = list(importances.values())

        # reverse for better display (biggest at top)
        readable_labels = readable_labels[::-1]
        values = values[::-1]

        self.chart.axes.cla()
        self.chart.axes.barh(readable_labels, values, color='#4a90e2')
        self.chart.axes.set_title("Model Feature Importances", fontsize=11, fontweight='bold', pad=10)
        self.chart.axes.set_xlabel("Importance Score", fontsize=9)
        self.chart.axes.set_ylabel("Feature", fontsize=9)
        self.chart.axes.tick_params(axis='y', labelsize=8)
        self.chart.axes.tick_params(axis='x', labelsize=8)
        self.chart.figure.subplots_adjust(bottom=0.15, left=0.42, right=0.95, top=0.92)
        self.chart.draw()

    def on_predict_click(self):
        # called when user clicks classify button

        # collect all dropdown selections and convert back to letters
        user_input_dict = {}
        for feature_name, combo_box in self.combo_boxes.items():
            selected_word = combo_box.currentText()
            # convert word back to letter using feature map
            letter_to_word_map = FEATURE_MAP.get(feature_name)
            if letter_to_word_map:
                # find the letter that maps to this word
                letter = None
                for l, w in letter_to_word_map.items():
                    if w == selected_word:
                        letter = l
                        break
                user_input_dict[feature_name] = letter if letter else selected_word
            else:
                user_input_dict[feature_name] = selected_word

        # get prediction from model
        prediction = self.model.get_prediction(user_input_dict)

        # show result popup
        self.show_prediction_dialog(prediction)

    def show_prediction_dialog(self, prediction):
        # popup showing prediction result

        dialog = QDialog(self)
        dialog.setWindowTitle("Prediction Result")

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # result text with styling
        result_label = QLabel(f"PREDICTED:\n{prediction}")
        result_label.setAlignment(Qt.AlignCenter)

        if prediction == "POISONOUS":
            font = QtGui.QFont("Arial", 28, QtGui.QFont.Bold)
            result_label.setStyleSheet("color: red;")
        else:
            font = QtGui.QFont("Arial", 28, QtGui.QFont.Bold)
            result_label.setStyleSheet("color: green;")

        result_label.setFont(font)
        layout.addWidget(result_label)

        layout.addSpacing(15)

        # warning disclaimer
        disclaimer = QLabel(
            "Warning: This is a university project model.\n"
            "Do not eat wild mushrooms based on this prediction."
        )
        disclaimer.setAlignment(Qt.AlignCenter)
        disclaimer.setFont(QtGui.QFont("Arial", 9))
        layout.addWidget(disclaimer)

        layout.addSpacing(15)

        # ok button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)

        dialog.exec_()

    def show_error_dialog(self, message):
        # simple error popup

        dialog = QDialog(self)
        dialog.setWindowTitle("Error")
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        label = QLabel(message)
        layout.addWidget(label)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)

        dialog.exec_()


# run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
