import bitdotio
import os

BITIO_TOKEN = os.environ.get('BITIO_TOKEN')
SEASONS_START = [302, 360]
SEASONS_HARD = [True, True, False]

b = bitdotio.bitdotio(BITIO_TOKEN)


def add_wordle_attempt(user_id, wordle_number, wordle_in, hard_mode, first_guess):
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO "Ekimerton/ekimbot"."wordle" (user_id, wordle_number, wordle_in, hard_mode, first_guess)
                VALUES ({user_id}, {wordle_number}, {wordle_in}, {hard_mode}, '{first_guess}')
            '''.format(user_id=user_id, wordle_number=wordle_number, wordle_in=wordle_in, hard_mode=hard_mode, first_guess=first_guess))
            conn.commit()


def get_latest_wordle():
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT max("wordle_number") FROM "Ekimerton/ekimbot"."wordle"
            ''')
            latest_wordle = cur.fetchone()[0]
            return latest_wordle


def get_wordle_stats(wordle_number):
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
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
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT user_id, count(wordle_number) as win_count FROM (
                    SELECT DISTINCT user_id, wordle_number FROM "Ekimerton/ekimbot"."wordle" as w1
                    WHERE wordle_in = (
                        SELECT min(wordle_in) FROM "Ekimerton/ekimbot"."wordle" as w2
                        WHERE w2.wordle_number = w1.wordle_number
                    ) AND wordle_number > 360
                ) as w3
                GROUP BY w3.user_id
                ORDER BY win_count DESC LIMIT 3
            ''')
            top_winners = cur.fetchall()
            return top_winners


def get_alltime_averages():
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT user_id, avg(best_in) as avg_in FROM (
                    SELECT user_id, wordle_number, min(wordle_in) as best_in FROM "Ekimerton/ekimbot"."wordle"
                    WHERE wordle_number > {season}
                    GROUP BY user_id, wordle_number) as w1
                GROUP BY w1.user_id
                ORDER BY avg_in LIMIT 3
            '''.format(season=SEASONS_START[-1]))
            top_averages = cur.fetchall()
            return top_averages


def get_user_wins(user_id):
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT count(1) as win_count FROM (
                    SELECT DISTINCT user_id, wordle_number FROM "Ekimerton/ekimbot"."wordle" as w1
                    WHERE wordle_in = (
                        SELECT min(wordle_in) FROM "Ekimerton/ekimbot"."wordle" as w2
                        WHERE w2.wordle_number = w1.wordle_number
                    ) AND wordle_number > {season}
                ) as w3
                GROUP BY w3.user_id
                HAVING w3.user_id = {user_id}
            '''.format(user_id=user_id, season=SEASONS_START[0]))
            user_stats = cur.fetchone()

            if not user_stats:
                return None

            user_wins = user_stats[0] if user_stats else 0

            return user_wins


def get_user_averages_tries(user_id):
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT avg(best_in) AS user_avg, count(1) AS user_days FROM (
                    SELECT user_id, wordle_number, min(wordle_in) AS best_in FROM "Ekimerton/ekimbot"."wordle"
                    WHERE wordle_number > {season}
                    GROUP BY user_id, wordle_number
                ) AS w1
                GROUP BY w1.user_id
                HAVING w1.user_id = {user_id}
            '''.format(user_id=user_id, season=SEASONS_START[0]))
            user_stats = cur.fetchone()

            if not user_stats:
                return None, None

            user_avg = round(user_stats[0], 2)
            user_days = user_stats[1]

            return user_avg, user_days


def get_user_trophies(user_id):
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
            pass


def get_season_winners(season_num):
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT user_id, final_rank from 
                    (SELECT t1.user_id, (win_rank + avg_rank) as final_score, RANK() OVER (ORDER BY (win_rank + avg_rank)) as final_rank FROM
                        (SELECT user_id, count(wordle_number) as win_count, RANK() OVER (ORDER BY count(wordle_number) DESC) as win_rank FROM (
                            SELECT DISTINCT user_id, wordle_number FROM "Ekimerton/ekimbot"."wordle" as w11
                            WHERE wordle_in = (
                                SELECT min(wordle_in) FROM "Ekimerton/ekimbot"."wordle" as w12
                                    WHERE w12.wordle_number = w11.wordle_number
                                ) AND wordle_number > 302 AND wordle_number <= 360 AND hard_mode = True
                            ) as w13
                        GROUP BY w13.user_id) t1
                        INNER JOIN
                        (SELECT user_id, avg(best_in) as avg_in, RANK() OVER (ORDER BY avg(best_in)) as avg_rank FROM (
                            SELECT user_id, wordle_number, min(wordle_in) as best_in FROM "Ekimerton/ekimbot"."wordle"
                            WHERE wordle_number > 302 AND wordle_number <= 360 AND hard_mode = True
                            GROUP BY user_id, wordle_number) as w21
                        GROUP BY w21.user_id) t2
                    ON t1.user_id = t2.user_id) as temp
                WHERE final_rank < 4
            ''')


def get_user_starters(user_id):
    with b.get_connection("Ekimerton/ekimbot") as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT DISTINCT wordle_number, first_guess FROM "Ekimerton/ekimbot"."wordle"
                WHERE user_id = {user_id} AND first_guess IS NOT NULL AND wordle_number > {season}
                ORDER BY wordle_number DESC
            '''.format(user_id=user_id, season=SEASONS_START[0]))
            user_starters = cur.fetchall()
            return user_starters
