from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PublishingPanel,
)
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)
from wagtail.fields import RichTextField
from wagtail.models import (
    ClusterableModel,
    DraftStateMixin,
    Page,
    PreviewableMixin,
    RevisionMixin,
    TranslatableMixin,
)
from wagtail.snippets.models import register_snippet


@register_snippet
class FooterText(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    TranslatableMixin,
    models.Model,
):
    body = RichTextField(blank=True)

    panels = [FieldPanel("body"), PublishingPanel()]

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = _("Footer Text")

    def __str__(self) -> str:
        return "Footer text"

    def get_preview_template(self, request, mode_name):
        return "home/layout.html"

    def get_preview_context(self, request, mode_name):
        return {"footer_text": self.body}


class HomePage(Page):
    cta_text = models.CharField(
        max_length=128,
        verbose_name=_("Call to Action Text"),
        help_text=_("Text to display on Call to Action"),
        blank=True,
    )
    cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Call to Action Link"),
        help_text=_("Choose a page to link to for the Call to Action"),
    )
    featured_section_1_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    featured_section_1_headline = models.CharField(blank=True)
    featured_section_1_text = RichTextField(blank=True)
    featured_section_2_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    featured_section_2_headline = models.CharField(blank=True)
    featured_section_2_text = RichTextField(blank=True)
    featured_section_3_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    featured_section_3_headline = models.CharField(blank=True)
    featured_section_3_text = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("cta_text"), FieldPanel("cta_link")],
            heading=_("Call to Action section"),
        ),
        MultiFieldPanel(
            [
                MultiFieldPanel(
                    [
                        FieldPanel("featured_section_1_image"),
                        FieldPanel("featured_section_1_headline"),
                        FieldPanel("featured_section_1_text"),
                    ]
                ),
                MultiFieldPanel(
                    [
                        FieldPanel("featured_section_2_image"),
                        FieldPanel("featured_section_2_headline"),
                        FieldPanel("featured_section_2_text"),
                    ]
                ),
                MultiFieldPanel(
                    [
                        FieldPanel("featured_section_3_image"),
                        FieldPanel("featured_section_3_headline"),
                        FieldPanel("featured_section_3_text"),
                    ]
                ),
            ],
            heading=_("Featured homepage sections"),
        ),
    ]


class StandardPage(Page):
    header_title = models.CharField(blank=True)
    header_subtitle = models.CharField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = RichTextField(blank=True)
    show_last_updated = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel("header_title"),
        FieldPanel("header_subtitle"),
        FieldPanel("show_last_updated"),
        FieldPanel("image"),
        FieldPanel("body"),
    ]


class FormField(AbstractFormField):
    page = ParentalKey(
        "FormPage", on_delete=models.CASCADE, related_name="form_fields"
    )
    placeholder = models.CharField(blank=True, max_length=256)

    panels = AbstractFormField.panels + [FieldPanel("placeholder")]


class CustomFormBuilder(FormBuilder):
    def get_create_field_function(self, type):
        create_field_function = super().get_create_field_function(type)

        def wrapped_create_field_function(field, options):
            created_field = create_field_function(field, options)
            created_field.widget.attrs.update(
                {"placeholder": field.placeholder}
            )
            return created_field

        return wrapped_create_field_function


class FormPage(AbstractEmailForm):
    form_builder = CustomFormBuilder
    header_title = models.CharField(blank=True)
    header_subtitle = models.CharField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("header_title"),
        FieldPanel("header_subtitle"),
        InlinePanel("form_fields"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [FieldPanel("from_address"), FieldPanel("to_address")]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
    ]


@register_setting(icon="link-external")
class ExternalURLSettings(
    ClusterableModel, PreviewableMixin, BaseGenericSetting
):
    cameras_url = models.URLField(
        blank=True, verbose_name=_("Terminus GPS Cameras URL")
    )
    hosting_url = models.URLField(
        blank=True, verbose_name=_("Terminus GPS Hosting URL")
    )
    ios_app_url = models.URLField(
        blank=True, verbose_name=_("Terminus GPS iOS App URL")
    )
    android_app_url = models.URLField(
        blank=True, verbose_name=_("Terminus GPS Android App URL")
    )
    wialon_cms_url = models.URLField(
        blank=True, verbose_name=_("Wialon CMS URL")
    )
    repository_url = models.URLField(
        blank=True, verbose_name=_("GitHub Repository URL")
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("cameras_url"),
                FieldPanel("hosting_url"),
                FieldPanel("ios_app_url"),
                FieldPanel("android_app_url"),
                FieldPanel("wialon_cms_url"),
                FieldPanel("repository_url"),
            ]
        )
    ]

    class Meta:
        verbose_name = _("External URL settings")

    def get_preview_template(self, request, mode_name):
        return "home/layout.html"


@register_setting(icon="site")
class SiteSettings(BaseSiteSetting):
    title_suffix = models.CharField(
        verbose_name=_("Title Suffix"),
        max_length=255,
        help_text=_(
            "The suffix for the title meta tag e.g. ' | Terminus GPS'"
        ),
        default="Terminus GPS",
    )

    panels = [FieldPanel("title_suffix")]

    class Meta:
        verbose_name = _("Site settings")
