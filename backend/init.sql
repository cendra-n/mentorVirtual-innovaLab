-- ============================================================
--  Mentor Virtual Adaptativo — init.sql
--  Tablas propias + Stored Procedures
--  Las tablas de auth.* las crea Django con migrate
-- ============================================================

-- ── Tablas ───────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS goals (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    goal_text   TEXT    NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'active',   -- active | completed | archived
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_goals_user ON goals(user_id);

CREATE TABLE IF NOT EXISTS steps (
    id             SERIAL PRIMARY KEY,
    goal_id        INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    "order"        SMALLINT NOT NULL,
    title          VARCHAR(255) NOT NULL,
    description    TEXT,
    youtube_query  TEXT,
    completed      BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at   TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_steps_goal ON steps(goal_id);

CREATE TABLE IF NOT EXISTS videos (
    id         SERIAL PRIMARY KEY,
    step_id    INTEGER NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    video_id   VARCHAR(20)  NOT NULL,   -- YouTube video ID
    title      TEXT         NOT NULL,
    thumbnail  TEXT,
    url        TEXT         NOT NULL,
    channel    VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS logros (
    id           SERIAL PRIMARY KEY,
    goal_id      INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    name         VARCHAR(100) NOT NULL,
    description  TEXT,
    icon         VARCHAR(10)  NOT NULL DEFAULT '🏆',
    unlocked     BOOLEAN      NOT NULL DEFAULT FALSE,
    unlocked_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS user_progress (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    step_id      INTEGER NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, step_id)
);

CREATE TABLE IF NOT EXISTS video_views (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    video_id    INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    step_id     INTEGER NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    viewed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, video_id)
);

CREATE TABLE IF NOT EXISTS streaks (
    user_id         INTEGER PRIMARY KEY REFERENCES auth_user(id) ON DELETE CASCADE,
    current_streak  INTEGER NOT NULL DEFAULT 0,
    longest_streak  INTEGER NOT NULL DEFAULT 0,
    last_activity   DATE
);


-- ── Stored Procedures ─────────────────────────────────────────────────────────

-- ── Goals ──────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION sp_get_goal_by_user_and_text(p_user_id INT, p_goal_text TEXT)
RETURNS TABLE(id INT, user_id INT, goal_text TEXT, status VARCHAR, created_at TIMESTAMPTZ) AS $$
BEGIN
    RETURN QUERY
    SELECT g.id, g.user_id, g.goal_text, g.status, g.created_at
    FROM goals g
    WHERE g.user_id = p_user_id
      AND LOWER(TRIM(g.goal_text)) = LOWER(TRIM(p_goal_text))
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_create_goal(p_user_id INT, p_goal_text TEXT)
RETURNS TABLE(id INT) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO goals (user_id, goal_text)
    VALUES (p_user_id, p_goal_text)
    RETURNING goals.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_goals_by_user(p_user_id INT)
RETURNS TABLE(
    id INT, goal_text TEXT, status VARCHAR, created_at TIMESTAMPTZ,
    total_steps BIGINT, completed_steps BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        g.id,
        g.goal_text,
        g.status,
        g.created_at,
        COUNT(s.id)                                          AS total_steps,
        COUNT(s.id) FILTER (WHERE s.completed = TRUE)       AS completed_steps
    FROM goals g
    LEFT JOIN steps s ON s.goal_id = g.id
    WHERE g.user_id = p_user_id
    GROUP BY g.id
    ORDER BY g.created_at DESC;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_goal_detail(p_goal_id INT, p_user_id INT)
RETURNS TABLE(id INT, user_id INT, goal_text TEXT, status VARCHAR, created_at TIMESTAMPTZ) AS $$
BEGIN
    RETURN QUERY
    SELECT g.id, g.user_id, g.goal_text, g.status, g.created_at
    FROM goals g
    WHERE g.id = p_goal_id AND g.user_id = p_user_id
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;


-- ── Steps ──────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION sp_create_step(
    p_goal_id INT, p_order SMALLINT, p_title VARCHAR, p_description TEXT, p_youtube_query TEXT
)
RETURNS TABLE(id INT) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO steps (goal_id, "order", title, description, youtube_query)
    VALUES (p_goal_id, p_order, p_title, p_description, p_youtube_query)
    RETURNING steps.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_steps_by_goal(p_goal_id INT, p_user_id INT)
RETURNS TABLE(
    id INT, goal_id INT, "order" SMALLINT, title VARCHAR,
    description TEXT, completed BOOLEAN, completed_at TIMESTAMPTZ
) AS $$
BEGIN
    -- Verifica que el goal pertenezca al usuario
    IF NOT EXISTS (SELECT 1 FROM goals WHERE id = p_goal_id AND user_id = p_user_id) THEN
        RETURN;
    END IF;

    RETURN QUERY
    SELECT s.id, s.goal_id, s."order", s.title, s.description, s.completed, s.completed_at
    FROM steps s
    WHERE s.goal_id = p_goal_id
    ORDER BY s."order";
END;
$$ LANGUAGE plpgsql;


-- ── Videos ─────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION sp_save_video(
    p_step_id INT, p_video_id VARCHAR, p_title TEXT,
    p_thumbnail TEXT, p_url TEXT, p_channel VARCHAR
)
RETURNS TABLE(id INT) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO videos (step_id, video_id, title, thumbnail, url, channel)
    VALUES (p_step_id, p_video_id, p_title, p_thumbnail, p_url, p_channel)
    RETURNING videos.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_videos_by_step(p_step_id INT)
RETURNS TABLE(id INT, step_id INT, video_id VARCHAR, title TEXT, thumbnail TEXT, url TEXT, channel VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT v.id, v.step_id, v.video_id, v.title, v.thumbnail, v.url, v.channel
    FROM videos v
    WHERE v.step_id = p_step_id;
END;
$$ LANGUAGE plpgsql;


-- ── Logros ─────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION sp_create_logro(
    p_goal_id INT, p_name VARCHAR, p_description TEXT, p_icon VARCHAR
)
RETURNS TABLE(id INT) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO logros (goal_id, name, description, icon)
    VALUES (p_goal_id, p_name, p_description, p_icon)
    RETURNING logros.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_logros_by_goal(p_goal_id INT)
RETURNS TABLE(
    id INT, goal_id INT, name VARCHAR, description TEXT,
    icon VARCHAR, unlocked BOOLEAN, unlocked_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT l.id, l.goal_id, l.name, l.description, l.icon, l.unlocked, l.unlocked_at
    FROM logros l
    WHERE l.goal_id = p_goal_id
    ORDER BY l.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_user_logros(p_user_id INT)
RETURNS TABLE(
    id INT, goal_id INT, goal_text TEXT, name VARCHAR, description TEXT,
    icon VARCHAR, unlocked BOOLEAN, unlocked_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT l.id, l.goal_id, g.goal_text, l.name, l.description, l.icon, l.unlocked, l.unlocked_at
    FROM logros l
    JOIN goals g ON g.id = l.goal_id
    WHERE g.user_id = p_user_id
    ORDER BY l.unlocked DESC, l.id;
END;
$$ LANGUAGE plpgsql;


-- Desbloquea logros según el % de avance del goal
CREATE OR REPLACE FUNCTION sp_unlock_logro_if_eligible(p_goal_id INT, p_user_id INT)
RETURNS TABLE(id INT, name VARCHAR, description TEXT, icon VARCHAR) AS $$
DECLARE
    v_total     INT;
    v_completed INT;
    v_pct       NUMERIC;
BEGIN
    SELECT COUNT(*) INTO v_total    FROM steps WHERE goal_id = p_goal_id;
    SELECT COUNT(*) INTO v_completed FROM steps WHERE goal_id = p_goal_id AND completed = TRUE;

    IF v_total = 0 THEN RETURN; END IF;
    v_pct := (v_completed::NUMERIC / v_total) * 100;

    -- Lógica: 1er logro al 25%, 2do al 60%, 3ro al 100%
    IF v_pct >= 25 THEN
        UPDATE logros SET unlocked = TRUE, unlocked_at = NOW()
        WHERE goal_id = p_goal_id AND unlocked = FALSE
          AND id = (SELECT MIN(id) FROM logros WHERE goal_id = p_goal_id AND unlocked = FALSE);
    END IF;

    IF v_pct >= 60 THEN
        UPDATE logros SET unlocked = TRUE, unlocked_at = NOW()
        WHERE goal_id = p_goal_id AND unlocked = FALSE
          AND id = (SELECT MIN(id) FROM logros WHERE goal_id = p_goal_id AND unlocked = FALSE);
    END IF;

    IF v_pct >= 100 THEN
        UPDATE logros SET unlocked = TRUE, unlocked_at = NOW()
        WHERE goal_id = p_goal_id AND unlocked = FALSE;
    END IF;

    -- Devuelve logros recién desbloqueados en esta llamada
    RETURN QUERY
    SELECT l.id, l.name, l.description, l.icon
    FROM logros l
    WHERE l.goal_id = p_goal_id
      AND l.unlocked = TRUE
      AND l.unlocked_at >= NOW() - INTERVAL '5 seconds';
END;
$$ LANGUAGE plpgsql;


-- ── User Progress ──────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION sp_complete_step(p_step_id INT, p_user_id INT)
RETURNS TABLE(step_id INT, completed BOOLEAN, already_completed BOOLEAN) AS $$
DECLARE
    v_already BOOLEAN := FALSE;
BEGIN
    -- ¿Ya estaba completado?
    SELECT TRUE INTO v_already FROM user_progress
    WHERE user_progress.step_id = p_step_id AND user_id = p_user_id;

    IF NOT FOUND THEN
        INSERT INTO user_progress (user_id, step_id) VALUES (p_user_id, p_step_id)
        ON CONFLICT DO NOTHING;

        UPDATE steps SET completed = TRUE, completed_at = NOW()
        WHERE id = p_step_id;
    END IF;

    RETURN QUERY SELECT p_step_id, TRUE, COALESCE(v_already, FALSE);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_user_progress(p_user_id INT, p_goal_id INT)
RETURNS TABLE(
    goal_id INT, total_steps BIGINT, completed_steps BIGINT,
    percent_complete NUMERIC, goal_completed BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p_goal_id,
        COUNT(s.id),
        COUNT(s.id) FILTER (WHERE s.completed = TRUE),
        CASE WHEN COUNT(s.id) = 0 THEN 0
             ELSE ROUND((COUNT(s.id) FILTER (WHERE s.completed = TRUE)::NUMERIC / COUNT(s.id)) * 100, 1)
        END,
        COUNT(s.id) = COUNT(s.id) FILTER (WHERE s.completed = TRUE)
    FROM steps s
    JOIN goals g ON g.id = s.goal_id
    WHERE s.goal_id = p_goal_id AND g.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;


-- ── Video Views ────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION sp_register_video_view(p_user_id INT, p_video_id INT, p_step_id INT)
RETURNS TABLE(view_id INT, already_viewed BOOLEAN) AS $$
DECLARE
    v_view_id INT;
    v_already BOOLEAN := FALSE;
BEGIN
    SELECT id INTO v_view_id FROM video_views
    WHERE user_id = p_user_id AND video_id = p_video_id;

    IF FOUND THEN
        v_already := TRUE;
    ELSE
        INSERT INTO video_views (user_id, video_id, step_id)
        VALUES (p_user_id, p_video_id, p_step_id)
        RETURNING id INTO v_view_id;
    END IF;

    RETURN QUERY SELECT v_view_id, v_already;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_viewed_videos(p_user_id INT, p_goal_id INT)
RETURNS TABLE(video_id INT, title TEXT, step_id INT, viewed_at TIMESTAMPTZ) AS $$
BEGIN
    RETURN QUERY
    SELECT vv.video_id, v.title, vv.step_id, vv.viewed_at
    FROM video_views vv
    JOIN videos v  ON v.id   = vv.video_id
    JOIN steps  s  ON s.id   = vv.step_id
    WHERE vv.user_id = p_user_id AND s.goal_id = p_goal_id
    ORDER BY vv.viewed_at DESC;
END;
$$ LANGUAGE plpgsql;


-- ── Streaks ────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION sp_update_streak(p_user_id INT)
RETURNS TABLE(current_streak INT, longest_streak INT, last_activity DATE) AS $$
DECLARE
    v_today         DATE := CURRENT_DATE;
    v_last_activity DATE;
    v_current       INT;
    v_longest       INT;
BEGIN
    SELECT s.last_activity, s.current_streak, s.longest_streak
    INTO v_last_activity, v_current, v_longest
    FROM streaks s WHERE s.user_id = p_user_id;

    IF NOT FOUND THEN
        INSERT INTO streaks (user_id, current_streak, longest_streak, last_activity)
        VALUES (p_user_id, 1, 1, v_today);
        RETURN QUERY SELECT 1, 1, v_today;
        RETURN;
    END IF;

    IF v_last_activity = v_today THEN
        -- Ya hubo actividad hoy, no cambiar
        RETURN QUERY SELECT v_current, v_longest, v_last_activity;
        RETURN;
    ELSIF v_last_activity = v_today - INTERVAL '1 day' THEN
        -- Día consecutivo
        v_current := v_current + 1;
    ELSE
        -- Rompió el streak
        v_current := 1;
    END IF;

    v_longest := GREATEST(v_current, v_longest);

    UPDATE streaks
    SET current_streak = v_current, longest_streak = v_longest, last_activity = v_today
    WHERE user_id = p_user_id;

    RETURN QUERY SELECT v_current, v_longest, v_today;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sp_get_streak(p_user_id INT)
RETURNS TABLE(current_streak INT, longest_streak INT, last_activity DATE) AS $$
BEGIN
    RETURN QUERY
    SELECT s.current_streak, s.longest_streak, s.last_activity
    FROM streaks s WHERE s.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;
