from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from app.models import Item


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        call_command('flush', interactive=False)

        User = get_user_model()
        users=[]
        for i in range(1,4):
            user=User.objects.create_user(
                username=f'user{i}',
                password='password123'
            )
            
            users.append(user)
            
        Item.objects.create(
            item_name='broken piano',
            item_loaner=users[0]
        )
        Item.objects.create(
            item_name='walking talking guitar',
            item_loaner=users[2]
        )
        Item.objects.create(
            item_name='burnt man',
            item_loaner=None
        )
        Item.objects.create(
            item_name='destroyed car',
            item_loaner=users[1]
        )
        Item.objects.create(
            item_name='upside-down mountain',
            item_loaner=None
        )
        Item.objects.create(
            item_name='black hole',
            item_loaner=users[1]
        )
        Item.objects.create(
            item_name='crazy zombie',
            item_loaner=None
        )
        Item.objects.create(
            item_name='what else',
            item_loaner=None
        )
        Item.objects.create(
            item_name='ihan mitä vaan',
            item_loaner=users[2]
        )