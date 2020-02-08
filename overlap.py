import csv
import json
import os
from collections import OrderedDict

import numpy as np


def analyze(list1, list2):
    length1 = len(list1)
    length2 = len(list2)
    overlap_count = 0
    overlap_percent = 0
    di2_list = list()
    if length2 >= 1:
        for i in range(length1):
            for j in range(length2):
                url_1 = list1[i].replace("https://", "").replace("http://", "")
                url_2 = list2[j].replace("https://", "").replace("http://", "")
                if url_1.endswith("/"):
                    url_1 = url_1[:-1]
                if url_2.endswith("/"):
                    url_2 = url_2[:-1]
                if url_1.lower() == url_2.lower():
                    overlap_count += 1
                    di2_list.append((i - j) ** 2)
        overlap_percent = (overlap_count / 10) * 100
    return [overlap_count, overlap_percent, di2_list]


if __name__ == "__main__":
    ask_results_json_filename = "demo.txt"
    google_results_json_filename = 'google.txt'
    csv_output_filename = 'hw1.csv'
    if not os.path.exists(ask_results_json_filename) or not os.path.exists(google_results_json_filename):
        print("Results files not detected. Please retry.")
    else:
        with open(google_results_json_filename) as gj, open(ask_results_json_filename) as aj:
            google_dict = json.load(gj, object_pairs_hook=OrderedDict)
            ask_dict = json.load(aj, object_pairs_hook=OrderedDict)

        rows = list()
        counter = 0
        averages_list = np.zeros((100, 3))
        for key in google_dict.keys():
            counter += 1
            semi_result = analyze(google_dict[key], ask_dict[key])
            di2_sum = sum(semi_result[2])
            overlap_c = semi_result[0]
            denom = (overlap_c * (overlap_c ** 2 - 1))
            right_term = 0
            try:
                right_term = (6 * di2_sum) / denom
                spearman_coeff = 1 - right_term
            except ZeroDivisionError as ze:
                # see piazza @10 for explanation.
                if overlap_c == 1 and semi_result[2][0] == 0:
                    # case where n=1 (exactly one overlap) and google_rank == ask_rank
                    spearman_coeff = 1
                else:
                    # case when n=0 (zero overlaps) OR ( n=1 (exactly 1 overlap) and google_rank != ask_rank )
                    spearman_coeff = 0

            row = ['Query ' + str(counter), semi_result[0], semi_result[1], spearman_coeff]
            averages_list[counter - 1][0] = semi_result[0]
            averages_list[counter - 1][1] = semi_result[1]
            averages_list[counter - 1][2] = spearman_coeff
            rows.append(row)

        average = np.average(averages_list, axis=0)
        average_row = ['Averages', average[0], average[1], average[2]]
        with open(csv_output_filename, 'w') as csv_file:
            writer = csv.writer(csv_file)
            header_row = ["Queries", " Number of Overlapping Results", " Percent Overlap", " Spearman Coefficient"]
            writer.writerow(header_row)
            for row in rows:
                writer.writerow(row)
            writer.writerow(average_row)
        print("Finished generating CSV file.")