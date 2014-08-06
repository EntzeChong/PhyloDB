from django import forms

class DocumentForm(forms.Form):
    docfile1 = forms.FileField(label='Select meta_Project.csv file:')
    docfile2 = forms.FileField(label='Select meta_Sample.csv file:')
    docfile3 = forms.FileField(label='Select a conserved taxonomy file:')
    docfile4 = forms.FileField(label='Select a .shared file:')