import random
from datetime import date, timedelta
import pkg_resources
import joblib
import pandas as pd
import sklearn
from catboost import CatBoostClassifier

static_dir = pkg_resources.resource_filename(__name__, 'static')

model = CatBoostClassifier()
model.load_model(static_dir+"/cringe_model.cbm")

label_encoder = joblib.load(static_dir+"/label_encoder.joblib")


def hate_ml(
    month: int, year: int, polygon_name: str, vehicle_number: list[str]
) -> list[dict]:
    """Возвращает список словарей, состоящего из дат, значений по датам, штрафам и манере вождения"""

    # генерация количества числа поездок за месяц для каждого номера
    list_count_rides = [random.randint(5, 25) for x in range(len(vehicle_number))]
    result_list = []

    for ride_count_index in range(len(list_count_rides)):
        # генерация дат, когда в этом месяце данный номер ездил
        dates = _generate_dates(month, year, list_count_rides[ride_count_index])
        for current_date in dates:
            new_data = pd.DataFrame(
                {
                    "день недели путевого листа": [current_date.weekday()],
                    "Дата сигнала телематики": [current_date.weekday()],
                    "Номерной знак ТС": [vehicle_number[ride_count_index]],
                    "Полигон": [polygon_name],
                }
            )

            new_data["Номерной знак ТС"] = label_encoder.fit_transform(
                new_data["Номерной знак ТС"]
            )
            new_data["Полигон"] = label_encoder.fit_transform(new_data["Полигон"])
            km_by_pappers = model.predict(new_data)[0][0] * random.uniform(1, 2.5)
            result_list.append(
                {
                    "Наименование полигона": polygon_name,
                    "Номерной знак ТС": vehicle_number[ride_count_index],
                    "дата путевого листа": current_date.strftime('%d-%m-%Y'),
                    "Данные путевых листов, пробег": km_by_pappers,
                    "Дата сигнала телематики": current_date.strftime('%d-%m-%Y'),
                    "Данные телематики, пробег": random.uniform(
                        km_by_pappers * 0.8, km_by_pappers * 1.2
                    ),
                    "Штрафы": random.randint(0, 5),
                    "манера вождения": random.uniform(0, 6),
                }
            )
    return result_list


def _generate_dates(month: int, year: int, number_of_dates: int) -> list:
    dates = []
    first_day = date(year, month, 1)
    last_day = date(year, month + 1, 1) - timedelta(days=1)
    for _ in range(number_of_dates):
        random_day = random.randint(first_day.day, last_day.day)
        random_date = date(year, month, random_day)
        dates.append(random_date)

    return dates



# print(hate_ml(5, 2024, "xd", ["0600РХ70"]))
