import sys
import numpy as np
import cv2

def decodifica_mensagem(mensagem_binaria):
    assert len(mensagem_binaria) % 24 == 0, "O vetor de bits não é múltiplo de 24"
    mensagem_extraida = ""
    for i in range(0, len(mensagem_binaria), 24):
        c_bin = 0
        for j in range(24):
            c_bin = c_bin << 1
            c_bin += mensagem_binaria[i+j]
        mensagem_extraida += chr(c_bin)
    return mensagem_extraida

def extrai_vetor(imagem: np.ndarray, tamanho: int, canal=0):
    imagem_flattened = imagem.flatten()[:tamanho]
    imagem_flattened = (imagem_flattened & (1<<canal))>>canal
    return imagem_flattened

def decodificar(imagem_saida, bits, texto_saida):
    imagem = cv2.imread(imagem_saida)[:, :, ::-1]
    cabecalho_vetor = extrai_vetor(imagem, 24*4+32+8, bits)
    tamanho_maximo_por_plano = imagem.shape[0] * imagem.shape[1] * 3
    try:
        assinatura = decodifica_mensagem(cabecalho_vetor[:24*4])
    except:
        print("A imagem não contém uma mensagem no padrão NHS🐙 no canal inicial dado")
        return
    if assinatura != "NHS🐙":
        print("A imagem não contém uma mensagem no padrão NHS🐙 no canal inicial dado")
        return
    tamanho_mensagem = 0
    for i in range(32):
        tamanho_mensagem += cabecalho_vetor[24*4+i] << i
    bits = []
    for i in range(8):
        if cabecalho_vetor[24*4+32+i]:
            bits.append(i)
    pos = 24*4+32+8
    mensagem = []
    tamanhoAtual = 0
    for canal in bits:
        maximo = min(tamanho_mensagem-tamanhoAtual, tamanho_maximo_por_plano)
        tmp_message=extrai_vetor(imagem, tamanho_maximo_por_plano, canal)[pos:pos+maximo]
        mensagem.extend(tmp_message)
        tamanhoAtual += len(tmp_message)
        if tamanhoAtual >= tamanho_mensagem:
            break
        pos = 0
    mensagem = decodifica_mensagem(np.asarray(mensagem).flatten())
    #salva a mensagem no arquivo texto_saida
    with open(texto_saida, 'w', encoding="UTF-8") as f:
        f.write(mensagem)

def main():
    # recebe os parametros passados pela linha de comando
    # e chama a função que codifica o texto
    parametros = sys.argv
    if len(parametros) != 4:
        print("Os parametros corretos são: imagem_saida.png plano_bits texto_saida.txt")
        return 
    this, imagem_saida, plano_bits, texto_saida  = parametros
    decodificar(imagem_saida, int(plano_bits[0]), texto_saida)


if __name__ == "__main__":
    main()