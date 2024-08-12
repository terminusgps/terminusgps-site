import logging
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

from .markdown_config import ALLOWED_TAGS

logger = logging.getLogger(__name__)

class DataAttributeTreeprocessor(Treeprocessor):
    def run(self, root):
        logger.info("Running run.DataAttributeTreeprocessor")
        for element in root.iter():
            if element.tag in ALLOWED_TAGS:
                element.set("data-md-element", element.tag)
        return root

class DataAttributeExtension(Extension):
    def extendMarkdown(self, md):
        logger.info("Running extendMarkdown.DataAttributeExtension")
        md.treeprocessors.register(
            DataAttributeTreeprocessor(md),
            "data_attribute",
            15
        )
