from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class TemplateManager:
    def __init__(self):
        templates_path = Path(__file__).parent.parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(templates_path), autoescape=True)

    def render_template(self, template_name: str, **kwargs) -> str:
        template = self.env.get_template(template_name)
        return template.render(**kwargs)


template_manager = TemplateManager()
