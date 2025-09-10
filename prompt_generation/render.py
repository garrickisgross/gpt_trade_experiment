from jinja2 import Environment , FileSystemLoader, StrictUndefined, Template
from typing import Any

class Renderer:
    """ Simple Renderer for Jinja Templates """
    def __init__(self):
        self.env = Environment(
            loader = FileSystemLoader("prompt_generation/templates"),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def get_template(self, template_file: str) -> Template:
        """Get Template from env directory"""
        return self.env.get_template(template_file)
    
    def render_to_file(self, template_file: str, dest_file: str, data: Any) -> None:
        """Renders the template to a given file with provided data
        
        Args:
            template_file: name (not path) of the template file
            dest_file: path (w/name) of desired file
            data: Object for rendering"""
        template = self.get_template(template_file)
        text = template.render(data=data)

        with open(dest_file, 'w') as f:
            f.write(text)

        
