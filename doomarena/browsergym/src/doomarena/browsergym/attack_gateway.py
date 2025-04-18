import json
from browsergym.core.env import BrowserEnv
import logging
import time
from typing import Any, List

from doomarena.core.agent_defenses.base import AttackSafetyCheck
from .init_scripts import (
    get_banner_injection_script,
)
from .attack_scripts import (
    get_popup_insertion_script,
    get_user_content_replacement_script,
    get_banner_update_script,
    get_div_injection_script,
)
from doomarena.core.attack_gateways.attack_gateway import AttackGateway
from doomarena.core.attack_gateways.register_attack_gateway import (
    register_attack_gateway,
)
from doomarena.core.attack_config import AttackConfig
from browsergym.utils.obs import flatten_axtree_to_str

logger = logging.getLogger(__name__)


@register_attack_gateway("browsergym_attack_gateway")
class BrowserGymAttackGateway(AttackGateway):
    timeout = 10

    def __init__(
        self,
        env: BrowserEnv,
        attack_configs: List[AttackConfig],
        task_name: str,
        defenses: list[AttackSafetyCheck] | None = None,
        abort_on_detection: bool = True,
        abort_on_successful_attack: bool = True,
    ):
        super().__init__(env, attack_configs)
        self.attackable_components = set()
        for attack_config in attack_configs:
            self.attackable_components.add(attack_config.attackable_component["type"])
        self.init_scripts = []
        self.init_flags = []
        self.popup_counter = 0
        self.task_name = task_name
        self.defenses = defenses or []
        self.abort_on_detection = abort_on_detection
        self.abort_on_successful_attack = abort_on_successful_attack

    def get_matching_attack_config(self, observation: dict) -> List[AttackConfig]:
        attack_configs = []
        for attack_config in self.attack_configs:
            if attack_config.filter and attack_config.filter(observation, self.env):
                attack_configs.append(attack_config)
        return attack_configs

    def reset(self, seed=None, *args, **kwargs):
        obs, info = self.env.reset(seed=seed, *args, **kwargs)
        self.run_init_scripts()
        done = False
        truncated = False
        reward = 0.0
        obs, reward, done, truncated, info = self.run_attacks_and_defenses(
            obs, reward, done, truncated, info
        )
        self.previous_transition = (
            obs,
            reward,
            done,
            truncated,
            info,  # hack to recover info in step() because cannot abort from reset()
        )
        return obs, info

    def run_defenses(self, obs: dict):
        # This is optimized
        obs_as_text = flatten_axtree_to_str(obs["axtree_object"])

        defense_results = []
        triggered_defenses = []
        for idx, defense in enumerate(self.defenses):
            r = defense.attack_detected([{"role": "user", "content": obs_as_text}])
            defense_results.append(r)
            if r:
                triggered_defenses.append(defense.defense_name)
        logger.warning(f"Defense results: {defense_results}")

        return triggered_defenses

    def run_attacks(self, attack_configs: List[AttackConfig], step_idx: int = 0):
        load_flags = []
        attack_contents = []
        for attack_config in attack_configs:
            # TODO: enforce attackable component types
            if attack_config.attackable_component["type"] == "banner":
                banner_flag, banner_script = get_banner_update_script(step_idx)
                banner_obs = self.env.unwrapped._get_obs()
                left_banner_uri, left_banner_alt_text = (
                    attack_config.attack.get_next_attack(obs=banner_obs)
                )
                right_banner_uri, right_banner_alt_text = (
                    attack_config.attack.get_next_attack(obs=banner_obs)
                )
                banner_args = (
                    left_banner_uri,
                    right_banner_uri,
                    left_banner_alt_text,
                    right_banner_alt_text,
                )

                self.run_attack_script(
                    banner_script,
                    banner_args,
                )
                load_flags.append(banner_flag)

                attack_contents.append(("banner", banner_args))
            elif attack_config.attackable_component["type"] == "user-generated-content":
                user_generated_content_flag, user_generated_content_script = (
                    get_user_content_replacement_script(
                        step_idx,
                        [
                            "div.comment__body.break-text.text-flow p",  # Comments in reddit-WA
                            ".product-item-link",  # Product item link in shopping-WA (list view)
                            "#shortDescription",  # Product description in shopping-WA (detail view)
                            "#customer-reviews > div.block-content > ol > li > div.review-content-container > div.review-content",  # Product reviews in shopping-WA (detail view)
                        ],
                    )
                )
                user_generated_content = attack_config.attack.get_next_attack(
                    obs=self.env.unwrapped._get_obs()
                )
                self.run_attack_script(
                    user_generated_content_script, user_generated_content
                )
                load_flags.append(user_generated_content_flag)

                attack_contents.append(
                    ("user-generated-content", user_generated_content)
                )
            elif attack_config.attackable_component["type"] == "popup-element":
                popup_div = attack_config.attack.get_next_attack(
                    obs=self.env.unwrapped._get_obs()
                )
                popup_flag, popup_script = get_popup_insertion_script(step_idx)

                self.run_attack_script(
                    popup_script,
                    popup_div,
                )
                load_flags.append(popup_flag)
                self.popup_counter += 1

                attack_contents.append(("popup-element", popup_div))
            elif attack_config.attackable_component["type"] == "div-element":
                div_flag, div_script = get_div_injection_script(step_idx)
                flags_set = self._check_flags(
                    page=self.env.unwrapped.context.pages[0], flags=[div_flag]
                )
                if flags_set:
                    continue
                div_args = attack_config.attack.get_next_attack(
                    obs=self.env.unwrapped._get_obs()
                )
                self.run_attack_script(
                    div_script,
                    div_args,
                )
                load_flags.append(div_flag)

                attack_contents.append(("div-element", div_args))
        self.wait_for_flags(flags=load_flags)
        return attack_contents

    def run_attack_script(self, script: str, args: Any = None) -> bool:
        """Run the attack script."""
        pages = self.env.unwrapped.context.pages
        for page in pages:
            try:
                page.main_frame.wait_for_load_state("domcontentloaded")
                result = page.evaluate(script, args)
                return bool(result)
            except Exception as e:
                logging.warning(f"Error executing attack script: {str(e)}")
                return False

    def run_init_scripts(self):
        """Run the init scripts and wait for their respective flags to be set."""
        if "banner" in self.attackable_components:
            flag, script = get_banner_injection_script()
            self.init_scripts.append(script)
            self.init_flags.append(flag)
        for script in self.init_scripts:
            self.env.unwrapped.context.add_init_script(script)
        page = self.env.unwrapped.context.pages[0]
        page.reload()
        self.wait_for_flags(flags=self.init_flags)

    def wait_for_flags(self, flags: list[str]) -> None:
        """Wait for the flags to be set on the page."""
        if not flags or not flags[0]:
            return
        page = self.env.unwrapped.context.pages[0]
        # Wait for flags to be set
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if self._check_flags(page, flags):
                print(f"Flag {flags} successfully verified")
                return
            time.sleep(0.5)
        missing_flags = [flag for flag in flags if not page.evaluate(f"window.{flag}")]
        raise TimeoutError(
            f"Flags {missing_flags} not set within {self.timeout} seconds"
        )

    def _check_flags(self, page, flags) -> bool:
        """Check if all required flags are set."""
        if not flags:
            return True
        for flag in flags:
            if not page.evaluate(f"window.{flag}"):
                return False

        return True

    def step(self, action: str):
        obs, reward, done, truncated, info = self.previous_transition
        if done:
            obs, reward, __, truncated, info = self.env.step("noop(0.1)")
            return obs, reward, True, truncated, info
        obs, reward, done, truncated, info = self.env.step(action)
        obs, reward, done, truncated, info = self.run_attacks_and_defenses(
            obs, reward, done, truncated, info
        )
        return obs, reward, done, truncated, info

    def run_attacks_and_defenses(self, obs, reward, done, truncated, info):
        info = info or {}
        info.setdefault("task_info", {})
        attack_configs = self.get_matching_attack_config(obs)
        attack_contents = []
        if attack_configs:
            attack_contents = self.run_attacks(attack_configs)
            obs = self.env.unwrapped._get_obs()

        successful_attacks = []
        successful_attack_contents = []
        for idx, attack_config in enumerate(self.attack_configs):
            attack_successful = False
            if attack_config.success_filter and attack_config.success_filter(
                obs, self.env
            ):
                successful_attacks.append(attack_config.attack.attack_name)
                successful_attack_contents.append(attack_contents[idx])
                attack_successful = True

        info["task_info"]["successful_attacks"] = successful_attacks
        info["task_info"]["successful_attack_contents"] = successful_attack_contents
        info["task_info"][
            "abort_on_successful_attack"
        ] = self.abort_on_successful_attack

        # Abort if attack is successful
        if successful_attacks:
            logger.info("Attack successful")
            if self.abort_on_successful_attack:
                done = True
                truncated = False
                logger.info("Attack successful, aborting task")

        # Defenses
        triggered_defenses = self.run_defenses(obs)
        info["task_info"]["triggered_defenses"] = triggered_defenses
        info["task_info"]["abort_on_detection"] = self.abort_on_detection

        if triggered_defenses:
            logger.info(f"Defenses triggered: {triggered_defenses}")
            if self.abort_on_detection:
                done = True
                truncated = False
                logger.info("Defense triggered, aborting task")

        return obs, reward, done, truncated, info

    def attack_success(self, **kwargs):
        raise NotImplementedError  # unclear what this function should look like, see step() implementaiton

    def close(self):
        self.env.close()

    def get_elements_by_class_name(self, class_name: str):
        """Get the XPath of all elements with the given class name."""
        script = f"""
            (() => {{
                function getXPathForElement(element) {{
                    const idx = (sib, name) => sib 
                        ? idx(sib.previousElementSibling, name || sib.localName) + (sib.localName == name)
                        : 1;
                    const segs = (elm) => !elm || elm.nodeType !== 1 
                        ? ['']
                        : elm.id && document.getElementById(elm.id) === elm
                        ? [`id("${{elm.id}}")`]
                        : [...segs(elm.parentNode), elm.localName + (elm.className ? `[@class="${{elm.className}}"]` : '') + (elm.previousElementSibling ? `[${{idx(elm)}}]` : '')];
                    return segs(element).join('/');
                }}

                function getAllAttackedElements(root = document) {{
                    const elements = Array.from(root.querySelectorAll('.{class_name}'));
                    const iframes = root.querySelectorAll('iframe');
                    iframes.forEach(iframe => {{
                        try {{
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                            elements.push(...getAllAttackedElements(iframeDoc));
                        }} catch (e) {{
                            // Ignore cross-origin iframes
                        }}
                    }});
                    return elements.map(el => getXPathForElement(el));
                }}
                return getAllAttackedElements();
            }})()
            """
        return self.env.unwrapped.page.evaluate(script)

    def get_elements_by_selector(self, selector: str):
        """Get the XPath of all elements with the given selector."""
        script = f"""
            (() => {{
                function getXPathForElement(element) {{
                    const idx = (sib, name) => sib 
                        ? idx(sib.previousElementSibling, name || sib.localName) + (sib.localName == name)
                        : 1;
                    const segs = (elm) => !elm || elm.nodeType !== 1 
                        ? ['']
                        : elm.id && document.getElementById(elm.id) === elm
                        ? [`id("${{elm.id}}")`]
                        : [...segs(elm.parentNode), elm.localName + (elm.className ? `[@class="${{elm.className}}"]` : '') + (elm.previousElementSibling ? `[${{idx(elm)}}]` : '')];
                    return segs(element).join('/');
                }}

                function getAllAttackedElements(root = document) {{
                    const elements = Array.from(root.querySelectorAll('{selector}'));
                    const iframes = root.querySelectorAll('iframe');
                    iframes.forEach(iframe => {{
                        try {{
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                            elements.push(...getAllAttackedElements(iframeDoc));
                        }} catch (e) {{
                            // Ignore cross-origin iframes
                        }}
                    }});
                    return elements.map(el => getXPathForElement(el));
                }}
                return getAllAttackedElements();
            }})()
            """
        return self.env.unwrapped.page.evaluate(script)
