''' Tries its best to automatically batch-rename PDF files
    by extracting the student's name from them using OCR. '''

import atexit
import os
import re
from threading import Thread
import sys
from pdf2image import convert_from_path
import pytesseract
import wx

DEBUG_MODE = 'DEBUG' in os.environ and bool(os.environ['DEBUG'])

def exit_handler():
    ''' Prevents the app window from closing itself after execution finishes. (PyInstaller-only) '''
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        input('\n\nPressione a tecla <ENTER> para continuar...')

def dprint(*args, **kwargs):
    ''' Helper print function used for debugging. '''
    if DEBUG_MODE:
        print('DEBUG:', *args, file=sys.stderr, **kwargs)

def pdf_to_jpeg(pdf_path, poppler_path):
    ''' Converts only the first page of a PDF file to a JPEG image. '''
    jpegs = convert_from_path(pdf_path,
                               fmt='jpeg',
                               grayscale=True,
                               jpegopt={
                                   'quality': 100
                               },
                               last_page=1,
                               poppler_path=poppler_path,
                               thread_count=os.cpu_count())

    return jpegs[0]

def extract_all_text_from_jpeg(jpeg):
    ''' Extracts all text from a JPEG image using tesseract. '''

    return pytesseract.image_to_string(jpeg, lang='por')

def extract_student_name_from_text(text):
    ''' Bravely tries to extract a student's name from random text extracted
        by tesseract, using only a single regular expression!. '''

    # hic sunt dracones...
    student_name_regex = r'n?o?me:\s*(.+?)(?:(?:\n*i?RG\b)|(?:\s[lm]?atr[ií]?cula))'
    likely_student_name = re.search(student_name_regex, text, re.IGNORECASE)

    if likely_student_name is None:
        dprint('ERRO: Não foi possível extrair o nome do estudante... Ajustar a regex?')
        return None

    return likely_student_name.group(1)

def sanitize_student_name(name):
    ''' This will remove from a student's name:
        - Any non-latin character
        - Numbers
        - Two or more whitespaces
        Plus, all lowercase characters will be converted to uppercase. '''
    return re.sub(r'[^\w\s]|\s{2,}|[\d_]', '', name).upper().strip()

def fix_name_spelling(name):
    ''' Fixes common spelling mistakes in names, after extracting them with tesseract. '''
    fixes = {
        'MIQUEL': 'MIGUEL',
        'NOQUEIRA': 'NOGUEIRA',
        'RODRIQUES': 'RODRIGUES',
    }

    for wrong, correct in fixes.items():
        if name.find(wrong) > -1:
            dprint(f'Substituindo nome incorreto \'{wrong}\' por \'{correct}\'')
            name = name.replace(wrong, correct)

    return name

