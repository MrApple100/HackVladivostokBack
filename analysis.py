import pandas as pd
import ai
import json

class RzdParser():
    def __init__(self, filename):

        df = pd.read_excel(filename)
        a = None
        dl = []
        for index, row in df.iterrows():
            if pd.notna(row['Наименование полигона']) and pd.notna(row['Краткое наименование']) and pd.notna(row['Полигон']) and pd.notna(row['Номерной знак ТС']) and pd.notna(row['Наименование структурного подразделения']):
                a = row
                if not pd.notna(row['Дата сигнала телематики']):
                    dl.append(index)
                # print("a", index)
            else:
            # print("b", index, a['Наименование полигона'])
                df.at[index,'Наименование полигона'] = a['Наименование полигона']
                df.at[index,'Краткое наименование'] = a['Краткое наименование']
                df.at[index,'Полигон'] = a['Полигон']
                df.at[index,'Номерной знак ТС'] = a['Номерной знак ТС']
                df.at[index,'Тип закрепления'] = a['Тип закрепления']
                df.at[index,'манера вождения'] = a['манера вождения']
                df.at[index,'Наименование структурного подразделения'] = a['Наименование структурного подразделения']
                df.at[index,'Выполняемые функции'] = a['Выполняемые функции']
                df.at[index,'Должность за кем закреплен ТС'] = a['Должность за кем закреплен ТС']

        df.drop(dl, inplace=True)

        df.to_excel(filename[:-5]+"_1.xlsx", index=False)
        
        self.df = df
        self.df['дата путевого листа'] = pd.to_datetime(self.df['дата путевого листа'], format='%d.%m.%Y')
        self.df['Дата сигнала телематики'] = pd.to_datetime(self.df['Дата сигнала телематики'], format='%d.%m.%Y')

    def get_values(self, name):
        if name == None:
            return list(self.df.columns.values)
        return list(self.df[name].unique())

# Про подразделения

    def get_vehicle_division_info(self, name):
    # Фильтрация данных по имени подразделения
        division_data = self.df[self.df['Наименование структурного подразделения'] == name]

        if division_data.empty:
            return {'error': 'Подразделение не найдено'}

        # Вычисление метрик для данного подразделения
        penalty_sum = division_data['Штрафы'].sum()
        mileage_match = division_data['Данные путевых листов, пробег'].sum() / division_data['Данные телематики, пробег'].sum()
        
        # Уникальные ТС в подразделении
        unique_vehicles = division_data['Номерной знак ТС'].nunique()
        
        # Уникальные ТС в целевой структуре парка
        target_structure_vehicles = division_data[division_data['Тип закрепления'] == 'В целевой структуре парка']['Номерной знак ТС'].nunique()
        
        total_vehicle_ratio = unique_vehicles / target_structure_vehicles if target_structure_vehicles else 0
        
        most_used_vehicles = division_data['Номерной знак ТС'].value_counts().index[:3].tolist()
        least_used_vehicles = division_data['Номерной знак ТС'].value_counts().index[-3:].tolist()
        average_driving_style = division_data['манера вождения'].mean()

        # Формирование словаря с информацией о подразделении
        division_info = {
            'Название подразделения': name,
            'Сумма штрафов': penalty_sum,
            'Соотношение пробега': mileage_match,
            'Соотношение ТС': total_vehicle_ratio,
            'Топ-3 часто используемых ТС': most_used_vehicles,
            'Топ-3 редко используемых ТС': least_used_vehicles,
            'Средняя манера вождения': average_driving_style
        }

        return division_info
    
# Про полигон
    def get_polygon_info(self, name):
        # Фильтрация данных по полигону
        polygon_data = self.df[self.df['Полигон'] == name]

        if polygon_data.empty:
            return {'error': 'Полигон не найден'}

        # Вычисление метрик для данного полигона
        penalty_sum = polygon_data['Штрафы'].sum()
        total_mileage = polygon_data['Данные путевых листов, пробег'].sum()
        penalty_rank = polygon_data.groupby('Наименование структурного подразделения')['Штрафы'].sum().sort_values(ascending=False)
        mileage_rank = polygon_data.groupby('Наименование структурного подразделения')['Данные путевых листов, пробег'].sum().sort_values(ascending=False)

        # Формирование словаря с информацией о полигоне
        polygon_info = {
            'Название полигона': name,
            'Сумма штрафов': penalty_sum,
            'Общий пробег': total_mileage,
            'Рейтинг подразделений по количеству штрафов': penalty_rank.to_dict(),
            'Рейтинг подразделений по количеству пробега': mileage_rank.to_dict()
        }

        return polygon_info
    
