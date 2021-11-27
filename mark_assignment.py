import os, shutil
import zipfile
import patoolib

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
        print(path)
        if file_name.endswith(".zip"):
            with zipfile.ZipFile(path) as zip_file:
                zip_file.extractall("./assignment")
            os.remove(path)
        elif file_name.endswith(".rar"):
            patoolib.extract_archive(path, outdir="./assignment")
            os.remove(path)
    # print(os.listdir("./assignment"))

# extract_assignments("assignments.rar")

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

# print(get_paths_and_files_content())
def vectorize(text):
    return TfidfVectorizer().fit_transform(text).toarray()

def get_paths_and_vectors(paths, files_content):
    paths_vectors = list(zip(paths, vectorize(files_content)))
    return paths_vectors


def check_plag(paths_vectors):
    report = []
    for i in range(len(paths_vectors)):
        for j in range(i+1, len(paths_vectors)):
            vector_1 = paths_vectors[i][1]
            vector_2 = paths_vectors[j][1]
            score = round(cosine_similarity([vector_1, vector_2])[0][1]*100, 3)
            report.append((paths_vectors[i][0], paths_vectors[j][0], score))
    return report

# print(get_paths_and_files_content())
# print(check_plag(get_paths_and_vectors(*get_paths_and_files_content())))

def check_plagiarism():
    print(check_plag(get_paths_and_vectors(*get_paths_and_files_content())))

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