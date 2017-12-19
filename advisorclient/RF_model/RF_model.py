import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier


def data_preprocess():
    train_data = pd.read_csv("train.csv")
    test_data = pd.read_csv("test.csv")

    train_data.insert(loc=0, column="CabinNull", value=np.array(train_data.isnull()["Cabin"], dtype=int))
    train_data.insert(loc=0, column="AgeNull", value=np.array(train_data.isnull()["Age"], dtype=int))

    train_data.insert(loc=0, column="FamilyName", value=train_data["Name"].str.split(pat=",", expand=True)[0])
    train_data["Name"] = train_data["Name"].str.split(pat=",", expand=True)[1]
    train_data.insert(loc=0, column="Title", value=train_data["Name"].str.split(pat=".", expand=True)[0])
    train_data["Name"] = train_data["Name"].str.split(pat=".", expand=True)[1]

    family_size = train_data.groupby("FamilyName", as_index=False).agg({"PassengerId": np.size})
    family_size = family_size.rename(columns={"PassengerId": "FamilySize"})
    train_data = pd.merge(train_data, family_size, on='FamilyName')

    t1 = np.zeros((train_data.shape[0],))
    t2 = []

    ticket_split = train_data["Ticket"].str.split(pat=" ")
    for i in range(len(ticket_split)):
        if ticket_split[i][0] == "LINE":
            t1[i] = 1
            t2.append(0)
        elif len(ticket_split[i]) >= 2:
            t1[i] = 1
            t2.append(float(int(ticket_split[i][len(ticket_split[i]) - 1])))
        else:
            t2.append(float(int(ticket_split[i][0])))
    train_data.insert(loc=0, column="ExtraTicketInfo", value=t1)
    train_data.insert(loc=0, column="TicketNum", value=t2)

    t1 = np.zeros((test_data.shape[0],))
    t2 = []

    ticket_split = test_data["Ticket"].str.split(pat=" ")
    for i in range(len(ticket_split)):
        if ticket_split[i][0] == "LINE":
            t1[i] = 1
            t2.append(0)
        elif len(ticket_split[i]) >= 2:
            t1[i] = 1
            t2.append(float(int(ticket_split[i][len(ticket_split[i]) - 1])))
        else:
            t2.append(float(int(ticket_split[i][0])))
    test_data.insert(loc=0, column="ExtraTicketInfo", value=t1)
    test_data.insert(loc=0, column="TicketNum", value=t2)

    ticket_bucket = []
    for i in range(len(train_data["TicketNum"])):
        if train_data["TicketNum"][i] < 310131.7:
            ticket_bucket.append(2)
        elif train_data["TicketNum"][i] >= 310131.7 and train_data["TicketNum"][i] <= 620263.4:
            ticket_bucket.append(0)
        else:
            ticket_bucket.append(1)

    train_data.insert(loc=0, column="TicketCat", value=ticket_bucket)

    le = preprocessing.LabelEncoder()
    le.fit(["female", "male"])
    train_data["Sex"] = le.fit_transform(train_data["Sex"])
    train_data.head(n=5)

    title_map = dict({
        " Capt": 0,
        " Don": 1,
        " Dona": 1,
        " Jonkheer": 2,
        " Rev": 3,
        " Mr": 4,
        " Dr": 5,
        " Col": 6,
        " Major": 7,
        " Master": 8,
        " Miss": 9,
        " Mrs": 10,
        " Mme": 11,
        " Sir": 12,
        " Ms": 13,
        " Lady": 14,
        " Mlle": 15,
        " the Countess": 16
    })
    title_encode = []
    for i in train_data["Title"]:
        title_encode.append(title_map[i])
    train_data["Title"] = title_encode
    train_data.head(n=5)

    train_data = pd.get_dummies(train_data, columns=["Embarked"], dummy_na=True)

    train_data = train_data.fillna(-999)

    train_age_full = train_data[train_data["Age"] >= 0][["PassengerId", "Age"]]
    pridict_age_full = train_data[train_data["Age"] < 0][["PassengerId", "Age"]]
    train_age = np.array(train_data[train_data["Age"] >= 0]["Age"])

    train_sibsp = np.array(train_data[train_data["Age"] >= 0]["SibSp"])
    train_sibsp = np.reshape(train_sibsp, (train_sibsp.shape[0], 1))

    predict_sibsp = np.array(train_data[train_data["Age"] < 0]["SibSp"])
    predict_sibsp = np.reshape(predict_sibsp, (predict_sibsp.shape[0], 1))

    neigh = KNeighborsRegressor(n_neighbors=5)
    neigh.fit(train_sibsp, train_age)
    predict_age = neigh.predict(predict_sibsp)
    pridict_age_full["Age"] = predict_age
    new_age = pd.concat([train_age_full, pridict_age_full], axis=0)
    new_age = new_age.rename(columns={"Age": "NewAge"})

    train_data = pd.merge(train_data, new_age, on="PassengerId")

    y_train = train_data["Survived"]
    train_data = train_data.drop(["Age", "FamilyName", "PassengerId", "Survived", "Name", "Cabin", "Ticket"], axis=1)

    y_train = np.array(y_train)
    X_train = np.array(train_data)
    y_train = np.reshape(y_train, (y_train.shape[0],))

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    return X_train, y_train


def model(n_estimator, criterion, max_features, max_depth):
    # Xtrain, Xtest, ytrain, ytest = train_test_split(X_train, y_train, test_size=0.3)
    # print(Xtrain.shape)
    # print(ytrain.shape)
    rf = RandomForestClassifier(
        # integer 100
        n_estimators=int(n_estimator),
        # "gini" or "entropy"
        criterion=criterion,
        # float 0.4
        max_features=float(max_features),
        # integer 7
        max_depth=int(max_depth),
        # random_state=4,
    )
    # rf.fit(Xtrain, ytrain)
    X_train, y_train = data_preprocess()
    scores = cross_val_score(rf, X_train, y_train, cv=10)
    return np.mean(scores)


def usage():
    print('RF_model.py usage')
    print('-h, --help:          Print help message')
    print('-n, --n_estimators:  The number of trees in the forest')
    print('-c, --criterion:     The function to measure the quality of a split')
    print('-f, --max_features:  The number of features to consider when looking for the best split')
    print('-d, --max_depth:     The maximum depth of the tree')


def get_metric():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("trail", nargs="+", type=str)
    # args = parser.parse_args()

    import getopt
    import sys
    argv = sys.argv
    opts, args = getopt.getopt(argv[1:], 'n:c:f:d:h',
                               ['n_estimators=', 'criterion=', 'max_features=', 'max_depth=', 'help'])
    n_estimator = None
    criterion = None
    max_features = None
    max_depth = None

    for o, v in opts:
        if o in ['-h', '--help']:
            usage()
            sys.exit(0)
        if o in ['-n', '--n_estimators']:
            n_estimator = v
        if o in ['-c', '--criterion']:
            criterion = v
        if o in ['-f', '--max_features']:
            max_features = v
        if o in ['-d', '--max_depth']:
            max_depth = v
    if None in [n_estimator, criterion, max_features, max_depth]:
        print(n_estimator, criterion, max_features, max_depth)
        usage()
        sys.exit(1)

    metric = model(n_estimator, criterion, max_features, max_depth)
    print(metric)


if __name__ == "__main__":
    get_metric()
