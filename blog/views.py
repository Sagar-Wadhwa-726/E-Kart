from django.shortcuts import render
from .models import blogpost
from django.http import HttpResponse


def index(request):
    context = {
        #getting all the blogs from the model to display on the main blog page which displays all blogs
        'myallposts':blogpost.objects.all()
    }
    return render(request, "blog/index.html", context)

def blogposts(request, blogid):

    # 0th index since it returns a list and we want the first post in that list
    # [{post_at_0th_index_to_be_Stored_in_variable_post}]

    post = blogpost.objects.filter(post_id=blogid)[0]
    print(post)
    return render(request, "blog/blogPost.html", {'post': post})
