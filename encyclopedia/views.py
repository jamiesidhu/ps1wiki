from django import forms

from django.shortcuts import render, redirect

from . import util

from markdown2 import Markdown

from django.http import HttpResponseRedirect
from django.urls import reverse

import random

class newPageForm(forms.Form):
    title = forms.CharField(label="Page Title",  required=True)
    markd = forms.CharField(label="Content",  required=True, widget=forms.Textarea(attrs={"rows":"3"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entries(request, title):

    mdtxt = util.get_entry(title)
    head = "Error"
    if mdtxt != None:
        mdtxt = Markdown().convert(mdtxt)
    return render(request, "encyclopedia/entry.html", {
        "entry": mdtxt, "head": title
    })

def newpage(request):
    if request.method == "POST":
        form = newPageForm(request.POST)
        if form.is_valid():
            newtitle = form.cleaned_data["title"]
            if util.get_entry(newtitle) != None:
                return render(request, "encyclopedia/newpage.html", {
                    "form": form, "errMsg": "Entry already exists"
                })
            else:
                with open(f'entries/{newtitle}.md', 'w') as f:
                    f.write(form.cleaned_data["markd"])
                return HttpResponseRedirect(reverse("entries", args=(newtitle,)))
        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/newpage.html", {
                "form": form
            })

    return render(request, "encyclopedia/newpage.html", {
        "form": newPageForm()
    })


def search(request):

    query = request.GET.get('q', '')

    if util.get_entry(query):
        return entries(request, query)
    
    entrydb = util.list_entries()
    results = []
    for entry in entrydb:
        if query in entry:
            results.append(entry)
    
    return render(request, "encyclopedia/search.html", {
        "results" : results
    })

def edit(request, title):
    if request.method == "GET":
        mdtxt = util.get_entry(title)
        form = newPageForm({"title": title, "markd": mdtxt})
        return render(
            request,
            "encyclopedia/edit.html",
            {"form": form, "title": title},
        )

    form = newPageForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data["title"]
        content = form.cleaned_data["markd"]

        util.save_entry(title=title, content=content)
        return redirect("entries", title)
    

def randompage(request):
    randomEntry = random.choice(util.list_entries())
    content = util.get_entry(randomEntry)
    return render(request, "encyclopedia/entry.html", {
        "entry": Markdown().convert(content), "head": randomEntry
    })