# Про ТС
    def get_vehicle_info(self, name):

        vehicle_data = self.df[self.df['Номерной знак ТС'] == name].copy()
        vehicle_data.loc[:, 'Данные путевых листов, пробег'] = pd.to_numeric(vehicle_data['Данные путевых листов, пробег'], errors='coerce')
        vehicle_data.loc[:, 'Штрафы'] = pd.to_numeric(vehicle_data['Штрафы'], errors='coerce').fillna(0)
        vehicle_data = vehicle_data.dropna(subset=['Данные путевых листов, пробег'])

        if vehicle_data.empty:
            return {'error': 'Транспортное средство не найдено'}

        mean_driving_style = vehicle_data['манера вождения'].mean()
        total_mileage = vehicle_data['Данные путевых листов, пробег'].sum()
        signal_count = vehicle_data['Дата сигнала телематики'].count()
        severity = 6 - mean_driving_style
        complex_coefficient = severity * signal_count

        return {
            'Номерной знак ТС': name,
            'Средняя манера вождения': float(mean_driving_style),
            'Суммарный пробег': float(total_mileage),
            'Частота использования': float(signal_count),
            'Убитость': float(severity),
            'Сложный коэффициент': float(complex_coefficient)
        }
    
    def get_vehicle_recommendations(self):
    # Фильтрация данных по типу закрепления
        target_structure_vehicles = self.df[self.df['Тип закрепления'] == 'В целевой структуре парка']
        other_vehicles = self.df[self.df['Тип закрепления'] == 'Прочие']
        no_type_vehicles = self.df[self.df['Тип закрепления'].isnull()]

        # Анализ использования ТС на уровне полигона
        poligon_usage = self.df.groupby('Наименование полигона').size()
        avg_poligon_usage = poligon_usage.mean()

        recommendations = []

        # Анализ ТС в целевой структуре парка
        for vehicle, usage in target_structure_vehicles.groupby('Номерной знак ТС').size().items():
            if usage < avg_poligon_usage:
                target_poligon = poligon_usage[poligon_usage > avg_poligon_usage].index[0]
                recommendations.append({
                    'Номерной знак ТС': vehicle,
                    'Текущий тип закрепления': 'В целевой структуре парка',
                    'Рекомендуемое действие': 'Переместить в Прочие',
                    'Рекомендуемое место': target_poligon,
                    'Причина': 'Низкое использование'
                })

        # Анализ ТС в прочих
        for vehicle, usage in other_vehicles.groupby('Номерной знак ТС').size().items():
            if usage > avg_poligon_usage:
                target_poligon = poligon_usage[poligon_usage < avg_poligon_usage].index[0]
                recommendations.append({
                    'Номерной знак ТС': vehicle,
                    'Текущий тип закрепления': 'Прочие',
                    'Рекомендуемое действие': 'Переместить в В целевой структуре парка',
                    'Рекомендуемое место': target_poligon,
                    'Причина': 'Высокое использование'
                })

        # Анализ ТС без типа закрепления
        for vehicle, usage in no_type_vehicles.groupby('Номерной знак ТС').size().items():
            if usage > avg_poligon_usage:
                target_poligon = poligon_usage[poligon_usage < avg_poligon_usage].index[0]
                recommendations.append({
                    'Номерной знак ТС': vehicle,
                    'Текущий тип закрепления': 'Нет данных',
                    'Рекомендуемое действие': 'Переместить в В целевой структуре парка',
                    'Рекомендуемое место': target_poligon,
                    'Причина': 'Высокое использование'
                })
            elif usage < avg_poligon_usage:
                target_poligon = poligon_usage[poligon_usage > avg_poligon_usage].index[0]
                recommendations.append({
                    'Номерной знак ТС': vehicle,
                    'Текущий тип закрепления': 'Нет данных',
                    'Рекомендуемое действие': 'Переместить в Прочие',
                    'Рекомендуемое место': target_poligon,
                    'Причина': 'Низкое использование'
                })

        # Анализ использования транспорта на уровне полигона
        for poligon, usage in poligon_usage.items():
            if usage < avg_poligon_usage:
                # Предложение переноса транспорта из менее нагруженных полигонов в более нагруженные
                for vehicle, vehicle_usage in self.df[self.df['Наименование полигона'] == poligon].groupby('Номерной знак ТС').size().items():
                    if vehicle_usage < avg_poligon_usage:
                        target_poligon = poligon_usage[poligon_usage > avg_poligon_usage].index[0]
                        recommendations.append({
                            'Номерной знак ТС': vehicle,
                            'Текущий полигон': poligon,
                            'Рекомендуемое действие': 'Переместить в другой полигон',
                            'Рекомендуемое место': target_poligon,
                            'Причина': 'Низкое использование'
                        })

        # Анализ подразделений внутри каждого полигона
        for poligon, poligon_data in self.df.groupby('Наименование полигона'):
            subdivision_usage = poligon_data.groupby('Наименование структурного подразделения').size()
            avg_subdivision_usage = subdivision_usage.mean()
            
            for subdivision, usage in subdivision_usage.items():
                if usage < avg_subdivision_usage:
                    # Предложение обмена техникой между подразделениями
                    for vehicle, vehicle_usage in poligon_data[poligon_data['Наименование структурного подразделения'] == subdivision].groupby('Номерной знак ТС').size().items():
                        if vehicle_usage < avg_subdivision_usage:
                            target_subdivision = subdivision_usage[subdivision_usage > avg_subdivision_usage].index[0]
                            recommendations.append({
                                'Номерной знак ТС': vehicle,
                                'Текущее подразделение': subdivision,
                                'Рекомендуемое действие': 'Обменять с другим подразделением',
                                'Рекомендуемое место': target_subdivision,
                                'Причина': 'Низкое использование',
                                'Текущий полигон': poligon
                            })

        return recommendations
    
    def get_vehicle_transfer_recommendations(self, name):
        if name == None:
            recommendations = self.get_vehicle_recommendations()
        else:
            recommendations = self.get_vehicle_recommendations()
            recommendations = [
                rec for rec in recommendations if name in rec.values()
            ]
        return recommendations

    def calculate_coefficient(self, value, reference, thresholds, coefficients):
        deviation = abs((value - reference) / reference) * 100
        for threshold, coefficient in zip(thresholds, coefficients):
            if deviation > threshold:
                return coefficient
        return 1

    def calculate_efficiency_rating(self, mileage_ratio, structure_ratio, penalties, driving_style):
        # Весовые коэффициенты
        weights = {
            'mileage': 0.4,
            'structure': 0.3,
            'penalties': 0.15,
            'driving_style': 0.15
        }

        # Коэффициенты для пробега
        mileage_thresholds = [5, 10, 20]
        mileage_coefficients = [0.8, 0.7, 0.6]
        mileage_coefficient = self.calculate_coefficient(mileage_ratio, 1, mileage_thresholds, mileage_coefficients)

        # Коэффициенты для соответствия целевой структуре
        structure_thresholds = [5, 10, 20]
        structure_coefficients = [0.8, 0.7, 0.6]
        structure_coefficient = self.calculate_coefficient(structure_ratio, 1, structure_thresholds, structure_coefficients)

        # Коэффициенты для штрафов
        penalties_thresholds = [5, 15, 25]
        penalties_coefficients = [0.9, 0.8, 0.7]
        penalties_coefficient = self.calculate_coefficient(penalties, 1, penalties_thresholds, penalties_coefficients)

        # Коэффициенты для манеры вождения
        driving_style_thresholds = [10, 15, 20]
        driving_style_coefficients = [0.9, 0.8, 0.7]
        driving_style_coefficient = self.calculate_coefficient(driving_style, 6, driving_style_thresholds, driving_style_coefficients)

        # Вычисление итогового рейтинга
        rating = (mileage_coefficient * weights['mileage'] +
                  structure_coefficient * weights['structure'] +
                  penalties_coefficient * weights['penalties'] +
                  driving_style_coefficient * weights['driving_style'])

        return rating
    
    def calculate_efficiency_rating_division(self,name):
        if name==None:
            arr = []
            for i in self.get_values('Наименование структурного подразделения'):
                res = self.get_vehicle_division_info(i)
                arr.append({i:self.calculate_efficiency_rating(res['Соотношение пробега'], res['Соотношение ТС'], res['Сумма штрафов'], res['Средняя манера вождения'])})
            return arr
        else:
            res = self.get_vehicle_division_info(name)
            return {name:self.calculate_efficiency_rating(res['Соотношение пробега'], res['Соотношение ТС'], res['Сумма штрафов'], res['Средняя манера вождения'])}
        



    ### AI


    def ai_vehicle_division_info(self, name, cars, types):
    # Фильтрация данных по имени подразделения
        res = ai.hate_ml(5, 2024, name, cars)

        for i in res:
            i['Тип закрепления'] = types[cars.index(i['Номерной знак ТС'])]

        with open("data.json", 'w') as f:
            f.write(json.dumps(res))

        division_data = pd.read_json('data.json', orient='columns')

        if division_data.empty:
            return {'error': 'Подразделение не найдено'}

        # Вычисление метрик для данного подразделения
        penalty_sum = division_data['Штрафы'].sum()
        mileage_match = division_data['Данные путевых листов, пробег'].sum() / division_data['Данные телематики, пробег'].sum()
        
        # Уникальные ТС в подразделении
        unique_vehicles = division_data['Номерной знак ТС'].nunique()
        
        # Уникальные ТС в целевой структуре парка
        target_structure_vehicles = division_data[division_data['Тип закрепления'] == 'В целевой структуре парка']['Номерной знак ТС'].nunique()
        
        total_vehicle_ratio = unique_vehicles / target_structure_vehicles if target_structure_vehicles else 0
        
        most_used_vehicles = division_data['Номерной знак ТС'].value_counts().index[:3].tolist()
        least_used_vehicles = division_data['Номерной знак ТС'].value_counts().index[-3:].tolist()
        average_driving_style = division_data['манера вождения'].mean()

        # Формирование словаря с информацией о подразделении
        division_info = {
            'Название подразделения': name,
            'Сумма штрафов': penalty_sum,
            'Соотношение пробега': mileage_match,
            'Соотношение ТС': total_vehicle_ratio,
            'Топ-3 часто используемых ТС': most_used_vehicles,
            'Топ-3 редко используемых ТС': least_used_vehicles,
            'Средняя манера вождения': average_driving_style
        }

        return division_info

    def ai_efficiency_rating_division(self,name):
        if name==None:
            arr = []
            for i in self.get_values('Наименование структурного подразделения'):

                division_data = self.df[self.df['Наименование структурного подразделения'] == i]
                
                vehicle_numbers = division_data['Номерной знак ТС'].tolist()
                vehicle_types = division_data['Тип закрепления'].tolist()

                res = self.ai_vehicle_division_info(i, vehicle_numbers[:10], vehicle_types[:10])
                arr.append({i:self.calculate_efficiency_rating(res['Соотношение пробега'], res['Соотношение ТС'], res['Сумма штрафов'], res['Средняя манера вождения'])})
            return arr
        else:

            division_data = self.df[self.df['Наименование структурного подразделения'] == name]
            
            vehicle_numbers = division_data['Номерной знак ТС'].tolist()
            vehicle_types = division_data['Тип закрепления'].tolist()

            res = self.ai_vehicle_division_info(name, vehicle_numbers[:10], vehicle_types[:10])
            return {name:self.calculate_efficiency_rating(res['Соотношение пробега'], res['Соотношение ТС'], res['Сумма штрафов'], res['Средняя манера вождения'])}