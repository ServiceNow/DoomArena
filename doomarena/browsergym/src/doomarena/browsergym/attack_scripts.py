from typing import List


def get_banner_update_script(step_index: int):
    load_flag = "GATEWAY_BANNER_UPDATED_" + str(step_index)
    attack_script = f"""
        ([left_img, right_img, left_alt, right_alt]) => {{
            const leftImg = document.getElementById('left-banner-img');
            const rightImg = document.getElementById('right-banner-img');
            
            if (!leftImg || !rightImg) {{
                return false;
            }}
            
            try {{
                leftImg.src = left_img;
                leftImg.alt = left_alt;
                rightImg.src = right_img;
                rightImg.alt = right_alt;
                window.{load_flag} = true;
                return true;
            }} catch (e) {{
                console.error('Banner update failed:', e);
                return false;
            }}
        }}
    """
    return load_flag, attack_script


def get_user_content_replacement_script(
    step_index: int, content_selectors: List[str] = "p"
):
    combined_selectors = ", ".join(content_selectors)
    load_flag = "USER_GENERATED_CONTENT_UPDATED_" + str(step_index)
    attack_script = f"""
        (replacements) => {{
            // If flag is already set, do nothing
            if (window.{load_flag} === true) {{
                return true;
            }}

            // Replace content
            const elements = document.querySelectorAll("{combined_selectors}");
            replacements.forEach((newText, index) => {{
                // Only process if we have a corresponding element
                if (index < elements.length && newText !== null) {{
                    elements[index].textContent += newText;
                }}
            }});
            window.{load_flag} = true;
            return true;
        }}
    """
    return load_flag, attack_script


def get_popup_insertion_script(step_index: int):
    load_flag = "GATEWAY_POPUP_INSERTED_" + str(step_index)
    attack_script = f"""
(popup_div) => {{
    /* 1 ── show only once per tab  ───────────────────────────── */
    if (window.{load_flag}) return true; 

    document.getElementById('message-overlay')?.remove(); 

    const overlay = document.createElement('div');
    overlay.id = 'message-overlay';             
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.style.cssText = `
        position: fixed;
        top:0; left:0;
        width:100%; height:100%;
        background: rgba(0,0,0,0.5);
        display:flex !important;           
        justify-content:center !important;
        align-items:center !important;
        z-index:10000;
    `;

    overlay.innerHTML = popup_div;

    /* 2 ── absolutely centre the card (no flexbox dependencies) ─ */
    const card = overlay.firstElementChild;    
    if (card){{
        card.style.setProperty('position',  'absolute',             'important');
        card.style.setProperty('top',       '50%',                  'important');
        card.style.setProperty('left',      '50%',                  'important');
        card.style.setProperty('transform', 'translate(-50%,-50%)', 'important');
    }}
    document.body.prepend(overlay);          

    const proceedButton = document.getElementById('proceed-btn');
    const closeButton   = document.getElementById('close-btn');

    proceedButton?.focus();
    proceedButton?.addEventListener('click', () => {{ overlay.remove(); }});
    closeButton?.addEventListener('click', () => overlay.remove());

    const escHandler = (e) => {{
        if (e.key === 'Escape') {{
            overlay.remove();
            document.removeEventListener('keydown', escHandler);
        }}
    }};
    document.addEventListener('keydown', escHandler);

    window.{load_flag} = true;  
    return true;
}}
"""

    return load_flag, attack_script


def get_div_injection_script(step_index: int):
    """
    Create a script that injects a div with styles into a webpage.
    The script expects to receive the exact div HTML and styles as arguments.

    Args:
        step_index (int): Step index for the load flag
    """
    load_flag = f"DIV_INJECTION_COMPLETED_{step_index}"

    # Simple injection script that takes div HTML and styles directly
    attack_script = f"""
    ([div_html, styles]) => {{
        // Insert the div
        document.body.insertAdjacentHTML('afterbegin', div_html);
        
        // Apply styles to all matching elements
        for (const [selector, styleObj] of Object.entries(styles)) {{
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {{
                if (element) {{
                    Object.assign(element.style, styleObj);
                }}
            }});
        }}

        window.{load_flag} = true;
        return true;
    }}
    """

    return load_flag, attack_script
