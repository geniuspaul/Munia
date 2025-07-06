from .models import Leaderboard

def update_leaderboard():
    leaderboard = Leaderboard.objects.all().order_by('-balance')

    for rank, entry in enumerate(leaderboard, start=1):
        if entry.rank != rank:
            entry.rank = rank
            entry.save(update_fields=['rank'])