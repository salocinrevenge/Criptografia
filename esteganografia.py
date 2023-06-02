from PIL import Image
import wave
import struct
import os

def change(numero, bits):
    temp = 0
    for i in range(bits):
        temp = temp << 1
        temp |= numero & 1
        numero = numero >> 1
    return temp

def escreverPalavra(palavra, vetor, pos, reversed):
    for letra in palavra:
        nletra = ord(letra)
        for _ in range(16):
            if (nletra & 1) == 1:
                vetor[pos] |= 1
            else:
                vetor[pos] &= ~1
            pos += 1
            if reversed:
                pos -=2
            nletra = nletra >> 1
    return vetor, pos

def escreverNumero(numero, vetor, pos, reversed):
    for _ in range(32):
        if (numero & 1) == 1:
            vetor[pos] |= 1
        else:
            vetor[pos] &= ~1
        pos += 1
        if reversed:
            pos -=2
        numero = numero >> 1
    return vetor, pos

def lerPalavra(vetor, tamanho, pos, reversed):
    palavra = ""
    for _ in range(tamanho):
        letra = 0
        for _ in range(16):
            letra = letra << 1
            if (vetor[pos] & 1) == 1:
                letra |= 1
            pos += 1
            if reversed:
                pos -=2
        palavra += chr(change(letra,16))
    return palavra, pos

def lerNumero(vetor, pos, reversed):
    numero = 0
    for _ in range(32):
        numero = numero << 1
        if (vetor[pos] & 1) == 1:
            numero |= 1
        pos += 1
        if reversed:
            pos -=2
    return change(numero,32), pos

def esconderImagem(image_path, reversed = False):
    # Abrir a imagem
    img = Image.open(image_path)

    # Converter a imagem para o modo "RGB"
    img = img.convert('RGB')

    # Obtem formato da imagem
    image_size = img.size

    # Obter os pixels da imagem como uma lista de tuplas (R, G, B)
    pixels = list(img.getdata())

    # Converter a lista de tuplas em um vetor de números inteiros
    vector = [value for pixel in pixels for value in pixel]

    while True:
        mensagem = input("Digite a mensagem a ser escondida: ")
        
        if 32+ len(mensagem)*16+ 7*16 > len(vector):
            print("Mensagem muito grande para o arquivo!")
            continue
        break
    #a mensagem tera cada letra com tamanho maximo de 16 bits
    tamanho = len(mensagem)
    # a mensagem tera tamanho maximo de um numero que caiba em 32 bits
    assinatura = "NHS#Est"

    pos = 0
    if reversed:
        pos = len(vector)-1

    vector, pos = escreverPalavra(assinatura, vector, pos, reversed)

    vector, pos = escreverNumero(tamanho, vector, pos, reversed)

    vector, pos = escreverPalavra(mensagem, vector, pos, reversed)

    # Criar uma nova imagem com o tamanho especificado
    img = Image.new('RGB', image_size)

    # Preencher a imagem com os pixels do vetor
    img.putdata([(vector[i], vector[i+1], vector[i+2]) for i in range(0, len(vector), 3)])

    # Salvar a imagem no caminho de saída especificado
    img.save(input("Indique o nome do arquivo de saída com sua extensão\n"))


def lerImagem(image_path, reversed = False):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = list(img.getdata())
    vector = [value for pixel in pixels for value in pixel]
    
    pos = 0
    if reversed:
        pos = len(vector)-1
    assinatura, pos = lerPalavra(vector, len("NHS#Est"), pos, reversed)
    if assinatura != "NHS#Est":
        print("Arquivo nao contem mensagem!")
        return
    
    tamanho, pos = lerNumero(vector, pos, reversed)
    
    mensagem, pos = lerPalavra(vector, tamanho, pos, reversed)
    
    return mensagem





