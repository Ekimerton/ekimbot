import bitdotio
import os

BITIO_TOKEN = os.environ.get('BITIO_TOKEN')

b = bitdotio.bitdotio(BITIO_TOKEN)


def add_wordle_attempt(user_id, wordle_number, wordle_in, hard_mode, first_guess):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO "Ekimerton/ekimbot"."wordle" (user_id, wordle_number, wordle_in, hard_mode, first_guess)
        VALUES ({user_id}, {wordle_number}, {wordle_in}, {hard_mode}, '{first_guess}')
    '''.format(user_id=user_id, wordle_number=wordle_number, wordle_in=wordle_in,       hard_mode=hard_mode, first_guess=first_guess))
    conn.commit()


def get_latest_wordle():
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT max("wordle_number") FROM "Ekimerton/ekimbot"."wordle"
    ''')
    latest_wordle = cur.fetchone()[0]
    return latest_wordle


def get_wordle_stats(wordle_number):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT count(user_id), avg(wordle_in), min(wordle_in) FROM "Ekimerton/ekimbot"."wordle"
        WHERE "wordle_number" = {wordle_number}
    '''.format(wordle_number=wordle_number))
    daily_stats = cur.fetchone()
    player_count = daily_stats[0]
    avg_attempt = round(daily_stats[1], 2)
    min_attempt = daily_stats[2]

    cur.execute('''
        SELECT DISTINCT user_id FROM "Ekimerton/ekimbot"."wordle"
        WHERE wordle_number = {wordle_number} AND wordle_in = {min_attempt}
    '''.format(wordle_number=wordle_number, min_attempt=min_attempt))
    winners = cur.fetchall()
    winners = [winner[0] for winner in winners]

    return player_count, avg_attempt, min_attempt, winners


def get_alltime_winners():
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT user_id, count(wordle_number) as win_count FROM (
            SELECT DISTINCT user_id, wordle_number FROM "Ekimerton/ekimbot"."wordle" as w1
            WHERE wordle_in = (
                SELECT min(wordle_in) FROM "Ekimerton/ekimbot"."wordle" as w2
                WHERE w2.wordle_number = w1.wordle_number
            ) AND wordle_number > 300 AND hard_mode = true
        ) as w3
        GROUP BY w3.user_id
        ORDER BY win_count DESC LIMIT 3
    ''')
    top_winners = cur.fetchall()
    return top_winners


def get_alltime_averages():
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT user_id, avg(best_in) as avg_in FROM (
            SELECT user_id, wordle_number, min(wordle_in) as best_in FROM "Ekimerton/ekimbot"."wordle"
            WHERE wordle_number > 300 AND hard_mode = true
            GROUP BY user_id, wordle_number) as w1
        GROUP BY w1.user_id
        ORDER BY avg_in LIMIT 3
    ''')
    top_averages = cur.fetchall()
    return top_averages


def get_user_wins(user_id):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT count(1) as win_count FROM (
            SELECT DISTINCT user_id, wordle_number FROM "Ekimerton/ekimbot"."wordle" as w1
            WHERE wordle_in = (
                SELECT min(wordle_in) FROM "Ekimerton/ekimbot"."wordle" as w2
                WHERE w2.wordle_number = w1.wordle_number
            ) AND wordle_number > 300 AND hard_mode = true
        ) as w3
        GROUP BY w3.user_id
        HAVING w3.user_id = {user_id}
    '''.format(user_id=user_id))
    user_stats = cur.fetchone()

    if not user_stats:
        return None

    user_wins = user_stats[0] if user_stats else 0

    return user_wins


def get_user_averages_tries(user_id):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT avg(best_in) AS user_avg, count(1) AS user_days FROM (
            SELECT user_id, wordle_number, min(wordle_in) AS best_in FROM "Ekimerton/ekimbot"."wordle"
            WHERE wordle_number > 300 AND hard_mode = true
            GROUP BY user_id, wordle_number
        ) AS w1
        GROUP BY w1.user_id
        HAVING w1.user_id = {user_id}
    '''.format(user_id=user_id))
    user_stats = cur.fetchone()

    if not user_stats:
        return None

    user_avg = round(user_stats[0], 2)
    user_days = user_stats[1]

    return user_avg, user_days


def get_user_starters(user_id):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT DISTINCT wordle_number, first_guess FROM "Ekimerton/ekimbot"."wordle"
        WHERE user_id = {user_id} AND first_guess IS NOT NULL AND wordle_number > 300
        ORDER BY wordle_number DESC
    '''.format(user_id=user_id))
    user_starters = cur.fetchall()
    return user_starters
