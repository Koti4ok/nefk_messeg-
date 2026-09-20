from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Group, GroupMembership
from .forms import GroupForm
from posts.models import Post
from posts.forms import PostForm


@login_required
def groups_list_view(request):
    all_groups = Group.objects.all().order_by('-created_at')
    my_groups = Group.objects.filter(memberships__user=request.user, memberships__is_active=True)
    return render(request, 'groups/groups_list.html', {
        'all_groups': all_groups,
        'my_groups': my_groups,
    })


@login_required
def group_detail_view(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership = GroupMembership.objects.filter(group=group, user=request.user, is_active=True).first()
    is_member = membership is not None
    is_admin = membership and membership.role in ('admin', 'moderator')

    posts = Post.objects.filter(group=group).select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')
    members = GroupMembership.objects.filter(group=group, is_active=True).select_related('user')

    post_form = None
    if is_member:
        post_form = PostForm()
        if request.method == 'POST' and 'post_submit' in request.POST:
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.author = request.user
                post.group = group
                post.save()
                messages.success(request, 'Публікацію додано до групи.')
                return redirect('group_detail', pk=pk)

    return render(request, 'groups/group_detail.html', {
        'group': group,
        'is_member': is_member,
        'is_admin': is_admin,
        'posts': posts,
        'members': members,
        'post_form': post_form,
    })


@login_required
def create_group_view(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            GroupMembership.objects.create(group=group, user=request.user, role='admin')
            messages.success(request, f'Групу «{group.name}» створено.')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupForm()
    return render(request, 'groups/create_group.html', {'form': form})


@login_required
def join_group_view(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership, created = GroupMembership.objects.get_or_create(
        group=group, user=request.user,
        defaults={'is_active': True}
    )
    if not created and not membership.is_active:
        membership.is_active = True
        membership.save()
    messages.success(request, f'Ви приєдналися до групи «{group.name}».')
    return redirect('group_detail', pk=pk)


@login_required
def leave_group_view(request, pk):
    group = get_object_or_404(Group, pk=pk)
    GroupMembership.objects.filter(group=group, user=request.user).update(is_active=False)
    messages.info(request, f'Ви вийшли з групи «{group.name}».')
    return redirect('groups')


@login_required
def kick_member_view(request, pk, user_id):
    group = get_object_or_404(Group, pk=pk)
    admin_membership = GroupMembership.objects.filter(
        group=group, user=request.user, role__in=['admin', 'moderator'], is_active=True
    ).first()
    if not admin_membership:
        messages.error(request, 'Недостатньо прав.')
        return redirect('group_detail', pk=pk)
    GroupMembership.objects.filter(group=group, user_id=user_id).update(is_active=False)
    messages.success(request, 'Учасника видалено.')
    return redirect('group_detail', pk=pk)
