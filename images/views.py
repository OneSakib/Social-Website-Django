from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreaterForm
from .models import Image
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from common.decorators import ajax_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from actions.utils import create_action
import redis
from django.conf import settings

# Connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


# Create your views here.
@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreaterForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully')
            return redirect(new_item.get_absolute_url())
    else:
        form = ImageCreaterForm(data=request.GET)
    return render(request, 'images/image/create.html', {'form': form, 'section': 'images'})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # increment the image view by 1
    total_views = r.incr('image:{}:views'.format(image.id))
    # increment image ranking  by 1
    r.zincrby('image_ranking', image.id, 1)

    return render(request, 'images/image/detail.html',
                  {'image': image, 'section': 'images', 'total_views': total_views})


# @ajax_required
@require_POST
@login_required
@csrf_exempt
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ok'})


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 9)
    page = request.GET.get('page')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if is_ajax(request=request):
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if is_ajax(request=request):
        return render(request, 'images/image/list.html', {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})


@login_required
def image_rankings (request):
    #     get ranking dict
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)
    image_ranking_ids = [int(id) for id in image_ranking]
    #     get most viewd images
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html', {'section': 'images', 'most_viewed': most_viewed})
