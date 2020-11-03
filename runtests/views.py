import os
import subprocess
from django import forms

from django.http import HttpResponse
from django.shortcuts import render
from runtests.functional_testing.site_testing import _tests, Test


# Create your views here.
def main(request):
    return render(request, "main.html")

def run_full_test(request):
    context = {
        "test_name": "run_all_tests",
    }
    class TestForm(forms.Form):
        url = forms.CharField(label="url", max_length=50)
    if request.method == "GET":
        form = TestForm()
        context["form"] = form
        return render(request, "test_input.html", context)
    elif request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["url"]
            os.chdir("runtests/functional_testing/")
            proc = subprocess.Popen(['py', f'all_test.py', url], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            stdout = stdout.decode('latin-1')
            stderr = stderr.decode('utf-8')
            status = proc.poll()
            stdout = stdout.split("\n")
            stderr = stderr.split("\n")
            context["stdout"] = stdout
            context["stderr"] = stderr
            os.chdir("../..")
            return render(request, "test_output.html", context)




def select_test(request):
    context = {
        "tests": _tests
    }

    return render(request, "select_test.html", context)


def test(request, test_name):
    context = {
        "tests": _tests,
        "test_name": test_name,
        "values": _tests[test_name]
    }

    class TestForm(forms.Form):
        param1 = forms.CharField(label=_tests[test_name][0], max_length=50)
        if len(_tests[test_name]) > 1:
            param2 = forms.CharField(label=_tests[test_name][1], max_length=50)

    if request.method == "GET":
        form = TestForm()
        context["form"] = form
        return render(request, "test_input.html", context)
    elif request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            params = [form.cleaned_data["param1"]]
            if len(_tests[test_name]) > 1:
                param2 = form.cleaned_data["param2"]
                param2 = param2.split(",")
                for arg in param2:
                    params.append(arg)
        os.chdir("runtests/functional_testing/")
        proc = subprocess.Popen(['py', f'site_testing.py', test_name] + params, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        stdout = stdout.decode('latin-1')
        stderr = stderr.decode('utf-8')
        status = proc.poll()
        stdout = stdout.split("\n")
        stderr = stderr.split("\n")
        context["stdout"] = stdout
        context["stderr"] = stderr
        os.chdir("../..")
        return render(request, "test_output.html", context)
