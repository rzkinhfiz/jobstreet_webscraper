from playwright.async_api import async_playwright
import asyncio
import random

async def debug_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Headless=False biar kelihatan
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            locale="id-ID",
        )
        page = await context.new_page()
        
        url = "https://id.jobstreet.com/data-scientist-jobs/in-Jakarta-Raya"
        print(f"Membuka: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Tunggu agak lama
        await asyncio.sleep(5)
        
        # Scroll gradual
        for _ in range(6):
            await page.evaluate("window.scrollBy(0, 700)")
            await asyncio.sleep(random.uniform(1.2, 2.5))
        
        # Ambil jumlah elemen penting
        job_cards = await page.query_selector_all('div[data-search-sol-meta]')
        print(f"✅ Jumlah job card ditemukan: {len(job_cards)}")
        
        title_count = await page.query_selector_all(
            'a[data-automation="jobTitle"], a[data-testid="job-card-title"], [data-automation="jobTitle"]'
        )
        print(f"✅ Jumlah job title: {len(title_count)}")
        
        salary_count = await page.query_selector_all(
            '[data-automation="jobSalary"], [data-automation*="salary"], [aria-label^="Salary"]'
        )
        print(f"✅ Jumlah elemen salary: {len(salary_count)}")
        
        # Save untuk analisis
        await page.screenshot(path="DEBUG_FULL_PAGE.png", full_page=True)
        content = await page.content()
        with open("DEBUG_PAGE.html", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("📸 Screenshot & HTML sudah disimpan")
        print("Buka file DEBUG_PAGE.html dan DEBUG_FULL_PAGE.png")
        
        await asyncio.sleep(30)  # Biar bisa lihat manual
        await browser.close()

asyncio.run(debug_page())