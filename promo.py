import requests

# =========================
# CONFIG (ENV VARS)
# =========================
TOKEN = "8574298516:AAGEmd-XZh5uyoTLtStrjVDSswSC106GksI"
CHAT_ID ="@promosdodiaAmazon"
    def enviar mensagem(texto):
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"    
        payload = {"chat_id": CHAT_ID, "text": texto} 
        response = requests.post(url, data=payload)
        print(response.text)

        nome_produto = "SSD Kingston 480GB"
        preco_produto = "R$ 299,90"
        link_produto = "https://www.amazon.com.br/Produto1"

        mensagem = f"""📢 Promoção do Dia! 📢

        📦 Produto: {nome_produto}
        💰 Preço: {preco_produto}
        🔗 Link: {link_produto}
        """

        enviar_mensagem(mensagem)