class HiddenFrame(wx.Frame):
    ''' Wrapper for wx.Frame. '''

    def __init__(self, parent):
        ''' It's very likely that doing it this way is cursed... '''
        wx.Frame.__init__(self, parent)
        # Spawns the main() function below in a separate thread, so that GUI events aren't blocked.
        t = Thread(target=self.main)
        t.run()

    def main(self):
        ''' The app's entry point. '''

        # We might use this to configure pdf2image correctly when running through PyInstaller
        poppler_path = None

        # Checks if the app is running through a PyInstaller package
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = getattr(sys, '_MEIPASS')
            # Configure pytesseract correctly.
            tesseract_bin = 'tesseract.exe' if sys.platform == 'win32' else 'tesseract'
            pytesseract.pytesseract.tesseract_cmd = os.path.join(base_path, tesseract_bin)
            # We'll forward this to pdf2image later
            poppler_path = base_path

        wx.MessageBox('Por favor, selecione a pasta onde estão os arquivos PDF.',
                      'Bem-vindo(a)!', wx.OK)

        while True:
            pdfs_dir = wx.DirSelector('Selecione a pasta dos PDFs')

            if pdfs_dir.strip():
                break

            answer = wx.MessageBox('Nenhuma pasta foi selecionada. Deseja sair?',
                                   'Sair?',
                                   wx.YES_NO | wx.ICON_WARNING | wx.CENTRE | wx.STAY_ON_TOP)
            if answer == wx.YES:
                self.Close()
                return

        success = 0
        failed = 0
        pdf_list = []

        with os.scandir(pdfs_dir) as it:
            for file in it:
                if not file.is_file() or not file.name.lower().endswith('.pdf'):
                    dprint(f'Ignorando arquivo desconhecido: {file.path}')
                    continue

                pdf_list.append(file.path)

        total = len(pdf_list)
        i = 1

        print(f'Encontrado {total} arquivos PDFs em \'{pdfs_dir}\'!\n')

        for pdf_path in pdf_list:
            print(f'[{i}/{total}] Arquivo PDF atual: {pdf_path}')

            print('Convertendo arquivo PDF para image JPEG...')
            jpeg = pdf_to_jpeg(pdf_path, poppler_path)

            if DEBUG_MODE:
                jpeg.save(os.path.splitext(pdf_path)[0] + '.jpg', 'JPEG')

            print('Extraindo todo texto da imagem JPEG...')
            text = extract_all_text_from_jpeg(jpeg)

            if DEBUG_MODE:
                text_file = os.path.splitext(pdf_path)[0] + '.txt'
                with open(text_file, 'w', encoding='utf-8') as file:
                    file.write(text)
                    file.close()
                    dprint(f'Escrevi o texto extraído deste arquivo PDF para \'{text_file}\'!')

            print('Extraindo nome do estudante do texto gerado pelo tesseract...')
            likely_student_name = extract_student_name_from_text(text)

            if likely_student_name is None:
                print('ERRO: Não foi possível extrair o nome do estudante!\n')
                failed += 1
                i += 1
                continue

            dprint(f'Nome extraído: {likely_student_name}')

            print('Removendo caracteres incompatíveis do nome extraído...')
            clean_student_name = fix_name_spelling(sanitize_student_name(likely_student_name))

            if clean_student_name == '':
                print('ERRO: Nome em branco após remover caracteres incompatíveis!\n')
                failed += 1
                i += 1
                continue

            print(f'Nome extraído da imagem JPEG: {clean_student_name}')

            old_name, old_ext = os.path.splitext(os.path.basename(pdf_path))
            old_file_number = None
            old_name_parts = re.search(r'(.+?)\s*\((\d+)\)\s*$', old_name, re.IGNORECASE)

            if old_name_parts:
                old_name = old_name_parts.group(1)
                old_file_number = int(old_name_parts.group(2))

            new_pdf_path = os.path.join(os.path.dirname(pdf_path), clean_student_name + old_ext)

            next_file = False
            correct_name = False
            counter = 1
            while True:
                if not os.path.exists(new_pdf_path):
                    break

                if old_file_number is None:
                    if old_name.upper() == clean_student_name:
                        correct_name = True
                else:
                    if counter == old_file_number:
                        correct_name = True

                if correct_name:
                    print('AVISO: Este arquivo PDF já está com o nome correto! :)\n')
                    next_file = True
                    break

                dprint('AVISO: Já existe um arquivo PDF com o nome',
                      f'\'{new_pdf_path}\', escolhendo outro...')

                new_pdf_path = os.path.join(os.path.dirname(pdf_path),
                                            clean_student_name + f' ({str(counter)})' + old_ext)
                counter += 1

            if next_file:
                success += 1
                i += 1
                continue

            print(f'Renomeando arquivo PDF \'{pdf_path}\' para \'{new_pdf_path}\'...')
            os.rename(pdf_path, new_pdf_path)
            print('Arquivo PDF renomeado com sucesso!\n')
            success += 1
            i += 1

        if success > 0 or failed > 0:
            print('\n--- Resumo: ---')
            print(f'{success} arquivos PDF renomeados com sucesso.')
            print(f'{failed} arquivos PDF com erro.')
            print('---------------')
            self.Close()
            sys.exit(0)
        else:
            print(f'ERRO: Nenhum arquivo PDF encontrado na pasta \'{pdfs_dir}\'!')
            self.Close()
            sys.exit(1)

if __name__ == '__main__':
    atexit.register(exit_handler)
    app = wx.App()
    frame = HiddenFrame(None)
    app.MainLoop()
