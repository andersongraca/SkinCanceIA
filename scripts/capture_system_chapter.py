from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path("/home/ubuntu/work/SkinCanceIA")
OUT = ROOT / "docs" / "chapter-system" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

APP_URL = "http://127.0.0.1:3011/"
HAM_IMAGE = ROOT / "docs" / "chapter-system" / "assets" / "ham10000_isic_0027419.jpg"
OOD_IMAGE = ROOT / "docs" / "chapter-system" / "assets" / "ood_car_public_domain.jpg"


def capture_locator(page, title: str, output_name: str) -> None:
    locator = page.get_by_text(title, exact=True).first.locator("xpath=ancestor::*[contains(@class,'rounded') or contains(@class,'Card')][1]")
    if locator.count() == 0:
        locator = page.get_by_text(title, exact=True).first.locator("xpath=ancestor::div[1]")
    locator.scroll_into_view_if_needed()
    page.wait_for_timeout(400)
    locator.screenshot(path=str(OUT / output_name))


def main() -> None:
    evidence: dict[str, object] = {"app_url": APP_URL, "screenshots": []}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        page = context.new_page()
        page.goto(APP_URL, wait_until="networkidle", timeout=60_000)
        page.get_by_text("Upload de imagem dermatoscópica", exact=True).wait_for(timeout=30_000)
        page.screenshot(path=str(OUT / "01_upload_initial.png"), full_page=True)
        evidence["screenshots"].append("01_upload_initial.png")

        page.locator("input[type=file]").set_input_files(str(HAM_IMAGE))
        page.get_by_text("Iniciar análise de câncer", exact=True).wait_for(timeout=10_000)
        page.screenshot(path=str(OUT / "02_upload_preview_ham10000.png"), full_page=True)
        evidence["screenshots"].append("02_upload_preview_ham10000.png")

        page.get_by_text("Iniciar análise de câncer", exact=True).click()
        page.wait_for_timeout(2_500)
        page.screenshot(path=str(OUT / "03_processing_pipeline.png"), full_page=True)
        evidence["screenshots"].append("03_processing_pipeline.png")

        page.get_by_text("Resultado da classificação", exact=True).wait_for(timeout=180_000)
        page.wait_for_timeout(1_000)
        page.screenshot(path=str(OUT / "04_result_full.png"), full_page=True)
        evidence["screenshots"].append("04_result_full.png")

        model_section = page.get_by_text("Análise detalhada por modelo", exact=True).locator("xpath=ancestor::*[contains(@class,'rounded')][1]")
        model_section.scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        model_section.screenshot(path=str(OUT / "05_model_cards.png"))
        evidence["screenshots"].append("05_model_cards.png")

        xai_section = page.get_by_text("Mapas de explicabilidade", exact=True).locator("xpath=ancestor::*[contains(@class,'rounded')][1]")
        xai_section.scroll_into_view_if_needed()
        page.wait_for_timeout(800)
        xai_section.screenshot(path=str(OUT / "06_xai_heatmaps_grid.png"))
        evidence["screenshots"].append("06_xai_heatmaps_grid.png")

        page.get_by_role("tab", name="Histórico").click()
        page.get_by_text("Histórico de diagnósticos", exact=True).wait_for(timeout=20_000)
        page.screenshot(path=str(OUT / "07_history.png"), full_page=True)
        evidence["screenshots"].append("07_history.png")

        page.get_by_role("tab", name="Métricas").click()
        page.get_by_text("Métricas de desempenho dos modelos", exact=True).wait_for(timeout=20_000)
        page.wait_for_timeout(1_000)
        page.screenshot(path=str(OUT / "08_metrics_dashboard.png"), full_page=True)
        evidence["screenshots"].append("08_metrics_dashboard.png")

        page.goto(APP_URL, wait_until="networkidle", timeout=60_000)
        page.locator("input[type=file]").set_input_files(str(OOD_IMAGE))
        page.get_by_text("Iniciar análise de câncer", exact=True).click()
        page.get_by_text("Imagem rejeitada antes da classificação", exact=True).wait_for(timeout=60_000)
        page.wait_for_timeout(600)
        page.screenshot(path=str(OUT / "09_ood_rejection.png"), full_page=True)
        evidence["screenshots"].append("09_ood_rejection.png")

        browser.close()

    (OUT / "capture_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
