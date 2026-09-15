from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score

from app.ingestion import normalized_tickets


ml_records = []

for index, ticket in enumerate(normalized_tickets):
    previous_escalation_count = sum(
        1
        for previous_ticket in normalized_tickets[:index]
        if (
            previous_ticket.customer_id == ticket.customer_id
            and previous_ticket.escalated is True
        )
    )

    previous_ticket_count = sum(
        1
        for previous_ticket in normalized_tickets[:index]
        if previous_ticket.customer_id == ticket.customer_id
    )

    if previous_ticket_count == 0:
        previous_escalation_rate = 0
    else:
        previous_escalation_rate = (
            previous_escalation_count / previous_ticket_count
        )

    previous_resolution_times = [
        previous_ticket.resolution_time_hours
        for previous_ticket in normalized_tickets[:index]
        if (
            previous_ticket.customer_id == ticket.customer_id
            and previous_ticket.resolution_time_hours is not None
        )
    ]

    average_previous_resolution_time = (
        sum(previous_resolution_times) / len(previous_resolution_times)
        if previous_resolution_times
        else None
    )

    ml_records.append({
        "ticket_id": ticket.ticket_id,
        "customer_id": ticket.customer_id,
        "created_at": ticket.created_at,
        "previous_ticket_count": previous_ticket_count,
        "previous_escalation_count": previous_escalation_count,
        "previous_escalation_rate": previous_escalation_rate,
        "average_previous_resolution_time": average_previous_resolution_time,
        "resolution_time_hours": ticket.resolution_time_hours,
        "priority": ticket.priority,
        "impact": ticket.impact,
        "recent_change": ticket.recent_change,
        "escalated": ticket.escalated,
    })


historical_records = [
    record for record in ml_records
    if record["escalated"] is not None
]

open_records = [
    record for record in ml_records
    if record["escalated"] is None
]


train_records, test_records = train_test_split(
    historical_records,
    test_size=0.20,
    random_state=42,
    stratify=[record["escalated"] for record in historical_records],
)


X_train = []
y_train = []

for record in train_records:
    X_train.append([
        record["previous_ticket_count"],
        record["previous_escalation_count"],
        record["previous_escalation_rate"],
        record["average_previous_resolution_time"],
        record["priority"],
        record["impact"],
        record["recent_change"],
    ])
    y_train.append(record["escalated"])


X_test = []
y_test = []

for record in test_records:
    X_test.append([
        record["previous_ticket_count"],
        record["previous_escalation_count"],
        record["previous_escalation_rate"],
        record["average_previous_resolution_time"],
        record["priority"],
        record["impact"],
        record["recent_change"],
    ])
    y_test.append(record["escalated"])


numeric_features = [0, 1, 2, 3]
categorical_features = [4, 5, 6]

numeric_transformer = SimpleImputer(strategy="median")

categorical_transformer = OneHotEncoder(
    handle_unknown="ignore",
    sparse_output=False,
)

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", numeric_transformer, numeric_features),
        ("categorical", categorical_transformer, categorical_features),
    ]
)


X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)


model = LogisticRegression(max_iter=1000 )
model.fit(X_train_transformed, y_train)


predictions = model.predict(X_test_transformed)
probabilities = model.predict_proba(X_test_transformed)


threshold = 0.70

threshold_predictions = [
    probability[1] >= threshold
    for probability in probabilities
]


X_open = []

for record in open_records:
    X_open.append([
        record["previous_ticket_count"],
        record["previous_escalation_count"],
        record["previous_escalation_rate"],
        record["average_previous_resolution_time"],
        record["priority"],
        record["impact"],
        record["recent_change"],
    ])

X_open_transformed = preprocessor.transform(X_open)
open_probabilities = model.predict_proba(X_open_transformed)[:, 1]


open_ticket_predictions = {}

for record, probability in zip(open_records, open_probabilities):
    open_ticket_predictions[record["ticket_id"]] = {
        "ticket_id": record["ticket_id"],
        "customer_id": record["customer_id"],
        "escalation_probability": float(probability),
        "risk_level": "high" if probability >= threshold else "low",
    }


if __name__ == "__main__":
    print("ML records:", len(ml_records))
    print("Historical records:", len(historical_records))
    print("Open records:", len(open_records))
    print("Training records:", len(train_records))
    print("Test records:", len(test_records))
    print("Training class distribution:", Counter(y_train))
    print("Test class distribution:", Counter(y_test))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, predictions))
    print("70% Threshold Confusion Matrix:")
    print(confusion_matrix(y_test, threshold_predictions, labels=[False, True]))
    print("ROC-AUC:", roc_auc_score(y_test, probabilities[:, 1]))
    print("\nOpen ticket predictions:")
    for ticket_id, prediction in open_ticket_predictions.items():
        print(
            ticket_id,
            prediction["customer_id"],
            round(prediction["escalation_probability"], 3),
        )
