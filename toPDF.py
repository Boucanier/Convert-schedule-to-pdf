"""
    This module will convert a file into a pdf file and open it
"""
import platform
import subprocess
import os

def convertToPdf(fileName : str) -> None:
    path = str(os.path.dirname(__file__))
    '''
        Convert a file to pdf using a libreOffice command\n
        Clear the terminal\n
        Open the previously created pdf

        - Args :
            - filename (str) : file name with extension
    '''
    if platform.system() == "Linux" :
        subprocess.run('mv ' +  fileName + ' ' + path + '/' + fileName, shell = True)
        subprocess.run('libreoffice --convert-to pdf ' + path + '/'+ fileName + ' --outdir ' + path, shell = True)
        subprocess.run('clear', shell = True)
        subprocess.run('xdg-open ' + path + "/" + fileName.split('.')[0] + '.pdf', shell = True)
        
    elif platform.system() == "Windows" :
        subprocess.run('cd > path.txt', shell = True)
        with open("path.txt", "r") as fl :
            path = str(fl.readlines()[0][:-1])
        file_path = path
        path = '\"' + path + '\"'
        file_path += '/' + fileName
        file_path = '\"' + file_path + '\"'
        subprocess.run('"C:/Program Files/LibreOffice/program/soffice.exe" --convert-to pdf:writer_pdf_Export ' + file_path + ' --outdir ' + path)
        subprocess.run('del path.txt', shell = True)
        subprocess.run('cls', shell = True)
        subprocess.run('start /B ' + fileName.split('.')[0] + '.pdf', shell = True)


if __name__ == "__main__" :
    convertToPdf(input("File to convert with its extension : "))
