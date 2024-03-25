import sys
import numpy as np
import cv2

def codifica_mensagem(mensagem: str):
    # Cria um vetor numpy com capacidade para 3 * 8 * len(mensagem) bits
    mensagem_binaria = np.zeros(3 * 8 * len(mensagem), dtype=bool)
    pos = 0
    for c in mensagem:
        # Converte o caracter para binário
        c_bin = ord(c)
        mascara = 0x800000 # 1000 0000 0000 0000 0000 0000, coleta apenas o bit mais significativo
        for i in range(24):
            mensagem_binaria[pos] = (c_bin & mascara)>0
            c_bin = c_bin << 1
            pos += 1
    return mensagem_binaria

def cabecalho(tamanho_msg, canal_bits: list):
    assinatura = "NHS🐙"
    assinatura_bin = codifica_mensagem(assinatura)
    tamanho_bin = np.zeros(32, dtype=bool)
    for i in range(32):
        tamanho_bin[i] = (tamanho_msg & (1 << i)) > 0
    canal_bits_bin = np.zeros(8, dtype=bool) # 1010 0000 usa o primeiro e o terceiro bit
    for i in range(8):
        canal_bits_bin[i] = (i in canal_bits)
    return np.concatenate((assinatura_bin, tamanho_bin, canal_bits_bin))

def insere_vetor(imagem: np.ndarray, vetor: np.ndarray, canal=0):
    formato_inicial = imagem.shape
    imagem_flattened = imagem.flatten()
    vetor = vetor.astype(np.uint8)
    # faz a mascara ser uint8
    mascara = ~(1<<canal)
    mascara = np.array(mascara).astype(np.uint8)

    #mostra o tipo do vetor numpy imagem_flattened
    imagem_flattened[:len(vetor)] &= mascara
    imagem_flattened[:len(vetor)] |= (vetor<<canal)
    return imagem_flattened.reshape(formato_inicial)

def codificar(imagem_entrada, texto_entrada, plano_bits, imagem_saida):
    imagem = cv2.imread(imagem_entrada)[:, :, ::-1]
    if type(texto_entrada) == str:
        if texto_entrada[-4:] == ".txt":
            with open(texto_entrada, 'r', encoding="UTF-8") as f:
                vetor_mensagem = codifica_mensagem(f.read())
        else:
            vetor_mensagem = codifica_mensagem(texto_entrada)
    else:
        raise Exception("Outros formatos de imagem não são suportados")
    tamanho_maximo_por_plano = imagem.shape[0] * imagem.shape[1] * 3
    tamanho_mensagem = len(vetor_mensagem)
    assert type(plano_bits) == list, "Os planos bits devem ser uma lista"
    assert type(plano_bits[0]) == int, "Os planos bits devem ser uma lista de inteiros"
    assert len(plano_bits) > 0, "Os planos bits devem ter pelo menos um plano"
    assert max(plano_bits) < 8, "Os planos bits devem ser menores que 8"
    assert min(plano_bits) >= 0, "Os planos bits devem ser maiores ou iguais a 0"
    tamanhoLimiteDaMensagem = tamanho_maximo_por_plano*len(plano_bits)-136
    assert tamanho_mensagem <= tamanhoLimiteDaMensagem, f"A mensagem é muito grande para ser escondida na imagem. O tamanho máximo é {tamanhoLimiteDaMensagem} bits e a mensagem tem {tamanho_mensagem} bits."
    # A partir daqui, é garantido que a mensagem cabe na imagem.
    vetor_cabecalho = cabecalho(tamanho_mensagem, plano_bits)
    vetor_completo = np.concatenate((vetor_cabecalho, vetor_mensagem))
    pos = 0
    for canal in plano_bits:
        posMaxima = pos + tamanho_maximo_por_plano
        extourou = False
        if posMaxima >= len(vetor_completo):
            extourou = True
            posMaxima = len(vetor_completo)
        imagem = insere_vetor(imagem, vetor_completo[pos:posMaxima], canal)
        pos += tamanho_maximo_por_plano
        if extourou:
            break
    cv2.imwrite(imagem_saida, imagem[:, :, ::-1])


def main():
    # recebe os parametros passados pela linha de comando
    # e chama a função que codifica o texto
    parametros = sys.argv
    if len(parametros) != 5:
        print("Os parametros corretos são: imagem_entrada.png texto_entrada.txt plano_bits imagem_saida.png")
        return 
    this, imagem_entrada, texto_entrada, plano_bits, imagem_saida = parametros
    codificar(imagem_entrada, texto_entrada, [int(bit) for bit in plano_bits], imagem_saida)


if __name__ == "__main__":
    main()