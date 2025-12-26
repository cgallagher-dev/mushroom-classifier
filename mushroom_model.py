import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix


class MushroomModel:
    # backend class that handles the data and ml

    def __init__(self, dataset_path='mushroom.csv'):
        # load csv, clean it up, and train the model

        # load the csv file
        self.raw_data = pd.read_csv(dataset_path)

        # define target and features
        self.target = 'class'
        self.features = self.raw_data.drop(self.target, axis=1).columns.tolist()

        # placeholders
        self.tree = None
        self.accuracy = 0.0
        self.encoded_columns = []  # important for predictions later

        # get options for gui dropdowns
        self.feature_options = self._get_feature_options()

        # train the model
        print("Model: Training...")
        self.run_training_pipeline()
        print(f"Model: Done. Accuracy: {self.get_model_accuracy()}")

    def _get_feature_options(self):
        # get unique values for each feature (for gui dropdowns)

        print("Model: Getting options...")
        options = {}
        for feature in self.features:
            options[feature] = self.raw_data[feature].unique().tolist()
        return options

    def run_training_pipeline(self):
        # prep the data and train the decision tree

        # split into features and target
        y = self.raw_data[self.target]
        X = self.raw_data[self.features]

        # one-hot encode categorical features
        X_encoded = pd.get_dummies(X)

        # save column names for predictions
        self.encoded_columns = X_encoded.columns.tolist()

        # train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y, random_state=42, test_size=0.25
        )

        # train decision tree
        self.tree = DecisionTreeClassifier()
        self.tree.fit(X_train, y_train)

        # calculate accuracy
        y_pred = self.tree.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)

    def get_prediction(self, user_input_dict):
        # predict if mushroom is edible or poisonous

        # convert user input to dataframe
        input_df = pd.DataFrame([user_input_dict])

        # one-hot encode
        input_encoded = pd.get_dummies(input_df)

        # make sure columns match training data
        input_reindexed = input_encoded.reindex(columns=self.encoded_columns, fill_value=0)

        # predict
        prediction = self.tree.predict(input_reindexed)

        # return readable result
        if prediction[0] == 'p':
            return "POISONOUS"
        else:
            return "EDIBLE"

    def get_model_accuracy(self):
        # return accuracy as percentage string
        return f"{self.accuracy * 100:.2f}%"

    def get_feature_importances(self, top_n=5):
        # get top feature importances for the chart

        importances = pd.Series(
            self.tree.feature_importances_,
            index=self.encoded_columns
        ).nlargest(top_n)

        return importances.to_dict()


# test the model if run directly
if __name__ == "__main__":
    # create and test model
    model = MushroomModel()

    # show accuracy
    print(f"\nAccuracy: {model.get_model_accuracy()}")

    # show top features
    print("\n--- Top 5 feature importances ---")
    print(model.get_feature_importances())

    # test with poisonous mushroom (foul odour)
    test_poisonous = {
        'cap-shape': 'x', 'cap-surface': 's', 'cap-color': 'n', 'bruises': 't',
        'odor': 'f', 'gill-attachment': 'f', 'gill-spacing': 'c', 'gill-size': 'n',
        'gill-color': 'b', 'stalk-shape': 'e', 'stalk-root': '?',
        'stalk-surface-above-ring': 's', 'stalk-surface-below-ring': 's',
        'stalk-color-above-ring': 'w', 'stalk-color-below-ring': 'w',
        'veil-type': 'p', 'veil-color': 'w', 'ring-number': 'o', 'ring-type': 'p',
        'spore-print-color': 'k', 'population': 'v', 'habitat': 'u'
    }

    # test with edible mushroom (no odour)
    test_edible = {
        'cap-shape': 'x', 'cap-surface': 's', 'cap-color': 'n', 'bruises': 't',
        'odor': 'n', 'gill-attachment': 'f', 'gill-spacing': 'c', 'gill-size': 'b',
        'gill-color': 'w', 'stalk-shape': 'e', 'stalk-root': 'c',
        'stalk-surface-above-ring': 's', 'stalk-surface-below-ring': 's',
        'stalk-color-above-ring': 'w', 'stalk-color-below-ring': 'w',
        'veil-type': 'p', 'veil-color': 'w', 'ring-number': 'o', 'ring-type': 'p',
        'spore-print-color': 'k', 'population': 's', 'habitat': 'u'
    }

    print("\n--- Prediction Test ---")
    prediction_1 = model.get_prediction(test_poisonous)
    print(f"Test 1 (Poisonous): {prediction_1}")

    prediction_2 = model.get_prediction(test_edible)
    print(f"Test 2 (Edible):    {prediction_2}")
