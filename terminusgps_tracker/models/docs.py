from django.db import models

class DocumentationPage(models.Model):
    title = models.CharField(max_length=64)
    source = models.FileField(upload_to="docs/")
    section = models.ForeignKey("DocumentationSection", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title.title()

class DocumentationSection(models.Model):
    title = models.CharField(max_length=64)
    pages = models.ManyToManyField(DocumentationPage)
    slug = models.SlugField(length=64, unique=True)
