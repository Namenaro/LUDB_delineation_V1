import math

from .one_CNN_get_activations_on_signal import get_activations_of_CNN_on_signal
from .one_CNN_activations_to_delineation import get_delineation_from_activation_by_mean
from settings import TOLERANCE

import numpy as np


def get_F1_of_one_CNN(trained_CNN, signals, true_delinations, threshold):
    """ signals - сигналы одно и того же отведения, разных пациентов"""

    pairs = []

    TP = 0
    FP = 0
    FN = 0

    dist_border = 700

    for i in range(len(signals)):

        signal = signals[i]
        true_delination = true_delinations[i]

        activations = get_activations_of_CNN_on_signal(trained_CNN, signal)
        delineation, weights = get_delineation_from_activation_by_mean(threshold, activations)

        program_labels = np.array([i for i in delineation if (i >= dist_border) and (i <= len(signal) - dist_border)])
        doctor_labels = np.array(
            [i for i in true_delination if (i >= dist_border) and (i <= len(signal) - dist_border)])

        if len(doctor_labels) == 0:
            continue

        TP_ = 0  # True Positives
        FP_ = 0  # False Positives
        FN_ = 0  # False Negatives

        # Копируем программную разметку, чтобы удалять использованные точки
        available_program_labels = program_labels.tolist()

        # Проверяем каждую точку докторской разметки
        for doctor_point in doctor_labels:
            # Находим ближайшую точку программной разметки в пределах толерантного окна
            min_distance = float('inf')
            closest_point = None

            for program_point in available_program_labels:
                distance = abs(program_point - doctor_point)
                if distance <= TOLERANCE and distance < min_distance:
                    min_distance = distance
                    closest_point = program_point

            # Если найдена ближайшая точка, фиксируем её как TP и удаляем из доступных
            if closest_point is not None:
                TP_ += 1
                pairs.append((doctor_point, closest_point))
                available_program_labels.remove(closest_point)
            else:
                FN_ += 1

        # Оставшиеся точки программной разметки считаем как FP
        FP_ = len(available_program_labels)

        TP += TP_
        FP += FP_
        FN += FN_

    # F1
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    F1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # mean_err
    total_distance = 0
    for doctor_point, program_point in pairs:
        distance = abs(doctor_point - program_point)
        total_distance += distance

    if len(pairs) != 0:
        mean_err = total_distance / len(pairs)
    else:
        mean_err = None

    return F1, mean_err


def get_F1_segmentation_of_one_CNN(trained_CNN, signals, true_delineations, threshold, seg_size):
    segments_with_wave = [signal for signal, delin in zip(signals, true_delineations) if delin == 1]

    TP = 0
    FP = 0
    FN = 0

    total_dist = []

    for i in range(len(segments_with_wave)):

        seg = segments_with_wave[i]
        activations = get_activations_of_CNN_on_signal(trained_CNN, seg)

        delineation, weights = get_delineation_from_activation_by_mean(threshold, activations)

        distances = []
        # проход по предсказанным точкам
        for program_point in delineation:

            distance = abs(program_point - seg_size - 1)
            # если предсказанная точка находится в рамках TOLERANCE, то записываем ее расстояние до истинной точки
            # иначе такая точка (вышедшая за пределы TOLERANCE) является FP
            if distance <= TOLERANCE:
                distances.append(distance)
            else:
                FP += 1

        #если в рамках TOLERANCE точки есть
        if len(distances) != 0:
            min_distance_in_tolerance = min(distances)
            total_dist.append(min_distance_in_tolerance)
            # сопоставлены истинная и предсказанная точки
            TP += 1
            FP += len(distances) - 1
        # если же точек в рамках TOLERANCE нет, то
        else:
            FN += 1

    # F1
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    F1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    mean_err = np.mean(total_dist)

    return F1, mean_err
