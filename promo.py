import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
import requests
import time
import json
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

TOKEN = "8574398516:AAGEmd-XZh5uyoTLtStrjVDSswSC106Gksl"
CHAT_ID = "@promosdodiaAmazon"

enviados = set()


# =========================
# TELEGRAM
# =========================
def enviar_imagem(caminho, legenda):

    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    with open(caminho, "rb") as foto:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "caption": legenda
        }, files={"photo": foto})


# =========================
# DESCONTO REAL
# =========================
def calcular_desconto(preco_atual, preco_antigo):

    try:
        preco_atual = float(preco_atual.replace(".", "").replace(",", "."))
        preco_antigo = float(preco_antigo.replace(".", "").replace(",", "."))

        desconto = ((preco_antigo - preco_atual) / preco_antigo) * 100

        return round(desconto, 2)

    except:
        return 0


# =========================
# BANCO DE PREÇOS
# =========================
def carregar_precos():
    try:
        with open("precos.json", "r") as f:
            return json.load(f)
    except:
        return {}


def salvar_precos(dados):
    with open("precos.json", "w") as f:
        json.dump(dados, f)


# =========================
# GERAR IMAGEM
# =========================
def criar_imagem(nome, preco, desconto):

    img = Image.new("RGB", (800, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.text((20, 50), nome[:40], fill=(0, 0, 0))
    draw.text((20, 150), f"R$ {preco}", fill=(255, 0, 0))
    draw.text((20, 250), f"{desconto}% OFF", fill=(0, 150, 0))

    caminho = "promo.png"
    img.save(caminho)

    return caminho


# =========================
# BUSCAR OFERTAS (PLAYWRIGHT)
# =========================
def buscar_ofertas():

    with sync_playwright() as p:

        browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        page.goto("https://www.amazon.com.br/s?k=ssd")

        page.wait_for_timeout('[data-component-type="s-search-result"]')

        produtos = page.query_selector_all('[data-component-type="s-search-result"]')

        precos_salvos = carregar_precos()

        for produto in produtos[:10]:

            try:
                titulo = produto.query_selector("h2 span")
                preco = produto.query_selector(".a-price-whole")
                preco_antigo = produto.query_selector(".a-price.a-text-price span")
                link = produto.query_selector("a")

                if not titulo or not preco:
                    continue

                nome = titulo.inner_text()
                valor = preco.inner_text()

                url_produto = "https://amazon.com.br" + link.get_attribute("href") + "&tag=promosama0678-20"

                if url_produto in enviados:
                    continue

                enviados.add(url_produto)

                # =========================
                # MONITORAR PREÇO
                # =========================
                preco_atual_float = float(valor.replace(".", "").replace(",", "."))

                if url_produto in precos_salvos:
                    preco_antigo_salvo = precos_salvos[url_produto]

                    if preco_atual_float >= preco_antigo_salvo:
                        continue

                precos_salvos[url_produto] = preco_atual_float
                salvar_precos(precos_salvos)

                # =========================
                # DESCONTO
                # =========================
                desconto = 0

                if preco_antigo:
                    antigo = preco_antigo.inner_text()
                    desconto = calcular_desconto(valor, antigo)

                if desconto < 30:
                    continue

                # =========================
                # GERAR IMAGEM
                # =========================
                imagem = criar_imagem(nome, valor, desconto)

                mensagem = f"""
🔥 PROMOÇÃO IMPERDÍVEL

📦 {nome[:80]}

💰 R$ {valor}
📉 {desconto}% OFF

🛒 {url_produto}
"""

                enviar_imagem(imagem, mensagem)

                time.sleep(15)

            except Exception as e:
                print("Erro:", e)

        browser.close()


# =========================
# LOOP INFINITO
# =========================
if __name__ == "__main__":

    while True:

        print("Buscando promoções com Playwright...")

        buscar_ofertas()

        time.sleep(180)