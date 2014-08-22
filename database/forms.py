from django import forms


class FileUploadForm(forms.Form):
    docfile1 = forms.FileField(label='Select meta_Project.csv file:')
    docfile2 = forms.FileField(label='Select meta_Sample.csv file:')
    docfile3 = forms.FileField(label='Select conserved taxonomy file:')
    docfile4 = forms.FileField(label='Select .shared file:')
    docfile5 = forms.FileField(label='Select QIIME BIOM file:')
    docfile6 = forms.FileField(label='Select QIIME OTU Table file:')
    docfile7 = forms.FileField(label='Select MG-RAST table file:')