"""
    This module will convert a file into a pdf file and open it
"""
import platform
import subprocess


def convertToPdf(file_name : str, display = True) -> None:
    '''
        Convert a file to pdf using a libreOffice command\n
        Clear the terminal\n
        Open the previously created pdf

        - Args :
            - file_name (str) : file name with extension
    '''
    outdir = str()
    out_option = str()

    # If the file is in a subdirectory
    if "/" in file_name :
        outdir = '/'.join(file_name.split('/')[:-1])
        out_option = " --outdir " + outdir

    if platform.system() == "Linux" :
        subprocess.run('libreoffice --convert-to pdf ' + file_name + out_option, shell = True)
        if display :
            subprocess.run('clear', shell = True)
            subprocess.run('xdg-open ' + file_name.split('.')[0] + '.pdf', shell = True)
        
    elif platform.system() == "Windows" :
        subprocess.run('cd > path.txt', shell = True)
        with open("path.txt", "r") as fl :
            path = str(fl.readlines()[0][:-1])
        file_path = path
        path = '\"' + path + '\"'
        file_path += '/' + file_name
        file_path = '\"' + file_path + '\"'
        subprocess.run('"C:/Program Files/LibreOffice/program/soffice.exe" --convert-to pdf:writer_pdf_Export ' + file_path + ' --outdir ' + path + '/' + outdir)
        subprocess.run('del path.txt', shell = True)
        if display :
            subprocess.run('cls', shell = True)
            subprocess.run('start /B ' + file_name.split('.')[0] + '.pdf', shell = True)


if __name__ == "__main__" :
    convertToPdf(input("File to convert with its extension : "))