def esconderSom(entrada):
    # Abre o arquivo de áudio em formato WAV
    with wave.open(entrada, 'rb') as audio_file:
        # Obtém os parâmetros do arquivo de áudio
        n_channels = audio_file.getnchannels()
        sample_width = audio_file.getsampwidth()
        frame_rate = audio_file.getframerate()
        n_frames = audio_file.getnframes()
        audio_data = audio_file.readframes(n_frames)

        # Converte os valores da onda do áudio em uma lista de inteiros
        audio_samples = list(struct.unpack_from("<{}h".format(n_frames * n_channels), audio_data))

        mensagem = input("Digite a mensagem a ser escondida: ")
        #a mensagem tera cada letra com tamanho maximo de 16 bits
        tamanho = len(mensagem)
        # a mensagem tera tamanho maximo de um numero que caiba em 32 bits
        assinatura = "NHS#Est"

        pos = 0

        audio_samples, pos = escreverPalavra(assinatura, audio_samples, pos)

        audio_samples, pos = escreverNumero(tamanho, audio_samples, pos)

        audio_samples, pos = escreverPalavra(mensagem, audio_samples, pos)

        # Converte os valores da onda do áudio de volta para bytes
        audio_data = struct.pack("<{}h".format(n_frames * n_channels), *audio_samples)

    # Escreve os dados manipulados em um novo arquivo de áudio
    with wave.open(input("Indique o nome do arquivo de saída com sua extensão\n"), 'wb') as audio_file:
        audio_file.setnchannels(n_channels)
        audio_file.setsampwidth(sample_width)
        audio_file.setframerate(frame_rate)
        audio_file.writeframes(audio_data)


def lerSom(path):
    with wave.open(path, 'rb') as audio_file:
        # Obtém os parâmetros do arquivo de áudio
        n_channels = audio_file.getnchannels()
        sample_width = audio_file.getsampwidth()
        frame_rate = audio_file.getframerate()
        n_frames = audio_file.getnframes()
        audio_data = audio_file.readframes(n_frames)

        # Converte os valores da onda do áudio em uma lista de inteiros
        audio_samples = list(struct.unpack_from("<{}h".format(n_frames * n_channels), audio_data))
        pos = 0
        assinatura, pos  = lerPalavra(audio_samples, 7, pos)

        if assinatura != "NHS#Est":
            print("Arquivo nao contem mensagem!")
            return
        
        tamanho, pos = lerNumero(audio_samples, pos)

        mensagem, pos = lerPalavra(audio_samples, tamanho, pos)

        return mensagem
        




def hub():
    while True:
        try:
            opcao = int(input("Selecione uma opcao: 1 esconder uma mensagem em um arquivo de audio ou imagem\n"))
        except ValueError:
            print("Opcao invalida! Responde direito seu animal!")
            continue
        match opcao:
            case 1:
                entrada = input("Indique o nome do arquivo com sua extensão\n")
                if not os.path.exists(entrada):
                    print("Arquivo não encontrado!")
                    continue

                match os.path.splitext(entrada)[1]:
                    case ".wav":
                        esconderSom(entrada)

                    case ".png" | ".bmp" | ".gif":
                        esconderImagem(entrada)
                    case _:
                        print("A extensão do arquivo não é suportada! \n Apenas .wav, .png, .bmp, .gif")
                        continue

                break
            case 2:

                entrada = input("Indique o nome do arquivo com sua extensão\n")
                if not os.path.exists(entrada):
                    print("Arquivo não encontrado!")
                    continue

                match os.path.splitext(entrada)[1]:
                    case ".wav":
                        mensagem = lerSom(entrada)

                    case ".png" | ".bmp" | ".gif":
                        mensagem = lerImagem(entrada)
                    case _:
                        print("A extensão do arquivo não é suportada! \n Apenas .wav, .png, .bmp, .gif")
                        continue
                if mensagem != None:
                    print("A mensagem é:\n", mensagem)
                break
            case _:
                print("instrucao invalida!")
                continue

hub()