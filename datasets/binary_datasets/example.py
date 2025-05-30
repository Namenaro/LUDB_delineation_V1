# from datasets.binary_datasets import BinaryDataset
from datasets.binary_datasets.binary_dataset_creator import create_dataset_from_scratch
from datasets.binary_datasets.serialization import save_binary_dataset_to_file, load_binary_dataset_from_file
from settings import POINTS_TYPES, LEADS_NAMES
from paths import PATH_TO_LUDB

from pathlib import Path
import json

if __name__ == "__main__":
    from datasets.GUI import UIBinaryDataset

    # Открываем LUDB
    path_to_dataset = Path(PATH_TO_LUDB)
    with open(path_to_dataset, 'r') as file:
        LUDB_dataset = json.load(file)

    # Составляем свой датасет
    binary_dataset = create_dataset_from_scratch(point_name=POINTS_TYPES.QRS_PEAK,
                                                 radius=200,
                                                 lead_name=LEADS_NAMES.iii,
                                                 LUDB_dataset=LUDB_dataset,
                                                 dataset_size=5000
                                                 )
    step = 10
    binary_dataset.add_jitter(num_of_jitter_examples=200, jitter_range=(50, 29, -step))  # 1 - 2000

    # сохраняем в файл
    #name = binary_dataset.get_name()
    #save_binary_dataset_to_file(binary_dataset=binary_dataset, save_dir="SAVED_DATASETS")
    #del binary_dataset

    # загружаем из файла
    #binary_dataset = load_binary_dataset_from_file(name=name, save_dir="SAVED_DATASETS")

    # Листаем его в UI с визуализацией картинок
    binary_dataset_visualizator = UIBinaryDataset(binary_dataset)


    bin_datset_with_nigative = create_dataset_from_scratch(point_name=POINTS_TYPES.T_PEAK,
                                                 radius=200,
                                                 lead_name=LEADS_NAMES.ii,
                                                 LUDB_dataset=LUDB_dataset,
                                                 dataset_size=50
                                                )

    bin_datset_with_nigative.add_negative_examples(-20, 100, LUDB_dataset)

    bin_datset_with_nigative_visual = UIBinaryDataset(bin_datset_with_nigative)