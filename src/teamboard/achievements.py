from math import floor

from random import random

from flask import Blueprint, render_template
from flask import current_app

ach_app = Blueprint("achievements_app", __name__)


def calculate_achievement(achievement_setting):
    achievement = dict(achievement_setting)

    achievement['progress'] = round(random() * 200)
    achievement['progress_percent'] = floor(100.0 * achievement['progress'] / achievement['count'])
    achievement['style'] = "green-blink" if achievement['progress_percent'] >= 100.0 else ""

    return achievement


@ach_app.route("/")
def get_achievements():
    achievement_settings = current_app.config.get('TEAMBOARD_SETTINGS')['achievements']

    achievements = []
    for achievement_setting in achievement_settings:
        achievement = calculate_achievement(achievement_setting)
        achievements.append(achievement)

    return render_template('achievements.html', achievements=achievements)
