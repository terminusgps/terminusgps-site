from django import forms


class EmailTemplateUploadForm(forms.Form):
    name = forms.CharField(
        max_length=256,
        widget=forms.widgets.TextInput(
            attrs={"class": "w-full block p-2 rounded", "placeholder": "Name"}
        ),
    )
    subject = forms.CharField(
        max_length=256,
        widget=forms.widgets.TextInput(
            attrs={"class": "w-full block p-2 rounded", "placeholder": "Subject"}
        ),
    )
    text_content = forms.FileField(
        allow_empty_file=False,
        widget=forms.widgets.FileInput(
            attrs={
                "class": "file:p-2 file:border-terminus-red-600 file:border file:hover:bg-terminus-red-500 file:bg-terminus-red-800 file:text-white file:rounded file:cursor-pointer block w-full cursor-pointer file:font-semibold p-2 bg-white rounded"
            }
        ),
    )
    html_content = forms.FileField(
        allow_empty_file=True,
        widget=forms.widgets.FileInput(
            attrs={
                "class": "file:p-2 file:border-terminus-red-600 file:border file:hover:bg-terminus-red-500 file:bg-terminus-red-800 file:text-white file:rounded file:cursor-pointer block w-full cursor-pointer file:font-semibold p-2 bg-white rounded"
            }
        ),
    )
