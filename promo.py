import requests  # importa a biblioteca para fazer requisições HTTP
import json
from playwright.sync_api import sync_playwright

TOKEN = "8574298516:AAGEmd-XZh5uyoTLtStrjVDSswSC106GksI"
CHAT_ID = "@promosdodiaAmazon"
AFFLILIATE_TAG = "promosama0678-20"



def buscar_varios_produtos():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=300
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="pt-BR"
        )

        page = context.new_page()

        page.goto(
            "https://www.amazon.com.br/s?k=teclado+gamer",
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(10000)

        print("Título da página:", page.title())
        print("URL atual:", page.url)

        produtos = page.locator('[data-component-type="s-search-result"]')
        qtd = produtos.count()
        produtos_validos = []
        print("Quantidade de resultados encontrados:", qtd)

        if qtd == 0:
            print("Nenhum produto encontrado.")
            page.screenshot(path="debug_amazon.png")
            browser.close()
            return None

        produto = produtos.first
        for i in range(min(qtd, 10)):
            produto = produtos.nth(i)
            print(f"\nTestando produto {i + 1}...")
            try:
                nome = produto.locator("h2 span").first.inner_text(timeout=10000)
            except:
                nome = None

            try:
                preco = produto.locator("span.a-price > span.a-offscreen").first.inner_text(timeout=10000)
            except:
                preco = None

            link = None

            try:
                links = produto.locator("a").evaluate_all(
                    "(els) => els.map(a => a.getAttribute('href')).filter(Boolean)"
                )

                for href in links:
                    if href and "/dp/" in href:
                        link = href
                        break
            except:
                link = None

            if link and link.startswith("/"):
                link = "https://www.amazon.com.br" + link
            if link and "tag=" not in link:
                separador = "&" if "?" in link else "?"
                link = f"{link}{separador}tag={AFFLILIATE_TAG}"

            print("Nome:", nome)
            print("Preço:", preco)
            print("Link:", link)

            if nome and preco and link:
                produtos_validos.append({
                    "nome": nome,
                    "preco": preco,
                    "link": link
                })

        browser.close()
        return produtos_validos

def carregar_enviados():
    try:
        with open("enviados.json", "r") as f:
            return set(json.load(f))
    except:
        return set()

def salvar_enviados(enviados):
    with open("enviados.json", "w") as f:
        json.dump(list(enviados), f)

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    response = requests.post(url, data=payload)
    print("Status Telegram:", response.status_code)
    print("Resposta Telegram:", response.text)

produtos = buscar_varios_produtos()

if not produtos:
    print("Não foi possível capturar produtos.")
else:
    enviados = carregar_enviados()

    for produto in produtos:
        if produto["link"] in enviados:
            print("Produto já enviado:", produto["link"])
            continue

        mensagem = f"""🚨 Promoção na Amazon!

            📦 {produto['nome']}
            💰 {produto['preco']}
            🔗 {produto['link']}
            ⚠️ Corre que o preço pode mudar!
        """
        enviar_mensagem(mensagem)
        enviados.add(produto["link"])
        salvar_enviados(enviados)
