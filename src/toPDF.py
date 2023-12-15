"""
    This module will convert a file into a pdf file and open it
"""
import platform
import subprocess


def convertToPdf(fileName : str, display = True) -> None:
    '''
        Convert a file to pdf using a libreOffice command\n
        Clear the terminal\n
        Open the previously created pdf

        - Args :
            - filename (str) : file name with extension
    '''
    if platform.system() == "Linux" :
        subprocess.run('libreoffice --convert-to pdf ' + fileName, shell = True)
        if display :
            subprocess.run('clear', shell = True)
            subprocess.run('xdg-open ' + fileName.split('.')[0] + '.pdf', shell = True)
        
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
        if display :
            subprocess.run('cls', shell = True)
            subprocess.run('start /B ' + fileName.split('.')[0] + '.pdf', shell = True)


if __name__ == "__main__" :
    convertToPdf(input("File to convert with its extension : "))
