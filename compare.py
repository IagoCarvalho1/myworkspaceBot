import requests  # importa a biblioteca para fazer requisições HTTP
from playwright.sync_api import sync_playwright

TOKEN = "8574298516:AAGEmd-XZh5uyoTLtStrjVDSswSC106GksI"
CHAT_ID = "@promosdodiaAmazon"


def enviar_mensagem(texto):  # função que recebe um texto
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID,
               "text": texto}
    response = requests.post(url, data=payload)
    print("Status Telegram:", response.status_code)
    print("Resposta Telegram:", response.text)

    def buscar_primeiro_produto():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto("https://www.amazon.com.br/s?k=teclado+gamer", wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            produto = page.locator('[data-component-type="s-search-result"]').first

            nome = produto.locator("h2 span").inner_text()
            preco = produto.locator(".a-price-whole").first.inner_text()
            link = produto.locator("h2 a").get_attribute("href")

            if link and link.startswith("/"):
                link = "https://www.amazon.com.br" + link

            browser.close()

            return {
                "nome": nome,
                "preco": f"R$ {preco}",
                "link": link
            }

    produto = buscar_primeiro_produto()

    mensagem = f"""🔥 Promoção encontrada!

📦 Produto: {produto["nome"]}
💰 Preço: {produto["preco"]}
🔗 Link: {produto["link"]}
"""

    enviar_mensagem(mensagem)
