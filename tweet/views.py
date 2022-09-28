from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TweetModel
from .models import TweetComment
from django.views.generic import ListView, TemplateView

# Create your views here.

def home(request):
    user = request.user.is_authenticated
    if user:
        return redirect('/tweet')
    else:
        return redirect('/sign-in')

def tweet(request):
    if request.method == 'GET':
        user = request.user.is_authenticated
        
        if user:
            # TweetModel에 저장한 모든 모델을 불러오겠다 / 생성일 역순으로 정렬한다.
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, 'tweet/home.html', {'tweet' : all_tweet})
        else:
            return redirect('/sign-in')
    
    elif request.method == 'POST':
        user = request.user
        content = request.POST.get('my-content', '')
        tags = request.POST.get('tag','').split(',')
        if content == '':
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, 'tweet/home.html', {'error' : '글은 공백일 수 없습니다.', 'tweet' : all_tweet})
        
        else:
            my_tweet = TweetModel.objects.create(author=user, content=content)
            for tag in tags:
                tag = tag.strip()
                if tag != '':
                    my_tweet.tags.add(tag)
                    
            my_tweet.save()
            return redirect('/tweet')


@login_required
def delete_tweet(request, id):
    my_tweet = TweetModel.objects.get(id = id)
    my_tweet.delete()
    return redirect('/tweet')

@login_required # 답안 참고
def detail_tweet(request, id):
    my_tweet = TweetModel.objects.get(id=id)
    tweet_comment = TweetComment.objects.filter(tweet_id=id).order_by('-created_at') # 답안 참고
    return render(request, 'tweet/tweet_detail.html', {'tweet' : my_tweet, 'comment' : tweet_comment}) # 답안 참고

@login_required # 답안 참고
def write_comment(request, id):
    if request.method == 'POST':
        comment = request.POST.get("comment", "") # 답안 참고
        current_tweet = TweetModel.objects.get(id=id)
        
        TC = TweetComment()
        TC.comment = comment
        TC.author = request.user
        TC.tweet = current_tweet
        TC.save()
    return redirect('/tweet/'+str(id)) # 답안 참고

@login_required # 답안 참고
def delete_comment(request, id):
    comment = TweetComment.objects.get(id=id)
    current_tweet = comment.tweet.id # 답안 참고
    comment.delete()
    return redirect('/tweet/'+str(current_tweet)) # 답안 참고


class TagCloudTV(TemplateView):
    template_name = 'taggit/tag_cloud_view.html'


class TaggedObjectLV(ListView):
    template_name = 'taggit/tag_with_post.html'
    model = TweetModel

    def get_queryset(self):
        return TweetModel.objects.filter(tags__name=self.kwargs.get('tag'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagname'] = self.kwargs['tag']
        return context