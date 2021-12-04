import os, shutil
import zipfile
import patoolib
import pandas as pd
import datetime
import tracemalloc
import gc
from multiprocessing import Process

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_assignments(filename):
    path = "./assignment/" + filename
    if filename.endswith(".zip"):
        with zipfile.ZipFile(path) as zip_file:
            zip_file.extractall("./assignment")
    else:
        patoolib.extract_archive(path, outdir="./assignment")
    os.remove(path)
    # print(os.listdir("./assignment"))

    for file_name in os.listdir('./assignment'):
        path = "./assignment/" + file_name
        # print(path)
        if file_name.endswith(".zip"):
            with zipfile.ZipFile(path) as zip_file:
                zip_file.extractall("./assignment")
            os.remove(path)
        elif file_name.endswith(".rar"):
            patoolib.extract_archive(path, outdir="./assignment")
            os.remove(path)
    # print(os.listdir("./assignment"))

def get_paths_and_files_content():
    files_content = []
    root = './assignment'
    paths = []
    for i in os.listdir(root):
        p = os.path.join(root, i)
        if os.path.isdir(p):
            path = os.path.join(p, "assignment.py")
            with open(path, encoding="utf8") as file:
                paths.append(i)
                files_content.append(file.read())
    return paths, files_content

def vectorize(text):
    return TfidfVectorizer().fit_transform(text).toarray()

def get_paths_and_vectors(paths, files_content):
    paths_vectors = list(zip(paths, vectorize(files_content)))
    return paths_vectors

def check_plag(paths_vectors):
    report = []
    for i in range(len(paths_vectors)):
        for j in range(i, len(paths_vectors)):
            vector_1 = paths_vectors[i][1]
            vector_2 = paths_vectors[j][1]
            score = round(cosine_similarity([vector_1, vector_2])[0][1]*100, 3)
            report.append((paths_vectors[i][0], paths_vectors[j][0], score))
    return report

def check_plagiarism():
    return check_plag(get_paths_and_vectors(*get_paths_and_files_content()))

def generate_plag_report():
    result = check_plagiarism()
    print("result: ", result)
    temp = {}
    for i in result:
        if i[0] in temp.keys():
            temp[i[0]].append(i[2])
        else:
            temp[i[0]] = [i[2]]
        if i[0] == i[1]:
            continue
        if i[1] in temp.keys():
            temp[i[1]].append(i[2])
        else:
            temp[i[1]] = [i[2]]
    # print(temp)
    df = pd.DataFrame(temp, index=temp.keys())
    # print(df)
    df.to_csv("./report/plagiarism report.csv")

def clean_assignment_dir():
    folder = './assignment'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def clean_reports_dir():
    folder = './report'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def get_directories():
    root = './assignment'
    directories = []
    for i in os.listdir(root):
        path = os.path.join(root, i)
        if os.path.isdir(path):
            directories.append(i)
    return directories

def test_function(test_cases, directories, log=False, plag=False):
    result = {}
    size = {}
    for t in test_cases:
        func = t[0]
        params = t[1]
        expected = t[2]
        marks = t[3]
        # if func not in size.keys():
        for d in directories:
            if plag:
                if d not in size.keys():
                    size[d] = {}
                else:
                    if func not in size[d].keys():
                        size[d][func] = 0
            score = 0
            
            i = __import__("assignment." + d+'.assignment')
            # print(dir())
            # print(getattr(getattr(i, d), "assignment"))
            function = getattr(getattr(getattr(i, d), "assignment"), func)
            value = None
            try:
                p = Process(target=function, args=(params))
                p.start()
                p.join(timeout=10)
                p.terminate()
                if p.exitcode is None:
                    raise Exception("The Function took too long to compute.")
                if plag:
                    tracemalloc.start()
                value = function(*params)
                if plag:
                    current, peak = tracemalloc.get_traced_memory()
                    gc.collect()
                    size[d][func] += current
            except Exception as e:
                if log == True:
                    create_log(d, str(e))
            if value == expected:
                score = marks
            else:
                if log == True:
                    error_msg = f"Expected {{ {expected} }} but got {{ {value} }} on parameter {{{params}}}"
                    create_log(d, error_msg)
            # print(d, function(*params), value == expected)
            if d in result.keys():
                if func in result[d].keys():
                    result[d][func] += score
                else:
                    result[d][func] = score
            else:
                result[d] = {func:score}
    if plag:
        tracemalloc.stop()
        size = change_format(size)
        diff = diff_size(size)
        pd.DataFrame(diff).to_csv("./report/memory plagiarism.csv")
    pd.DataFrame(result).T.to_csv("./report/evaluated report.csv")
    return pd.DataFrame(result).T

def diff_size(size):
    result = {}
    for k,v in size.items():
        for i in range(len(v)):
            for j in range(i+1, len(v)):
                f1 = v[i][1]
                f2 = v[j][1]
                score = difference_percentage(f1,f2)
                if score < 5.0:
                    s1 = v[i][0]
                    s2 = v[j][0]
                    if k not in result.keys():
                        result[k] = [(s1, s2, round(100 - score, 4))]
                    else:
                        result[k].append((s1, s2, round(100 - score, 4)))
    return result

def change_format(size):
    temp = {}
    for k, v in size.items():
        for key in v.keys():# keys --> factorial, ...
            if key not in temp.keys():
                temp[key] = [(k, v[key])]
            else:
                temp[key].append((k, v[key]))
    return temp

def difference_percentage(f1,f2):
    return abs(f1-f2)/((f1+f2)/2) * 100

def create_log(roll_num, error_msg):
    # formating the current local time
    date_time = datetime.datetime.now().strftime("%b-%d-%y %H:%M:%S")
    # create assignment log file
    msg = f"[{date_time}] [{roll_num}] " + error_msg + "\n"
    with open("./log/"+str(roll_num)+".log", "a") as log_file:
        log_file.write(msg)
        
def archive(val):
    if val == "log":
        shutil.make_archive("./report/log", 'zip', "./log")
        shutil.rmtree("./log")
    if val == "reports":
        shutil.make_archive("./reports/reports", 'zip', "./report")
        shutil.rmtree("./report")
        shutil.rmtree("./assignment")
        
if __name__ == "__main__":
    # test_function(get_test_cases(1), get_directories())
    # print(check_plagiarism())
    # generate_plag_report()
    """ 
    test_cases = [
        ['factorial', [5], 120],
        ['factorial', [12], zxklcjvlzxcjv],
    ]
     """
    clean_reports_dir()