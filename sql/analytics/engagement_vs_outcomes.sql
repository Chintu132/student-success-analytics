-- ============================================================
-- ENGAGEMENT VS OUTCOMES
-- Does LMS engagement actually predict grades?
-- ============================================================
SELECT
    CASE
        WHEN we.total_clicks < 100 THEN '1. Low (<100 clicks)'
        WHEN we.total_clicks < 500 THEN '2. Medium (100-500)'
        WHEN we.total_clicks < 1000 THEN '3. High (500-1000)'
        ELSE '4. Very High (1000+)'
    END AS engagement_tier,
    COUNT(DISTINCT we.id_student) AS students,
    AVG(e.grade_points) AS avg_gpa,
    ROUND(SUM(CASE WHEN e.passed = 1 THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 1) AS pass_rate_pct,
    ROUND(SUM(CASE WHEN e.withdrew = 1 THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 1) AS withdraw_rate_pct
FROM fact_enrollment e
JOIN (
    SELECT id_student, code_module, code_presentation, SUM(total_clicks) AS total_clicks
    FROM fact_weekly_engagement
    GROUP BY id_student, code_module, code_presentation
) we ON we.id_student = e.id_student
    AND we.code_module = e.code_module
    AND we.code_presentation = e.code_presentation
GROUP BY 1
ORDER BY 1;
