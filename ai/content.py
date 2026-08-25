from __future__ import annotations

from providers.meesho import Product


def build_script(product: Product) -> str:
    """Deterministic fallback script; AI provider can replace this later."""
    return (
        f"Aaj ka product: {product.title}. "
        f"Price lagbhag ₹{product.price_inr:.0f} hai. "
        "Product details check karke hi purchase karein. "
        "Link ke liye bio ya available CTA dekhein."
    )


def build_video_prompt(product: Product, script: str) -> str:
    return (
        "Create a vertical 9:16 short-form product showcase. "
        "Use the supplied product reference images and preserve the product's "
        "appearance accurately. Do not invent logos, claims, discounts, or features. "
        f"Product: {product.title}. Script/voiceover: {script}"
    )


def build_caption(product: Product) -> str:
    return (
        f"{product.title}\n\n"
        f"Price shown in the creator workflow: ₹{product.price_inr:.0f}.\n"
        "Check the current product page for availability, price and details.\n\n"
        "#meesho #shopping #fashion #productfinds #reels"
    )
