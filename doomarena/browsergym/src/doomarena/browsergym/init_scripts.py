def get_banner_injection_script(
    left_image_url="",
    right_image_url="",
    banner_width_pct=15,
):
    """Get the script for injecting banners into a web page."""

    banner_width_pct = 15
    init_flag = "GATEWAY_BANNER_LOADED"

    return (
        init_flag,
        f"""
(() => {{
    console.log('Script started executing');

    const wrapper = document.createElement('div');
    wrapper.id = 'viewport-wrapper';
    wrapper.style.position = 'absolute';
    wrapper.style.top = '0';
    wrapper.style.left = '0';
    wrapper.style.width = '100%';
    wrapper.style.height = '100%';
    wrapper.style.margin = '0';
    wrapper.style.padding = '0';
    wrapper.style.border = 'none';

    // Create left panel
    const leftPanel = document.createElement('div');
    leftPanel.id = 'left-panel';
    leftPanel.style.position = 'fixed';
    leftPanel.style.top = '0';
    leftPanel.style.bottom = '0';
    leftPanel.style.left = '0';
    leftPanel.style.width = '{banner_width_pct}%';
    leftPanel.style.height = '100vh';
    leftPanel.style.margin = '0';
    leftPanel.style.padding = '0';
    leftPanel.style.border = 'none';

    // Add an image to the left panel
    const leftImage = document.createElement('img');
    leftImage.id = 'left-banner-img';  // Added ID for future updates
    leftPanel.classList.add('gateway-banner', 'left');
    leftImage.src = `{left_image_url}`; // Replace with the actual URL of the left banner image
    leftImage.alt = 'Left Banner';
    leftImage.style.width = '100%';
    leftImage.style.height = '100%';
    leftImage.style.objectFit = 'cover'; // Ensures the image fits the panel
    leftPanel.appendChild(leftImage);

    // Create right panel
    const rightPanel = document.createElement('div');
    rightPanel.classList.add('gateway-banner', 'right');
    rightPanel.id = 'right-panel';
    rightPanel.style.position = 'fixed';
    rightPanel.style.top = '0';
    rightPanel.style.bottom = '0';
    rightPanel.style.right = '0';
    rightPanel.style.width = '{banner_width_pct}%';
    rightPanel.style.height = '100vh';
    rightPanel.style.margin = '0';
    rightPanel.style.padding = '0';
    rightPanel.style.border = 'none';

    // Add an image to the right panel
    const rightImage = document.createElement('img');
    rightImage.id = 'right-banner-img';  // Added ID for future updates
    rightImage.src = `{right_image_url}`; // Replace with the actual URL of the right banner image
    rightImage.alt = 'Right Banner';
    rightImage.style.width = '100%';
    rightImage.style.height = '100%';
    rightImage.style.objectFit = 'cover'; // Ensures the image fits the panel
    rightPanel.appendChild(rightImage);

    // Create content container
    const contentContainer = document.createElement('div');
    contentContainer.id = 'content-container';
    contentContainer.style.position = 'absolute';
    contentContainer.style.left = '15%';
    contentContainer.style.width = '70%';
    contentContainer.style.minHeight = '100vh';
    contentContainer.style.background = 'transparent';

    const originalContent = document.createElement('div');
    originalContent.id = 'original-content';
    originalContent.style.width = '100%';

    function moveContent() {{
        if (!document.body) return;

        // Clean up if already exists
        const existingWrapper = document.getElementById('viewport-wrapper');
        if (existingWrapper) {{
            existingWrapper.remove();
        }}

        // Preserve original body styles
        const originalBodyStyles = document.body.getAttribute('style') || '';
        
        // Move all body content to our container
        while (document.body.firstChild) {{
            if (document.body.firstChild === wrapper) {{
                document.body.removeChild(document.body.firstChild);
                continue;
            }}
            originalContent.appendChild(document.body.firstChild);
        }}

        // Restore original body styles
        document.body.setAttribute('style', originalBodyStyles);

        // Assemble and inject our structure
        contentContainer.appendChild(originalContent);
        wrapper.appendChild(leftPanel);
        wrapper.appendChild(contentContainer);
        wrapper.appendChild(rightPanel);
        document.body.appendChild(wrapper);
    }}

    // Initial setup
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', () => {{
            moveContent();
            setupObserver();
        }});
    }} else {{
        moveContent();
        setupObserver();
    }}

    // Handle dynamic content changes
    function setupObserver() {{
        const observer = new MutationObserver((mutations) => {{
            mutations.forEach((mutation) => {{
                if (mutation.target === document.body && 
                    !document.getElementById('viewport-wrapper')) {{
                    moveContent();
                }}
            }});
        }});

        // Only observe if we have a valid target
        const target = document.body || document.documentElement;
        if (target) {{
            observer.observe(target, {{
                childList: true,
                subtree: true
            }});
        }} else {{
            console.warn('No valid target found for MutationObserver');
        }}
    }}

    window.{init_flag} = true;
}})();
""",
    )
