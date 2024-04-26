import psycopg2


class DB:
    def __init__(self, db_config):
        self.db_config = db_config

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def bad_submissions(self, submitter, start_date, end_date):
        query = """
            SELECT 
                submitted_at, 
                verified, 
                validation_error, 
                remote_addr, 
                block_hash, 
                state_hash 
            FROM submissions 
            WHERE 
                submitter = %s 
                AND submitted_at_date BETWEEN %s AND %s
                AND (validation_error != '' OR verified is not true)
            ORDER BY submitted_at DESC;
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (submitter, start_date, end_date))
                    return cursor.fetchall()
        except psycopg2.Error as e:
            print("Database error: ", e)
            return None

    def total_submissions(self, submitter, start_date, end_date):
        query = """
            SELECT 
                COUNT(*) AS total_submissions,
                COUNT(*) FILTER (WHERE validation_error = '') AS validated_submissions,
                COUNT(*) FILTER (WHERE validation_error != '') AS unvalidated_submissions,
                COUNT(*) FILTER (WHERE verified is not true) AS unverified_submissions
            FROM submissions 
            WHERE submitter = %s AND submitted_at_date BETWEEN %s AND %s;
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (submitter, start_date, end_date))
                    return cursor.fetchall()
        except psycopg2.Error as e:
            print("Database error: ", e)
            return None

    def submissions_per_batch(self, submitter, start_date, end_date):
        query = """
            SELECT 
                (to_timestamp(b.batch_start_epoch) AT TIME ZONE 'UTC')::timestamp without time zone as batch_start, 
                (to_timestamp(b.batch_end_epoch) AT TIME ZONE 'UTC')::timestamp without time zone as batch_end, 
                COUNT(s.id) AS total_submissions,
                COUNT(*) FILTER (WHERE s.validation_error = '' AND s.id IS NOT NULL) AS validated_submissions,
                COUNT(*) FILTER (WHERE s.validation_error != '' AND s.id IS NOT NULL) AS unvalidated_submissions,
                COUNT(*) FILTER (WHERE verified IS NOT TRUE AND s.id IS NOT NULL) AS unverified_submissions
            FROM 
                bot_logs b 
            LEFT JOIN 
                submissions s 
            ON 
                s.submitted_at BETWEEN 
                    (to_timestamp(b.batch_start_epoch) AT TIME ZONE 'UTC')::timestamp without time zone 
                AND 
                    (to_timestamp(b.batch_end_epoch) AT TIME ZONE 'UTC')::timestamp without time zone
                AND s.submitter = %s 
                AND s.submitted_at_date BETWEEN %s AND %s
            WHERE 
                b.files_processed > 0 
                AND (to_timestamp(b.batch_start_epoch) AT TIME ZONE 'UTC')::date >= %s 
                AND (to_timestamp(b.batch_end_epoch) AT TIME ZONE 'UTC')::date <= %s
            GROUP BY 
                batch_start, batch_end
            ORDER BY 
                batch_start;
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        query, (submitter, start_date, end_date, start_date, end_date)
                    )
                    return cursor.fetchall()
        except psycopg2.Error as e:
            print("Database error: ", e)
            return None

    def points_per_batch(self, submitter, start_date, end_date):
        query = """
            SELECT 
                (to_timestamp(b.batch_start_epoch) AT TIME ZONE 'UTC')::timestamp without time zone as batch_start, 
                (to_timestamp(b.batch_end_epoch) AT TIME ZONE 'UTC')::timestamp without time zone as batch_end,
                CASE 
                    WHEN SUM(CASE WHEN n.block_producer_key = %s THEN 1 ELSE 0 END) > 0 THEN 1
                    ELSE 0 
                END AS points_granted
            FROM 
                bot_logs b
            LEFT JOIN 
                points_summary ps ON b.id = ps.bot_log_id
            LEFT JOIN 
                nodes n ON ps.node_id = n.id
            WHERE 
                b.files_processed > 0
                AND (to_timestamp(b.batch_start_epoch) AT TIME ZONE 'UTC')::date >= %s 
                AND (to_timestamp(b.batch_end_epoch) AT TIME ZONE 'UTC')::date <= %s
            GROUP BY 
                b.batch_start_epoch, b.batch_end_epoch
            ORDER BY 
                batch_start;
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (submitter, start_date, end_date))
                    return cursor.fetchall()
        except psycopg2.Error as e:
            print("Database error: ", e)
            return None

    def batches_without_points(self, submitter, start_date, end_date):
        query = """
            SELECT 
                (to_timestamp(b.batch_start_epoch) AT TIME ZONE 'UTC')::timestamp without time zone as batch_start, 
                (to_timestamp(b.batch_end_epoch) AT TIME ZONE 'UTC')::timestamp without time zone as batch_end
            FROM 
                bot_logs b
            LEFT JOIN 
                (SELECT bot_log_id, node_id FROM points_summary
                JOIN nodes n ON points_summary.node_id = n.id
                WHERE n.block_producer_key = %s) ps
            ON 
                b.id = ps.bot_log_id
            WHERE 
                ps.bot_log_id IS NULL
                AND b.files_processed > 0
                AND (to_timestamp(b.batch_start_epoch) AT TIME ZONE 'UTC')::date >= %s 
                AND (to_timestamp(b.batch_end_epoch) AT TIME ZONE 'UTC')::date <= %s
            ORDER BY 
                batch_start;
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (submitter, start_date, end_date))
                    return cursor.fetchall()
        except psycopg2.Error as e:
            print("Database error: ", e)
            return None
